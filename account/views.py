from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from account.serializers import *
from rest_framework import mixins
from account.models import *
from Vestivise.permission import *
from rest_framework.response import Response
from rest_framework import status
from django.core.validators import validate_email
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from rest_framework import viewsets
from rest_framework.views import APIView
import requests
import json
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from yodlee import apis as YodleeAPIs
from Vestivise import mailchimp as MailChimp
import logging

logger = logging.getLogger(__name__)

# Create your views here.

# ROUTE VIEWS


def logout(request):
    auth_logout(request)
    return redirect(reverse('loginPage'))


def loginPage(request):

    if request.user.is_authenticated() and request.session.get('tokenIsValid') and request.session.get('tokenIsValid') == True:
        return redirect(reverse('dashboard'))
    return render(request, "dashboard/loginView.html")


def signUpPage(request):
    if request.user.is_authenticated():
        return redirect(reverse('dashboard'))
    return render(request, "dashboard/registerView.html")

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


class UserBasicAccountView(APIView):
    def get_object(self):
        return self.request.user.profile.vest_account

    def get(self, request, format=None):
        try:
            serializer = BasicAccountSerializer(self.get_object())
            response = serializer.data
            response['processing'] = False
            if(hasattr(request.user.profile.data, 'yodleeAccounts')):
                for account in request.user.profile.data.yodleeAccounts.all():
                    if account.needsProcessing:
                        response['processing'] = True
            return Response(response)
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
        # log user into yodlee
        try:
            appToken = YodleeAPIs.getAuthToken()
            accessToken = YodleeAPIs.getUserToken(username, password, appToken)
            print(appToken)
            print(accessToken)
            request.session["cobSessionToken"] = appToken
            request.session["userToken"] = accessToken
            request.session["tokenIsValid"] = True
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

    if error:
        return JsonResponse({
                'error': errorDict
            }, status=400)

    username = request.POST['username'].strip()
    password = request.POST['password'].strip()
    email = request.POST['email'].strip()

    try:
        validate_email(email)
    except:
        return JsonResponse({
            'error' : {'email' : 'this is not a valid email'}
        }, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'error' : {'username' : 'username exists'}
        }, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'error' : {'email' : 'email already taken, please try another one'}
        }, status=400)
    
    # create profile
    data=request.POST.copy()
    
    #remove whitespace
    for key in data:
        if isinstance(data[key], basestring):
            data[key] = data[key].strip()

    serializer = UserProfileWriteSerializer(data=data)

    if serializer.is_valid(): 
        yodleeAccountCreated = create_yodlee_account(email, username, password, request.POST["firstName"], request.POST["lastName"])        
        if yodleeAccountCreated:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            response = MailChimp.subscribeToMailChimp(request.POST["firstName"], request.POST["lastName"], email)
            if response["status"] != 200:
                logger.error(response)
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'Yodlee account failed'}, status=400)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#AUXILARY METHODS
def create_yodlee_account(email, username, password, firstName, lastName):
    payload={
            "user": {
                "loginName": username,
                "password": password,
                "email": email,
                "name": {
                    "first": firstName,
                    "last": lastName
                }
            },
            "preferences": {
                "currency": "USD",
                "timeZone": "PST",
                "dateFormat": "MM/dd/yyyy",
                "locale": "en_US"
            }
        }
    try:
        YodleeAPIs.registerUser(payload, YodleeAPIs.getAuthToken())
        return True
    except YodleeAPIs.YodleeException as e:
        # log exception
        print("Yodlee Exception error: %s" % e.args)
        return False
