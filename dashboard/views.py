import logging
import os
import re
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from Vestivise import mailchimp as MailChimp
from Vestivise.mailchimp import *
from dashboard.serializers import *

# Create your views here.

logger = logging.getLogger(__name__)

# ROUTE VIEWS
def dashboard(request):
    if not request.user.is_authenticated():
        return redirect(reverse('loginPage'))
    return render(request, "dashboard/dashboard.html")

def linkAccountPage(request):
    if not request.user.is_authenticated():
        return redirect(reverse('loginPage'))
    return render(request, "dashboard/linkAccount.html")

def dataUpdatePage(request):
    if not request.user.is_authenticated():
        return redirect(reverse('loginPage'))
    return render(request, "dashboard/updateData.html")

def optionsPage(request):
    if not request.user.is_authenticated():
        return redirect(reverse('loginPage'))
    return render(request, "dashboard/optionsView.html")

def homeRouter(request):
    if request.user.is_authenticated():
        return redirect(reverse('dashboard'))
    return redirect(reverse('loginPage'))


def logout(request):
    auth_logout(request)
    return redirect(reverse('loginPage'))


def loginPage(request):

    if request.user.is_authenticated():
        return redirect(reverse('dashboard'))
    return render(request, "dashboard/loginView.html")


def signUpPage(request):
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
    jsonFile = open(os.path.join(settings.BASE_DIR, 'dashboard/fixtures/basicAccountModel.json'))
    return JsonResponse(json.loads(jsonFile.read()))


# VIEW SETS

class UserProfileView(APIView):

    def get_object(self):
        return self.request.user.profile

    def get(self, request, format=None):
        try:
            serializer = UserProfileWriteSerializer(self.get_object())
            return Response(serializer.data)
        except Exception as e:
            return Response({"error" : e}, status=400)


# AUTHENTICATION VIEWS

@api_view(['POST'])
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        auth_login(request, user)
        # TODO create quovo user
        try:
            pass
        except Exception as e:
            logout(request)
            return JsonResponse({'error': e.args}, status=400)
        return JsonResponse({'success': 'user authentication successful'}, status=200)
    else:
        # the authentication system was unable to verify the username and password
        return JsonResponse({'error': 'username or password was incorrect'}, status=400)


def validate(errorDict, request):
    error = False
    for key in request.POST:
        if key == 'password' and not re.match(r'^(?=.{8,})(?=.*[a-z])(?=.*[0-9])(?=.*[A-Z])(?=.*[!@#$%^&+=]).*$', request.POST[key]):
            error = True
            errorDict[key] = "At least 8 characters, upper, lower case characters, a number, and any one of these characters !@#$%^&*()"
        elif key == 'username' and (not request.POST[key].strip()
                                    or not request.POST[key]
                                    or len(request.POST[key]) > 30):
            error = True
            errorDict[key] = "Please enter valid username: less than 30 characters"
        elif key == 'email' and (not request.POST[key].strip()
                                or not request.POST[key]):
            error = True
            errorDict[key] = "Please enter a valid email"
        elif key == 'state' and not request.POST[key].strip():
            error = True
            errorDict[key] = "%s cannot be blank" % (key.title())
        elif key == 'income' and not request.POST[key].isdigit():
            error = True
            errorDict[key] = "%s needs to be a number" % (key.title())
        elif (key == 'firstName' and not request.POST[key]) or (key == 'lastName' and not request.POST[key]):
            error = True
            errorDict[key] = "Cannot be blank"
    return error


@api_view(['POST'])
def register(request):

    errorDict = {}
    error = validate(errorDict, request)

    if error: return JsonResponse({'error': errorDict}, status=400)

    username, password, email = strip_data(request.POST['username'], request.POST['password'], request.POST['email'])

    email_validation_response = is_valid_email(email)
    if(email_validation_response): return email_validation_response

    user_validation_response = user_validation_field_validation(username, email)
    if(user_validation_response) : return user_validation_response

    # create profile
    data=request.POST.copy()

    #remove whitespace
    remove_whitespace_from_data(data)

    serializer = UserProfileWriteSerializer(data=data)

    if serializer.is_valid():
        yodleeAccountCreated = create_quovo_user(email, username, password, request.POST["firstName"], request.POST["lastName"])
        if yodleeAccountCreated:
            subscribe_mailchimp(request.POST["firstName"], request.POST["lastName"], email)
            serializer.save(user=create_user(username, password, email))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'Yodlee account failed'}, status=400)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#AUXILARY METHODS


def create_quovo_user(email, username, password, firstName, lastName):
    #TODO
    return True


def strip_data(username, password, email):
    return (username.strip(), password.strip(), email())


def is_valid_email(email):
    try:
        validate_email(email)
    except:
        return JsonResponse({
            'error' : {'email' : 'this is not a valid email'}
        }, status=400)
    return None


def user_validation_field_validation(username, email):
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'error' : {'username' : 'username exists'}
        }, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'error' : {'email' : 'email already taken, please try another one'}
        }, status=400)
    return None

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


def subscribe_mailchimp(firstName, lastName, email):
    response = MailChimp.subscribeToMailChimp(firstName, lastName, email)
    if response["status"] != 200:
        logger.error(response)