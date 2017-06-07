from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from dashboard.views import register, login, UserProfileView


class TestAPI(TestCase):

    def setUp(self):
        self.registration_payload = {
            "birthday": "",
            "username": "",
            "password": ""
        }

    def test_registration(self):
        factory = APIRequestFactory()
        payload = self.registration_payload
        payload["username"] = "test@test.com"
        payload["password"] = "ThisIsSecure123!$"
        payload["birthday"] = "02/13/1995"
        request = factory.post(reverse('register'), payload, format='json')

    def test_registration_fail(self):
        pass

    def test_login(self):
        pass

    def test_login_fail(self):
        pass

    def test_module_display(self):
        pass
