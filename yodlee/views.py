import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Create your views here.

coBrandUser = "sbCobvestivise"
coBrandPass = "ad9adaf9-45cd-49f8-993d-51ffc1cedf97"

apiBase = "https://developer.api.yodlee.com/ysl/restserver/" + coBrandUser + "/"

apis = {
    "cobrandLogin": apiBase + "v1/cobrand/login",
    "userLogin": apiBase + "v1/user/login",
    "holdings": apiBase + "v1/holdings",
    "holdingListType": apiBase + "v1/holdings/holdingListType",
    "assetClassificationList": apiBase + "v1/holdings/assetClassificationList",
    "historicalBalances": apiBase + "v1/accounts/historicalBalances",
    "investmentOptions": apiBase + "v1/accounts/investmentPlan/InvestmentOptions",
    "fastLinkiFrame" : "https://node.developer.yodlee.com/authenticate/restserver/"
}

def registerUser(payload):
    pass

def getAppToken():
    data = {
        "cobrandLogin": coBrandUser,
        "cobrandPassword": coBrandPass
    }
    r = requests.post(apis["cobrandLogin"], data=data)
    if "Error" in r.json():
        raise Exception("Incorrect Cobrand Credientals")
    return r.json()["cobrandConversationCredentials"]["sessionToken"]


def getAccessToken(loginName, loginPassword):
    r = requests.post(apis["userLogin"], data={
            "loginName" : loginName,
            "password" : loginPassword
        })
    if "Error" in r.json():
        raise Exception("Incorrect Credientals")
    accessToken = r.json()["userContext"]["conversationCredentials"]["sessionToken"]
    return accessToken


@api_view(['POST'])
def getFastLinkToken(request):
    y = YodleeAPI()
    sessionToken = request.POST['cobSessionToken']
    rsession = request.POST['rsession']
    data = {
        "cobSessionToken": sessionToken,
        "rsession": rsession,
        "finAppId": "10003600"
    }

    r = requests.post(y.fastLinkToken, data=data)
    if "Error" in r.json():
            return JsonResponse({"error" : "Incorrect Credientials"}, status=400)
    res = r.json()
    return JsonResponse(res)

@api_view(['POST'])
def getFastLinkiFrame(request):
    y = YodleeAPI()
    print(request.POST)
    r = requests.post(y.fastLinkiFrame, data=request.POST)
    return JsonResponse({'test': r.text})