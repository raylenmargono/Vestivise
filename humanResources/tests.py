from django.contrib.auth import authenticate
from django.contrib.auth.views import login
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
import csv
import os
from django.contrib.auth.models import User
from models import *
from Vestivise.Vestivise import VestErrors
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
        headers = ["email", "first_name", "last_name"]
        rows = [
            ["raylen@vestivise.com", "Raylen", "Margono"],
            ["alex@vestivise.com", "Alex", "Novak"],
            ["josh@vestivise.com", "Josh", "Gelinas"],
            ["jason@vestivise.com", "Jason", "Li"]
        ]
        rows.insert(0, headers)
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
                self.assertTrue(raylen_user.first_name == "Raylen")
                self.assertTrue(alex_user.email == 'alex@vestivise.com')
                self.assertTrue(alex_user.first_name == "Alex")
            except SetUpUser.DoesNotExist as e:
                self.fail(e.message)
        headers = ["", "", "last_name"]
        rows = [
            ["raylen@vestivise.com", "Raylen", "Margono"],
            ["alex@vestivise.com", "Alex", "Novak"],
            ["josh@vestivise.com", "Josh", "Gelinas"],
            ["jason@vestivise.com", "Jason", "Li"]
        ]
        rows.insert(0, headers)
        csv_file = open('test.csv', 'w+')
        csv_writer = csv.writer(csv_file)
        for i in rows:
            csv_writer.writerow(i)
        csv_file.close()
        with open('test.csv', 'r') as fp:
            url = reverse('employeeCreateCSV')
            payload = {"csv_file": fp}
            response = self.client.post(url, payload, format='multipart')
            os.remove('test.csv')
            self.assertEquals(response.status_code, 400)
            self.assertEquals(json.loads(response.content).get('error'), "Missing columns")

        headers = ["test", "test", "last_name"]
        rows = [
            ["raylen@vestivise.com", "Raylen", "Margono"],
            ["alex@vestivise.com", "Alex", "Novak"],
            ["josh@vestivise.com", "Josh", "Gelinas"],
            ["jason@vestivise.com", "Jason", "Li"]
        ]
        rows.insert(0, headers)
        csv_file = open('test.csv', 'w+')
        csv_writer = csv.writer(csv_file)
        for i in rows:
            csv_writer.writerow(i)
        csv_file.close()
        with open('test.csv', 'r') as fp:
            url = reverse('employeeCreateCSV')
            payload = {"csv_file": fp}
            response = self.client.post(url, payload, format='multipart')
            os.remove('test.csv')
            self.assertEquals(response.status_code, 400)
            self.assertEquals(json.loads(response.content).get('error'), "Missing columns")

        headers = ["email", "first_name", "last_name"]
        rows = [
            ["", "Raylen", "Margono"],
            ["alex@vestivise.com", "Alex", "Novak"],
            ["josh@vestivise.com", "Josh", "Gelinas"],
            ["jason@vestivise.com", "Jason", "Li"]
        ]
        rows.insert(0, headers)
        csv_file = open('test.csv', 'w+')
        csv_writer = csv.writer(csv_file)
        for i in rows:
            csv_writer.writerow(i)
        csv_file.close()
        with open('test.csv', 'r') as fp:
            url = reverse('employeeCreateCSV')
            payload = {"csv_file": fp}
            response = self.client.post(url, payload, format='multipart')
            os.remove('test.csv')
            self.assertEquals(response.status_code, 400)
            self.assertEquals(json.loads(response.content).get('error'), "Detected some empty fields")

