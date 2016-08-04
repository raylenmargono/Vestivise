from django.shortcuts import render
from django.http import Http404
from rest_framework.decorators import api_view
from django.http import JsonResponse
from data.models import *
from account.models import *
import data.algos
from rest_framework.decorators import api_view
from yodlee import apis as YodleeAPI
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
        investmentOptions = YodleeAPI.getInvestmentOptions(sessionToken, userToken)

        serialize_accounts(accounts)
        serialize_holding_list(holdingListType)
        serialize_asset_classes(assetClasses)
        serialize_investment_options(investmentOptions)
    except Exception as e:
        request.session["tokenIsValid"] = False
        request.session["cobSessionToken"] = None
        request.session["userToken"] = None
        return JsonResponse({'error': e.args}, status=400)


def serialize_accounts(accounts, userData):
    currentAccountsIDs = userData.yodleeAccount.all().values_list('accountID', flat=True)
    #for loop get historical balances for each account
    for account in accounts:
        account["userData"] = userData.id
        serializer = YodleeAccountSerializer(data=account)
        if serializer.is_valid():
            # check if account exists then update
            if serializer.data.id in currentAccountsIDs:
                userAccount = YodleeAccount.objects.get(accountID=serializer.data.id)
                serializer = YodleeAccountSerializer(userAccount, data=account, partial=True)
                currentAccountsIDs.remove(serializer.data.id)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # log partial update failed
            # if not then create
            else:
                serializer.save()
        else:
            # log create failed

    #anything left in currentAccounts has been a deleted account
    for leftOverIDs in currentAccountsIDs:
        YodleeAccount.objects.get(accountID=leftOverIDs).delete() 

def serialize_holding_list(holdingTypeList, userData):
    for holdingType in holdingTypeList:
        # if holding is new
        # if 

def serialize_asset_classes(assetClasses, userData):
    pass

def serialize_investment_options(investmentOptions, userData):
    pass
