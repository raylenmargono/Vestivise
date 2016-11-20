from django.http import JsonResponse
import numpy as np
import pandas as pd
from django.utils.datetime_safe import datetime
from data.models import Holding
from Vestivise.Vestivise import network_response
from datetime import timedelta

AgeBenchDict = {2010: 'VTENX', 2020: 'VTWNX', 2030: 'VTHRX', 2040: 'VFORX',
                2050: 'VFIFX', 2060: 'VTTSX'}


def riskReturnProfile(request):
    """
    BASIC RISK MODULE:
    Returns the calculated Sharpe Ratio of the
    user's portfolio, using the shortest term
    treasury bond rate as risk free rate of
    return.

    OUTPUT:
    A JSON containing only the ratio of the portfolio.
    {'ratio': <value>}

    """
    try:
        holds = request.user.profile.quovoUser.getDisplayHoldings()
        sizMin = 252*3
        prices = []
        for hold in holds:
            tempPrice = [x.price for x in hold.holding.holdingPrices.filter(
                closingDate__lte=datetime.now()
            ).filter(
                closingDate__gte=datetime.now()-timedelta(weeks=3*52)
            ).order_by('closingDate')]
            if len(tempPrice) < sizMin:
                sizMin = len(tempPrice)
            prices.append(tempPrice)
        for i in range(len(prices)):
            if len(prices[i]) > sizMin:
                prices[i] = prices[i][len(prices[i])-sizMin:]

        returns = pd.DataFrame(prices).pct_change(axis=1).iloc[:, 1:]
        mu = returns.mean(axis=1)
        sigma = returns.T.cov()
        totVal = sum([x.value for x in holds])
        weights = [x.value / totVal for x in holds]
        ratio = (mu.dot(weights) - .36) / np.sqrt(sigma.dot(weights).dot(weights))

        ratScale = 0
        if ratio > 0:
            ratScale = np.log(ratio+1)/np.log(5)
        if ratScale > 1:
            ratScale = 1
        if ratScale < .33:
            ret = 'Bad'
        elif ratScale > .66:
            ret = 'Good'
        else:
            ret = 'Moderate'

        return network_response({'riskLevel': ret, 'barVal': ratScale})
    except Exception as err:
        # Log error when we have that down.
        print(err)
        return JsonResponse({'Error': str(err)})


def fees(request):
    """
    BASIC COST MODULE:
    Returns the sum over the net expense ratios
    of the user's investment options.

    OUTPUT:
    A JSON containing only the aggregate net expense
    ratio.
    {'ERsum' : <value>}
    """
    try:
        holds = request.user.profile.quovoUser.getDisplayHoldings()
        totVal = sum([x.value for x in holds])
        weights = [x.value/totVal for x in holds]
        costRet = np.dot(weights, [x.holding.expenseRatios.latest('createdAt').expense for x in holds])
        if costRet < .64-.2:
            averagePlacement = 'less'
        elif costRet > .64 + .2:
            averagePlacement = 'more'
        else:
            averagePlacement = 'similar to'
        return network_response({'fee': costRet, 'averagePlacement': averagePlacement})
    except Exception as err:
        # Log error when we have that down
        print(err)
        return JsonResponse({'Error': str(err)})


def returns(request):
    """
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
    """
    global AgeBenchDict
    try:
        returns = request.user.profile.quovoUser.userReturns.latest('createdAt')
        dispReturns = [returns.oneYearReturns, returns.twoYearReturns, returns.threeYearReturns]

        birthday = request.user.profile.birthday
        retYear = birthday.year + 65
        targYear = retYear + ((10-retYear % 10) if retYear % 10 > 5 else -(retYear%10))
        if targYear < 2010:
            target = AgeBenchDict[2010]
        elif targYear > 2060:
            target = AgeBenchDict[2060]
        else:
            target = AgeBenchDict[targYear]

        bench = Holding.objects.get(ticker=target)
        curVal = bench.holdingPrices.latest('closingDate').price
        bVal1 = bench.holdingPrices.filter(closingDate__gte=datetime.now()-timedelta(weeks=1*52)).order_by('closingDate')[0].price
        bVal2 = bench.holdingPrices.filter(closingDate__gte=datetime.now()-timedelta(weeks=2*52)).order_by('closingDate')[0].price
        bVal3 = bench.holdingPrices.filter(closingDate__gte=datetime.now()-timedelta(weeks=3*52)).order_by('closingDate')[0].price
        benchRet = [(curVal-bVal1)/bVal1, (curVal-bVal2)/bVal2, (curVal-bVal3)/bVal3]
        return network_response({
            "returns": dispReturns,
            "benchMark": benchRet
        })
    except Exception as err:
        # Log error when we have that down
        return JsonResponse({'Error': str(err)})


def holdingTypes(request):
    """
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
    """
    try:
        holds = request.user.profile.quovoUser.userDisplayHoldings.all()
        totalVal = sum([x.value for x in holds])
        breakDowns = [dict([(x.asset, x.percentage * h.value/totalVal)
                      for x in h.holding.assetBreakdowns.filter(updateIndex__exact=h.holding.currentUpdateIndex)])
                      for h in holds]
        resDict = {'StockLong': 0.0, 'StockShort': 0.0,
                   'BondLong': 0.0, 'BondShort': 0.0,
                   'CashLong': 0.0, 'CashShort': 0.0,
                   'OtherLong': 0.0, 'OtherShort': 0.0}
        for breakDown in breakDowns:
            for kind in resDict:
                if kind in breakDown:
                    resDict[kind] += breakDown[kind]
        return network_response({
            'percentages': resDict,
            'totalInvested': totalVal
        })
    except Exception as err:
        # Log error when we can diddily-do that.
        return JsonResponse({'Error': str(err)})


def stockTypes(request):
    pass


def bondTypes(request):
    pass


def contributionWithdraws(request):
    pass


def returnsComparison(request):
    pass


def riskAgeProfile(request):
    pass


def riskComparison(request):
    pass


def taxTreatment(request):
    pass


def compInterest(request):
    pass


# TEST DATA
def basicRiskTest(request):
    data = {
        "riskLevel": "Moderate"
    }
    return JsonResponse(data)


def basicReturnsTest(request):
    returnData = {
        "returns": [0.3, 2, 4, 5],
        "benchMark": [0.48, 4.06, 4.70, 8.94]
    }
    return JsonResponse(returnData)


def basicAssetTest(request):
    assetData = {
        "percentages": [
            {
                "name": "Bonds",
                "percentage": 35,
            },
            {
                "name": "Stocks",
                "percentage": 26.8,
            },
            {
                "name": 'Commodities',
                "percentage": 28.8,
            },
            {
                "name": 'Real Estate',
                "percentage": 10,
            }
        ],
        "totalInvested": 30000
    }
    return JsonResponse(assetData)


def basicCostTest(request):
    data = {
        "fee": 2.2,
        "averagePlacement": "more"
    }
    return JsonResponse(data)
