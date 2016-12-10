from django.contrib.auth import authenticate
from django.contrib.auth.views import login
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
import csv
import os
from django.contrib.auth.models import User
from models import *
import json
from humanResources.models import HumanResourceProfile

# Create your tests here.


class HumanResourceEmployeeAPITest(APITestCase):

    def setUp(self):
        user = User.objects.create(username='testtest', email='post@test.com')
        user.set_password('testtest123!')
        user.save()
        self.client.login(username='testtest', password='testtest123!')
        HumanResourceProfile(company='Vestivise', user=user, is_roth=False).save()

    def test_create_employeee(self):
        rows = [
            ["raylen@vestivise.com"],
            ["alex@vestivise.com"],
            ["josh@vestivise.com"],
            ["jason@vestivise.com"]
        ]
        csv_file = open('test.csv', 'w+')
        csv_writer = csv.writer(csv_file)
        for i in rows:
            csv_writer.writerow(i)
        csv_file.close()
        with open('test.csv', 'r') as fp:
            url = reverse('employeeCreateCSV')
            payload = {"csv_file" : fp}
            response = self.client.post(url, payload, format='multipart')
            os.remove('test.csv')
            self.assertTrue(response.status_code == 200, response)
            self.assertTrue(SetUpUser.objects.all().count(), 4)
            try:
                raylen_user = SetUpUser.objects.get(id=1)
                alex_user = SetUpUser.objects.get(id=2)
                self.assertTrue(raylen_user.magic_link != alex_user.magic_link)
                self.assertTrue(raylen_user.email == 'raylen@vestivise.com')
                self.assertTrue(alex_user.email == 'alex@vestivise.com')
            except SetUpUser.DoesNotExist as e:
                self.fail(e.message)

    def test_manage_employee_api(self):
        list_url = reverse('companyEmployeeManagement-list')

        setupuser1 = SetUpUser(company='Vestivise', email='test@test.com', magic_link='testurl').save()
        setupuser2 = SetUpUser(company='Vestivise', email='test1@test.com', magic_link='testurl')
        setupuser2.save()
        setupuser3 = SetUpUser(company='Test1', email='test2@test.com', magic_link='testurl')
        setupuser3.save()

        response = self.client.get(list_url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()['data']) == 2)

        response = self.client.post(list_url, {'email' : 'api_create@test.com'})
        self.assertTrue(response.status_code == 201)
        self.assertEqual(response.json()['data']['email'], 'api_create@test.com')
        delete_id = response.json()['data']['id']

        detail_url = reverse('companyEmployeeManagement-detail', kwargs={'pk': delete_id})
        response = self.client.delete(detail_url)
        self.assertTrue(response.status_code == 204)
        self.assertFalse(SetUpUser.objects.filter(id=delete_id).exists())

        detail_url = reverse('companyEmployeeManagement-detail', kwargs={'pk': setupuser2.id})

        response = self.client.put(detail_url, {
            "email" : "post@test.com"
        })
        self.assertTrue(response.status_code == 200)
        self.assertEqual(SetUpUser.objects.get(id=setupuser2.id).email, "post@test.com")

        response = self.client.get(detail_url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['data'].get("is_active"))


        detail_url = reverse('companyEmployeeManagement-detail', kwargs={'pk': setupuser3.id})

        response = self.client.delete(detail_url)
        self.assertTrue(response.status_code == 404)
        self.assertTrue(SetUpUser.objects.filter(id=setupuser3.id).exists())

        setupuser3.company = "Vestivise"
        setupuser3.save()
        detail_url = reverse('companyEmployeeManagement-detail', kwargs={'pk': setupuser3.id})
        response = self.client.delete(detail_url)
        self.assertTrue(response.status_code == 204)
        self.assertFalse(SetUpUser.objects.filter(id=setupuser3.id).exists())


        response = self.client.post(list_url, {'email': 'test@test.com'})
        self.assertTrue(response.status_code == 400)


    def test_manage_employee_pagination_api(self):
        list_url = reverse('companyEmployeeManagement-list')
        for x in range(101):
            SetUpUser(company='Vestivise', email='%s@test.com' % (x,), magic_link='testurl').save()
        response = self.client.get(list_url).json()
        self.assertTrue("count" in response)
        self.assertTrue("next" in response)
        self.assertEqual(len(response.get("data")), 100)

        response = self.client.get(response.get('next')).json()
        self.assertEqual(len(response.get("data")), 1)
