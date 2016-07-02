from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from serializers import *
from rest_framework import generics
from models import *
from Vestivise.permission import *
from rest_framework.response import Response
from rest_framework import status
from django.core.validators import validate_email
from django.contrib.auth import login as auth_login

# Create your views here.


# ROUTE VIEWS

def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def landingPage(request):
    return render(request, "landing/landingPage.html")


def linkAccountPage(request):
    return render(request, "dashboard/linkAccount.html")


def loginPage(request):
    return render(request, "dashboard/loginView.html")


def signUpPage(request):
    return render(request, "dashboard/registerView.html")

# VIEW SETS

class UserProfileViewSet(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileWriteSerializer
    permission_classes = (IsOwnerOrReadOnly,)

# AUTHENTICATION VIEWS 

@api_view(['POST'])
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        auth_login(request, user)
        # log user into yodlee
        return JsonResponse({'success' : 'user authentication successful'}, status=200)
    else:
        # the authentication system was unable to verify the username and password
        return JsonResponse({'error' : 'username or password was incorrect'}, status=400)


@api_view(['POST'])
def register(request):

    error = False
    errorDict = {}
    for key in request.POST:
        if key == 'password' and (not re.search(r'\d', request.POST[key]) 
                            or not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', request.POST[key])):
            error=True
            errorDict[key] = "At least 8 characters, upper, lower case characters, a number, and any one of these characters !@#$%^&*()"
        elif key == 'username' and (not request.POST[key].strip() 
                                    or not request.POST[key] 
                                    or len(request.POST[key]) > 30):
            error=True
            errorDict[key] = "Please enter valid username: less than 30 characters"
        elif key == 'email' and (not request.POST[key].strip() 
                                or not request.POST[key]):
            error=True
            errorDict[key] = "Please enter a valid email"
        elif not request.POST[key] or not request.POST[key].strip():
            error=True
            errorDict[key] = "%s cannot be blank" % (key.title())

    if error:
        return JsonResponse({
                'error': errorDict
            }, status=400)

    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']

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
    user = User.objects.create_user(username, email, password)
    user.save()
    # create profile
    data=request.POST.copy()
    data["user"]=user.id
    serializer = UserProfileWriteSerializer(data=data)
    if serializer.is_valid(): 
        serializer.save()
        # create yodlee account
        payload={
            "loginName": username, 
            "password": password, 
            "email": email, 
            "name": {
                "first": request.POST["firstName"],
                "last": request.POST["lastName"] 
            },
            "preferences": {
                "currency": "USD",
                "timeZone": "PST",
                "dateFormat": "MM/dd/yyyy",
                "locale": "en_US"
            }
        }
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

