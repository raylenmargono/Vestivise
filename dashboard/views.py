from django.shortcuts import render

# Create your views here.


# ROUTE VIEWS

def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def linkAccountPage(request):
    return render(request, "dashboard/linkAccount.html")


# VIEW SETS

