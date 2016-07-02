from django.test import Client
import unittest
from django.utils import timezone
from yodlee import views as yodleeViews
from django.core.urlresolvers import reverse

class TestEmailAPI(unittest.TestCase):

    def testRefreealCompletion(self):
        self.client = Client()
        response = self.client.post('/api/email/', {'email': 'test@test.com', 'createdAt': timezone.now()})
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/referal/', {'email': 'test2@test.com', 'createdAt': timezone.now(), "refree": "test@test.com"})
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/email/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], "test@test.com")
        self.assertEqual(response.json()['acceptedEmails'], 0)

        response = self.client.post('/api/email/', {'email': 'test2@test.com', 'createdAt': timezone.now()})
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/email/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], "test@test.com")
        self.assertEqual(response.json()['acceptedEmails'], 1)

        response = self.client.get('/api/referal/1/')
        self.assertEqual(response.json()['accepted'], True)


class TestYodleeAPI(unittest.TestCase):

    def testGetAppToken(self):
        self.client = Client()

        response = self.client.post(reverse('appToken'))

        apptoken = response.json()["token"]

        response = self.client.post(reverse('accessToken'), {
            'login' : "sbMemvestivise1",
            'password' : "sbMemvestivise1#123",
            'cobSessionToken' : apptoken    
        })

        accesstoken = response.json()["token"]

        response = self.client.post(reverse('searchSites'), {
            'cobSessionToken' : apptoken,
            'userSessionToken' : accesstoken
        })

        print(response)
