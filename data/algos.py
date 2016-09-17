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
        acctWeights = request.user.profile.data.getWeights()
        print(acctWeights)
        #Check that the acctWeights aren't uniformly zero, or a singlular zero.
        if(acctWeights == [0] or acctWeights == [0]*len(acctWeights)):
            return JsonResponse({})

        #With the hideous part out of the way, pandas makes everything else
        #easy.

        identifiers = [h[0] for h in acctWeights]
        weight = [h[1] for h in acctWeights]

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
        print(err)
        return JsonResponse({'Error': str(err)})


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
        acctWeights = request.user.profile.data.getWeights()

        #Check that the acctWeights aren't uniformly zero, or a singlular zero.
        if(acctWeights == [0] or acctWeights == [0]*len(acctWeights)):
            return JsonResponse({})

        #With the hideous part out of the way, pandas makes everything else
        #easy.

        identifiers = [h[0] for h in acctWeights]
        weight = [h[1] for h in acctWeights]

        ers = trapi.securityExpenseRatio(identifiers)


        #If no account has an expense ratio, or if the expense
        #ratio list is otherwise empty, return a null dict
        if(not ers):
            return JsonResponse({})

        #Looks like everything else went well, so let's return
        #the weighted expense ratio
        fee = np.dot(ers, weight)
        averagePlacement = ''
        if fee < .64 - .2:
            averagePlacement = "less"
        elif fee > .64 + .2:
            averagePlacement = "more"
        else:
            averagePlacement = "similar to"
        return JsonResponse({'fee': fee, "averagePlacement" : averagePlacement}, status=200)
    except Exception as err:
        #Log error when we have that down
        print(err)
        return JsonResponse({'Error': str(err)})


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

        #Return null dict if they have no accounts in their yodleeAccounts
        if(not accounts):
            return JsonResponse({})

        #Hideous, but constructs a list of each account's percentage of the
        #overall portfolio. IE, the weight of each account.
        #If an account has no holdings, it is given a weight
        #of 0.
        acctWeights = request.user.profile.data.getWeights()
        print(acctWeights)
        #Check that the acctWeights aren't uniformly zero, or a singlular zero.
        if(acctWeights == [0] or acctWeights == [0]*len(acctWeights)):
            return JsonResponse({})

        #With the hideous part out of the way, pandas makes everything else
        #easy.

        identifiers = [h[0] for h in acctWeights]
        weights = [h[1] for h in acctWeights]

        #NOTE PUT FUCKIN' S&P 500 RIC HERE
        #NOTE READ ABOVE
        #NOTE IT'S REALLY IMPORTANT
        secHist = trapi.securityHistory(identifiers + [('.SPX', 'Ric')],
                    datetime.date.today()-datetime.timedelta(days=365),
                    datetime.date.today(),
                    dataFrame=True).fillna(method='ffill')
        #Returns for portfolio and returns for benchmark.
        print(secHist)
        retP = []
        retB = []
        monthRets = secHist.loc[[secHist.index[-1]-datetime.timedelta(days=21),
                secHist.index[-1]]].pct_change().values[1]
        retP.append(np.dot(weights,monthRets[:-1])*100)
        retB.append(monthRets[-1]*100)

        month3Rets = secHist.loc[[secHist.index[-1]-datetime.timedelta(days=63),
                secHist.index[-1]]].pct_change().values[1]
        retP.append(np.dot(weights,month3Rets[:-1])*100)
        retB.append(monthRets[-1]*100)

        yearRets = secHist.loc[[secHist.index[0], secHist.index[-1]]].pct_change().values[1]

        retP.append(np.dot(weights,yearRets[:-1])*100)
        retB.append(yearRets[-1]*100)


        returnData = {
            "returns" : retP,
            "benchMark" : retB
            }
        return JsonResponse(returnData)
    except Exception as err:
        #Log error when we have that down
        return JsonResponse({'Error': str(err)})

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

        #Return null dict if they have no accounts in their yodleeAccounts
        if(not accounts):
            return JsonResponse({})

        #Hideous, but constructs a list of each account's percentage of the
        #overall portfolio. IE, the weight of each account.
        #If an account has no holdings, it is given a weight
        #of 0.
        acctWeights, totalValue = request.user.profile.data.getWeights(totalValue=True)

        #Check that the acctWeights aren't uniformly zero, or a singlular zero.
        if(acctWeights == [0] or acctWeights == [0]*len(acctWeights)):
            return JsonResponse({})

        #With the hideous part out of the way, pandas makes everything else
        #easy.

        identifiers = [h[0] for h in acctWeights]
        identWeight = dict([(h[0][0], h[1]) for h in acctWeights])

        #Associate each hold with its holdingtype,
        #and totaling the value of that holdingtype
        #while totaling the value of the portfolio.
        #Ignore holdings that are missing the value
        #or type.
        holds = trapi.fundAllocation(identifiers)
        assetPerc = dict()
        for h in holds:
            if h['Allocation Percentage'] > 0:
                if h['Allocation Asset Type'] not in assetPerc:
                    assetPerc[h['Allocation Asset Type']] = h['Allocation Percentage']*identWeight[h['Identifier']]
                else:
                    assetPerc[h['Allocation Asset Type']] += h['Allocation Percentage']*identWeight[h['Identifier']]
        return JsonResponse({'percentages': [{'name' : h, 'percentage' : assetPerc[h]} for h in assetPerc],
                            'totalInvested':totalValue},
                            status=200)
    except Exception as err:
        #Log error when we can diddily-do that.
        return JsonResponse({'Error': str(err)})

# TEST DATA
def basicRiskTest(request):
    data = {
        "riskLevel" : "Moderate"
    }
    return JsonResponse(data)


def basicReturnsTest(request):
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


def basicCostTest(request):
    data = {
        "fee" : 2.2,
        "averagePlacement" : "more"
    }
    return JsonResponse(data)
