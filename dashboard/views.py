import os
import re
import datetime
import json
import logging
from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from dashboard.models import RecoveryLink, ProgressTracker, Module
from dashboard.serializers import ModuleSerializer, UserProfileReadSerializer, UserProfileWriteSerializer, \
    QuovoUserSerializer
from humanResources.models import SetUpUser
from sources.quovo import Quovo
from sources import mailchimp
from Vestivise import Vestivise, permission

logger = logging.getLogger('vestivise_exception')


# ROUTE VIEWS
def dashboard(request):
    if not request.user.is_authenticated() or not hasattr(request.user, "profile"):
        return redirect(reverse('loginPage'))
    progress = request.user.profile.progress
    progress.last_dashboard_view = timezone.now()
    progress.save()
    return render(request, "clientDashboard/clientDashboard.html", context={
        "isDemo": False
    })


def demo(request):
    return render(request, "clientDashboard/clientDashboard.html", context={
        "isDemo": True
    })


def home_router(request):
    if request.user.is_authenticated() and hasattr(request.user, "profile"):
        return redirect(reverse('dashboard'))
    return redirect(reverse('loginPage'))


def logout(request):
    auth_logout(request)
    return redirect(reverse('loginPage'))


def login_page(request):
    if request.user.is_authenticated() and hasattr(request.user, "profile"):
        return redirect(reverse('dashboard'))
    return render(request, "clientDashboard/clientLogin.html")


def sign_up_page(request, magic_link):
    #check if magic link is valid
    context = {
        "setUpUserID": "",
        "email": ""
    }
    if magic_link:
        setup_user = get_object_or_404(SetUpUser, magic_link=magic_link, is_active=False)
        context = {
            "setUpUserID": setup_user.id,
            "email": setup_user.email
        }
    return render(request, "clientDashboard/registration.html", context=context)


def settings_page(request):
    if not request.user.is_authenticated() or not hasattr(request.user, "profile"):
        return redirect(reverse('loginPage'))
    return render(request, "clientDashboard/settingsPage.html", context={
        "email": request.user.email
    })


def password_recovery_page_handler(request, link):
    context = {
        'linkID': ""
    }
    if link:
        link_id = get_object_or_404(RecoveryLink, link=link)
        context = {'linkID': link_id.id}
    return render(request, 'clientDashboard/passwordRecovery.html', context=context)


# VIEW SETS

@api_view(['POST'])
def track_progress(request):
    data = request.data
    track_info = data.get("track_info")
    ProgressTracker.track_progress(request.user, track_info)
    return Vestivise.network_response("ok")


@api_view(['POST'])
def password_reset(request):
    data = request.data
    try:
        validate(data)
        link_id = data.get('linkID')
        recovery_link = RecoveryLink.objects.filter(id=link_id).first()
        user = recovery_link.user
        password = data.get('password')
        user.set_password(password)
        user.save()
        recovery_link.delete()
        return Vestivise.network_response("success")
    except Vestivise.VestiviseException as e:
        e.log_error()
        return e.generate_error_response()


@api_view(['PUT'])
def profile_update(request):
    data = request.data
    try:
        user = request.user
        email = data.get('email')
        password = data.get('password')
        if not password:
            data.pop('password', None)
        validate(data)
        if password:
            user.set_password(password)
        if email != user.email:
            user_validation_field_validation(email)
            user.email = email
        user.save()
        return Vestivise.network_response("success")
    except Vestivise.VestiviseException as e:
        e.log_error()
        return e.generate_error_response()


@api_view(['POST'])
def password_recovery(request):
    email = request.data.get('email')
    user = get_user_model().objects.filter(email=email).first()
    if user:
        rl = RecoveryLink.objects.create(user=user)
        domain = request.build_absolute_uri('/')[:-1]
        link = domain + reverse('passwordRecoveryPage', kwargs={'link': rl.link})
        mailchimp.send_password_reset_email(email, link)
    return Vestivise.network_response({
        'status': 'success'
    })


@api_view(['POST'])
def subscribe_to_sales_list(request):

    def set_cookie(response, key, value, days_expire=7):
        max_age = days_expire * 24 * 60 * 60
        if days_expire is None:
            max_age = 365 * 24 * 60 * 60  # one year
        expires_raw = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
        expires = expires_raw.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                            secure=settings.SESSION_COOKIE_SECURE or None)
    data = request.data
    name = data.get("name")
    company = data.get("company")
    email = data.get("email")
    mailchimp.subscribe_to_sales_lead(name, company, email)
    network_response = Vestivise.network_response("success")
    set_cookie(network_response, 'demo_access', True)
    return network_response


# TEST VIEWS
@api_view(('GET',))
def dashboard_test_data(request):
    payload = {}
    json_file = open(os.path.join(settings.BASE_DIR, 'dashboard/fixtures/demo_user.json'))
    demo_data = json.loads(json_file.read())

    modules = Module.objects.all()
    modules_dict = ModuleSerializer(modules, many=True).data

    for key, value in demo_data.iteritems():
        payload[key] = value

    payload['modules'] = modules_dict

    return Vestivise.network_response(payload)


# VIEW SETS
@permission_classes((IsAuthenticated,))
class UserProfileView(APIView):
    def get_object(self):
        return self.request.user.profile

    def needs_mfa_notification(self, questions):
        result = {
            "has_mfa_notification" : False,
            "notification_count" : 0
        }
        for question in questions:
            if question.get("should_answer"):
                result["has_mfa_notification"] = True
                result["notification_count"] += 1
        return result

    def get(self, request):
        serializer = UserProfileReadSerializer(self.get_object())
        data = serializer.data

        modules = Module.objects.all()
        modules_dict = ModuleSerializer(modules, many=True).data

        data["modules"] = modules_dict

        # if linked and completed then display dashboard
        # if not linked and not completed then prompt to link
        # if linked and not completed - number monkeys
        data["isCompleted"] = True
        data["isLinked"] = True
        data["notification"] = {
            "has_mfa_notification" : False,
            "notification_count" : 0
        }
        if len(data.get("accounts")) > 0:
            quovo_user = self.request.user.profile.quovoUser
            data["isCompleted"] = len(quovo_user.get_display_holdings()) != 0
            try:
                accounts = Quovo.get_accounts(quovo_user.quovoID).get("accounts")
                questions = []
                for account in accounts:
                    questions += Quovo.get_mfa_questions(account.get("id")).get("challenges")
                data["notification"] = self.needs_mfa_notification(questions)
            except Vestivise.VestiviseException as e:
                e.log_error()

        else:
            data["isLinked"] = False
            data["notification"]["has_mfa_notification"] = True
            data["notification"]["notification_count"] = 1

        ProgressTracker.track_progress(self.request.user, {
            "track_id": "did_open_dashboard",
            "track_data": data["isLinked"] and data["isCompleted"]
        })

        return Vestivise.network_response(data)


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


# AUTHENTICATION VIEWS
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    try:
        verify_user(user, request)
        return Vestivise.network_response("User login sucesss")
    except Vestivise.VestiviseException as e:
        return e.generate_error_response()


@api_view(['POST'])
def register(request):
    """
    request params:
    setUpUserID,
    password,
    expectedRetirementAge,
    zipCode,
    birthday,
    firstName,
    lastName
    """
    data = request.data

    set_up_user_id = data.get("setUpUserID")

    set_up_user = SetUpUser.objects.filter(id=set_up_user_id).first()

    email = data.get('username')
    company = set_up_user.company if set_up_user else None

    data["email"] = data.get('username')
    data["company"] = company

    username, password, email = strip_data(
        data.get('username'),
        data.get('password'),
        email
    )

    try:
        validate(data)
        is_valid_email(email)
        user_validation_field_validation(email)
    except Vestivise.VestiviseException as e:
        e.log_error()
        return e.generate_error_response()

    # remove whitespace
    remove_whitespace_from_data(data)
    data['birthday'] = parse(data['birthday']).date()
    try:
        serializer = validate_user_profile(data)
        quovoAccount = create_quovo_user(username)
        profileUser = serializer.save(user=create_user(password, email))
        create_local_quovo_user(quovoAccount["user"]["id"], profileUser.id)
        if set_up_user:
            set_up_user.activate()
        subscribe_mailchimp(email)
        return Vestivise.network_response("user profile created")
    except Vestivise.VestiviseException as e:
        e.log_error()
        return e.generate_error_response()


# ACCOUNT SETTING
@permission_classes((IsAuthenticated, permission.QuovoAccountPermission))
class QuovoAccountQuestionView(APIView):

    def get(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovo_id = quovo_user.quovo_id
        response = Quovo.get_mfa_questions(quovo_id)
        return Vestivise.network_response(response)

    def put(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovo_id = quovo_user.quovoID

        payload = request.PUT
        answer = payload.get("answer")
        question = payload.get("question")
        try:
            response = Quovo.answer_mfa_question(quovo_id, question=question, answer=answer)
            return Vestivise.network_response(response)
        except Vestivise.VestiviseException as e:
            e.log_error()
            return e.generate_error_response()


@permission_classes((permission.QuovoAccountPermission, ))
class QuovoSyncView(APIView):

    def get(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovo_id = quovo_user.quovo_id
        response = Quovo.get_sync_status(quovo_id)
        return Vestivise.network_response(response)

    def post(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovo_id = quovo_user.quovo_id
        response = Quovo.sync_account(quovo_id)
        return Vestivise.network_response(response)


# GET IFRAME
@api_view(['GET'])
@permission_classes((IsAuthenticated,permission.QuovoAccountPermission))
def get_iframe_widget(request):
    quovo_user = request.user.profile.get_quovo_user()
    quovo_id = quovo_user.quovoID
    try:
        url = Quovo.get_iframe_url(quovo_id)
        return Vestivise.network_response({
            "iframe_url": url
        })
    except Vestivise.VestiviseException as e:
        e.log_error()
        return e.generate_error_response()


# AUXILARY METHODS
def verify_user(user, request):
    """
    Verifies if a user credentials are correct
    """
    if user is not None and hasattr(user, "profile"):
        auth_login(request, user)
    else:
        # the authentication system was unable to verify the username and password
        raise Vestivise.LoginException("username or password was incorrect")


def validate(payload):
    """
    Validate payload for user registration
    password: needs to be of length 8 and have special characters, lower case and uppercase
    username: needs to be less than length and cannot be empty
    email: cannot be empty email
    first name and last name: cannot be empty
    state: cannot be empty
    """

    def is_date(string):
        try:
            parse(string)
            return True
        except ValueError:
            return False

    error_dict = {}
    error = False
    for key, value in payload.iteritems():
        if key == 'password' and not re.match(r'^(?=.{8,})(?=.*[a-z])(?=.*[0-9])(?=.*[A-Z])(?=.*[!@#$%^&+=]).*$',
                                              value):
            error = True
            error_dict[key] = "At least 8 characters, upper, lower case characters, " \
                              "a number, and any one of these characters !@#$%^&*()"
        elif key == 'email' and (not value.strip() or not value or "@" not in value):
            error = True
            error_dict[key] = "Please enter a valid email"
        elif(key == 'birthday' and not value) or (key == 'birthday' and not is_date(value)):
            error = True
            error_dict[key] = "Incorrect data format, should be MM/DD/YYYY"
    if error:
        raise Vestivise.UserCreationException(error_dict)
    return True


def validate_user_profile(data):
    """
    Validate profile user
    :param data: user profile data
    :return: serializer if valid
    """
    serializer = UserProfileWriteSerializer(data=data)
    if serializer.is_valid():
        return serializer
    raise Vestivise.UserCreationException(serializer.errors)


def create_quovo_user(username):
    """
    Creates Quovo User in Quovo's service
    :return: quovo user object
    """
    try:
        user = Quovo.create_user(username)
        return user
    except Vestivise.QuovoRequestError as e:
        raise Vestivise.UserCreationException(e.message)


def create_local_quovo_user(quovo_id, user_profile):
    """
    Creates QuovoUser object locally
    """
    serializer = QuovoUserSerializer(data={'quovoID': quovo_id, 'userProfile': user_profile})
    if serializer.is_valid():
        serializer.save()
        return True
    else:
        raise Vestivise.UserCreationException(serializer.errors)


def strip_data(username, password, email):
    if username:
        username = username.strip()
    if password:
        password = password.strip()
    if email:
        email = email.strip()
    return username, password, email


def is_valid_email(email):
    try:
        validate_email(email)
    except:
        raise Vestivise.UserCreationException('this is not a valid email')


def user_validation_field_validation(email):
    error_message = {}
    if get_user_model().objects.filter(email=email).exists():
        error_message = {'email': 'email already taken, please try another one'}
    if error_message:
        raise Vestivise.UserCreationException(error_message)


def remove_whitespace_from_data(data):
    for key in data:
        if isinstance(data[key], basestring):
            data[key] = data[key].strip()


def create_user(password, email):
    return get_user_model().objects.create_user(
        password=password,
        email=email
    )


def subscribe_mailchimp(email):
    response = mailchimp.subscribe_to_mailchimp(email)
    if "failure" in response:
        logger.error(response)
