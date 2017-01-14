from dashboard.models import *
from Vestivise.mailchimp import *
from django.utils.datetime_safe import datetime
from django.utils import timezone
from Vestivise.morningstar import MorningstarRequestError
from Vestivise.Vestivise import NightlyProcessException
import logging
import random
import requests
import xml.etree.cElementTree as ET
from dateutil.parser import parse
from math import floor
from data.models import  AverageUserReturns, AverageUserSharpe, TreasuryBondValue

"""
This file includes all functions to be run in overnight processes
for the sake of updating the database for day to day operations.
"""
logger = logging.getLogger("nightly_process")

def updateQuovoUserAccounts():
    logger.info("Beginning updateQuovoUserAccounts at %s" % (str(datetime.now().time()),))
    for qUser in QuovoUser.objects.all():
        qUser.updateAccounts()

def updateQuovoUserPortfolios():
    logger.info("Beginning updateQuovoUserPortfolios at %s" % (str(datetime.now().time()),))
    for qUser in QuovoUser.objects.all():
        qUser.updatePortfolios()


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
        if(not qUser.currentHoldingsEqualHoldingJson(newHolds)):
            logger.info("{0} has new holdings, changing their current holdings".format(name))
            qUser.setCurrentHoldings(newHolds)
        if(not qUser.hasCompletedUserHoldings()):
            logger.info("{0} has incomplete holdings, will have to update".format(name))
            qUser.isCompleted = False
        else:
            qUser.updateDisplayHoldings()
        qUser.save()


def updateHoldingInformation():
    """
    This method iterates through all Holding objects
    in the database and updates their pricing, breakdown, expense,
    and other information related to the Holding.
    """
    # TODO ENSURE CASE WHERE UPDATE NUMBER HAS BEEN INCREMENTED.
    for holding in Holding.objects.filter(shouldIgnore__exact=False, isFundOfFunds__exact=False):
        if holding.isIdentified():
            try:
                logger.info("Beginning to fill past prices for pk: {0}, identifier: {1}".format(holding.pk, holding.getIdentifier()))
                holding.fillPrices()

                logger.info("Now updating all returns for pk: {0}, identifier: {1}".format(holding.pk, holding.getIdentifier()))
                holding.updateReturns()

                if holding.isNAVValued:
                    logger.info("Beginning to update expenses for pk: {0}, identifier: {1}".format(holding.pk, holding.getIdentifier()))
                    holding.updateExpenses()

                    logger.info("Now updating all breakdowns for pk: {0}, identifier: {1}".format(holding.pk, holding.getIdentifier()))
                    holding.updateAllBreakdowns()

                    logger.info("Now updating distributions for pk: {0}, identifier: {1}".format(holding.pk, holding.getIdentifier()))
                    holding.updateDividends()

                holding.updatedAt = timezone.now()
                holding.save()
            except MorningstarRequestError as err:
                if err.args[1].get('status', "").get('message', "") == "Invalid Ticker":
                    logger.error("Holding " + holding.secname
                                 + " has been given an Invalid identifier: "
                                 + str(holding.getIdentifier()) + " wiping information.")
                    holding.mstarid = ""
                    holding.ticker = ""
                    holding.cusip = ""
                    holding.save()
                    alertMislabeledHolding(holding.secname)
                else:
                    logger.error("Error retrieving information for holding pk: " + str(holding.pk) + ". Received " +
                                 "response: \n" + str(err.args[1]))
    fillTreasuryBondValues()


def updateQuovoUserCompleteness():
    """
    This method iterates through all incomplete QuovoUsers,
    check if their holdings are now complete, and if they are,
    updates their display holdings, and marks them as complete.
    :return:
    """
    # Get all incomplete QuovoUsers
    for qUser in QuovoUser.objects.filter(isCompleted__exact=False):
        if qUser.hasCompletedUserHoldings():
            logger.info("pk: {0}, {1} {2} now has complete holdings. Updating and notifying.".format(qUser.pk, qUser.userProfile.firstName, qUser.userProfile.lastName))
            qUser.updateDisplayHoldings()
            qUser.isCompleted = True
            qUser.save()
            sendHoldingProcessingCompleteNotification(qUser.userProfile.user.email)


def updateUserReturns():
    """
    This method iterates through all completed QuovoUsers
    and computes their returns for use in their returns module.
    """
    for qUser in QuovoUser.objects.filter(isCompleted__exact=True):
        logger.info("Determining returns and sharpe for pk: {0}".format(qUser.userProfile.pk))
        qUser.getUserReturns()
        qUser.getUserSharpe()
    logger.info("Determining average returns and sharpe")
    getAverageReturns()
    getAverageSharpe()


def updateUserHistory():
    for qUser in QuovoUser.objects.all():
        qUser.updateTransactions()


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
            indicies = random.sample(range(siz), int(floor(.2*siz)))
        else:
            indicies = range(siz)
        if(siz == 0):
            continue
        oneYearRes = 0
        twoYearRes = 0
        threeYearRes = 0
        oneMonthRes = 0
        threeMonthRes = 0
        for i in indicies:
            person = group[i].userReturns.latest('createdAt')
            oneYearRes += person.oneYearReturns
            twoYearRes += person.twoYearReturns
            threeYearRes += person.threeYearReturns
            oneMonthRes += person.oneMonthReturns
            threeMonthRes += person.threeMonthReturns
        AverageUserReturns.objects.create(
            oneYearReturns=oneYearRes/len(indicies),
            twoYearReturns=twoYearRes/len(indicies),
            threeYearReturns=threeYearRes/len(indicies),
            oneMonthReturns=oneMonthRes/len(indicies),
            threeMonthReturns=threeMonthRes/len(indicies),
            ageGroup=age
        )

    group = QuovoUser.objects.filter(isCompleted__exact=True)
    siz = len(group)
    if siz > 100:
        indicies = random.sample(range(siz), int(floor(.2*siz)))
    else:
        indicies = range(siz)
    if(siz == 0):
        return
    oneYearRes = 0
    twoYearRes = 0
    threeYearRes = 0
    oneMonthRes = 0
    threeMonthRes = 0
    for i in indicies:
        person = group[i].userReturns.latest('createdAt')
        oneYearRes += person.oneYearReturns
        twoYearRes += person.twoYearReturns
        threeYearRes += person.threeYearReturns
        oneMonthRes += person.oneMonthReturns
        threeMonthRes += person.threeMonthReturns
    AverageUserReturns.objects.create(
        oneYearReturns=oneYearRes / len(indicies),
        twoYearReturns=twoYearRes / len(indicies),
        threeYearReturns=threeYearRes / len(indicies),
        oneMonthReturns=oneMonthRes / len(indicies),
        threeMonthReturns=threeMonthRes / len(indicies),
        ageGroup=0
    )


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
    while(start <= end):
        data = requests.get(base.format(start.month, start.year))

        tree = ET.fromstring(data.text)
        monthRet = None
        for entry in tree.findall("{http://www.w3.org/2005/Atom}entry"):
            for content in entry.findall("{http://www.w3.org/2005/Atom}content"):
                monthRet = (content[0][1].text, content[0][4].text)

        if monthRet is None:
            raise NightlyProcessException("Could not find returns for {0}/{1}".format(start.year, start.month))

        TreasuryBondValue.objects.create(
            date=parse(monthRet[0]).date(),
            value=float(monthRet[1])
        )

        start += relativedelta(months=1)
