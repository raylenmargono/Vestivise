from django.contrib.auth import get_user_model
from django.test import TestCase
from Vestivise.quovo import Quovo
import views
from Vestivise.Vestivise import *
from dashboard.models import UserProfile
from humanResources.models import *
from datetime import date, datetime
from mock import patch
import traceback
import logging

# Create your tests here.
class QuovoTest(TestCase):

    def test_token_is_valid(self):
        false_response_date = {
            "expiration" : "2016-03-31T18:45:09Z"
        }
        correct_response_date = {
            "expiration" :"2216-03-31T18:45:09Z"
        }

        Quovo.set_token(correct_response_date)
        self.assertTrue(Quovo.token_is_valid())
        Quovo.set_token(false_response_date)
        self.assertFalse(Quovo.token_is_valid())

class UserProfileTest(TestCase):

    def test_progress_creation(self):
        u = get_user_model().objects.create(
            email="email@email.com"
        )
        u.set_password("ThisisSecureP1111sword!")
        p = UserProfile.objects.create(
            firstName="f",
            lastName='l',
            birthday=datetime.now(),
            state='AZ',
            zipCode='10016',
            user=u
        )
        self.assertTrue(hasattr(p, "progress"))
        self.assertEqual(p.progress.annotation_view_count, 0)

class DashboardTest(TestCase):

    def setUp(self):
         self.s = SetUpUser(
            email="test@test.com",
            company='vestivise',
            magic_link='32432423432423'
        )
         self.s.save()

    def test_validate_registration_payload(self):
        pass_1 = {
            'username' : "raylenmargono",
            "password" : "TestTest1!",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono",
            "birthday" : "02/20/1995"
        }
        self.assertTrue(views.validate(pass_1))
        pass_2 = {
            'username': "",
            "password": "",
            "email": "",
            "state": "",
            "firstName": "",
            "lastName": "",
        }
        self.assertRaises(UserCreationException, views.validate, pass_2)
        pass_3 = {
            'username' : "raylenmargono",
            "password" : "daklsjfasf",
            "email" : "raylen@vestivise.com",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono",
        }
        self.assertRaises(UserCreationException, views.validate, pass_3)
        pass_4 = {
            'username' : "raylenmargono",
            "password" : "123213123",
            "email" : "raylen@vestivise.com",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono",
        }
        self.assertRaises(UserCreationException, views.validate, pass_4)
        pass_5 = {
            'username' : "raylenmargono",
            "password" : "*()*)(!",
            "email" : "raylen@vestivise.com",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono",
        }
        self.assertRaises(UserCreationException, views.validate, pass_5)
        pass_6 = {
            'username': "raylenmargono",
            "password": "testtest1!",
            "email": "raylen@vestivise.com",
            "state": "California",
            "firstName": "Raylen",
            "lastName": "Margono",
        }
        self.assertRaises(UserCreationException, views.validate, pass_6)
        pass_7 = {
            'username': "raylenmargono",
            "password": "TestTest1!",
            "email": "raylenhello.com",
            "state": "California",
            "firstName": "Raylen",
            "lastName": "Margono",
        }
        self.assertRaises(UserCreationException, views.validate, pass_7)
        pass_8 = {
            'username': "raylenmargono",
            "password": "TestTest1!",
            "email": "raylenhello.com",
            "state": "California",
            "firstName": "Raylen",
            "lastName": "Margono",
        }
        self.assertRaises(UserCreationException, views.validate, pass_8)

    def test_delete_setup_user(self):
        setup_user = SetUpUser.objects.get(id=1)
        self.assertEquals(len(SetUpUser.objects.all()), 1)
        SetUpUser.deleteSetupUser(setup_user.id)
        self.assertEquals(SetUpUser.objects.all().count(), 0)

    def test_validateUserProfile(self):
        from dateutil.parser import parse
        pass_1 = {
            'firstName' : 'Raylen',
            'lastName' : "Margono",
            'birthday' : parse("02/20/1995").date(),
            'state' : "CA",
            'createdAt' : datetime.now(),
            'zipCode' : "10016",
            'company' : "Vestivise"
        }
        serializer = None
        try:
            serializer = views.validateUserProfile(pass_1)
        except UserCreationException as e:
            self.fail(e.message)
        user = views.create_user("raylenmargono", "TestTest!1", "raylenmargono@gmail.com")
        serializer.save(user=user)
        self.assertEquals(User.objects.get(id=1).username, "raylenmargono")
        self.assertEquals(UserProfile.objects.get(id=1).zipCode, "10016")
        pass_2 = {
            'firstName': '',
            'lastName': "",
            'birthday': date.today(),
            'state': "",
            'createdAt': datetime.now(),
            'zipCode': "",
            'company': ""
        }
        self.assertRaises(UserCreationException,views.validateUserProfile, pass_2)

    def test_createLocalQuovoUser(self):
        pass_1 = {
            'firstName': 'Raylen',
            'lastName': "Margono",
            'birthday': date.today(),
            'state': "CA",
            'createdAt': datetime.now(),
            'company': "Vestivise"
        }
        serializer = views.validateUserProfile(pass_1)
        user = views.create_user("raylenmargono", "TestTest!1", "raylenmargono@gmail.com")
        user_profile = serializer.save(user=user)

        data = {
            "user": {
                "email": "fakeemail@quovo.com",
                "id": 165703,
                "name": "Test User 1",
                "phone": "",
                "username": "quovo_myfirstuser",
                "value": ""
            }
        }
        try:
            self.assertTrue(views.createLocalQuovoUser(data["user"]["id"], user_profile.id))
        except UserCreationException as e:
            self.fail(e.message)

        data = {
            "user": {
                "id" : None
            }
        }
        self.assertRaises(UserCreationException, views.createLocalQuovoUser, data["user"]["id"], user_profile.id)


    def test_strip_data(self):
        pass

    def test_is_valid_email(self):
        pass

    def test_user_validation_field_validation(self):
        pass