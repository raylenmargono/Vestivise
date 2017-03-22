from django.contrib.auth import get_user_model

from dashboard.models import *
from Vestivise.mailchimp import *
from django.utils.datetime_safe import datetime
from django.utils import timezone
from Vestivise.morningstar import MorningstarRequestError
from Vestivise.Vestivise import NightlyProcessException, VestiviseException
import logging
import random
import requests
import xml.etree.cElementTree as ET
from dateutil.parser import parse
from math import floor
from data.models import AverageUserFee,AverageUserReturns, AverageUserSharpe, AverageUserBondEquity, TreasuryBondValue, HoldingExpenseRatio

"""
This file includes all functions to be run in overnight processes
for the sake of updating the database for day to day operations.
"""
logger = logging.getLogger("nightly_process")

def updateQuovoUserAccounts():
    logger.info("Beginning updateQuovoUserAccounts at %s" % (str(datetime.now().time()),))
    for qUser in QuovoUser.objects.all():
        name = qUser.userProfile.user.email
        logger.info("Beginning to update account for {0}".format(name))
        try:
            qUser.updateAccounts()
        except NightlyProcessException as e:
            e.log_error()


def updateQuovoUserPortfolios():
    logger.info("Beginning updateQuovoUserPortfolios at %s" % (str(datetime.now().time()),))
    for qUser in QuovoUser.objects.all():
        name = qUser.userProfile.user.email
        logger.info("Beginning to update portfolio for {0}".format(name))
        try:
            qUser.updatePortfolios()
        except NightlyProcessException as e:
            e.log_error()

def updateQuovoUserHoldings():
    """
    Updates every QuovoUser's holdings. Should they have
    new Holdings, updates their CurrentHoldings, and
    replaces their DisplayHoldings with their CurrentHoldings
    should all CurrentHoldings be identified.
    """
    logger.info("Beginning updateQuovoUserHoldings at %s" % (str(datetime.now().time()),))
    for qUser in QuovoUser.objects.all():
        name = qUser.userProfile.user.email
        logger.info("Beginning to update holdings for {0}".format(name))
        logger.info("Getting new holdings for {0}".format(name))
        newHolds = qUser.getNewHoldings()
        if newHolds and not qUser.currentHoldingsEqualHoldingJson(newHolds):
            logger.info("{0} has new holdings, changing their current holdings".format(name))
            qUser.setCurrentHoldings(newHolds)
        if not qUser.hasCompletedUserHoldings():
            logger.info("{0} has incomplete holdings, will have to update".format(name))
            qUser.isCompleted = False
        else:
            _updateQuovoUserDisplayHoldings(qUser)
        qUser.save()


def updateHoldingInformation():
    """
    This method iterates through all Holding objects
    in the database and updates their pricing, breakdown, expense,
    and other information related to the Holding.
    """
    # TODO ENSURE CASE WHERE UPDATE NUMBER HAS BEEN INCREMENTED.
    for holding in Holding.objects.exclude(category__in=["FOFF", "IGNO", "CASH"]):
        if holding.isIdentified():
            update_holding(holding)
    for holding in Holding.objects.filter(category__exact="CASH"):
        logging.info("Beginning to update returns for cash position pk: {0}, secname: {1}".format(holding.pk, holding.secname))
        holding.updateReturns()

        logging.info("Beginning to update expenses for cash position pk: {0}, secname: {1}".format(holding.pk, holding.secname))
        holding.updateExpenses()

        logging.info("Beginning to update breakdowns for cash position pk: {0}, secname: {1}".format(holding.pk, holding.secname))
        holding.updateAllBreakdowns()

    fillTreasuryBondValues()
    logging.info("Finished collecting treasuray bond values")


def update_holding(holding):
    try:
        logger.info(
            "Beginning to fill past prices for pk: {0}, identifier: {1}".format(holding.pk, holding.secname))
        holding.fillPrices()

        logger.info("Now updating all returns for pk: {0}, identifier: {1}".format(holding.pk, holding.secname))
        holding.updateReturns()

        logger.info(
            "Beginning to update expenses for pk: {0}, identifier: {1}".format(holding.pk, holding.secname))
        holding.updateExpenses()

        logger.info(
            "Now updating all breakdowns for pk: {0}, identifier: {1}".format(holding.pk, holding.secname))
        holding.updateAllBreakdowns()

        logger.info(
            "Now updating distributions for pk: {0}, identifier: {1}".format(holding.pk, holding.secname))
        holding.updateDividends()

        holding.updatedAt = timezone.now()
        holding.save()
    except MorningstarRequestError as err:
        isInvalid = False
        try:
            isInvalid = err.args[1].get('status', "").get('message', "").split(' ')[0] == "Invalid"
        except Exception:
            pass
        if isInvalid:
            logger.error("Holding " + holding.secname
                         + " has been given an Invalid identifier: "
                         + str(holding.getIdentifier()) + " wiping information.")
            ident = holding.getIdentifier()[1]
            if ident == "mstarid":
                holding.mstarid = ""
            elif ident == "ticker":
                holding.ticker = ""
            elif ident == "cusip":
                holding.cusip = ""
            holding.save()
            alertMislabeledHolding(holding.secname)
        else:
            if hasattr(err, "args") and len(err.args) > 1:
                a = err.args[1]
                status = a.get('status')
                if status and not status.get('messsage') == "OK":
                    logger.error("Error retrieving information for holding pk: " + str(holding.pk) + ". Received " +
                                 "response: \n" + str(a))
            else:
                #TODO MAKE THIS A MORE DESCRIPTIVE MESSAGE
                logger.error("Error retrieving information for holding pk: " + str(holding.pk) + ".")



def updateQuovoUserCompleteness():
    """
    This method iterates through all incomplete QuovoUsers,
    check if their holdings are now complete, and if they are,
    updates their display holdings, and marks them as complete.
    :return:
    """
    # Get all incomplete QuovoUsers
    for qUser in QuovoUser.objects.filter(isCompleted__exact=False):
        _updateQuovoUserDisplayHoldings(qUser)


def _updateQuovoUserDisplayHoldings(qUser):
    qUser.updateDisplayHoldings()
    track_data = True
    if qUser.hasCompletedUserHoldings():
        qUser.isCompleted = True
        qUser.save()
        sendHoldingProcessingCompleteNotification(qUser.userProfile.user.email)
    else:
        track_data = False
    user = get_user_model().objects.get(profile__quovoUser=qUser)
    ProgressTracker.track_progress(user, {
        "track_id": "complete_identification",
        "track_data": track_data
    })


def updateUserReturns():
    """
    This method iterates through all completed QuovoUsers
    and computes their returns for use in their returns module.
    """
    for acct in Account.objects.filter(active=True):
        acct.getAccountReturns()
    for qUser in QuovoUser.objects.all():
        if qUser.getDisplayHoldings():
            logger.info("Determining returns and sharpe for user: {0}".format(qUser.userProfile.user.email))
            qUser.getUserReturns()
            qUser.getUserSharpe()
            qUser.getUserBondEquity()
    logger.info("Determining average returns, sharpe, fees")
    getAverageReturns()
    getAverageSharpe()
    getAverageBondEquity()
    getAverageFees()


def updateUserHistory():
    for qUser in QuovoUser.objects.all():
        name = qUser.userProfile.user.email
        logger.info("Beginning to update transactions for {0}".format(name))
        try:
            qUser.updateTransactions()
        except VestiviseException as e:
            e.log_error()

def updateUserFees():
    for qUser in QuovoUser.objects.all():
        qUser.updateFees()


#ACCESSORY / UTILITY METHODS

def getAverageReturns():
    today = datetime.now().date()
    for age in [20, 30, 40, 50, 60, 70, 80]:
        group = QuovoUser.objects.filter(isCompleted__exact=True
        ).filter(
            userProfile__birthday__lte=today.replace(year=today.year-age+5)
        ).filter(
            userProfile__birthday__gte=today.replace(year=today.year-age-4)
        )
        siz = len(group)
        if siz > 100:
            numCheck = max(100, int(floor(.2*siz)))
            indicies = random.sample(range(siz), numCheck)
        else:
            indicies = range(siz)
        if(siz == 0):
            continue
        yearToDate = 0
        oneYearRes = 0
        twoYearRes = 0
        threeYearRes = 0
        oneMonthRes = 0
        threeMonthRes = 0
        for i in indicies:
            person = group[i].getUserReturns()
            yearToDate += person['yearToDate']
            oneYearRes += person['oneYearReturns']
            twoYearRes += person['twoYearReturns']
            threeYearRes += person['threeYearReturns']
            oneMonthRes += person['oneMonthReturns']
            threeMonthRes += person['threeMonthReturns']
        AverageUserReturns.objects.create(
            yearToDate=yearToDate/len(indicies),
            oneYearReturns=oneYearRes/len(indicies),
            twoYearReturns=twoYearRes/len(indicies),
            threeYearReturns=threeYearRes/len(indicies),
            oneMonthReturns=oneMonthRes/len(indicies),
            threeMonthReturns=threeMonthRes/len(indicies),
            ageGroup=age
        )

    group = QuovoUser.objects.filter(isCompleted__exact=True)
    siz = group.count()
    if siz > 100:
        numCheck = max(100, int(floor(.2 * siz)))
        indicies = random.sample(range(siz), numCheck)
    else:
        indicies = range(siz)
    if(siz == 0):
        return
    yearToDate = 0
    oneYearRes = 0
    twoYearRes = 0
    threeYearRes = 0
    oneMonthRes = 0
    threeMonthRes = 0
    for i in indicies:
        person = group[i].getUserReturns()
        yearToDate += person['yearToDate']
        oneYearRes += person['oneYearReturns']
        twoYearRes += person['twoYearReturns']
        threeYearRes += person['threeYearReturns']
        oneMonthRes += person['oneMonthReturns']
        threeMonthRes += person['threeMonthReturns']
    AverageUserReturns.objects.create(
        yearToDate=yearToDate / len(indicies),
        oneYearReturns=oneYearRes / len(indicies),
        twoYearReturns=twoYearRes / len(indicies),
        threeYearReturns=threeYearRes / len(indicies),
        oneMonthReturns=oneMonthRes / len(indicies),
        threeMonthReturns=threeMonthRes / len(indicies),
        ageGroup=0
    )






def getAverageFees():
    today = datetime.now().date()
    feesum=0.0
    total_users = QuovoUser.objects.all()
    i=0
    for qUser in total_users:

        #similar to alex's code
        holds = qUser.getDisplayHoldings()
        currVal = sum([x.value for x in holds])

        weights = [x.value / currVal for x in holds]
        feeList = []
        for h in holds:
            try:
                feeList.append(h.holding.expenseRatios.latest('createdAt').expense)
            except HoldingExpenseRatio.DoesNotExist:
                feeList.append(0.0)
        currFees = np.dot(weights, feeList)
        if len(feeList) != 0:
            i = i + 1

        feesum+= currFees

    if i>0:
        averageFee = feesum/i
    else:
        averageFee=0
    AverageUserFee.objects.create(avgFees=averageFee)


def getAverageSharpe():
    today = datetime.now().date()
    for age in [20, 30, 40, 50, 60, 70, 80]:
        group = QuovoUser.objects.filter(isCompleted__exact=True
        ).filter(
            userProfile__birthday__lte=today.replace(year=today.year-age+5)
        ).filter(
            userProfile__birthday__gte=today.replace(year=today.year-age-4)
        )
        siz = len(group)
        if siz > 100:
            numCheck = max(100, int(floor(.2*siz)))
            indices = random.sample(range(siz), numCheck)
        else:
            indices = range(siz)
        if siz < 2:
            continue
        values = []
        for i in indices:
            val = group[i].userSharpes.latest('createdAt').value
            values.append(val)
        mu = np.mean(values)
        sigma = np.std(values)
        AverageUserSharpe.objects.create(
            mean=mu,
            std=sigma,
            ageGroup=age
        )

    group = QuovoUser.objects.filter(isCompleted__exact=True)
    siz = len(group)
    if siz > 100:
        numCheck = max(100, int(floor(.2*siz)))
        indices = random.sample(range(siz), numCheck)
    else:
        indices = range(siz)
    if siz < 2:
        AverageUserSharpe.objects.create(
            mean=1,
            std=1,
            ageGroup=0
        )
        return
    values = []
    for i in indices:
        val = group[i].userSharpes.latest('createdAt').value
        values.append(val)
    mu = np.mean(values)
    sigma = np.std(values)
    AverageUserSharpe.objects.create(
        mean=mu,
        std=sigma,
        ageGroup=0
    )


def getAverageBondEquity():
    today = datetime.now().date()
    for age in [20, 30, 40, 50, 60, 70, 80]:
        group = QuovoUser.objects.filter(isCompleted__exact=True,
                                         userProfile__birthday__lte=today.replace(year=today.year-age+5),
                                         userProfile__birthday__gte=today.replace(year=today.year-age-4))
        siz = group.count()
        if siz > 100:
            numCheck = max(100, int(floor(.2*siz)))
            indices = random.sample(range(siz), numCheck)
        else:
            indices = range(siz)
        if siz < 2:
            continue
        bond = 0
        equity = 0
        for i in indices:
            person = group[i].userBondEquity.latest('createdAt')
            bond += person.bond
            equity += person.equity
        AverageUserBondEquity.objects.create(
            ageGroup=age,
            bond=bond/len(indices),
            equity=equity/len(indices)
        )

    group = QuovoUser.objects.filter(isCompleted__exact=True)
    siz = group.count()
    if siz > 100:
        numCheck = max(100, int(floor(.2*siz)))
        indicies = random.sample(range(siz), numCheck)
    else:
        indicies = range(siz)
    if siz == 0:
        return
    bond = 0
    equity = 0
    for i in indicies:
        person = group[i].userBondEquity.latest('createdAt')
        bond += person.bond
        equity += person.equity
    AverageUserBondEquity.objects.create(
        bond=bond/len(indicies),
        equity=equity/len(indicies),
        ageGroup=0
    )



def fillTreasuryBondValues():
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
        monthRet = None
        for entry in tree.findall("{http://www.w3.org/2005/Atom}entry"):
            for content in entry.findall("{http://www.w3.org/2005/Atom}content"):
                monthRet = (content[0][1].text, content[0][2].text)

        if monthRet is None:
            raise NightlyProcessException("Could not find returns for {0}/{1}".format(start.year, start.month))

        TreasuryBondValue.objects.create(
            date=parse(monthRet[0]).date(),
            value=float(monthRet[1])
        )

        start += relativedelta(months=1)
