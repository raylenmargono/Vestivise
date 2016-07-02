import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Create your views here.

class YodleeAPI(object):
    def __init__(self):

        apiBase = "https://rest.developer.yodlee.com/services/srest/restserver/v1.0/"
        yodleeBase = "https://developer.api.yodlee.com/ysl/restserver/"

        self.getAppToken =  apiBase + "authenticate/coblogin"
        self.getAccessToken = apiBase + "authenticate/login"
        self.fastLinkToken = apiBase + "authenticator/token"
        self.register = yodleeBase + "sbCobvestivise/v1/user/register"
        self.fastLinkiFrame = "https://node.developer.yodlee.com/authenticate/restserver/"

        self.coBrandUser = "sbCobvestivise"
        self.coBrandPass = "ad9adaf9-45cd-49f8-993d-51ffc1cedf97"


def registerUser(payload):
    y = YodleeAPI()
    r = requests.post(y.register, data=payload)
    print r.json()

@api_view(['POST'])
def getAppToken(request):
    y = YodleeAPI()
    data = {
        "cobrandLogin": y.coBrandUser,
        "cobrandPassword": y.coBrandPass
    }
    r = requests.post(y.getAppToken, data=data)
    if "Error" in r.json():
        return JsonResponse({"error" : "Incorrect Cobrand Credientals"}, status=400)
    return JsonResponse({"token": r.json()["cobrandConversationCredentials"]["sessionToken"]}, status=200)


@api_view(['POST'])
def getAccessToken(request):
    y = YodleeAPI()
    r = requests.post(y.getAccessToken, data=request.POST)
    if "Error" in r.json():
            return JsonResponse({"error" : "Incorrect Credientials"}, status=400)
    accessToken = r.json()["userContext"]["conversationCredentials"]["sessionToken"]
    return JsonResponse({"token": accessToken})


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