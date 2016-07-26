import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view

apis = {
    "fastLinkToken": "https://rest.developer.yodlee.com/services/srest/restserver/v1.0/authenticator/token",
}


@api_view(['POST'])
def getFastLinkToken(request):

    if request.session.get('cobSessionToken') and request.session.get('userToken'):
        sessionToken = request.session.get('cobSessionToken')
        rsession = request.session.get('userToken')
        data = {
            "cobSessionToken": sessionToken,
            "rsession": rsession,
            "finAppId": "10003600"
        }

        r = requests.post(apis["fastLinkToken"], data=data)

        if "Error" in r.json():
                request.session['tokenIsValid'] = False
                return JsonResponse({"error": "Incorrect Credientials"}, status=400)
        res = r.json()
        res['rsession'] = request.session.get('userToken')
        return JsonResponse(res)
    else:
        return JsonResponse({"error": "Tokens not set"}, status=400)
