from dashboard.models import *
from Vestivise.mailchimp import *
from django.utils.datetime_safe import datetime
from django.utils import timezone
import logging
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
            holding.updateBreakdown()
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
