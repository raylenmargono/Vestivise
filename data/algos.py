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
        denom = np.sqrt(sigma.dot(weights).dot(weights))
        ratio = (mu.dot(weights) - .0036) / denom

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

        bench = Holding.objects.get(ticker=target).returns.latest('createdAt')
        # curVal = bench.holdingPrices.latest('closingDate').price
        # bVal1 = bench.holdingPrices.filter(closingDate__gte=datetime.now()-timedelta(weeks=1*52)).order_by('closingDate')[0].price
        # bVal2 = bench.holdingPrices.filter(closingDate__gte=datetime.now()-timedelta(weeks=2*52)).order_by('closingDate')[0].price
        # bVal3 = bench.holdingPrices.filter(closingDate__gte=datetime.now()-timedelta(weeks=3*52)).order_by('closingDate')[0].price
        # benchRet = [(curVal-bVal1)/bVal1, (curVal-bVal2)/bVal2, (curVal-bVal3)/bVal3]
        benchRet = [bench.oneYearReturns, bench.twoYearReturns, bench.threeYearReturns]
        return network_response({
            "returns": dispReturns,
            "benchmark": benchRet
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
    try:
        holds = request.user.profile.quovoUser.userDisplayHoldings.all()
        totalVal = sum([x.value for x in holds])
        breakDowns = [dict([(x.category, x.percentage * h.value/totalVal)
                    for x in h.holding.equityBreakdowns.filter(updateIndex__exact=h.holding.currentUpdateIndex)])
                    for h in holds]
        resDict = {'Materials': 0.0, 'ConsumerCyclic': 0.0, 'Financial': 0.0,
                   'RealEstate': 0.0, 'Healthcare': 0.0, 'Utilities': 0.0,
                   'Communication': 0.0, 'Energy': 0.0, 'Industrials': 0.0,
                   'Technology': 0.0, 'ConsumerDefense': 0.0}
        for breakDown in breakDowns:
            for kind in resDict:
                if kind in breakDown:
                    resDict[kind] += breakDown[kind]
        resDict['Consumer'] = resDict.pop('ConsumerCyclic') + resDict.pop('ConsumerDefense')
        return network_response(resDict)
    except Exception as err:
        # Log error.
        return JsonResponse({'Error': str(err)})


def bondTypes(request):
    try:
        holds = request.user.profile.quovoUser.userDisplayHoldings.all()
        totalVal = sum([x.value for x in holds])
        breakDowns = [dict([(x.category, x.percentage * h.value/totalVal)
                    for x in h.holding.equityBreakdowns.filter(updateIndex__exact=h.holding.currentUpdateIndex)])
                      for h in holds]
        resDict = {"Government": 0.0, "Municipal": 0.0, "Corporate": 0.0,
                   "Securitized": 0.0, "Cash": 0.0}
        for breakDown in breakDowns:
            for kind in resDict:
                if kind in breakDown:
                    resDict[kind] += breakDown[kind]
        return network_response(resDict)
    except Exception as err:
        #TODO log
        return JsonResponse({'Error': str(err)})


def contributionWithdraws(request):
    qUser = request.user.profile.quovoUser
    withdraws = qUser.getWithdraws()
    contributions = qUser.getContributions()

    today = datetime.today()
    year = today.year
    oneYear = year - 1
    twoYear = year - 2
    threeYear = year - 3

    payload = {
        "oneYear" : {
            "contributions": 0,
            "withdraw": 0,
            "net": 0
        },
        "twoYear" : {
            "contributions": 0,
            "withdraw": 0,
            "net": 0
        },
        "threeYear" : {
            "contributions": 0,
            "withdraw": 0,
            "net": 0
        },
        "total" : {
            "contributions": 0,
            "withdraw": 0,
            "net": 0
        }
    }

    def insert_payload(transaction, payload, category):
        date = transaction.date.year
        if date == oneYear:
            place = "oneYear"
        elif date == twoYear:
            place = "twoYear"
        elif date == threeYear:
            place = "threeYear"
        else:
            return
        payload[place][category] += abs(transaction.value)
        payload["total"][category] += abs(transaction.value)
        real_value = abs(transaction.value)
        if category == "withdraw":
            real_value = -real_value
        payload[place]["net"] += real_value
        payload["total"]["net"] += real_value

    for transaction in contributions:
        insert_payload(transaction, payload, "contributions")

    for transaction in withdraws:
        insert_payload(transaction, payload, "withdraw")

    return network_response(payload)


def returnsComparison(request):
    pass


def riskAgeProfile(request):
    profile = request.user.profile
    age = profile.get_age()

    holds = request.user.profile.quovoUser.userDisplayHoldings.all()
    totalVal = sum([x.value for x in holds])
    breakDowns = [dict([(x.asset, x.percentage * h.value / totalVal) for x in h.holding.assetBreakdowns.filter(updateIndex__exact=h.holding.currentUpdateIndex)]) for h in holds]
    type_list = ['BondLong', 'BondShort']

    total = 0
    for breakDown in breakDowns:
        for kind in type_list:
            if kind in breakDown:
                total += breakDown[kind]

    if age + 10 >= total >= age - 10:
        result = "Good"
        barVal = 0.8
    elif age + 20 >= total >= age - 20:
        result = "Moderate"
        barVal = 0.5
    else:
        result = "Bad"
        barVal = 0.2

    return network_response({
        "riskLevel": result,
        "barVal": barVal
    })



def riskComparison(request):
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
