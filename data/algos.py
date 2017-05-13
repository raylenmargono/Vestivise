import re
import math
import json

from django.db.models import F
from django.db.models import Func
from django.utils.datetime_safe import datetime
import numpy as np
from data.models import (AverageUserReturns, AverageUserBondEquity, HoldingExpenseRatio, AverageUserSharpe,
                         AverageUserFee, Benchmark)
from Vestivise import Vestivise


# UTILITY FUNCTIONS
def age_map(age):
    return age + (0 if age % 5 == 0 else 5 - age % 5)


# ALGOS
def risk_return_profile(request, acct_ignore=None):
    """
    BASIC RISK MODULE:
    Returns the calculated Sharpe Ratio of the
    user's portfolio, using the shortest term
    treasury bond rate as risk free rate of
    return, and average vestivise user sharpe for user's age group

    OUTPUT:
    {
        'riskLevel': <float>
        'averageUser' : <float>
        'ageRange': <string>
    }

    """
    if not acct_ignore:
        acct_ignore = []
    user = request.user
    profile = user.profile
    age = profile.get_age()
    if not acct_ignore:
        # Collect stored sharpe of user profile.
        sharpe = user.profile.quovo_user.userSharpes
        sharpe_ratio_exists = sharpe.exists()
        sp = sharpe.latest('createdAt').value if sharpe_ratio_exists else 0.0
    else:
        # Compute sharpe based on ignored accounts.
        tmp = profile.quovo_user.get_user_sharpe(acct_ignore=acct_ignore)
        if not tmp:
            sp = 0
        else:
            sp = tmp.value

    age_group = age_map(age)
    if age_group < 20:
        age_group = 20
    elif age_group > 80:
        age_group = 80
    average_user_sharpe = 0.7

    try:
        # Collect average user sharpe ratio for this agegroup.
        average_user_sharpe = AverageUserSharpe.objects.filter(ageGroup__exact=age_group).latest('createdAt').mean
    except AverageUserSharpe.DoesNotExist:
        try:
            # Collect average user sharpe ratio among all users.
            average_user_sharpe = AverageUserSharpe.objects.filter(ageGroup__exact=0).latest('createdAt').mean
        except:
            # It's okay we already set a default case of .7
            pass
    if average_user_sharpe == float("-inf") or average_user_sharpe == float("inf"):
        average_user_sharpe = 0.7

    # todo get risk return profile of benchmark
    # Benchmark.objects.annotate(abs_diff=Func(F('age_group') - age, function='ABS')).order_by('abs_diff').first()

    return Vestivise.network_response(
        {
            'riskLevel': round(sp, 2),
            'averageUser': round(average_user_sharpe, 2),
            'ageRange': "%s-%s" % (age_group-4, age_group)
        }
    )


def fees(request, acct_ignore=None):
    """
    BASIC COST MODULE:
    Returns the sum over the net expense ratios
    of the user's investment options.

    OUTPUT:
    A JSON containing only the aggregate net expense
    ratio.
    {
     'fee' : <float>,
     'averageFee': <float>,
     'averagePlacement': <string>
    }
    """

    if not acct_ignore:
        acct_ignore = []

    holds = request.user.profile.quovo_user.get_display_holdings(acct_ignore=acct_ignore)
    total_value = sum([hold.value for hold in holds])
    weights = [hold.value/total_value for hold in holds]
    # Take dot product of weight vector and expense ratios of holdings.
    expense_ratios = np.dot(weights, [hold.holding.expenseRatios.latest('createdAt').expense for hold in holds])
    try:
        auf = AverageUserFee.objects.latest('createdAt').avgFees
    except AverageUserFee.DoesNotExist:
        auf = .64

    average_placement = 'similar to'
    if expense_ratios < auf - .2:
        average_placement = 'less than'
    elif expense_ratios > auf + .2:
        average_placement = 'more than'

    return Vestivise.network_response({'fee': round(expense_ratios, 2),
                             "averageFee": round(auf, 2),
                             'averagePlacement': average_placement})


def returns(request, acct_ignore=None):
    """
    BASIC RETURNS MODULE:
    Returns a list of all the historic returns
    associated with a user's investment options.

    OUTPUT:
    A JSON containing a list of all the
    historic returns associated with that
    investment option, keys are the symbol of that
    option.
    {'returns': <list of len 3>,
     'benchmark': <list of len 3>,
     'benchmarkName': <string>
    }
    """

    if not acct_ignore:
        acct_ignore = []

    profile = request.user.profile
    quovo_user = profile.quovo_user
    user_returns_dict = {'yearToDate': 0.0, 'twoYearReturns': 0.0, 'oneYearReturns': 0.0}

    try:
        user_returns_dict = quovo_user.get_user_returns(acct_ignore=acct_ignore)
    except:
        pass

    display_returns = [
        user_returns_dict['yearToDate'],
        user_returns_dict['oneYearReturns'],
        user_returns_dict['twoYearReturns']
    ]
    display_returns_normalized = [round(display_return, 2) for display_return in display_returns]

    age = profile.get_age()

    bench = Benchmark.objects.annotate(abs_diff=Func(F('age_group') - age, function='ABS')).order_by('abs_diff').first()
    bench_mark_returns = bench.get_returns_wrapped()
    bench_mark_returns = [
        bench_mark_returns["year_to_date"],
        bench_mark_returns["one_year"],
        bench_mark_returns["two_year"]
    ]
    bench_mark_returns_normalized = [round(bench_mark_return, 2) for bench_mark_return in bench_mark_returns]
    return Vestivise.network_response({
        "returns": display_returns_normalized,
        "benchmark": bench_mark_returns_normalized,
        "benchmarkName": bench.name
    })



def holding_types(request, acct_ignore=None):
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
     'totalInvested': 100000,
     'holdingTypes' : 4
     }
    """

    if not acct_ignore:
        acct_ignore = []

    respond_dict = {'StockLong': 0.0, 'StockShort': 0.0,
                    'BondLong': 0.0, 'BondShort': 0.0,
                    'CashLong': 0.0, 'CashShort': 0.0,
                    'OtherLong': 0.0, 'OtherShort': 0.0}
    long_short_flip_dict = {'StockLong' : 'StockShort',
                            'StockShort': 'StockLong',
                            'BondLong': 'BondShort', 'BondShort': 'BondLong',
                            'CashLong': 'CashShort', 'CashShort': 'CashLong',
                            'OtherLong': 'OtherShort', 'OtherShort': 'OtherLong'}
    result = {
        'percentages': respond_dict,
        'totalInvested': round(0, 2),
        'holdingTypes': 0
    }
    holds = request.user.profile.quovo_user.get_display_holdings(acct_ignore=acct_ignore)

    if not holds:
        return Vestivise.network_response(result)

    total_value = sum([hold.value for hold in holds])
    # Compile a list of dictionaries, each of which associate the type of asset
    # with its corresponding percentage towards the overall portfolio.

    break_downs = []
    for hold in holds:
        for asset_breakdown in hold.holding.assetBreakdowns.filter(updateIndex__exact=hold.holding.currentUpdateIndex):
            break_downs.append({asset_breakdown.asset: asset_breakdown.percentage * hold.value/total_value})

    # Keep total_percent as a normalizing constant
    # Compile all the percentages across our breakdowns
    # into the resDict. If the percentage is negative
    # treat it as the opposite. A short becomes a long, etc.
    total_percent = 0
    for break_down in break_downs:
        for kind in respond_dict:
            if kind in break_down:
                if break_down[kind] >= 0.0:
                    respond_dict[kind] += break_down[kind]
                else:
                    respond_dict[long_short_flip_dict[kind]] += abs(break_down[kind])
                    total_percent += abs(break_down[kind])
    holding_types_count = 0
    kind_map = {
        "Stock" : False,
        "Bond": False,
        "Cash": False,
        "Other": False,
    }
    # Count the number of significant types.
    for kind in respond_dict:
        respond_dict[kind] = respond_dict[kind]/total_percent*100
        k = re.findall('[A-Z][^A-Z]*', kind)
        if respond_dict[kind] >= 0.5:
            if not kind_map.get(k[0]):
                kind_map[k[0]] = True
                holding_types_count += 1

    result["percentages"] = respond_dict
    result["totalInvested"] = round(total_value, 2)
    result["holdingTypes"] = holding_types_count

    return Vestivise.network_response(result)


def stockTypes(request, acctIgnore=None):
    """
    STOCK TYPES MODULE:
    Returns the percentage at which the user's
    equity portion of their portfolio is split among
    different stock categories.

    OUTPUT:
    A JSON mapping 'securities', to a dictionary
    of category strings to their corresponding percentages,.
    {'securities': <Dictionary>,
     'types' : 4
     }
    """
    holds = request.user.profile.quovoUser.getDisplayHoldings(acctIgnore=acctIgnore)
    totalVal = sum([x.value for x in holds])
    # Compile a list of dictionaries, each of which associate the category of the equity
    # with its corresponding percentage towards the overall portfolio.
    breakDowns = [dict([(x.category, x.percentage * h.value/totalVal)
                for x in h.holding.equityBreakdowns.filter(updateIndex__exact=h.holding.currentUpdateIndex)])
                for h in holds]
    resDict = {'Materials': 0.0, 'Consumer Cyclic': 0.0, 'Financial': 0.0,
               'Real Estate': 0.0, 'Healthcare': 0.0, 'Utilities': 0.0,
               'Communication': 0.0, 'Energy': 0.0, 'Industrials': 0.0,
               'Technology': 0.0, 'Consumer Defense': 0.0, 'Services': 0.0,
               'Other': 0.0}
    # Keep totPercent as a normalizing constant
    # Compile all the percentages across our breakdowns
    # into the resDict.
    totPercent = 0
    for breakDown in breakDowns:
        for kind in resDict:
            if kind in breakDown:
                k = " ".join(re.findall('[A-Z][^A-Z]*', kind))
                resDict[k] += breakDown[kind]
                totPercent += breakDown[kind]
    # Make a few things prettier.
    resDict['Consumer'] = resDict.pop('Consumer Cyclic') + resDict.pop('Consumer Defense')
    resDict['Health Care'] = resDict.pop('Healthcare')
    if totPercent == 0:
        result = {}
        result['securities'] = {"None" : 100}
        result["types"] = 0
        return network_response(result)

    types = 0
    for kind in resDict:
        p = resDict[kind]/totPercent*100
        resDict[kind] = p
        if p >= 0.5:
            types += 1
    result = {}
    result['securities'] = resDict
    result["types"] = types
    return network_response(result)


def bondTypes(request, acctIgnore=None):
    """
    BOND TYPES MODULE:
    Returns the percentage at which the user's
    bond portion of their portfolio is split among
    different bond categories.

    OUTPUT:
    A JSON mapping 'securities', to a dictionary
    of category strings to their corresponding percentages..
    {'securities': <Dictionary>,
     'types' : 4
     }
    """
    holds = request.user.profile.quovoUser.getDisplayHoldings(acctIgnore=acctIgnore)
    totalVal = sum([x.value for x in holds])
    # Compile a list of dictionaries, each of which associate the category of the bond
    # with its corresponding percentage towards the overall portfolio.
    breakDowns = [dict([(x.category, x.percentage * h.value/totalVal)
                  for x in h.holding.bondBreakdowns.filter(updateIndex__exact=h.holding.currentUpdateIndex)])
                  for h in holds]
    resDict = {"Government": 0.0, "Municipal": 0.0, "Corporate": 0.0,
               "Securitized": 0.0, "Cash": 0.0, "Derivatives": 0.0}
    # Keep totPercent as a normalizing constant
    # Compile all the percentages across our breakdowns
    # into the resDict.
    totPercent = 0
    for breakDown in breakDowns:
        for kind in resDict:
            if kind in breakDown:
                resDict[kind] += breakDown[kind]
                totPercent += breakDown[kind]

    if totPercent == 0:
        result = {}
        result['securities'] = {"None": 100}
        result["types"] = 0
        return network_response(result)

    types = 0

    for kind in resDict:
        p = resDict[kind] / totPercent * 100
        resDict[kind] = p
        if p >= 0.5:
            types += 1
    result = {}
    result['securities'] = resDict
    result["types"] = types
    return network_response(result)


def contributionWithdraws(request, acctIgnore=None):
    """
    CONTRIBUTION / WITHDRAWALS MODULE:
    Returns the amount of money the user has invested/taken out
    of their account over the past four years, and the net amounts.

    OUTPUT:
    A JSON following the format  of the payload variable below.
    """
    qUser = request.user.profile.quovoUser
    withdraws = qUser.get_withdraws(acctIgnore=acctIgnore)
    contributions = qUser.getContributions(acctIgnore=acctIgnore)

    today = datetime.today()
    year = today.year
    oneYear = year
    twoYear = year - 1
    threeYear = year - 2

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


def returnsComparison(request, acctIgnore=None):
    qu = request.user.profile.quovoUser
    try:
        returns = qu.getUserReturns(acctIgnore=acctIgnore)
    except Exception:
        returns = {'yearToDate': 0.0, 'twoYearReturns': 0.0, 'oneYearReturns': 0.0}

    dispReturns = [round(returns['yearToDate'], 2), round(returns['oneYearReturns'], 2), round(returns['twoYearReturns'], 2)]

    ageGroup = age_map(qu.userProfile.get_age())
    if ageGroup < 20: ageGroup = 20
    elif ageGroup > 80: ageGroup = 80
    try:
        avg = AverageUserReturns.objects.filter(ageGroup__exact=ageGroup).latest('createdAt')
    except AverageUserReturns.DoesNotExist:
        if AverageUserReturns.objects.exists():
            avg = AverageUserReturns.objects.filter(ageGroup__exact=0).latest('createdAt')
        else:
            avg = AverageUserReturns(yearToDate=0.0, oneYearReturns=0.0, twoYearReturns=0.0)
    avgUser = [round(avg.yearToDate, 2), round(avg.oneYearReturns, 2), round(avg.twoYearReturns, 2)]

    return network_response({
        "returns": dispReturns,
        "avgUser": avgUser,
        "ageGroup": str(ageGroup-4)+"-"+str(ageGroup)
    })


def riskAgeProfile(request, acctIgnore=None):
    profile = request.user.profile
    age = profile.get_age()
    birthyear = profile.birthday.year
    qu = profile.quovoUser
    if acctIgnore:
        userBondEq = qu.getUserBondEquity(acctIgnore=acctIgnore)
    else:
        userBondEq = qu.userBondEquity.latest('createdAt') if qu.userBondEquity.exists() else None

    bench = Benchmark.objects.annotate(abs_diff=Func(F('age_group') - age, function='ABS')).order_by('abs_diff').first()
    bench_bond_stock = bench.get_stock_bond_split()
    bench_stock_perc = bench_bond_stock.get("stock")
    bench_bond_perc = bench_bond_stock.get("bond")

    avgStock = 0
    avgBond = 0
    if AverageUserBondEquity.objects.exists():
        avgProf = AverageUserBondEquity.objects.latest('createdAt')
        avgStock = avgProf.equity
        avgBond = avgProf.bond

    stock_total = 0 if not userBondEq else userBondEq.equity
    bond_total = 0 if not userBondEq else userBondEq.bond

    a = age_map(age)

    return network_response({
        "stock": int(round(stock_total)),
        "bond": int(round(bond_total)),
        "benchStock" : bench_stock_perc * 100,
        "benchBond" : bench_bond_perc * 100,
        "avgStock" : int(round(avgStock)),
        "avgBond" : int(round(avgBond)),
        "ageRange" : "%s-%s" % (a-4, a)
    })


def _compoundRets(B, r, n, k, cont):
    if np.isclose(r, 0):
        return B+cont*k
    result = max(B*(1+r/n)**(n*k) + cont/n*((1+r/n)**(n*k)-1)/(r/n)*(1+r/n), cont/n, 0)
    if math.isnan(result):
        return 0
    return result


def compInterest(request, acctIgnore=None):

    result = {
        "currentValue": 0,
        "yearsToRetirement": 0,
        "currentFees": 0,
        "averageAnnualReturns": 0,
        "futureValues": 0,
        "futureValuesMinusFees": 0,
        "netRealFutureValue": 0
    }
    quovo_user = request.user.profile.quovoUser
    holds = quovo_user.getDisplayHoldings(acctIgnore=acctIgnore)
    dispVal = sum([x.value for x in quovo_user.userCurrentHoldings.exclude(account__quovoID__in=acctIgnore)])

    if not holds: return network_response(result)
    valReach = 10

    weights = [x.value / dispVal for x in holds]
    feeList = []
    for h in holds:
        try:
            feeList.append(h.holding.expenseRatios.latest('createdAt').expense)
        except HoldingExpenseRatio.DoesNotExist:
            feeList.append(0.0)
    currFees = np.dot(weights, feeList)

    cont_with = json.loads(contributionWithdraws(request, acctIgnore=acctIgnore).content)
    avgCont = cont_with['data']['total']['net']/3.0

    avgAnnRets = np.dot(weights, [x.holding.returns.latest('createdAt').oneYearReturns for x in holds])
    futureValues = [round(_compoundRets(dispVal, avgAnnRets/100, 12, k, avgCont), 2) for k in range(0, valReach+1)]
    futureValuesMinusFees = [round(_compoundRets(dispVal, (avgAnnRets-currFees)/100, 12, k, avgCont), 2) for k in range(0, valReach+1)]
    netRealFutureValue = [round(_compoundRets(dispVal, (avgAnnRets-currFees-2)/100, 12, k, avgCont), 2) for k in range(0, valReach+1)]

    result["currentValue"] = dispVal
    result["yearsToRetirement"] = 10
    result["currentFees"] = currFees
    result["averageAnnualReturns"] = avgAnnRets
    result["futureValues"] = futureValues
    result["futureValuesMinusFees"] = futureValuesMinusFees
    result["netRealFutureValue"] = netRealFutureValue

    return network_response(result)


def portfolioHoldings(request, acctIgnore=None):
    result = {
        "holdings" : {}
    }
    qu = request.user.profile.quovoUser
    user_display_holdings = qu.userDisplayHoldings.exclude(holding__category__exact="IGNO").exclude(account__quovoID__in=acctIgnore)
    current_holdings = qu.getCurrentHoldings(acctIgnore=acctIgnore, exclude_holdings=[x.holding.id for x in user_display_holdings],
                                             showIgnore=True)
    total = sum(i.value for i in user_display_holdings) + sum(i.value for i in current_holdings)
    for user_display_holding in user_display_holdings:
        returns = user_display_holding.holding.returns.latest("createdAt")
        result["holdings"]["%s ( %s )" % (user_display_holding.holding.secname, user_display_holding.account.brokerage_name)] = {
            "isLink" : True,
            "value" : round(user_display_holding.value, 2),
            "portfolioPercent" : round(user_display_holding.value/total,2),
            "returns": round(returns.yearToDate, 2),
            "pastReturns" : round(returns.oneYearReturns, 2),
            "expenseRatio": round(user_display_holding.holding.expenseRatios.latest("createdAt").expense, 2),
        }

    for current_holding in current_holdings:
        result["holdings"][current_holding.holding.secname] = {
            "isLink" : False,
            "value" : round(current_holding.value, 2),
            "portfolioPercent" : round(current_holding.value/total, 2),
            "returns": None,
            "pastReturns": None,
            "expenseRatio": None,
        }

    return network_response(result)
