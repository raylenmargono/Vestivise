from __future__ import unicode_literals
from django.contrib.auth.models import User
from data.models import *
import json
import datetime
import numpy as np
from Vestivise.quovo import Quovo


class UserProfile(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    birthday = models.DateField()
    state = models.CharField(max_length=5)
    createdAt = models.DateField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='profile')
    company = models.CharField(max_length=50)
    zipCode = models.CharField(max_length=5)

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def get_quovo_user(self):
        if hasattr(self, 'quovoUser'):
            return self.quovoUser
        return None

    def __str__(self):
        return "%s" % (self.user.email,)


class Module(models.Model):
    categories = (
        ('Risk', 'Risk'),
        ('Return', 'Return'),
        ('Asset', 'Asset'),
        ('Cost', 'Cost'),
    )

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=categories)
    endpoint = models.CharField(max_length=50)
    moduleID = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return self.moduleName


class QuovoUser(models.Model):
    quovoID = models.IntegerField()
    isCompleted = models.BooleanField(default=False)
    userProfile = models.OneToOneField('UserProfile', related_name='quovoUser')
    currentHistoricalIndex = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "QuovoUser"
        verbose_name_plural = "QuovoUsers"

    def __str__(self):
        return "%s" % (self.userProfile.user.email,)

    def hasCompletedUserHoldings(self):
        """
        Returns if the user has completed holdings for their current holdings
        :return: Boolean if the user's holdings for this account are all identified
                and completed.
        """
        if hasattr(self, "userCurrentHoldings"):
            current_holdings = self.userCurrentHoldings.all()
            for current_holding in current_holdings:
                if not current_holding.holding.isIdentified() or not current_holding.holding.isCompleted():
                    return False
        else:
            return False
        return True

    def getNewHoldings(self):
        """
        Gathers the new holdings JSON from a call to the Quovo API.
        :return: A Json of the user's most recent holdings.
        """
        try:
            positions = Quovo.get_user_positions(self.quovoID)
            if (not positions):
                return None
            return positions
        except:
            return None

    def setCurrentHoldings(self, newHoldings):
        """
        Accepts a Json of new holdings and sets the UserCurretHoldings
        of this user to contain the values of the newHoldings. This then
        deletes the old UserCurrentHoldings.
        :param: newHoldings The Json of new holdings to overwrite the
                UserCurrentHoldings
        """
        # Get rid of all the old UserCurrentHoldings
        for hold in self.userCurrentHoldings.all():
            hold.delete()

        # For each new position in Json response, create
        # a new UserCurrentHolding with its data.
        # Search for the Holding by its name. If it isn't present,
        # create a new one.
        positions = newHoldings["positions"]
        for position in positions:
            hold = UserCurrentHolding()
            hold.quovoUser = self
            hold.quantity = position["quantity"]
            hold.value = position["value"]
            hold.holding = Holding.getHoldingByPositionDict(position)
            hold.save()

    def updateDisplayHoldings(self):
        """
        Copies the values of the UserCurrentHoldings to the
        UserDisplayHoldings. This will move the old UserDisplayHoldings
        to UserHistoricalHoldings.
        """
        # Collect a time to organize the UserHistoricalHoldings
        timestamp = datetime.datetime.now()
        # Collect the old UserDisplayHoldings so they can be deleted
        # after the data is transferred to UserHistoricalHoldings
        oldDisplayHoldings = self.userDisplayHoldings.all()
        # Create a new UserDisplayHolding for each
        for currHold in self.userCurrentHoldings.all():
            dispHold = UserDisplayHolding()
            dispHold.quovoUser = self
            dispHold.quantity = currHold.quantity
            dispHold.value = currHold.quantity
            dispHold.holding = currHold.holding
            dispHold.save()

        self.currentHistoricalIndex += 1

        for dispHold in oldDisplayHoldings:
            histHold = UserHistoricalHolding.objects.create(
                quovoUser=self,
                quantity=dispHold.quantity,
                value=dispHold.quantity,
                holding=dispHold.holding,
                archivedAt=timestamp,
                portfolioIndex=self.currentHistoricalIndex
            )
            dispHold.delete()

        self.save()

    def currentHoldingsEqualHoldingJson(self, holdingJson):
        """
        Determines whether or not the user's current holdings
        possess the same assets as a holding JSON from Quovo.
        :param holdingJson: The json of holding names to be compared against.
        :return: Boolean value denoting whether or not the UserCurrentHolding possesses
        the same assets as the Json.
        """
        # Get the current user holds in touples of secname, to the
        # hold itself.
        userCurrentHolds = dict((x.holding.secname, x) for x in self.userCurrentHoldings.all())
        # Fetch the positions from the call.
        positions = holdingJson["positions"]
        for position in positions:
            # Check if the position is currently in the user's holdings, if not
            # return false.
            if position["ticker_name"] in userCurrentHolds:
                # Check that the user's holdings match (or at least are very close)
                # in terms of value and quantity. If they aren't, return false.
                hold = userCurrentHolds[position["ticker_name"]]
                if (not np.isclose(hold.value, position["value"])
                        and not np.isclose(hold.quantity, position["quantity"])):
                    return False
            else:
                return False
        return True

    def getUserReturns(self):
        #TODO: REQUIRES MORNINGSTAR
        pass
