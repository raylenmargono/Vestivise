from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
import csv
import os
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.
class CSVUploadTest(APITestCase):

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
            payload = {"company" : "Vestivise", "csv_file" : fp}
            response = self.client.post(url, payload, format='multipart')
            os.remove('test.csv')
            self.assertTrue(response.status_code == 200, response)

