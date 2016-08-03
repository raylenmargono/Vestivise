from django.test import TestCase
from models import *
from serializers import *
from testData import *
from account.models import UserProfile
from django.contrib.auth.models import User

# Create your tests here.


class SerializerMethodTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testUser')
        self.userProfile = UserProfile.objects.create(
            user=self.user,
            firstName="testUser",
            lastName="lastname",
            birthday="2016-08-03",
            state="NY",
            email="raylenmargono@gmail.com",
            income=1000000
        )
        self.userData = UserData.objects.create(userProfile=self.userProfile)

    def test_get_yodlee_account_response(self):
        # from testData
        res = yodlee_account_response

        res["userData"] = self.userProfile.data.id
        serializer = YodleeAccountSerializer(data=res)
        serializer.is_valid()
        self.assertEqual(serializer.is_valid(), True)
