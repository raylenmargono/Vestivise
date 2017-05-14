import logging
import random

import numpy as np
import requests
from dateutil.parser import parse
from math import floor
import xml.etree.cElementTree as ET

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.utils.datetime_safe import datetime
from django.utils import timezone

from Vestivise.Vestivise import NightlyProcessException, VestiviseException
from dashboard.models import QuovoUser, ProgressTracker
from data.models import (AverageUserFee, AverageUserReturns, AverageUserSharpe, AverageUserBondEquity,
                         TreasuryBondValue, HoldingExpenseRatio, Holding, Account)
from sources.morningstar import MorningstarRequestError
from sources import mailchimp

"""
This file includes all functions to be run in overnight processes
for the sake of updating the database for day to day operations.
"""
logger = logging.getLogger("nightly_process")


def update_quovo_user_accounts():
    logger.info("Beginning updateQuovoUserAccounts at {}".format(str(datetime.now().time())))
    for quovo_user in QuovoUser.objects.all():
        name = quovo_user.user_profile.user.email
        logger.info("Beginning to update account for {}".format(name))
        try:
            quovo_user.update_accounts()
        except NightlyProcessException as e:
            e.log_error()


def update_quovo_user_portfolios():
    logger.info("Beginning updateQuovoUserPortfolios at {}".format(str(datetime.now().time())))
    for quovo_user in QuovoUser.objects.all():
        name = quovo_user.user_profile.user.email
        logger.info("Beginning to update portfolio for {0}".format(name))
        try:
            quovo_user.update_portfolios()
        except NightlyProcessException as e:
            e.log_error()


def update_quovo_user_holdings():
    """
    Updates every QuovoUser's holdings. Should they have
    new Holdings, updates their CurrentHoldings, and
    replaces their DisplayHoldings with their CurrentHoldings
    should all CurrentHoldings be identified.
    """
    logger.info("Beginning updateQuovoUserHoldings at {}".format(str(datetime.now().time())))
    for quovo_user in QuovoUser.objects.all():
        name = quovo_user.user_profile.user.email
        logger.info("Beginning to update holdings for {}".format(name))
        logger.info("Getting new holdings for {}".format(name))
        new_holds = quovo_user.get_new_holdings()
        current_holding_not_equal = quovo_user.current_holdings_equal_holding_json(new_holds)
        if new_holds and not current_holding_not_equal:
            logger.info("{} has new holdings, changing their current holdings".format(name))
            quovo_user.set_current_holdings(new_holds)
        if not quovo_user.has_completed_user_holdings():
            logger.info("{} has incomplete holdings, will have to update".format(name))
            quovo_user.is_completed = False
        else:
            _update_quovo_user_display_holdings(quovo_user)
            quovo_user.save()


def update_holding_information():
    """
    This method iterates through all Holding objects
    in the database and updates their pricing, breakdown, expense,
    and other information related to the Holding.
    """
    # TODO ENSURE CASE WHERE UPDATE NUMBER HAS BEEN INCREMENTED.
    for holding in Holding.objects.exclude(category__in=["FOFF", "IGNO", "CASH"]):
        if holding.is_identified():
            update_holding(holding)

    logger_str = "Beginning to update {} for {} position pk: {}, secname: {}"
    for holding in Holding.objects.filter(category__exact="CASH"):
        logging.info(logger_str.format("returns", "cash", holding.pk, holding.secname))
        holding.update_returns()
        logging.info(logger_str.format("expense ratio", "cash", holding.pk, holding.secname))
        holding.update_expenses()
        logging.info(logger_str.format("breakdowns", "cash", holding.pk, holding.secname))
        holding.update_all_breakdowns()
    for holding in Holding.objects.filter(category__exact="FOFF"):
        logging.info(logger_str.format("returns", "foff", holding.pk, holding.secname))
        holding.update_returns()
        logging.info(logger_str.format("expenses", "foff", holding.pk, holding.secname))
        holding.update_expenses()

    fill_treasury_bond_values()
    logging.info("Finished collecting treasuray bond values")


def update_holding(holding):
    try:
        logger.info("Beginning to fill past prices for pk: {}, identifier: {}".format(holding.pk, holding.secname))
        holding.fill_prices()

        logger.info("Now updating all returns for pk: {}, identifier: {}".format(holding.pk, holding.secname))
        holding.update_returns()

        logger.info("Beginning to update expenses for pk: {}, identifier: {}".format(holding.pk, holding.secname))
        holding.update_expenses()

        logger.info("Now updating all breakdowns for pk: {}, identifier: {}".format(holding.pk, holding.secname))
        holding.update_all_breakdowns()

        logger.info("Now updating distributions for pk: {}, identifier: {}".format(holding.pk, holding.secname))
        holding.update_dividends()

        holding.updatedAt = timezone.now()
        holding.save()
    except MorningstarRequestError as err:
        is_invalid = False
        try:
            is_invalid = err.args[1].get('status', "").get('message', "").split(' ')[0] == "Invalid"
        except:
            pass
        if is_invalid:
            logger_str = "Holding {} has been given invalid identifer: {} wiping information"
            logger.error(logger_str.format(holding.secname, str(holding.get_identifier())))
            identifier = holding.get_identifier()[1]
            if identifier == "mstarid":
                holding.morning_star_id = ""
            elif identifier == "ticker":
                holding.ticker = ""
            elif identifier == "cusip":
                holding.cusip = ""
            holding.save()
            mailchimp.alert_mislabeled_holding(holding.secname)
        else:
            if hasattr(err, "args") and len(err.args) > 1:
                a = err.args[1]
                status = a.get('status')
                if status and not status.get('messsage') == "OK":
                    error_str = "Error retrieving information for holding pk: {}. Received response \n {}"
                    logger.error(error_str.format(str(holding.pk), str(a)))
            else:
                #TODO MAKE THIS A MORE DESCRIPTIVE MESSAGE
                logger.error("Error retrieving information for holding pk: " + str(holding.pk) + ".")


def update_quovo_user_completeness():
    """
    This method iterates through all incomplete QuovoUsers,
    check if their holdings are now complete, and if they are,
    updates their display holdings, and marks them as complete.
    :return:
    """
    # Get all incomplete QuovoUsers
    for quovo_user in QuovoUser.objects.filter(is_completed__exact=False):
        _update_quovo_user_display_holdings(quovo_user)
        if quovo_user.has_completed_user_holdings():
            mailchimp.send_holding_processing_complete_notification(quovo_user.user_profile.user.email)


def _update_quovo_user_display_holdings(quovo_user):
    quovo_user.update_display_holdings()
    track_data = True
    if quovo_user.hasCompletedUserHoldings():
        quovo_user.isCompeted = True
        quovo_user.save()
    else:
        track_data = False
    user = get_user_model().objects.get(profile__quovo_user=quovo_user)
    ProgressTracker.track_progress(user, {
        "track_id": "complete_identification",
        "track_data": track_data
    })


def update_user_returns():
    """
    This method iterates through all completed QuovoUsers
    and computes their returns for use in their returns module.
    """
    for acct in Account.objects.filter(active=True):
        acct.get_account_returns()
    for quovo_user in QuovoUser.objects.all():
        if quovo_user.get_display_holdings():
            logger.info("Determining returns and sharpe for user: {0}".format(quovo_user.user_profile.user.email))
            quovo_user.get_user_returns()
            quovo_user.get_user_sharpe()
            quovo_user.get_user_bond_equity()
    logger.info("Determining average returns, sharpe, fees")
    get_average_returns()
    get_average_sharpe()
    get_average_bond_equity()
    get_average_fees()


def update_user_history():
    for quovo_user in QuovoUser.objects.all():
        name = quovo_user.user_profile.user.email
        logger.info("Beginning to update transactions for {0}".format(name))
        try:
            quovo_user.update_transactions()
        except VestiviseException as e:
            e.log_error()


def update_user_fees():
    for quovo_user in QuovoUser.objects.all():
        quovo_user.update_fees()


# ACCESSORY / UTILITY METHODS

def get_average_returns():
    today = datetime.now().date()

    total_size = 0
    total_year_to_date = 0
    total_one_year_res = 0
    total_two_year_res = 0
    total_three_year_res = 0
    total_one_month_res = 0
    total_three_month_res = 0

    for age in [5*x for x in range(4, 17)]:
        group = QuovoUser.objects.filter(is_completed__exact=True,
                                         user_profile__birthday__lte=today.replace(year=today.year-age+5),
                                         user_profile__birthday__gte=today.replace(year=today.year - age - 4))
        size = group.count()
        indices = range(size)
        if size > 100:
            num_check = max(100, int(floor(.2*size)))
            indices = random.sample(range(size), num_check)

        if size == 0:
            continue

        total_size += len(indices)
        year_to_date = 0
        one_year_res = 0
        two_year_res = 0
        three_year_res = 0
        one_month_res = 0
        three_month_res = 0

        for indice in indices:
            person = group[indice].get_user_returns()
            year_to_date += person['yearToDate']
            one_year_res += person['oneYearReturns']
            two_year_res += person['twoYearReturns']
            three_year_res += person['threeYearReturns']
            one_month_res += person['oneMonthReturns']
            three_month_res += person['threeMonthReturns']

        total_year_to_date += year_to_date
        total_one_year_res += one_year_res
        total_two_year_res += two_year_res
        total_three_year_res += three_year_res
        total_one_month_res += one_month_res
        total_three_month_res += three_month_res

        AverageUserReturns.objects.create(
            year_to_date=year_to_date/len(indices),
            one_year_return=one_year_res/len(indices),
            two_year_return=two_year_res/len(indices),
            three_year_return=three_year_res/len(indices),
            one_month_return=one_month_res/len(indices),
            three_month_return=three_month_res/len(indices),
            age_group=age
        )

    if total_size == 0:
        return

    AverageUserReturns.objects.create(
        year_to_date=total_year_to_date / total_size,
        one_year_return=total_one_year_res / total_size,
        two_year_return=total_two_year_res / total_size,
        three_year_return=total_three_year_res / total_size,
        one_month_return=total_one_month_res / total_size,
        three_month_return=total_three_month_res / total_size,
        age_group=0
    )


def get_average_fees():
    fee_sum = 0.0
    total_users = QuovoUser.objects.all()
    i = 0
    for quovo_user in total_users:

        #similar to alex's code
        holds = quovo_user.get_display_holdings()
        current_value = sum([x.value for x in holds])

        weights = [hold.value / current_value for hold in holds]
        fee_list = []
        for hold in holds:
            try:
                fee_list.append(hold.holding.expense_ratios.latest('created_at').expense)
            except HoldingExpenseRatio.DoesNotExist:
                fee_list.append(0.0)
        current_fees = np.dot(weights, fee_list)
        if len(fee_list) != 0:
            i += 1

        fee_sum += current_fees

    average_fee = 0
    if i > 0:
        average_fee = fee_sum/i

    AverageUserFee.objects.create(average_fees=average_fee)


def get_average_sharpe():
    today = datetime.now().date()

    total_values = []

    quovo_users = QuovoUser.objects.filter(is_completed__exact=True)

    for age in [5*x for x in range(4, 17)]:
        group = quovo_users.filter(user_profile__birthday__lte=today.replace(year=today.year-age+5),
                                   user_profile__birthday__gte=today.replace(year=today.year - age - 4))
        size = group.count()
        indices = range(size)
        if size > 100:
            num_check = max(100, int(floor(.2*size)))
            indices = random.sample(range(size), num_check)
        elif size < 2:
            continue
        values = []
        for i in indices:
            val = group[i].user_sharpes.latest('created_at').value
            values.append(val)
            total_values.append(val)
        mu = np.mean(values)
        sigma = np.std(values)
        AverageUserSharpe.objects.create(
            mean=mu,
            std=sigma,
            ageGroup=age
        )

    total_mu = 0
    total_sigma = 0

    if quovo_users.count() > 2:
        total_mu = np.mean(total_values)
        total_sigma = np.std(total_values)

    AverageUserSharpe.objects.create(
        mean=total_mu,
        std=total_sigma,
        age_group=0
    )


def get_average_bond_equity():
    today = datetime.now().date()

    quovo_users = QuovoUser.objects.filter(is_completed__exact=True)

    total_bond = 0
    total_equity = 0
    total_size = 0

    for age in [5*x for x in range(4, 17)]:
        group = quovo_users.filter(user_profile__birthday__lte=today.replace(year=today.year-age+5),
                                   user_profile__birthday__gte=today.replace(year=today.year-age-4))
        size = group.count()
        indices = range(size)
        if size > 100:
            num_check = max(100, int(floor(.2*size)))
            indices = random.sample(range(size), num_check)
        elif size < 2:
            continue

        bond = 0
        equity = 0
        for i in indices:
            person = group[i].userBondEquity.latest('createdAt')
            bond += person.bond
            equity += person.equity

        total_size += size
        total_bond += bond
        total_equity += equity

        AverageUserBondEquity.objects.create(
            age_group=age,
            bond=bond/len(indices),
            equity=equity/len(indices)
        )

    if quovo_users.count() != 0:
        AverageUserBondEquity.objects.create(
            total_bond=bond / total_size,
            total_equity=equity / total_size,
            age_group=0
        )


def fill_treasury_bond_values():
    base = "http://data.treasury.gov/feed.svc/DailyTreasuryBillRateData?$filter=month(INDEX_DATE)%20eq%20{0}" \
           "%20and%20year(INDEX_DATE)%20eq%20{1}"
    end = (datetime.now() - relativedelta(months=1)).replace(day=1).date()
    try:
        start = TreasuryBondValue.objects.latest('date').date
    except TreasuryBondValue.DoesNotExist:
        start = (end - relativedelta(years=3))
    if start < end - relativedelta(years=3):
        start = end - relativedelta(years=3)
    while start <= end:
        data = requests.get(base.format(start.month, start.year))

        tree = ET.fromstring(data.text)
        monthly_returns = None
        for entry in tree.findall("{http://www.w3.org/2005/Atom}entry"):
            for content in entry.findall("{http://www.w3.org/2005/Atom}content"):
                monthly_returns = (content[0][1].text, content[0][2].text)

        if monthly_returns is None:
            raise NightlyProcessException("Could not find returns for {}/{}".format(start.year, start.month))

        TreasuryBondValue.objects.create(
            date=parse(monthly_returns[0]).date(),
            value=float(monthly_returns[1])
        )

        start += relativedelta(months=1)
