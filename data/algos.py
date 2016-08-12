from data.models import *
from django.http import JsonResponse
import numpy as np 
import pandas as pd 
import pandas.io.data as web
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

	NOTE: Change pandas.io.data to use pandas_datareader
	in the future, to prevent complaining.
	'''

	accounts = request.user.profile.data.yodleeAccounts.all()
	#Hideous, bug constructs a list of each account's percentage of the
	#overall account.
	acctWeights = np.array([sum([x.value.amount for x in a.holdings.all()]) for a in accounts])
	acctWeights = acctWeights/sum(acctWeights)
	#Also hideous, but constructs a list of touples with the symbols
	#and their corresponding (now correct) weights
	allocations = [(h.symbol, h.assetClassifications.all()[0].allocation*w/100) for h in a.holdings.all() for a,w in zip(accounts, acctWeights)]

	#With the hideous part out of the way, pandas makes everything else
	#easy. 

	symbols = [h[0] for h in allocations]
	weight = np.matrix([h[1] for h in allocations])

	secRets = web.DataReader(symbols, 'yahoo', datetime.datetime.now()-datetime.timedelta(years=1), datetime.datetime.now-datetime.timedelta(days=1))['Close'].pct_change()

	mu = np.matrix(secRets.mean().as_matrix())
	sigma = np.matrix(secRets.cov())
	#Collect the current risk free rate of return
	rfrr = web.DataReader('^IRX', 'yahoo', datetime.datetime.now()-datetime.timedelta(days=1))['Close'][0]

	ratio = (weight.T*mu - rfrr) / np.sqrt(weight.T * sigma * weight)

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