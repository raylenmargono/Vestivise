from data.models import *
from django.http import JsonResponse
import numpy as np 
import pandas as pd 
import decimal

def BasicRisk(request):
	'''
	BASIC RISK MODULE:
	Returns the calculated Sharpe Ratio of the
	user's portfolio, using the shortest term
	treasury bond rate as risk free rate of 
	return. 

	OUTPUT:
	A JSON containing only the ratio of the portfolio.
	{'ratio': <value>}
	'''
	account = request.user.profile.data.yodleeAccount
	allocations = [(x.symbol, x.allocation) for x in request.user.profile.data.YodleeAccount.latest('createdAt')]
	weight = np.matrix([float(x[1])/100 for x in allocations])
	stockValues = []
	for alloc in allocations:
		temp = Stock.objects.get(symbol=alloc[0])
		stockValues.append([float(x.price) for x in temp.stockprice_set.all().order_by('date')])
	returns = [np.diff(s)/s[:-1] for s in stockValues]
	mu = [x.mean() for x in returns]
	sigma = np.cov(returns)
	ratio = (weight.T*mu - .29)/ np.sqrt(weight.T*sigma*weight)
	return JsonResponse({'ratio':ratio.A[0][0]}, status=200)
