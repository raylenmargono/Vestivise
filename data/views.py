from django.shortcuts import render
from django.http import Http404
from rest_framework.decorators import api_view
from django.http import JsonResponse
from data.models import *
from account.models import *
import data.algos
from rest_framework.decorators import api_view
from yodlee import apis as YodleeAPI
from data.serializers import *
from rest_framework import generics
from django.http import Http404
from django.shortcuts import get_object_or_404
from Vestivise.permission import *
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import SuspiciousOperation
from rest_framework.exceptions import PermissionDenied
import json
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework import generics
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from Vestivise.mailchimp import *

def holdingEditor(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden() 
    return render(request, "data/holdingEditorView.html")


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
    if not request.user.is_authenticated() or not "Test" in module:
        raise Http404("Please Log In before using data API")
    module = module
    if hasattr(data.algos, module):
        method = getattr(data.algos, module)
        return method(request)
    else:
        raise Http404("Module not found")


class YodleeAccountDetail(generics.DestroyAPIView):
    model = YodleeAccount
    serializer_class = YodleeAccountSerializer
    lookup_field = 'accountID'
    permission_classes = (IsAuthenticated, YodleeAccountOwner)

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        accountID = self.kwargs['accountID']
        return YodleeAccount.objects.filter(accountID=accountID)

    def get_object(self):
        yodleeAccount = self.get_queryset().first()
        self.check_object_permissions(self.request, yodleeAccount)

        if self.request.method == "DELETE":
            try:
                sessionToken = self.request.session["cobSessionToken"]
                userToken = self.request.session["userToken"]
                YodleeAPI.deleteAccount(sessionToken, userToken, yodleeAccount.accountID)
            except YodleeAPI.YodleeException as e:
                revokeTokens(self.request)
                raise PermissionDenied(json.dumps({"error_code" : "Y1"}))

        return yodleeAccount


class YodleeAccountList(generics.ListAPIView):
    model = YodleeAccount
    serializer_class = YodleeAccountSerializerList
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if(not hasattr(self.request.user.profile.data, 'yodleeAccounts')):
            raise Http404("No yodlee accounts found")
        return self.request.user.profile.data.yodleeAccounts.all()


@api_view(['GET', 'POST'])
def update_user_data(request):
    # check if token is valid through requests if not then
    # tell client to redirect to home page for login

    if not request.user.is_authenticated():
        return JsonResponse({"error" : "User not logged in"}, status=400)

    sessionToken = request.session["cobSessionToken"]
    userToken = request.session["userToken"]
    try:
        userData = request.user.profile.data
        email = request.user.email
        accounts = YodleeAPI.getAccounts(sessionToken, userToken)
        holdingListType = YodleeAPI.getHoldingListTypes(sessionToken)
        #assetClasses = YodleeAPI.getAssetClassList(sessionToken, userToken)

        serialize_accounts(accounts, userData)

        if(hasattr(request.user.profile.data, 'yodleeAccounts')):
            # for yodleeAccount in userData.yodleeAccounts.all():
            #     print(YodleeAPI.refreshAccount(sessionToken, userToken, yodleeAccount.accountID)) 

            serialize_holding_list(holdingListType, userData, sessionToken, userToken, email)
            #serialize_asset_classes(assetClasses, userData)
            # serialize_investment_options(userData, sessionToken, userToken)
            serialize_transactions(sessionToken, userToken, userData)

            account = request.user.profile.vest_account
            account.linkedAccount = True
            account.save()

        return JsonResponse({'result' : 'success'}, status=200)

    except YodleeAPI.YodleeException as e:
        print(e.args)
        revokeTokens(request)
        return JsonResponse({"reason": e.args, "error_code" : "Y1"}, status=400)


def serialize_accounts(accounts, userData):
    currentAccountsIDs = []
    try:
        currentAccountsIDs = list(userData.yodleeAccounts.all().values_list('accountID', flat=True))
    except Exception as e:
        pass
    #for loop get historical balances for each account
    if "account" in accounts:
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
                        print(serializer.errors)
                # if not then create
                else:
                    serializer.save()
            else:
                # log create failed
                print(serializer.errors)

        #anything left in currentAccounts has been a deleted account
        for leftOverIDs in currentAccountsIDs:
            YodleeAccount.objects.get(accountID=leftOverIDs).delete() 


def serialize_holding_list(holdingTypeList, userData, authToken, userToken, email):
    for yodleeAccount in userData.yodleeAccounts.all():
        # if it has holdings then default should not update
        # if it does then we should be updating
        shouldUpdate = not hasattr(yodleeAccount, 'holdings')
        # variable to see if new holdings are not present in our backend
        needsProcessing = False

        # create if new snapshot 
        serializersList = []

        yodleeLastUpdate = yodleeAccount.updatedAt
        timeNow = timezone.now()

        for holdingType in holdingTypeList["holdingType"]:
            holdings = YodleeAPI.getHoldings(authToken, userToken, holdingType, yodleeAccount.accountID, yodleeAccount.providerID)
            for holding in holdings["holding"]:
                print(holding)
                holding["createdAt"] = timeNow
                holding["yodleeAccount"] = yodleeAccount.id
                holding["metaData"] = None
                metaData = {
                    "description": holding.get("description"),
                    "holdingType": holding.get("holdingType"),
                    "cusipNumber": holding.get("cusipNumber"),
                    "symbol": holding.get("symbol"),
                    "ric": ""
                }

                # if there is no holding available then we create one
                try:
                    holding["metaData"]  = HoldingMetaData.objects.get(description=metaData["description"]).id
                except HoldingMetaData.DoesNotExist:
                    # check if holding has information to ping TR for relevent info 
                    if not metaData['cusipNumber'] and not metaData['symbol']:
                        # send us email
                        send_mail(
                            'Missing Holding',
                            metaData['description'],
                            'danger@vestivise.com',
                            ['raylen@vestivise.com', 'alex@vestivise.com', 'josh@vestivise.com'],
                            fail_silently=False,
                        )
                        metaData["completed"] = False
                        # we need to process this account
                        needsProcessing = True
                        
                    holding["metaData"] = HoldingMetaData.objects.create(**metaData).id

                # get holding
                if hasattr(yodleeAccount, 'holdings'):
                    try:
                        holdingMetaData = HoldingMetaData.objects.get(
                            description=holding.get('description')
                        )
                        userHolding = yodleeAccount.holdings.get(
                            metaData=holdingMetaData,
                            createdAt=yodleeLastUpdate
                        )
                        if userHolding.quantity != holding.get('quantity'):
                            shouldUpdate = True
                    except Holding.DoesNotExist:
                        # found new holding
                        shouldUpdate = True
                serializersList.append(holding)

        # if the account has previously processed and the holdings now have been processed
        # the user is now ready to view his account
        # might have to move this to a method that saves the historical returns so that user can view once the returns
        # are in the backend
        if yodleeAccount.requiresProcessing and not needsProcessing:
            yodleeAccount.requiresProcessing = False
            yodleeAccount.save()
            # send email to user that account is ready to view
        
        if needsProcessing:
            sendProcessingHoldingNotification(email)

        if shouldUpdate:
            serializer = HoldingSerializer(data=serializersList, many=True)
            if serializer.is_valid():
                serializer.save()
                yodleeAccount.updatedAt = timeNow
                yodleeAccount.requiresProcessing = needsProcessing
                yodleeAccount.save()
            else:
                # log failed to serailze holding
                print("holdings serialization error")
                for error in serializer.errors:
                    for key, value in error.items():
                        print(unicode(value[0]))

def serialize_asset_classes(assetClasses, userData):
    pass

def serialize_investment_options(userData, authToken, userToken):
    for account in userData.yodleeAccounts.all():
        investmentOptions = YodleeAPI.getInvestmentOptions(authToken, userToken, account.accountID)
        print(investmentOptions)
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

def serialize_transactions(authToken, userToken, userData):
    pass
    # for yodleeAccount in userData.yodleeAccounts.all():
    #     
    #     if yodleeAccoutn has no transactions
    #     transactionDate = 3 years from today
    #     else it will be the the transaction date of the latest yodleeAcount transaction object
    #     transactions = YodleeAPI.getTransactions(authToken, userToken, yodleeAccount.container, yodleeAccount.accountID, transactionDate)
    #     for each transaction in transactions
    #     serialize and save


class HoldingMetaDataListView(generics.ListAPIView):
    serializer_class = HoldingMetaDataSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = HoldingMetaData.objects.all()

        completed = self.request.query_params.get('completed', None)
        if completed is not None:
            queryset = HoldingMetaData.objects.filter(completed=(completed.lower() == "true"))

        return queryset


class HoldingMetaDataDetailView(generics.UpdateAPIView):
    serializer_class = HoldingMetaDataSerializer
    permission_classes = (IsAdminUser,)
    queryset = HoldingMetaData.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save()
        userDatas = UserData.objects.filter(yodleeAccounts__holdings__metaData=instance.id).distinct()
        for userData in userDatas:
            yodleeAccounts = YodleeAccount.objects.filter(userData=userData, requiresProcessing=True)
            processedAccounts = 0
            for yodleeAccount in yodleeAccounts:
                holdings = Holding.objects.filter(
                        createdAt=yodleeAccount.updatedAt
                    )
                completedHoldings = True
                for holding in holdings:
                    if not holding.completed:
                        completedHoldings = False
                        break
                if completedHoldings and yodleeAccount.requiresProcessing:
                    processedAccounts += 1
                    yodleeAccount.requiresProcessing = False
                    yodleeAccount.save()
            if processedAccounts == yodleeAccounts.count():
                print("email send")
                userProfile = UserProfile.objects.get(data=userData)
                email = User.objects.get(profile=userProfile).email
                sendHoldingProcessingCompleteNotification(email)



# AXUILIARY METHODS
def revokeTokens(request):
    request.session["tokenIsValid"] = False
    request.session["cobSessionToken"] = None
    request.session["userToken"] = None
