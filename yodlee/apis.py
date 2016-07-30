import requests

coBrandUser = "sbCobvestivise"
coBrandPass = "ad9adaf9-45cd-49f8-993d-51ffc1cedf97"

apiBase = "https://developer.api.yodlee.com/ysl/restserver/"

apis = {
    "cobrandLogin": apiBase + "v1/cobrand/login",
    "userLogin": apiBase + "v1/user/login",
    "userRegister": apiBase + "v1/user/register",
    "accounts": apiBase + "v1/accounts",
    "holdings": apiBase + "v1/holdings",
    "holdingListType": apiBase + "v1/holdings/holdingListType",
    "assetClassificationList": apiBase + "v1/holdings/assetClassificationList",
    "historicalBalances": apiBase + "v1/accounts/historicalBalances",
    "investmentOptions": apiBase + "v1/accounts/investmentPlan/InvestmentOptions"
}


def getAuthToken():
    data = {
        "cobrandLogin": coBrandUser,
        "cobrandPassword": coBrandPass,
        "cobrandName": "restserver"
    }
    r = requests.post(apis["cobrandLogin"], data=data)
    if "Error" in r.json():
        raise Exception("Incorrect Cobrand Credientals")
    return r.json()["session"]["cobSession"]


def getUserToken(loginName, loginPassword, authToken):
    data = {
        "loginName": loginName,
        "password": loginPassword,
        "cobrandName": "restserver",
        "locale": "en_US"
    }
    headers = {'Authorization': "cobSession=" + authToken}
    r = requests.post(apis["userLogin"], data=data, headers=headers)
    if "Error" in r.json():
        raise Exception("Incorrect Credientals")
    accessToken = r.json()["user"]["session"]["userSession"]
    return accessToken


def registerUser(payload, authToken):
    payload['cobrandName'] = coBrandUser
    headers = {'Authorization': "cobSession=" + authToken}
    r = requests.post(apis["userRegister"], data=payload, headers=headers)
    if "Error" in r.json():
        raise Exception(r.json["Error"])
    return r.json()


def getAccounts(authToken, userToken):
    data = {
        "cobrandName": "restserver"
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.post(apis["accounts"], data=data, headers=headers)
    if "Error" in r.json():
        raise Exception(r.json()["Error"])
    return r.json()


def getHoldings(authToken, userToken, holdingType, accountID, providerAccountId):
    data = {
        "cobrandName": "restserver",
        "holdingType": holdingType,
        "accountId": accountID,
        "providerAccountId": providerAccountId
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.post(apis["holdings"], data=data, headers=headers)
    if "Error" in r.json():
        raise Exception(r.json()["Error"])
    return r.json()


def getHoldingListTypes(authToken, userToken):
    data = {
        "cobrandName": "restserver"
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.post(apis["holdingListType"], data=data, headers=headers)
    if "Error" in r.json():
        raise Exception(r.json()["Error"])
    return r.json()


def getAssetClassList(authToken, userToken):
    data = {
        "cobrandName": "restserver"
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.post(apis["assetClassificationList"], data=data, headers=headers)
    if "Error" in r.json():
        raise Exception(r.json()["Error"])
    return r.json()


def getHistoricalBalances(authToken, userToken, accountId, toDate, fromDate):
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
    r = requests.post(apis["historicalBalances"], data=data, headers=headers)
    if "Error" in r.json():
        raise Exception(r.json()["Error"])
    return r.json()


def getInvestmentOptions(authToken, userToken):
    data = {
        "cobrandName": "restserver"
    }
    headers = {
        "Authorization": "cobSession=%s,userSession=%s" % (authToken, userToken)
    }
    r = requests.post(apis["investmentOptions"], data=data, headers=headers)
    if "Error" in r.json():
        raise Exception(r.json()["Error"])
    return r.json()
