from django.test import TestCase
from data.models import *
from data.serializers import *
from data.testData import *
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

    def test_get_yodlee_account_response(self):
        res = yodlee_account_response['account'][0]
        res["userData"] = self.user.profile.data.id
        serializer = YodleeAccountSerializer(data=res)
        serializer.is_valid()
        self.assertEqual(serializer.is_valid(), True)

    def test_get_yodlee_account_list_response(self):
        res = yodlee_account_response_multiple['account']
        for item in res:
            item['userData'] = self.user.profile.data.id 
        serializers = [YodleeAccountSerializer(data=x) for x in res]
        validity = [x.is_valid() for x in serializers]
        
        self.assertEqual(validity, [True]*len(serializers))

    def test_get_holdings(self):
        #get holding type list
        # for each holding type get holding
        res = yodlee_account_response['account'][0]
        res["userData"] = self.user.profile.data.id
        serializer = YodleeAccountSerializer(data=res)
        serializer.is_valid()
        serializer.save()

        account = self.user.profile.data.yodleeAccounts.all()[0]

        for holding in holdings["holding"]:
            holding["yodleeAccount"] = account.id
            serializer = HoldingSerializer(data=holding)
            serializer.is_valid()
            print(serializer.errors)

            self.assertEqual(serializer.is_valid(), True)

