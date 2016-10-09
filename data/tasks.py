from dashboard.models import *
from Vestivise.mailchimp import *
import datetime
"""
This file includes all functions to be run in overnight processes
for the sake of updating the database for day to day operations.
"""


def updateQuovoUserHoldings():
    """
    Updates every QuovoUser's holdings. Should they have
    new Holdings, updates their CurrentHoldings, and
    replaces their DisplayHoldings with their CurrentHoldings
    should all CurrentHoldings be identified.
    """
    for qUser in QuovoUser.objects.all():
        newHolds = qUser.getNewHoldings()
        if(not qUser.currHoldings.equalsHoldingJson(newHolds)):
            qUser.setCurrHoldings(newHolds)
        if(not qUser.hasCompletedUserHoldings()):
            qUser.isCompleted = False
        else:
            qUser.updateDispHoldings()
        qUser.save()

def updateHoldingInformation():
    """
    This method iterates through all Holding objects
    in the database and updates their pricing, breakdown, expense,
    and other information related to the Holding.
    """

def updateHoldingInformation():
    for holding in Holding.objects.all():
        if (not holding.isCompleted()):
            holding.getReturns(datetime.datetime.now().date()-datetime.timedelta(days=365),
                               datetime.datetime.now().date())
        elif (holding.needsReturnsUpdate()):
            holding.getReturns(holding.updatedAt.date(),
                               datetime.datetime.now().date())

        holding.updateExpenses()
        holding.updateBreakdown()

        holding.updatedAt = datetime.datetime.now()
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
