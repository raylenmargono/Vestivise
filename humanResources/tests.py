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


class CSVUploadTest(APITestCase):

    def setUp(self):
        user = User.objects.create(username='testtest', email='test@test.com')
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
        list_url = reverse('companyEmployeeManagementmigr-list')

        setupuser1 = SetUpUser(company='Vestivise', email='test@test.com', magic_link='testurl').save()
        setupuser2 = SetUpUser(company='Vestivise', email='test1@test.com', magic_link='testurl').save()
        setupuser3 = SetUpUser(company='Test1', email='test2@test.com', magic_link='testurl').save()
        response = self.client.get(list_url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()['data']) == 2)

        response = self.client.post(list_url, {'email' : 'api_create@test.com'})
        self.assertTrue(response.status_code == 200)
        self.assertEqual(response.json()['data']['email'], 'api_create@test.com')
        delete_id = response.json()['data']['id']

        detail_url = reverse('companyEmployeeManagementmigr-detail', kwargs={'pk': delete_id})
        response = self.client.delete(detail_url)
        self.assertTrue(response.status_code == 204)
        self.assertFalse(SetUpUser.objects.filter(id=delete_id).exists())

        response = self.client.post(list_url, {'email': 'test@test.com'})
        self.assertTrue(response.status_code == 400)