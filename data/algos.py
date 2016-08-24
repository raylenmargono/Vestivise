from data.models import *
from django.http import JsonResponse
import numpy as np 
import pandas as pd 
import pandas.io.data as web
import itertools
from data.chartFormat import *
from yodlee.apis import getTransactions

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
		allocations = [(h.symbol, h.assetClassifications.all()[0].allocation*w/100) 
						for h in a.holdings.filter(createdAt__exact = a.updatedAt)
						if (hasattr(h, symbol) and hasattr(h, assetClassifications))
						for a,w in itertools.izip(accounts, acctWeights)]

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

		#Return null dict if they come up as having no yodleeAccounts
		if(not accounts):
			return JsonResponse({})

		#Create list of all investment options, if an account
		#has no associated investmentOptions object, then it will
		#be ignored.
		invOptions = itertools.chain([x.investmentOptions.all() 
					for x in accounts 
					if hasattr(x, 'investmentOptions')])

		#Return a null dict if invOptions is an empty list
		if(not list(invOptions)):
			return JsonResponse({})

		#Create the list of expense ratios, if an invOptions
		#doesn't have an expense ratio, it is ignored.
		ers = [x.netExpenseRatio for x in invOptions if hasattr(x, 'netExpenseRatio')]
		
		#If no account has an expense ratio, or if the expense
		#ratio list is otherwise empty, return a null dict
		if(not ers):
			return JsonResponse({})

		#Looks like everything else went well, so let's return
		#the average expense ratio.
		return JsonResponse({'ERavg': np.sum(ers)/len(invOptions)}, status=200)
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

		for x in accounts:
			sessionToken = request.session["cobSessionToken"]
			userToken = request.session["userToken"]
			print(getTransactions(sessionToken, userToken, x.container, x.accountID))

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