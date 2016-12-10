import os
import re
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from Vestivise import mailchimp as MailChimp
from Vestivise.mailchimp import *
from dashboard.serializers import *
from Vestivise.Vestivise import *
from humanResources.models import SetUpUser
from Vestivise.quovo import Quovo
from Vestivise import permission

# Create your views here.

# ROUTE VIEWS
def dashboard(request):
    #if not request.user.is_authenticated() and hasattr(request.user, "profile"):
    #    return redirect(reverse('loginPage'))
    return render(request, "clientDashboard/clientDashboard.html")


def homeRouter(request):
    if request.user.is_authenticated() and hasattr(request.user, "profile"):
        return redirect(reverse('dashboard'))
    return redirect(reverse('loginPage'))


def logout(request):
    auth_logout(request)
    return redirect(reverse('loginPage'))


def loginPage(request):
    if request.user.is_authenticated() and hasattr(request.user, "profile"):
        return redirect(reverse('dashboard'))
    return render(request, "clientDashboard/clientLogin.html")


def signUpPage(request, magic_link):
    # check if magic link is valid
    get_object_or_404(SetUpUser, magic_link=magic_link, is_active=True)
    if request.user.is_authenticated():
        return redirect(reverse('dashboard'))
    return render(request, "dashboard/registerView.html")


# VIEW SETS
@api_view(['POST'])
def subscribeToSalesList(request):
    fullName = request.POST.get('fullName')
    email = request.POST.get('email')
    company = request.POST.get('company')
    subscribeToSalesLead(fullName, company, email)
    return HttpResponse(status=200)


# TEST VIEWS
@api_view(('GET',))
def dashboardTestData(request):
    jsonFile = open(os.path.join(settings.BASE_DIR, 'dashboard/fixtures/demoData.json'))
    return JsonResponse(json.loads(jsonFile.read()))

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
        serializer = UserProfileWriteSerializer(self.get_object())
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
        if request.user.profile.get_quovo_user().didLink:
            quovo_user = self.request.user.profile.quovoUser
            data["isCompleted"] = quovo_user.isCompleted or quovo_user.getDisplayHoldings().count()
            try:
                accounts = Quovo.get_accounts(quovo_user.quovoID).get("accounts")
                questions = []
                for account in accounts:
                    questions += Quovo.get_mfa_questions(account.get("id")).get("challenges")
                data["notification"] = self.needs_mfa_notification(questions)
            except VestiviseException as e:
                e.log_error()
        else:
            data["isLinked"] = False
            data["notification"]["has_mfa_notification"] = True
            data["notification"]["notification_count"] = 1

        return network_response(data)


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
        verifyUser(user, request)
        return network_response("User login sucesss")
    except VestiviseException as e:
        e.log_error()
        return e.generateErrorResponse()


@api_view(['POST'])
def register(request):
    """
    request params:
    setUpUserID,
    password,
    state,
    zipCode,
    birthday
    """
    data = request.data

    set_up_userid = data["setUpUserID"]

    set_up_user = SetUpUser.objects.get(id=set_up_userid)

    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = set_up_user.email
    company = set_up_user.company

    data["email"] = email
    data["company"] = company

    username, password, email = strip_data(
        data.get('username'),
        data.get('password'),
        email
    )
    try:
        validate(data)
        is_valid_email(email)
        user_validation_field_validation(username, email)
    except VestiviseException as e:
        e.log_error()
        return e.generateErrorResponse()

    # remove whitespace
    remove_whitespace_from_data(data)
    try:
        serializer = validateUserProfile(data)
        quovoAccount = createQuovoUser(email, "%s %s" % (first_name, last_name))
        profileUser = serializer.save(user=create_user(username, password, email))
        createLocalQuovoUser(quovoAccount["user"]["id"], profileUser.id)
        SetUpUser.deleteSetupUser(set_up_userid)
        subscribe_mailchimp(first_name, last_name, email)
        return network_response("user profile created")
    except VestiviseException as e:
        e.log_error()
        return e.generateErrorResponse()


# ACCOUNT SETTING
@permission_classes((IsAuthenticated, permission.QuovoAccountPermission))
class QuovoAccountQuestionView(APIView):

    def get(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovoID = quovo_user.quovoID
        response = Quovo.get_mfa_questions(quovoID)
        return network_response(response)

    def put(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovoID = quovo_user.quovoID

        payload = request.PUT
        answer = payload.get("answer")
        question = payload.get("question")
        try:
            response = Quovo.answer_mfa_question(quovoID, question=question, answer=answer)
            return network_response(response)
        except VestiviseException as e:
            e.log_error()
            return e.generateErrorResponse()


@permission_classes((permission.QuovoAccountPermission, ))
class QuovoSyncView(APIView):

    def get(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovoID = quovo_user.quovoID
        response = Quovo.get_sync_status(quovoID)
        return network_response(response)

    def post(self, request):
        quovo_user = request.user.profile.get_quovo_user()
        quovoID = quovo_user.quovoID
        response = Quovo.sync_account(quovoID)
        return network_response(response)


# GET IFRAME
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_iframe_widget(request):
    quovo_user = request.user.profile.get_quovo_user()
    quovoID = quovo_user.quovoID
    try:
        url = Quovo.get_iframe_url(quovoID)
        return network_response({
            "iframe_url" : url
        })
    except VestiviseException as e:
        e.log_error()
        return e.generateErrorResponse()



# AUXILARY METHODS


def verifyUser(user, request):
    """
    Verifies if a user credentials are correct
    """
    if user is not None and hasattr(user, "profile"):
        auth_login(request, user)
    else:
        # the authentication system was unable to verify the username and password
        raise LoginException("username or password was incorrect")


def validate(payload):
    """
    Validate payload for user registration
    password: needs to be of length 8 and have special characters, lower case and uppercase
    username: needs to be less than length and cannot be empty
    email: cannot be empty email
    first name and last name: cannot be empty
    state: cannot be empty

    """
    errorDict = {}
    error = False
    for key, value in payload.iteritems():
        if key == 'password' and not re.match(r'^(?=.{8,})(?=.*[a-z])(?=.*[0-9])(?=.*[A-Z])(?=.*[!@#$%^&+=]).*$',
                                              value):
            error = True
            errorDict[key] = "At least 8 characters, upper, lower case characters, a number, and any one of these characters !@#$%^&*()"
        elif key == 'username' and (not value.strip()
                                    or not value
                                    or len(value) > 30):
            error = True
            errorDict[key] = "Please enter valid username: less than 30 characters"
        elif key == 'email' and (not value.strip()
                                 or not value
                                 or "@" not in value
                                 ):
            error = True
            errorDict[key] = "Please enter a valid email"
        elif (key == 'state') and not value.strip():
            error = True
            errorDict[key] = "%s cannot be blank" % (key.title())
        elif (key == 'zipCode') and len(value) != 5:
            error = True
            errorDict[key] = "%s must be a valid zip code" % (key.title())
        elif (key == 'firstName' and not value) or (key == 'lastName' and not value):
            error = True
            errorDict[key] = "Cannot be blank"
    if error: raise UserCreationException(errorDict)
    return True


def validateUserProfile(data):
    """
    Validate profile user
    :param data: user profile data
    :return: serializer if valid
    """
    serializer = UserProfileWriteSerializer(data=data)
    if serializer.is_valid():
        return serializer
    raise UserCreationException(serializer.errors)


def createQuovoUser(email, name):
    """
    Creates Quovo User in Quovo's service
    :param email: user's email which will also be the user's username
    :param name: the user's name
    :return: quovo user object
    """
    try:
        user = Quovo.create_user(email, name)
        return user
    except QuovoRequestError as e:
        raise UserCreationException(e.message)


def createLocalQuovoUser(quovoID, userProfile):
    """
    Creates QuovoUser object locally
    :param quovoID: quovo account id
    :param value: value of portfolio
    :param userProfile: user profile id
    """
    serializer = QuovoUserSerializer(data={'quovoID': quovoID, 'userProfile': userProfile})
    if serializer.is_valid():
        serializer.save()
        return True
    else:
        raise UserCreationException(serializer.errors)

def strip_data(username, password, email):
    return (username.strip(), password.strip(), email.strip())


def is_valid_email(email):
    try:
        validate_email(email)
    except:
        raise UserCreationException('this is not a valid email')


def user_validation_field_validation(username, email):
    error_message = {}
    if User.objects.filter(username=username).exists():
        error_message = {'username': 'username exists'}
    elif User.objects.filter(email=email).exists():
        error_message = {'email': 'email already taken, please try another one'}
    if error_message: raise UserCreationException(error_message)


def remove_whitespace_from_data(data):
    for key in data:
        if isinstance(data[key], basestring):
            data[key] = data[key].strip()


def create_user(username, password, email):
    return User.objects.create_user(
        username=username,
        password=password,
        email=email
    )

logger = logging.getLogger('vestivise_exception')
def subscribe_mailchimp(firstName, lastName, email):
    response = MailChimp.subscribeToMailChimp(firstName, lastName, email)
    if response["status"] != 200:
        logger.error(response)
