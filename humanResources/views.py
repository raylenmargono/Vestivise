import csv
from django.contrib.auth.models import User
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import PaginateByMaxMixin
from Vestivise.Vestivise import *
import random, string
from Vestivise import permission
from serializers import SetUpUserSerializer, HumanResourceProfileSerializer
from models import SetUpUser
from rest_framework.decorators import api_view, permission_classes
from django import forms
from django.contrib.auth import authenticate, login as auth_login
from Vestivise import mailchimp
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render


#TEMPLATE
def humanResourceLoginPage(request):
    if request.user.is_authenticated() and hasattr(request.user, "humanResourceProfile"):
        return redirect(reverse("humanResourceDashboard"))
    else:
        return render(request, "hrDashboard/hrLogin.html")

def humanResourceAdminPage(request):
    if not request.user.is_authenticated() or not hasattr(request.user, "humanResourceProfile"):
        return redirect(reverse("humanResourceLoginPage"))
    return render(request, "hrDashboard/hrDashboard.html")

class DocumentForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

#VIEWS
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
@permission_classes((IsAuthenticated, permission.HumanResourcePermission))
def add_employees_using_csv(request):

    try:
        confirmDocumentUpload(request.POST, request.FILES)
    except VestiviseException as e:
        e.log_error()
        return e.generateErrorResponse()

    csvfile = request.FILES.get('csv_file')
    user = request.user.humanResourceProfile
    errors, success = generateSetUpUsers(csvfile, user.company)
    for employee in success:
        link, email = employee.get("magic_link"), employee.get('email')
        domain = request.build_absolute_uri('/')[:-1]
        mailchimp.sendMagicLinkNotification(email, domain + reverse('signUpPage', kwargs={'magic_link': link}))

    handle_alert_reached_employee_ceiling(user)

    return network_response({
        "errors" : errors,
        "success" : success
    })

@api_view(['POST'])
@permission_classes((IsAuthenticated, permission.HumanResourcePermission))
def resend_user_creation_email(request):
    try:
        setupUserID = request.data.get('setupUserID')
        setupuser = handle_email_resent_eligibility(setupUserID)
        setupuser.is_active = False
        setupuser.magic_link = generateRandomString()
        setupuser.save()
        domain = request.build_absolute_uri('/')[:-1]
        mailchimp.sendMagicLinkNotification(setupuser.email, domain + reverse('signUpPage', kwargs={'magic_link': setupuser.magic_link}))
        return network_response({
            "email sent to: " + setupuser.email
        })
    except VestiviseException as e:
        return e.generateErrorResponse()


class HumanResourceUserViewSet(viewsets.GenericViewSet,
                               mixins.RetrieveModelMixin):

    serializer_class = HumanResourceProfileSerializer
    permission_classes = [permission.HumanResourcePermission]

    def get_object(self):
        return self.request.user.humanResourceProfile



class EmployeeManagementViewSet(mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.RetrieveModelMixin,
                                PaginateByMaxMixin,
                                viewsets.GenericViewSet):
    '''
    Individual User API
    '''
    serializer_class = SetUpUserSerializer
    permission_classes = [permission.HumanResourcePermission]
    max_paginate_by = 100
    renderer_classes = (VestivseRestRender,)

    def get_queryset(self):
        company = self.request.user.humanResourceProfile.company
        search_query = self.request.query_params.get('search_query', None)
        query_set = SetUpUser.objects.filter(company=company)
        if search_query is not None:
            query_set = query_set.filter(email__contains=search_query)
        return query_set

    def perform_create(self, instance):
        user = self.request.user.humanResourceProfile
        random_string = generateRandomString()
        instance.save(company=user.company, magic_link=random_string)
        domain = self.request.build_absolute_uri('/')[:-1]
        mailchimp.sendMagicLinkNotification(instance.email, domain + reverse('signUpPage', kwargs={'magic_link': random_string}))
        handle_alert_reached_employee_ceiling(user)

    def perform_destroy(self, instance):
        email = instance.email
        if User.objects.filter(email=email).exists():
            User.objects.filter(email=email).delete()
        instance.delete()


#AUXILARY FUNCTIONS

def verifyUser(user, request):
    """
    Verifies if a user credentials are correct
    """
    if user is not None and hasattr(user, "humanResourceProfile"):
        auth_login(request, user)
    else:
        # the authentication system was unable to verify the username and password
        raise LoginException("username or password was incorrect")


def generateSetUpUsers(file, company):
    '''
    Accepts csv file and creates new users
    @param file: csv file with field parameters
    @param company: name of the company
    @:return errors, successes: lists representing failure and success of upload
    '''

    csv_reader = csv.reader(file)

    errors = []
    successes = []
    for line in csv_reader:
        email = line[0]
        success, data = addEmployee(company, email)
        if success:
            successes.append(data)
        else:
            errors.append({
                "position" : csv_reader.line_num,
                "data": data
            })
    return errors, successes


def addEmployee(company, email):
    '''
    Create employee
    @param datas: datas could be list or single object
    @param many: if multiple employees
    '''
    data = {}
    random_string = generateRandomString()
    data["magic_link"] = random_string
    data["company"] = company
    data["email"] = email
    serializer = SetUpUserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return True, serializer.data
    else:
        return False, serializer.errors


def generateRandomString(stop=0, length=15):
    '''
    Generates random string for magic link
    '''
    result = ''.join(random.choice(string.letters + string.digits) for i in range(length))
    if SetUpUser.objects.filter(magic_link=result).exists() and stop != 5:
        result = generateRandomString(stop=stop+1)
    return result


def confirmDocumentUpload(post, file):
    form = DocumentForm(post, file)
    if form.is_valid():
        return True
    raise CSVException(form.errors)


def handle_email_resent_eligibility(setupUserID):
    setupuser = get_object_or_404(SetUpUser, id=setupUserID)
    employee_exists = User.objects.filter(email=setupuser.email).exists()
    if employee_exists:
        raise UserCreationResendException("User already exists")
    return setupuser

def handle_alert_reached_employee_ceiling(human_resource_user):
    company = human_resource_user.company
    setup_user_count = SetUpUser.objects.filter(company=company).count()
    ceiling = human_resource_user.get_employee_ceiling()
    if setup_user_count > ceiling:
        mailchimp.alertEmployeeCeiling(company)