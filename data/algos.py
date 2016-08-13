from data.models import *
from django.http import JsonResponse
import numpy as np
import pandas as pd
import itertools
from data.chartFormat import *

def basicRisk(request):
	'''
	BASIC RISK MODULE:
	Returns the calculated Sharpe Ratio of the
	user's portfolio, using the shortest term
	treasury bond rate as risk free rate of 
	return. 

	OUTPUT:
	A JSON containing only the ratio of the portfolio.
	{'ratio': <value>}

	NOTE: Some of this is patchwork right now. Fixing it.
	'''
	accounts = request.user.profile.data.yodleeAccounts.all()
	holds = itertools.chain([x.holdings.get(createdAt=x.lastHoldingsUpdate) for x in accounts])
	allocations = [(x.symbol, x.assetClassifications.all()[0].allocation) for x in holds]
	weight = np.matrix([x[1]/100 for x in allocations])
	securityValues = []
	for alloc in allocations:
		temp = Security.objects.get(symbol=alloc[0])
		securityValues.append([float(x.price) for x in temp.securityPrice_set.all().order_by('date')])
	returns = [np.diff(s)/s[:-1] for s in securityValues]
	mu = [x.mean() for x in returns]
	sigma = np.cov(returns)
	ratio = (weight.T*mu - .29) / np.sqrt(weight.T * sigma * weight)
	return JsonResponse({'ratio':ratio.A[0][0]}, status=200)

def basicCost(request):
	'''
	BASIC COST MODULE:
	Returns the sum over the net expense ratios
	of the user's investment options. 

	OUTPUT:
	A JSON containing only the aggregate net expense
	ratio. 
	{'ERsum' : <value>}
	'''
	accounts = request.user.profile.data.yodleeAccounts.all()
	invOptions = itertools.chain([x.investmentOptions.all() for x in accounts])
	ers = [x.netExpenseRatio for x in invOptions]
	return JsonResponse({'ERsum': np.sum(ers)}, status=200)

def basicReturns(request):
	'''
	BASIC RETURNS MODULE:
	Returns a list of all the historic returns 
	associated with a user's investment options. 

	OUTPUT:
	A JSON containing a list of all the 
	historic returns associated with that 
	investment option, keys are the symbol of that
	option. 
	'''
	accounts = request.user.profile.data.yodleeAccounts.all()
	invOptions = itertools.chain([x.investmentOptions.all() for x in accounts])
	returnDict = dict([(x.symbol, x.historicReturns) for x in invOptions])
	return JsonResponse(returnDict, status=200)

def basicAssets(request):
	'''
	BASIC ASSETS MODULE:
	Returns the total amount invested in the holdings,
	and the percentage of the total amount invested
	in which type of holdings.

	OUTPUT:
	A JSON mapping 'percentages', to a dictionary
	of holdingTypes to their corresponding percentages,
	and 'totalInvested' to the total amount invested in
	the portfolio.
	'''
	accounts = request.user.profile.data.yodleeAccounts.all()
	holds = itertools.chain([x.holdings.get(createdAt=x.lastHoldingsUpdate) for x in accounts])
	holdingValues = {}
	totalValue = 0
	for h in holds:
		if h.holdingType in holdingValues:
			holdingValues[h.holdingType] += h.value.amount
		else:
			holdingValues[h.holdingType] = h.value.amount
		totalValue += h.value.amount
	for h in holdingValues:
		holdingValues[h] = holdingValues[h]/totalValue
	return JsonResponse({'percentages': holdingValues,
						'totalInvested':totalValue},
						status=200)