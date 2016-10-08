from django.test import TestCase
from Vestivise.quovo import Quovo
import views
from Vestivise.Vestivise import VestErrors
from humanResources.models import *
from datetime import date, datetime

# Create your tests here.
class QuovoTest(TestCase):

    def test_token_is_valid(self):
        false_response_date = "2016-03-31T18:45:09Z"
        correct_response_date = "2216-03-31T18:45:09Z"
        response = Quovo.get_shared_instance().__token_is_valid(correct_response_date)
        self.assertTrue(response)
        self.assertFalse(false_response_date)


class DashboardTest(TestCase):

    def setUp(self):
         SetUpUser(
            email="test@test.com",
            first_name="ray",
            last_name='margono',
            company='vestivise',
            magic_link='32432423432423'
        ).save()

    def test_validate_registration_payload(self):
        pass_1 = {
            'username' : "raylenmargono",
            "password" : "TestTest1!",
            "email" : "raylen@vestivise.com",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono"
        }
        self.assertTrue(views.validate(pass_1))
        pass_2 = {
            'username': "",
            "password": "",
            "email": "",
            "state": "",
            "firstName": "",
            "lastName": ""
        }
        self.assertRaises(VestErrors.UserCreationException, views.validate(pass_2))
        pass_3 = {
            'username' : "raylenmargono",
            "password" : "daklsjfasf",
            "email" : "raylen@vestivise.com",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono"
        }
        self.assertRaises(VestErrors.UserCreationException, views.validate(pass_3))
        pass_4 = {
            'username' : "raylenmargono",
            "password" : "123213123",
            "email" : "raylen@vestivise.com",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono"
        }
        self.assertRaises(VestErrors.UserCreationException, views.validate(pass_4))
        pass_5 = {
            'username' : "raylenmargono",
            "password" : "*()*)(!",
            "email" : "raylen@vestivise.com",
            "state" : "California",
            "firstName" : "Raylen",
            "lastName" : "Margono"
        }
        self.assertRaises(VestErrors.UserCreationException, views.validate(pass_5))
        pass_6 = {
            'username': "raylenmargono",
            "password": "testtest1!",
            "email": "raylen@vestivise.com",
            "state": "California",
            "firstName": "Raylen",
            "lastName": "Margono"
        }
        self.assertRaises(VestErrors.UserCreationException, views.validate(pass_6))
        pass_7 = {
            'username': "raylenmargono",
            "password": "TestTest1!",
            "email": "raylenhello.com",
            "state": "California",
            "firstName": "Raylen",
            "lastName": "Margono"
        }
        self.assertRaises(VestErrors.UserCreationException, views.validate(pass_7))

    def test_delete_setup_user(self):
        setup_user = SetUpUser.objects.get(id=1)
        self.assertEquals(len(SetUpUser.objects.all()), 1)
        SetUpUser.deleteSetupUser(setup_user.id)
        self.assertEquals(SetUpUser.objects.all(), [])

    def test_validateUserProfile(self):
        pass_1 = {
            'firstName' : 'Raylen',
            'lastName' : "Margono",
            'birthday' : date.now(),
            'state' : "California",
            'createdAt' : datetime.now(),

        }

    def test_createLocalQuovoUser(self):
        pass

    def test_strip_data(self):
        pass

    def test_is_valid_email(self):
        pass

    def test_user_validation_field_validation(self):
        pass