from django.shortcuts import render
from django.http import Http404
from rest_framework.decorators import api_view
from django.http import JsonResponse
from data.models import *
from account.models import *
import data.algos
from rest_framework.decorators import api_view
from yodlee import apis as YodleeAPI
from serializers import *

'''
BROKER FUNCTION:
Imput the request with the name of the module,
redirect the request to the module in question
and return the output of that module, however it
is organized.

NOTES/QUESTIONS:
Currently, I'm thinking the Broker is only 
for GET requests. A post request is issued 
along with the user/their credentials/the
module name, and any updates that are 
necessary are handled within the data app
before returning the necessary components
for the module. I'm not currently seeing 
any position where we have to post anything
to the broker. If I'm wrong about this,
let me know. -- ALEX

TODO:
-Verify if user has permissions to get the
 module they are requesting. 

-Determine if Ray wants it structured like this
 or if he would rather that it's structured for
 internal calls instead of /api/data/... calls.

-Better error handling.
'''
def broker(request, module):
    if not request.user.is_authenticated():
        raise Http404("Please Log In before using data API")
    module = module
    if hasattr(data.algos, module):
        method = getattr(data.algos, module)
        return method(request)
    else:
        raise Http404("Module not found")


@api_view(['GET', 'POST'])
def update_user_data(request):
    # check if token is valid through requests if not then
    # tell client to redirect to home page for login
    sessionToken = request.session["cobSessionToken"]
    userToken = request.session["userToken"]
    try:
        userData = request.user.profile.data
        accounts = YodleeAPI.getAccounts(sessionToken, userToken)
        holdingListType = YodleeAPI.getHoldingListTypes(sessionToken, userToken)
        assetClasses = YodleeAPI.getAssetClassList(sessionToken, userToken)

        serialize_accounts(accounts, userData)
        serialize_holding_list(holdingListType, userData, sessionToken, userToken)
        serialize_asset_classes(assetClasses, userData)
        serialize_investment_options(userData, sessionToken, userToken)

        account = request.user.profile.vest_account
        account.linkedAccount = True
        account.save()

        return JsonResponse({'result' : 'success'}, status=200)

    except YodleeAPI.YodleeException as e:
        print(e.args)
        request.session["tokenIsValid"] = False
        request.session["cobSessionToken"] = None
        request.session["userToken"] = None
        return JsonResponse({'error': e.args}, status=400)


def serialize_accounts(accounts, userData):
    currentAccountsIDs = []
    try:
        currentAccountsIDs = list(userData.yodleeAccounts.all().values_list('accountID', flat=True))
    except Exception as e:
        pass
    #for loop get historical balances for each account
    for account in accounts["account"]:
        if account["CONTAINER"].lower() != "investment":
            continue
        account["userData"] = userData.id
        serializer = YodleeAccountSerializer(data=account)
        if serializer.is_valid():
            # check if account exists then update
            accountID = serializer.validated_data["accountID"]
            if serializer.validated_data["accountID"] in currentAccountsIDs:
                userAccount = YodleeAccount.objects.get(accountID=accountID)
                serializer = YodleeAccountSerializer(userAccount, data=account, partial=True)
                currentAccountsIDs.remove(accountID)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # log partial update failed
                    pass
            # if not then create
            else:
                serializer.save()
        else:
            # log create failed
            pass

    #anything left in currentAccounts has been a deleted account
    for leftOverIDs in currentAccountsIDs:
        YodleeAccount.objects.get(accountID=leftOverIDs).delete() 


def serialize_holding_list(holdingTypeList, userData, authToken, userToken):
    if userData.yodleeAccounts:
        for yodleeAccount in userData.yodleeAccounts.all():
            for holdingType in holdingTypeList:
                holdings = YodleeAPI.getHoldings(authToken, userToken, holdingType, yodleeAccount.accountID, yodleeAccount.providerAccountID)
                for holding in holdings["holding"]:
                    holding["createdAt"] = yodleeAccount.updatedAt
                    holding["yodleeAccount"] = yodleeAccount.id
                    serializer = HoldingSerializer(data=holding)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        # log failed to serailze holding
                        print(serializer.errors)
                        pass

def serialize_asset_classes(assetClasses, userData):
    pass

def serialize_investment_options(userData, authToken, userToken):
    for account in userData.yodleeAccounts.all():
        investmentOptions = YodleeAPI.getInvestmentOptions(authToken, userToken, account.accountID)
        if "account" in investmentOptions:
            investmentOption = investmentOptions["account"]
            print(investmentOption)
            for data in investmentOption:
                data["investmentPlan"]["yodleeAccount"] = account.id
                planSerializer = InvestmentPlanSerializer(data=data['investmentPlan'])
                if planSerializer.is_valid():
                    planSerializer.save()
                else:
                    #log error
                    pass
                for option in data["investmentOptions"]:
                    option["yodleeAccount"] = account.id
                    serializer = InvestmentOptionSerializer(data=option)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        # logg error
                        pass
