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
    userProfile = models.OneToOneField('UserProfile')
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
            q = Quovo.get_shared_instance()
            # assumption is only 1 portfolio linked
            portfolios = q.get_account_portfolios(self.quovoID)["portfolios"]
            if not portfolios:
                return None
            portfolio = portfolios.pop()
            return q.get_portfolio_positions(portfolio["id"])["positions"]
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
        positions = json.loads(newHoldings)["positions"]
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

        for dispHold in oldDisplayHoldings:
            histHold = UserHistoricalHolding()
            histHold.quovoUser = self
            histHold.quantity = dispHold.quantity
            histHold.value = dispHold.quantity
            histHold.holding = dispHold.holding
            histHold.archivedAt = timestamp
            histHold.portfolioIndex = self.currentHistoricalIndex
            histHold.save()
            dispHold.delete()

        self.currentHistoricalIndex += 1
        self.save()

    def CurrentHoldingsEqualHoldingJson(self, holdingJson):
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
        positions = json.loads(holdingJson)["positions"]
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
