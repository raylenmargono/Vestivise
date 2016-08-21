import requests
import json

coBrandUser = "sbCobvestivise"
coBrandPass = "ad9adaf9-45cd-49f8-993d-51ffc1cedf97"

apiBase = "https://developer.api.yodlee.com/ysl/restserver/"

apis = {
    "cobrandLogin": apiBase + "v1/cobrand/login",
    "userLogin": apiBase + "v1/user/login",
    "userRegister": apiBase + "v1/user/register",
    "accounts": apiBase + "v1/accounts",
    "accountsDetail": apiBase + "v1/accounts",
    "holdings": apiBase + "v1/holdings",
    "holdingListType": apiBase + "v1/holdings/holdingTypeList",
    "assetClassificationList": apiBase + "v1/holdings/assetClassificationList",
    "historicalBalances": apiBase + "v1/accounts/historicalBalances",
    "investmentOptions": apiBase + "v1/accounts/investmentPlan/investmentOptions"
}


class YodleeException(Exception):
    def __init___(self, dErrorArguments):
        Exception.__init__(self, dErrorArguments)


def getAuthToken():
    # log in the future
    print("obtaining auth token")
    data = {
        "cobrandLogin": coBrandUser,
        "cobrandPassword": coBrandPass,
        "cobrandName": "restserver"
    }
    r = requests.post(apis["cobrandLogin"], data=data)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()["session"]["cobSession"]


def getUserToken(loginName, loginPassword, authToken):
    print("obtaining user token")

    data = {
        "loginName": loginName,
        "password": loginPassword,
        "cobrandName": "restserver",
        "locale": "en_US"
    }
    headers = {'Authorization': "cobSession=" + authToken}
    r = requests.post(apis["userLogin"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    accessToken = r.json()["user"]["session"]["userSession"]
    return accessToken


def registerUser(payload, authToken):

    print("registering yodlee user")

    payload['cobrandName'] = coBrandUser
    headers = {'Authorization': "cobSession=" + authToken}
    print(json.dumps(payload))
    data = {
        "userParam" : json.dumps(payload),
        "registerParam" : json.dumps(payload)
    }
    r = requests.post(apis["userRegister"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()


def getAccounts(authToken, userToken):
    print("obtaining yodlee accounts")

    data = {
        "cobrandName": "restserver"
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }

    r = requests.get(apis["accounts"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()


def deleteAccount(authToken, userToken, accountID):
    print("deleting account %s" % (accountID,))

    data = {
        "cobrandName": "restserver",
        "accountId": accountID
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }

    r = requests.delete(apis["accountsDetail"] + "/" + str(accountID), data=data, headers=headers)

    if r.status_code == 204:
        return

    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])


def getHoldings(authToken, userToken, holdingType, accountID, providerAccountId):

    print("obtaining yodlee holdings")

    data = {
        "cobrandName": "restserver",
        "holdingType": holdingType,
        "accountId": accountID,
        "providerAccountId": providerAccountId
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.get(apis["holdings"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()


def getHoldingListTypes(authToken, userToken):

    print("obtaining yodlee holding type list")

    data = {
        "cobrandName": "restserver"
    }
    headers = {
        "Authorization": "cobSession=%s" % (authToken,)
    }
    r = requests.get(apis["holdingListType"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()


def getAssetClassList(authToken, userToken):

    print("obtaining yodlee asset class list")

    data = {
        "cobrandName": "restserver"
    }
    headers = {
        "Authorization": "cobSession=%s" % (authToken, )
    }
    r = requests.get(apis["assetClassificationList"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()


def getHistoricalBalances(authToken, userToken, accountId, toDate, fromDate):

    print("obtaining yodlee historical balances")

    data = {
        "cobrandName": "restserver",
        "accountId": accountId,
        "toDate": toDate,
        "fromDate": fromDate,
        "interval": "M",
        "includeCF": True
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.get(apis["historicalBalances"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()


def getInvestmentOptions(authToken, userToken, accountID):

    print("obtaining yodlee investment options")

    data = {
        "cobrandName": "restserver",
        "accountId": accountID,
        "include" : "assetClassification"
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.get(apis["investmentOptions"], data=data, headers=headers)
    if "errorMessage" in r.json():
        raise YodleeException(r.json()['errorMessage'])
    return r.json()
