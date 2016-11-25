import csv
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from Vestivise.Vestivise import *
import random, string
from dashboard.models import UserProfile
from Vestivise import permission
from serializers import SetUpUserSerializer
from models import SetUpUser
from dashboard.serializers import UserProfileReadSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django import forms
from django.contrib.auth import authenticate, login as auth_login
from Vestivise import mailchimp
from django.core.urlresolvers import reverse


#TEMPLATE
def humanResourceLoginPage(request):
    if request.user.is_authenticated() and hasattr(request.user, "humanResourceProfile"):
        pass
    else:
        pass

def humanResourceAdminPage(request):
    if request.user.is_authenticated() and hasattr(request.user, "humanResourceProfile"):
        pass
    else:
        pass

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
@permission_classes((IsAuthenticated, permission.QuovoAccountPermission))
def add_employees_using_csv(request):
    confirmDocumentUpload(request.POST, request.FILES)
    csvfile = request.FILES.get('csv_file')
    user = request.user.humanResourceProfile
    errors, success = generateSetUpUsers(csvfile, user.company)
    for employee in success:
        link, email = employee.magic_link, employee.email
        domain = request.build_absolute_uri('/')[:-1]
        mailchimp.sendMagicLinkNotification(email, domain + reverse('signUpPage', kwargs={'magic_link': link}))
    return network_response({
        "errors" : errors,
        "success" : success
    })


class EmployeeManagementViewSet(mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    '''
    Individual User API
    '''
    queryset = SetUpUser.objects.all()
    serializer_class = SetUpUserSerializer
    permission_classes = [permission.QuovoAccountPermission]

class EmployeeListView(viewsets.ReadOnlyModelViewSet):
    '''
    Employee List
    '''
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileReadSerializer
    permission_classes = [permission.QuovoAccountPermission]

    def list(self, request):
        queryset = UserProfile.objects.filter(company=request.user.humanResourceProfile.company)
        serializer = UserProfileReadSerializer(queryset)
        return Response(serializer.data)

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
        data = {}
        random_string = generateRandomString()
        data["magic_link"] = random_string
        data["company"] = company
        data["email"] = line[0]
        if addEmployee(data):
            successes.append(data)
        else:
            errors.append({
                "position" : csv_reader.line_num,
                "data": data
            })
    return errors, successes


def addEmployee(datas):
    '''
    Create employee
    @param datas: datas could be list or single object
    @param many: if multiple employees
    '''
    serializer = SetUpUserSerializer(data=datas)
    if serializer.is_valid():
        serializer.save()
        return True
    else:
        return False


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
