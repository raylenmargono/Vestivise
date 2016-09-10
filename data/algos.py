from data.models import *
from django.http import JsonResponse
import numpy as np
import pandas as pd
import pandas.io.data as web
import itertools
from data.chartFormat import *
import thomson.apis as trapi
import datetime

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
	try:
		#Return null dict if they have no yodleeAccounts object
		if(not hasattr(request.user.profile.data, 'yodleeAccounts')):
			return JsonResponse({})
		accounts = request.user.profile.data.yodleeAccounts.all()

		#Return null dict if they have no accounts in their yodleeAccounts
		if(not accounts):
			return JsonResponse({})

		#Hideous, but constructs a list of each account's percentage of the
		#overall portfolio. IE, the weight of each account.
		#If an account has no holdings, it is given a weight
		#of 0.
		acctWeights = np.array([sum([x.value.amount
					for x in a.holdings.filter(createdAt__exact = a.updatedAt)])
					if hasattr(a, 'holdings') else 0 for a in accounts])

		#Check that the acctWeights aren't uniformly zero, or a singlular zero.
		if(acctWeights == [0] or acctWeights == [0]*len(acctWeights)):
			return JsonResponse({})
		acctWeights = acctWeights/sum(acctWeights)

		#Also hideous, but constructs a list of touples with the symbols
		#and their corresponding (now correct) weights.
		#Assets without symbols (or an assetClassifications) are skipped
		allocations = [(h.getIdentifier(), h.assetClassifications.all()[0].allocation*w/100)
						for h in a.holdings.filter(createdAt__exact = a.updatedAt)
						if (hasattr(h, symbol) and hasattr(h, assetClassifications))
						for a,w in itertools.izip(accounts, acctWeights)]

		#With the hideous part out of the way, pandas makes everything else
		#easy.

		identifiers = [h[0] for h in allocations]
		weight = [h[1] for h in allocations]

		ratio = trapi.sharpeRatio(weight, identifiers,
		 	datetime.date.today()-datetime.timedelta(days=365),
			datetime.date.today())
		ratScale = 0
		if ratio > 0:
			ratScale = np.log(ratio)/np.log(4)
		ret = ''
		if ratScale is 0:
			ret = 'Bad'
		elif ratScale > .66:
			ret = 'Good'
		else:
			ret = 'Moderate'
		return JsonResponse({'riskLevel':ret}, status=200)
	except Exception as err:
		#Log error when we have that down.
		return JsonResponse({'Error': err})


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
	try:
		#Return null dict if they have no yodleeAccounts object
		if(not hasattr(request.user.profile.data, 'yodleeAccounts')):
			return JsonResponse({})
		accounts = request.user.profile.data.yodleeAccounts.all()

		#Return null dict if they have no accounts in their yodleeAccounts
		if(not accounts):
			return JsonResponse({})

		#Hideous, but constructs a list of each account's percentage of the
		#overall portfolio. IE, the weight of each account.
		#If an account has no holdings, it is given a weight
		#of 0.
		acctWeights = np.array([sum([x.value.amount
					for x in a.holdings.filter(createdAt__exact = a.updatedAt)])
					if hasattr(a, 'holdings') else 0 for a in accounts])

		#Check that the acctWeights aren't uniformly zero, or a singlular zero.
		if(acctWeights == [0] or acctWeights == [0]*len(acctWeights)):
			return JsonResponse({})
		acctWeights = acctWeights/sum(acctWeights)

		#Also hideous, but constructs a list of touples with the symbols
		#and their corresponding (now correct) weights.
		#Assets without symbols (or an assetClassifications) are skipped
		allocations = [(h.getIdentifier(), h.assetClassifications.all()[0].allocation*w/100)
						for h in a.holdings.filter(createdAt__exact = a.updatedAt)
						if (hasattr(h, symbol) and hasattr(h, assetClassifications))
						for a,w in itertools.izip(accounts, acctWeights)]
		weights = [x[1] for x in allocations]
		identifiers = [x[0] for x in allocations]

		ers = trapi.securityExpenseRatio(identifiers)

		#If no account has an expense ratio, or if the expense
		#ratio list is otherwise empty, return a null dict
		if(not ers):
			return JsonResponse({})

		#Looks like everything else went well, so let's return
		#the average expense ratio.
		return JsonResponse({'fee': np.dot(ers, weights), status=200)
	except Exception as err:
		#Log error when we have that down
		return JsonResponse({'Error': err})


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
	{'Symbol1': { some historic returns },
	 'Symbol2': { some more thrilling historic returns }
	}
	'''
	try:
		#Return null dict if they have no yodleeAccounts object
		if(not hasattr(request.user.profile.data, 'yodleeAccounts')):
			return JsonResponse({})

		accounts = request.user.profile.data.yodleeAccounts.all()

		#Return null dict if they come up as having no yodleeAccounts
		if(not accounts):
			return JsonResponse({})


		#Create the list of expense ratios, if an invOptions
		#doesn't have an expense ratio, it is ignored.
		invOptions = itertools.chain([x.investmentOptions.all()
					for x in accounts
					if hasattr(x, 'investmentOptions')])

		#Return a null dict if invOptions is an empty list
		if(not list(invOptions)):
			return JsonResponse({})

		returnDict = dict([(x.symbol, x.historicReturns)
		for x in invOptions
		if (hasattr(x, 'symbol') and hasattr(x, 'historicReturns'))])

		#We could send a null dict if the returnDict was empty
		#but I mean it's already empty and we plan on returning
		#it.

		return JsonResponse(returnDict, status=200)
	except Exception as err:
		#Log error when we can do that
		return JsonResponse({'Error': err})

def basicAsset(request):
	'''
	BASIC ASSETS MODULE:
	Returns the total amount invested in the holdings,
	and the percentage of the total amount invested
	in which type of holdings.

	OUTPUT:
	A JSON mapping 'percentages', to a dictionary
	of holdingTypes strings to their corresponding percentages,
	and 'totalInvested' to the total amount invested in
	the portfolio.
	{'percentages': {'realEstate': 75.00
					'someOtherThing':25.00}
	 'totalInvested': 100000
	 }
	'''
	try:
		#Return null dict if they have no yodleeAccounts object
		if(not hasattr(request.user.profile.data, 'yodleeAccounts')):
			return JsonResponse({})

		accounts = request.user.profile.data.yodleeAccounts.all()

		#Return null dict if they come up as having no yodleeAccounts
		if(not accounts):
			return JsonResponse({})

		holds = list(itertools.chain(*[x.holdings.filter(createdAt__exact = x.updatedAt)
				for x in accounts
				if hasattr(x, 'holdings')]))

		#Return null dict if user has no holdings in investmentOptions
		if(not list(holds)):
			return JsonResponse({})


		holdingValues = {}
		totalValue = 0
		#Associate each hold with its holdingtype,
		#and totaling the value of that holdingtype
		#while totaling the value of the portfolio.
		#Ignore holdings that are missing the value
		#or type.
		for h in holds:
			if hasattr(h, 'quantity') and hasattr(h, 'holdingType'):
				if not h.quantity or not h.holdingType:
					continue
				if h.holdingType in holdingValues:
					holdingValues[h.holdingType] += h.value.amount
				else:
					holdingValues[h.holdingType] = h.value.amount
				totalValue += h.value.amount
		#Turn those values into percentages.
		for h in holdingValues:
			holdingValues[h] = holdingValues[h]*100/totalValue
		#Return the results.
		return JsonResponse({'percentages': holdingValues,
							'totalInvested':totalValue},
							status=200)
	except Exception as err:
		#Log error when we can diddily-do that.
		return JsonResponse({'Error': err})

# TEST DATA
def basicRiskTest(request):
	data = {
		"riskLevel" : "moderate"
	}
	return JsonResponse(data)


def basicReturnTest(request):
	returnData = {
		"returns" : [0.3, 2, 4, 5],
	    "benchMark" : [0.48,4.06,4.70,8.94]
	}
	return JsonResponse(returnData)



def basicAssetTest(request):
	assetData = {
		"percentages" :[
			{
				"name" : "Bonds",
				"percentage" : 35,
			},
			{
				"name" : "Stocks",
				"percentage" : 26.8,
			},
			{
				"name": 'Commodities',
				"percentage": 28.8,
			},
			{
				"name" : 'Real Estate',
				"percentage": 10,
			}
		],
		"totalInvested" : 30000
	}
	return JsonResponse(assetData)


def basicFeeTest(request):
	data = {
		"fee" : 2.2,
		"averagePlacement" : "greater"
	}
	return JsonResponse(data)
