from dashboard.models import *
"""
This file includes all functions to be run in overnight processes
for the sake of updating teh database for day to day operations.
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
        if(qUser.currHoldings.equalsHoldingJson(newHolds)):
            qUser.setCurrHoldings(newHolds)
        if(not qUser.hasCompletedUserHoldings()):
            qUser.isCompleted = False
        else:
            qUser.updateDispHoldings()
        qUser.save()

def updateHoldingInformation():
    #for holding in Holding.objects.all():
    #    if holding.
    pass