from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import os
import json
from rest_framework.decorators import api_view

# Create your views here.


# ROUTE VIEWS

def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def linkAccountPage(request):
    return render(request, "dashboard/linkAccount.html")


# VIEW SETS







# TEST VIEWS
@api_view(('GET',))
def dashboardTestData(request):
    jsonFile = open(os.path.join(settings.BASE_DIR, 'dashboard/fixtures/basicAccountModel.json'))
    return JsonResponse(json.loads(jsonFile.read()))
