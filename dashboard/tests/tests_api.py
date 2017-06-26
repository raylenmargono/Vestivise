from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from dashboard.views import register, login, UserProfileView


class TestAPI(APITestCase):

    def setUp(self):
        self.registration_payload = {
            "birthday": "",
            "username": "",
            "password": ""
        }

        self.user = get_user_model().objects.create_user(
            email='registered@test.com', password='ThisIsSecure123!$')

    def test_registration(self):
        payload = self.registration_payload
        payload["username"] = "test@test.com"
        payload["password"] = "ThisIsSecure123!$"
        payload["birthday"] = "02/13/1995"
        request = self.client.post(reverse('register'), payload, format='json')
        self.assertEqual(request.status_code, 200)

    def test_registration_fail(self):
        payload = self.registration_payload

        # test with weak password
        payload["username"] = "test@test.com"
        payload["password"] = "pass"
        payload["birthday"] = "02/13/1995"
        request = self.client.post(reverse('register'), payload, format='json')
        self.assertEqual(request.status_code, 400)

        # test with already-registered email
        payload["username"] = "registered@test.com"
        payload["password"] = "ThisIsSecure123!$"
        payload["birthday"] = "02/13/1995"
        request = self.client.post(reverse('register'), payload, format='json')
        self.assertEqual(request.status_code, 400)

        # test with wrong email format
        payload["username"] = "test"
        payload["password"] = "ThisIsSecure123!$"
        payload["birthday"] = "02/13/1995"
        request = self.client.post(reverse('register'), payload, format='json')
        self.assertEqual(request.status_code, 400)

    def test_login(self):
        self.assertTrue(self.client.login(username="registered@test.com", password="ThisIsSecure123!$"))

    def test_login_fail(self):
        self.assertFalse(self.client.login(username="registered@test.com", password="ThisIsSecure123!%"))

    def test_module_display(self):
        pass
