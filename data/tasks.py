from data.models import *

def updateQuovoUserHoldings():
    for qUser in QuovoUser.objects.all():
        newHolds = qUser.getNewHoldings()
        if(qUser.currHoldings.equalsHoldingJson(newHolds)):
            qUser.setCurrHoldings(newHolds)
        if(qUser.hasIncompleteHolds()):
            qUser.isCompleted = False
        else:
            qUser.updateDispHoldings()
        qUser.save()

def updateHoldingInformation():
    #for holding in Holding.objects.all():
    #    if holding.
    pass