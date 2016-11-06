from django.http import JsonResponse
import numpy as np
import pandas as pd
from django.utils.datetime_safe import datetime
from data.models import Holding
from Vestivise.Vestivise import network_response
from datetime import timedelta


def basicRisk(request):
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
        holds = request.user.profile.quovoUser.userDisplayHoldings.all()
        sizMin = 252*3
        prices = []
        for hold in holds:
            tempPrice = [x.value for x in hold.holdingPrices.filter(
                closingDate__lte=datetime.now()
            ).filter(
                closingDate__gte=datetime.now()-timedelta(year=3)
            ).order_by('closingDate')]
            if len(tempPrice) < sizMin:
                sizMin = len(tempPrice)
            prices.append(tempPrice)
        for i in range(len(prices)):
            if len(prices[i]) > sizMin:
                prices[i] = prices[i][len(prices[i])-sizMin:]

        returns = pd.DataFrame(prices).pct_change(axis=1).iloc[:, 1:]
        mu = returns.mean(axis=1)
        sigma = returns.cov()
        totVal = sum([x.value for x in holds])
        weights = [x.value / totVal for x in holds]
        ratio = (mu.dot(weights) - .36) / sigma.dot(weights).dot(weights)

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


def basicCost(request):
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
        holds = request.user.profile.quovoUser.userDisplayHoldings.all()
        totVal = sum([x.value for x in holds])
        weights = [x.value/totVal for x in holds]
        costRet = np.dot(weights, [x.expenseRatios.latest('createdAt').expense for x in holds])
        averagePlacement = ''
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


def basicReturns(request):
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
    try:
        returns = request.user.profile.quovoUser.userReturns.latest('createdAt')
        dispReturns = [returns.oneYearReturns, returns.twoYearReturns, returns.threeYearReturns]
        bench = Holding.objects.get(ticker='SPX')
        curVal = bench.holdingPrices.latest('closingDate').value
        bVal1 = bench.holdingPrices.filter(closingDate__lt=datetime.now()-timedelta(years=1)).order_by('-closingDate')[0]
        bVal2 = bench.holdingPrices.filter(closingDate__lt=datetime.now()-timedelta(years=2)).order_by('-closingDate')[0]
        bVal3 = bench.holdingPrices.filter(closingDate__lt=datetime.now()-timedelta(years=3)).order_by('-closingDate')[0]
        benchRet = [(curVal-bVal1)/bVal1, (curVal-bVal2)/bVal2, (curVal-bVal3)/bVal3]
        return network_response({
            "returns": dispReturns,
            "benchMark": benchRet
        })
    except Exception as err:
        # Log error when we have that down
        return JsonResponse({'Error': str(err)})


def basicAsset(request):
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
                      for x in h.assetBreakdowns.filter(updateIndex__exact=h.currentUpdateIncex)])
                      for h in holds]
        resDict = {'Stock': 0.0, 'Bonds': 0.0, 'Cash': 0.0, 'Other': 0.0}
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
