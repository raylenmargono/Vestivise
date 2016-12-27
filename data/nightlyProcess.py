from dashboard.models import *
from Vestivise.mailchimp import *
from django.utils.datetime_safe import datetime
from django.utils import timezone
import logging
import random
from math import floor
from django.utils.dateparse import parse_date
from data.models import Transaction, AverageUserReturns, AverageUserSharpe

"""
This file includes all functions to be run in overnight processes
for the sake of updating the database for day to day operations.
"""
logger = logging.getLogger("nightly_process")


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
    for holding in Holding.objects.filter(shouldIgnore__exact=False):
        if holding.isIdentified():
            holding.fillPrices()

            holding.updateExpenses()
            holding.updateAllBreakdowns()
            holding.updateReturns()

            holding.updatedAt = timezone.now()
            holding.save()


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
        qUser.getUserReturns()
        qUser.getUserSharpe()

    getAverageReturns()
    getAverageSharpe()

def updateUserHistory():
    for qUser in QuovoUser.objects.all():
        history = qUser.getUserHistory()
        last_id = None
        if history:
            last_id = history.last().quovoID
        latest_history = Quovo.get_user_history(qUser.quovoID, start_id=last_id)
        for transaction in latest_history.get('history'):
            Transaction.objects.update_or_create(
                quovoUser=qUser,
                quovoID=transaction.get('id'),
                date=parse_date(transaction.get('date')),
                fees=transaction.get('fees'),
                value=transaction.get('value'),
                price=transaction.get('price'),
                quantity=transaction.get('quantity'),
                cusip=transaction.get('cusip'),
                expense_category=transaction.get('expense_category'),
                ticker=transaction.get('ticker'),
                ticker_name=transaction.get('ticker_name'),
                tran_category=transaction.get('tran_category'),
                tran_type=transaction.get('tran_type'),
                memo=transaction.get('memo')
            )


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
            indices = random.sample(range(siz), int(floor(.2*siz)))
        else:
            indices = range(siz)
        if siz == 0:
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
        indices = random.sample(range(siz), int(floor(.2*siz)))
    else:
        indices = range(siz)
    if siz == 0:
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
