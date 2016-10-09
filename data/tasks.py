from dashboard.models import *
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
    for holding in Holding.objects.all():
        if (not holding.isCompleted()):
            holding.getReturns(datetime.datetime.now().date()-datetime.timedelta(days=365),
                               datetime.datetime.now().date())
        elif (holding.needsReturnsUpdate()):
            holding.getReturns(holding.updatedAt.date(),
                               datetime.datetime.now().date())

