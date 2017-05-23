import re
import math
import json

from django.db.models import Func, F
from django.utils.datetime_safe import datetime
import numpy as np
from data.models import (AverageUserReturns, AverageUserBondEquity, HoldingExpenseRatio, AverageUserSharpe,
                         AverageUserFee, Benchmark)
from Vestivise import Vestivise


# UTILITY FUNCTIONS
def age_map(age):
    return age + (0 if age % 5 == 0 else 5 - age % 5)


def create_break_down_equity(total_value, holdings):
    # Compile a list of dictionaries, each of which associate the type of asset
    # with its corresponding percentage towards the overall portfolio.
    return [
        dict([
            (breakdowns.category, breakdowns.percentage * holding.value/total_value)
            for breakdowns in
            holding.holding.equity_breakdown.filter(update_index__exact=holding.holding.current_update_index)
        ])
        for holding in holdings
    ]


def create_break_down_bond(total_value, holdings):
    # Compile a list of dictionaries, each of which associate the type of asset
    # with its corresponding percentage towards the overall portfolio.
    return [
        dict([
            (breakdowns.category, breakdowns.percentage * holding.value/total_value)
            for breakdowns in
            holding.holding.bond_breakdown.filter(update_index__exact=holding.holding.current_update_index)
        ])
        for holding in holdings
    ]


def create_break_down_assets(total_value, holdings):
    return [
        dict([
            (breakdowns.asset, breakdowns.percentage * holding.value/total_value)
            for breakdowns in
            holding.holding.asset_breakdown.filter(update_index__exact=holding.holding.current_update_index)
        ])
        for holding in holdings
    ]


def get_compound_returns(B, r, n, k, cont):
    if np.isclose(r, 0):
        return B+cont*k
    result = max(B*(1+r/n)**(n*k) + cont/n*((1+r/n)**(n*k)-1)/(r/n)*(1+r/n), cont/n, 0)
    if math.isnan(result):
        return 0
    return result


def insert_payload(transaction, payload, category, one_year, two_year, three_year):
    date = transaction.date.year
    if date == one_year:
        place = "oneYear"
    elif date == two_year:
        place = "twoYear"
    elif date == three_year:
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
        sharpe = user.profile.quovo_user.user_sharpes
        sharpe_ratio_exists = sharpe.exists()
        sp = sharpe.latest('created_at').value if sharpe_ratio_exists else 0.0
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
        average_user_sharpe = AverageUserSharpe.objects.filter(age_group__exact=age_group).latest('created_at').mean
    except AverageUserSharpe.DoesNotExist:
        try:
            # Collect average user sharpe ratio among all users.
            average_user_sharpe = AverageUserSharpe.objects.filter(age_group__exact=0).latest('created_at').mean
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
    expense_ratios = np.dot(weights, [hold.holding.expense_ratios.latest('created_at').expense for hold in holds])
    try:
        auf = AverageUserFee.objects.latest('created_at').average_fees
    except AverageUserFee.DoesNotExist:
        auf = .64

    average_placement = 'similar to'
    if expense_ratios < auf - .2:
        average_placement = 'less than'
    elif expense_ratios > auf + .2:
        average_placement = 'more than'

    return Vestivise.network_response({
                            'fee': round(expense_ratios, 2),
                            'averageFee': round(auf, 2),
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
        user_returns_dict['year_to_date'],
        user_returns_dict['one_year_return'],
        user_returns_dict['two_year_return']
    ]
    display_returns_normalized = [round(display_return, 2) for display_return in display_returns]

    age = profile.get_age()

    bench = Benchmark.objects.annotate(abs_diff=Func(F('age_group') - age, function='ABS')).order_by('abs_diff').first()
    bench_mark_returns = bench.get_returns_wrapped()
    bench_mark_returns = [
        bench_mark_returns["year_to_date"],
        bench_mark_returns["one_year_return"],
        bench_mark_returns["two_year_return"]
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
    break_downs = create_break_down_assets(total_value, holds)

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


def stock_types(request, acct_ignore=None):
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

    if not acct_ignore:
        acct_ignore = []

    holds = request.user.profile.quovo_user.get_display_holdings(acct_ignore=acct_ignore)
    total_value = sum([hold.value for hold in holds])
    # Compile a list of dictionaries, each of which associate the category of the equity
    # with its corresponding percentage towards the overall portfolio.
    break_downs = create_break_down_equity(total_value, holds)
    respond_dict = {'Materials': 0.0, 'Consumer Cyclic': 0.0, 'Financial': 0.0,
                    'Real Estate': 0.0, 'Healthcare': 0.0, 'Utilities': 0.0,
                    'Communication': 0.0, 'Energy': 0.0, 'Industrials': 0.0,
                    'Technology': 0.0, 'Consumer Defense': 0.0, 'Services': 0.0,
                    'Other': 0.0}
    # Keep totPercent as a normalizing constant
    # Compile all the percentages across our breakdowns
    # into the resDict.
    total_percent = 0
    for break_down in break_downs:
        for kind in respond_dict:
            if kind in break_down:
                k = " ".join(re.findall('[A-Z][^A-Z]*', kind))
                respond_dict[k] += break_down[kind]
                total_percent += break_down[kind]
    # Make a few things prettier.
    respond_dict['Consumer'] = respond_dict.pop('Consumer Cyclic') + respond_dict.pop('Consumer Defense')
    respond_dict['Health Care'] = respond_dict.pop('Healthcare')
    if total_percent == 0:
        result = {
            'securities': {"None": 100},
            'types': 0
        }
        return Vestivise.network_response(result)

    types = 0
    for kind in respond_dict:
        p = respond_dict[kind]/total_percent*100
        respond_dict[kind] = p
        if p >= 0.5:
            types += 1
    result = {
        'securities': respond_dict,
        'types': types
    }
    return Vestivise.network_response(result)


def bond_types(request, acct_ignore=None):
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

    if not acct_ignore:
        acct_ignore = []

    holds = request.user.profile.quovo_user.get_display_holdings(acct_ignore=acct_ignore)
    total_value = sum([hold.value for hold in holds])
    # Compile a list of dictionaries, each of which associate the category of the bond
    # with its corresponding percentage towards the overall portfolio.
    break_downs = create_break_down_bond(total_value, holds)
    respond_dict = {"Government": 0.0, "Municipal": 0.0, "Corporate": 0.0,
                    "Securitized": 0.0, "Cash": 0.0, "Derivatives": 0.0}
    # Keep totPercent as a normalizing constant
    # Compile all the percentages across our breakdowns
    # into the resDict.
    total_percent = 0
    for break_down in break_downs:
        for kind in respond_dict:
            if kind in break_down:
                respond_dict[kind] += break_down[kind]
                total_percent += break_down[kind]

    if total_percent == 0:
        result = {
            'securities': {"None": 100},
            'types': 0
        }
        return Vestivise.network_response(result)

    types = 0

    for kind in respond_dict:
        p = respond_dict[kind] / total_percent * 100
        respond_dict[kind] = p
        if p >= 0.5:
            types += 1
    result = {
        'securities': respond_dict,
        'types': types
    }
    return Vestivise.network_response(result)


def contribution_withdraws(request, acct_ignore=None):
    """
    CONTRIBUTION / WITHDRAWALS MODULE:
    Returns the amount of money the user has invested/taken out
    of their account over the past four years, and the net amounts.

    OUTPUT:
    A JSON following the format  of the payload variable below.
    """

    if not acct_ignore:
        acct_ignore = []

    quovo_user = request.user.profile.quovo_user
    withdraws = quovo_user.get_withdraws(acct_ignore=acct_ignore)
    contributions = quovo_user.get_contributions(acct_ignore=acct_ignore)

    today = datetime.today()
    year = today.year
    one_year = year
    two_year = year - 1
    three_year = year - 2

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

    for transaction in contributions:
        insert_payload(transaction, payload, "contributions", one_year, two_year, three_year)

    for transaction in withdraws:
        insert_payload(transaction, payload, "withdraw", one_year, two_year, three_year)

    return Vestivise.network_response(payload)


def returns_comparison(request, acct_ignore=None):

    if not acct_ignore:
        acct_ignore = []

    quovo_user = request.user.profile.quovo_user

    age_group = age_map(quovo_user.user_profile.get_age())
    if age_group < 20:
        age_group = 20
    elif age_group > 80:
        age_group = 80

    try:
        avg = AverageUserReturns.objects.filter(age_group__exact=age_group).latest('created_at')
    except AverageUserReturns.DoesNotExist:
        if AverageUserReturns.objects.exists():
            avg = AverageUserReturns.objects.filter(age_group__exact=0).latest('created_at')
        else:
            avg = AverageUserReturns(year_to_date=0.0, one_year_returns=0.0, twoYearReturns=0.0)

    avg_user_returns = [
        round(avg.year_to_date, 2),
        round(avg.one_year_return, 2),
        round(avg.two_year_return, 2)
    ]

    date_returns = {'year_to_date': 0.0, 'two_year_return': 0.0, 'one_year_return': 0.0}

    try:
        date_returns = quovo_user.get_user_returns(acct_ignore=acct_ignore)
    except:
        pass

    display_returns = [
        round(date_returns['year_to_date'], 2),
        round(date_returns['one_year_return'], 2),
        round(date_returns['two_year_return'], 2)
    ]

    return Vestivise.network_response({
        "returns": display_returns,
        "avgUser": avg_user_returns,
        "ageGroup": "{}-{}".format(str(age_group-4), str(age_group))
    })


def risk_age_profile(request, acct_ignore=None):
    profile = request.user.profile
    age = profile.get_age()
    quovo_user = profile.quovo_user

    user_bond_equity = None
    if acct_ignore:
        user_bond_equity = quovo_user.get_user_bond_equity(acct_ignore=acct_ignore)
    else:
        latest_bond_equity = quovo_user.user_bond_equity.latest('created_at')
        user_bond_equity = latest_bond_equity if quovo_user.user_bond_equity.exists() else None

    stock_total = 0 if not user_bond_equity else user_bond_equity.equity
    bond_total = 0 if not user_bond_equity else user_bond_equity.bond

    bench = Benchmark.objects.annotate(abs_diff=Func(F('age_group') - age, function='ABS')).order_by('abs_diff').first()
    bench_bond_stock = bench.get_stock_bond_split()
    bench_stock_percent = bench_bond_stock.get("stock")
    bench_bond_percent = bench_bond_stock.get("bond")

    average_stock = 0
    average_bond = 0
    if AverageUserBondEquity.objects.exists():
        average_user_bond_equity = AverageUserBondEquity.objects.latest('created_at')
        average_stock = average_user_bond_equity.equity
        average_bond = average_user_bond_equity.bond

    age_group = age_map(profile.get_age())
    if age_group < 20:
        age_group = 20
    elif age_group > 80:
        age_group = 80

    return Vestivise.network_response({
        "stock": int(round(stock_total)),
        "bond": int(round(bond_total)),
        "benchStock": bench_stock_percent * 100,
        "benchBond": bench_bond_percent * 100,
        "avgStock": int(round(average_stock)),
        "avgBond": int(round(average_bond)),
        "ageRange": "{}-{}".format(str(age_group-4), str(age_group))
    })


def compound_interest(request, acct_ignore=None):

    if not acct_ignore:
        acct_ignore = []

    result = {
        "currentValue": 0,
        "yearsToRetirement": 0,
        "currentFees": 0,
        "averageAnnualReturns": 0,
        "futureValues": 0,
        "futureValuesMinusFees": 0,
        "netRealFutureValue": 0
    }
    quovo_user = request.user.profile.quovo_user
    holds = quovo_user.get_display_holdings(acct_ignore=acct_ignore)
    display_value = 0

    for holding in quovo_user.user_current_holdings.exclude(account__quovo_id__in=acct_ignore):
        display_value += holding.value

    if not holds:
        return Vestivise.network_response(result)

    weights = [hold.value / display_value for hold in holds]
    fee_list = []
    for hold in holds:
        try:
            fee_list.append(hold.holding.expense_ratios.latest('created_at').expense)
        except HoldingExpenseRatio.DoesNotExist:
            fee_list.append(0.0)

    current_fees = np.dot(weights, fee_list)

    contributions_withdraws = json.loads(contribution_withdraws(request, acct_ignore=acct_ignore).content)
    average_contributions = contributions_withdraws['data']['total']['net']/3.0

    latest_one_year_return = [hold.holding.returns.latest('created_at').one_year_return for hold in holds]
    average_annual_returns = np.dot(weights, latest_one_year_return)

    value_target = 10
    future_values = [
        round(get_compound_returns(display_value, average_annual_returns/100, 12, k, average_contributions), 2)
        for k in range(0, value_target+1)
    ]

    minus_fee_return_rate = (average_annual_returns-current_fees)/100
    future_values_minus_fees = [
        round(get_compound_returns(display_value, minus_fee_return_rate, 12, k, average_contributions), 2)
        for k in range(0, value_target+1)
    ]

    minus_fee_inflation_return_rate = (average_annual_returns-current_fees-2)/100
    net_real_future_value = [
        round(get_compound_returns(display_value, minus_fee_inflation_return_rate, 12, k, average_contributions), 2)
        for k in range(0, value_target+1)
    ]

    result["currentValue"] = display_value
    result["yearsToRetirement"] = 10
    result["currentFees"] = current_fees
    result["averageAnnualReturns"] = average_annual_returns
    result["futureValues"] = future_values
    result["futureValuesMinusFees"] = future_values_minus_fees
    result["netRealFutureValue"] = net_real_future_value

    return Vestivise.network_response(result)


def portfolio_holdings(request, acct_ignore=None):

    if not acct_ignore:
        acct_ignore = []

    result = {
        "holdings": {}
    }
    quovo_user = request.user.profile.quovo_user
    user_display_holdings = quovo_user.user_display_holdings.exclude(holding__category__exact="IGNO")\
                                      .exclude(account__quovo_id__in=acct_ignore)

    exclude_holdings = [user_display_holding.holding.id for user_display_holding in user_display_holdings]
    current_holdings = quovo_user.get_current_holdings(acct_ignore=acct_ignore,
                                                       exclude_holdings=exclude_holdings,
                                                       show_ignore=True)
    display_holding_total = sum(user_display_holding.value for user_display_holding in user_display_holdings)
    current_holding_total = sum(current_holding.value for current_holding in current_holdings)
    total = display_holding_total + current_holding_total
    for user_display_holding in user_display_holdings:
        holding = user_display_holding.holding
        display_holding_returns = holding.returns.latest("created_at")
        display_name = "{} ({})".format(holding.secname, user_display_holding.account.brokerage_name)
        result["holdings"][display_name] = {
            "isLink": True,
            "value": round(user_display_holding.value, 2),
            "portfolioPercent": round(user_display_holding.value/total, 2),
            "returns": round(display_holding_returns.year_to_date, 2),
            "pastReturns" : round(display_holding_returns.one_year_return, 2),
            "expenseRatio": round(user_display_holding.holding.expense_ratios.latest("created_at").expense, 2),
        }

    for current_holding in current_holdings:
        result["holdings"][current_holding.holding.secname] = {
            "isLink": False,
            "value": round(current_holding.value, 2),
            "portfolioPercent": round(current_holding.value/total, 2),
            "returns": None,
            "pastReturns": None,
            "expenseRatio": None,
        }

    return Vestivise.network_response(result)
