from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from data.models import *
from account.models import *
import numpy as np 
import pandas as pd 
import decimal

# Create your views here.

# SHOULD PUT ALGO INTO DIFFERENT FILE e.g. algo.py
# this method should only call that algo and itll return the value
# this is important from a developer standpoint because we can take advantage of
# dependency injections on algo development.
def sharpe(request):
    allocations = [(x.symbol, x.allocation) for x in request.user.data.holding_set.all()]
    weight = np.matrix([float(x[1])/100 for x in allocations])
    stockValues = []
    for alloc in allocations:
        temp = stock.objects.get(symbol=alloc[0])
        stockValues.append([float(x.price) for x in temp.stockprice_set.all().order_by('date')])
    returns = [np.diff(s)/s[:-1] for s in stockValues]
    mu = [x.mean() for x in returns]
    sigma = np.cov(returns)
    ratio = (weight.T*mu - .29)/ np.sqrt(weight.T*sigma*weight)
    return JsonResponse({'ratio':ratio.A[0][0]}, status=200)

#### UTILITY FUNCTIONS
def addStock(symbol):
    #s = stock(symbol = symbol, lastUpdated=datetime.datetime.now().date())
    pass
def updateStock(symbol):
    pass
