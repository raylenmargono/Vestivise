from django.test import TestCase
from data.models import *
from data.serializers import *
from data.testData import *
from data.views import *
from account.models import UserProfile
from django.contrib.auth.models import User
import copy
import itertools
import json
# Create your tests here.

class SerializerMethodTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testUser')
        UserProfile.objects.create(
            user=self.user,
            firstName="testUser",
            lastName="lastname",
            birthday="2016-08-03",
            state="NY",
            income=1000000
        )

    def test_get_yodlee_account_response(self):
        res = yodlee_account_response['account'][0]
        res["userData"] = self.user.profile.data.id
        serializer = YodleeAccountSerializer(data=res)
        serializer.is_valid()
        self.assertEqual(serializer.is_valid(), True)
        instance = serializer.save()
        self.assertTrue(YodleeAccount.objects.get(id=instance.id))
        instance = YodleeAccount.objects.get(id=instance.id)
        self.assertEqual(instance.providerAccountID, 12345)
        self.assertEqual(instance.accountName, "SMB account")
        self.assertEqual(instance.accountID, 801503)
        self.assertEqual(instance.accountNumber, "xxxx4933")
        self.assertEqual(instance.availableBalance.amount, 4699)
        self.assertEqual(instance.availableBalance.currency, "USD")
        self.assertEqual(instance.accountType, "SAVINGS")
        self.assertEqual(instance.isAsset, True)
        self.assertEqual(instance.container, "bank")
        self.assertEqual(instance.providerID, 16441)
        self.assertEqual(hasattr(instance, 'updatedAt'), True)

    def test_get_yodlee_account_update(self):
        res = yodlee_account_response['account'][0]
        res["userData"] = self.user.profile.data.id
        serializer = YodleeAccountSerializer(data=res)
        serializer.is_valid()
        self.assertEqual(serializer.is_valid(), True)
        instance = serializer.save()
        pastUpdateTime = instance.updatedAt
        self.assertTrue(YodleeAccount.objects.get(id=instance.id))
        
        instance2 = YodleeAccount.objects.get(id=instance.id)
        res = yodlee_account_response_update["account"][0]
        res["userData"] = self.user.profile.data.id
        serializer = YodleeAccountSerializer(instance2, data=res)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        self.assertTrue(YodleeAccount.objects.get(id=instance.id))
        final = YodleeAccount.objects.get(id=instance.id)
        self.assertEqual(final.availableBalance.amount, 1)
        self.assertEqual(final.accountBalance.amount, 1)



    def test_get_yodlee_account_list_response(self):
        res = copy.deepcopy(yodlee_account_response_multiple)['account']
        for item in res:
            item['userData'] = self.user.profile.data.id 
        serializers = [YodleeAccountSerializer(data=x) for x in res]
        validity = [x.is_valid() for x in serializers]
        self.assertEqual(validity, [True]*len(serializers))
        
        for x in serializers:
            x.save()
        self.assertEqual(YodleeAccount.objects.all().count(), 3)
        for i in range(1,4):
            responseAccount = yodlee_account_response_multiple['account'][i-1]
            instance = YodleeAccount.objects.get(id=i)

            self.assertTrue(instance)
            self.assertEqual(instance.providerAccountID, responseAccount["providerAccountId"])
            self.assertEqual(instance.accountName, responseAccount["accountName"])
            self.assertEqual(instance.accountID, responseAccount["id"])
            self.assertEqual(instance.accountNumber, responseAccount["accountNumber"])
            self.assertEqual(instance.accountType, responseAccount["accountType"])
            self.assertEqual(instance.container, responseAccount["CONTAINER"])
            self.assertEqual(instance.providerID, int(responseAccount["providerId"]))


    # def test_get_holdings(self):
    #     #get holding type list
    #     # for each holding type get holding
    #     res = yodlee_account_response['account'][0]
    #     res["userData"] = self.user.profile.data.id
    #     serializer = YodleeAccountSerializer(data=res)
    #     serializer.is_valid()
    #     serializer.save()

    #     account = self.user.profile.data.yodleeAccounts.all()[0]
    #     account.updatedAt = timezone.now()
    #     for holding in holdingsTestData["holding"]:
    #         holding["yodleeAccount"] = account.id
    #         holding['createdAt'] = account.updatedAt
    #         serializer = HoldingSerializer(data=holding)
    #         if(not serializer.is_valid()):
    #             print('serializer failed at get holdings')
    #             print(serializer.errors)
    #         self.assertEqual(serializer.is_valid(), True)
    #         internalHolding = serializer.save()
    #         self.assertEqual(bool(internalHolding.assetClassifications.all()), True)
    #         self.assertEqual(internalHolding.accountID,1111496500)
    #         self.assertEqual(internalHolding.providerAccountID,12345)
    #         self.assertTrue(internalHolding.costBasis)
    #         self.assertEqual(internalHolding.costBasis.amount, 2500)
    #         self.assertEqual(internalHolding.description,"IBM stocks")
    #         self.assertEqual(internalHolding.value.amount, 500000)
    #         self.assertEqual(internalHolding.createdAt, account.updatedAt)

    def test_get_investment_options(self):
        res = yodlee_account_response['account'][0]
        res["userData"] = self.user.profile.data.id
        serializer = YodleeAccountSerializer(data=res)
        serializer.is_valid()
        serializer.save()

        account = self.user.profile.data.yodleeAccounts.all()[0]

        invRes = investment_options['account']
        for plan in invRes:
            plan['investmentPlan']['yodleeAccount'] = account.id
            planSerializer = InvestmentPlanSerializer(data=plan['investmentPlan'])
            if(not planSerializer.is_valid()):
                print('INVESTMENT PLAN FAILED TO SERIALIZE')
                print(planSerializer.errors)
            self.assertEqual(planSerializer.is_valid(), True)
            intPlan = planSerializer.save()
            for option in plan['investmentOption']:
                option['yodleeAccount'] = account.id
                optSerializer = InvestmentOptionSerializer(data=option)
                if(not optSerializer.is_valid()):
                    print('INVESTMENT OPTION FAILED TO SERIALIZE')
                    print(optSerializer.errors)
                self.assertEqual(optSerializer.is_valid(), True)

    def test_holding_serializer(self):
        serializersList= []
        res = yodlee_account_response['account'][0]
        res["userData"] = self.user.profile.data.id
        serializer = YodleeAccountSerializer(data=res)
        serializer.is_valid()
        self.assertEqual(serializer.is_valid(), True)
        instance = serializer.save()
        for holding in holdingsTestData["holding"]:
            holding["createdAt"] = instance.createdAt
            holding["yodleeAccount"] = instance.id
            holding["metaData"] = {
                "description" : holding["description"],
                "holdingType" : holding["holdingType"],
                "cusipNumber" : holding["cusipNumber"],
                "symbol" : holding["symbol"],
                "ric" : ""
            }
            # get holding
            # if hasattr(yodleeAccount, 'holdings'):
            #     try:
            #         userHolding = yodleeAccount.holdings.get(
            #             description=holding.get('description'),
            #             createdAt=yodleeLastUpdate
            #         )
            #         if userHolding.quantity != holding.get('quantity'):
            #             shouldUpdate = True
            #     except Holding.DoesNotExist:
            #         # found new holding
            #         shouldUpdate = True
            serializersList.append(holding)

        serializer = HoldingSerializer(data=serializersList, many=True)
        if serializer.is_valid():
            serializer.save()
        else:
            # log failed to serailze holding
            print('serializer failed at get holdings serailizer')
            print(serializer.errors)
            pass
