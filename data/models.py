from django.db import models
from datetime import timedelta
from django.utils.datetime_safe import datetime
from Vestivise.morningstar import Morningstar as ms
from Vestivise.Vestivise import *
import dateutil.parser
import numpy as np

class Holding(models.Model):

    secname = models.CharField(max_length=200)
    cusip = models.CharField(max_length=9, null=True, blank=True)
    ticker = models.CharField(max_length=5, null=True, blank=True)
    updatedAt = models.DateTimeField(null=True, blank=True)
    isNAVValued = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = "Holding"
        verbose_name_plural = "Holdings"

    def __str__(self):
        return self.secname

    @staticmethod
    def getHoldingByPositionDict(posDict):
        """
        Queries Holdings by the security name, cusip, and
        ticker, organized in the format of a position from
        the Quovo API. If no such holding exists, it will create
        a new one using the information from this Json.
        :param posDict: Position Dictionary to be used in query/creation
        :return: A reference to the desired Holding.
        """
        try:
            if(posDict["cusip"] is not None and posDict["cusip"] != ""):
                return Holding.objects.get(cusip=posDict["cusip"])
        except (Holding.DoesNotExist, KeyError):
            pass
        try:
            return Holding.objects.get(secname=posDict["ticker_name"])
        except (Holding.DoesNotExist, KeyError):
            pass
        return Holding.objects.create(secname=posDict["ticker_name"],
                                      cusip=posDict["cusip"])

    @staticmethod
    def getHoldingBySecname(sname):
        """
        Queries Holdings by the security name, and returns its
        reference. If it doesn't exit, it will create a Holding
        with that secname, and return its reference.
        :param sname: Holding name to be queried.
        :return: Reference to the desired Holding.
        """
        try:
            return Holding.objects.get(secname=sname)
        except Holding.DoesNotExist:
            return Holding.objects.create(secname=sname)

    def getIdentifier(self):
        """
        Gets the identifier for the Holding for use in TR calls.
        If there is no proper identifier, returns a None type.
        :return: ( identifier, identifierType) or None.
        """
        if(self.ticker is not None and self.ticker != ""):
            return (self.ticker, 'ticker')
        if(self.cusip is not None and self.cusip != ""):
            return (self.cusip, 'cusip')
        else:
            raise UnidentifiedHoldingException("Holding id: {0}, secname: {1}, is unidentified!".format(
                self.id, self.secname
            ))

    def isIdentified(self):
        """
        Returns True if the holding is identified - cusip is filled or ric
        :return: Boolean if the holding is identified
        """
        return self.cusip != "" and not (self.cusip is None)

    def isCompleted(self):
        """
        Returns True if the holding is completed - has asset breakdown and holding price and expense ratio
        :return: Boolean if the holding is completed
        """
        return hasattr(self, 'assetBreakdown') and hasattr(self, 'holdingPrice') and hasattr(self, 'expenseRatio')

    def createPrices(self, timeStart, timeEnd):
        """
        Creates HoldingPrice objects associated with each available day in the
        the provided timespan, including the timeStart and the timeEnd if they are available.
        :param timeStart: The beginning time from which data will be collected.
        :param timeEnd: The findal day from which data will be collected.
        """
        ident = self.getIdentifier()
        if(self.isNAVValued):
            data = ms.getHistoricalNAV(ident[0], ident[1], timeStart, timeEnd)
        else:
            data = ms.getHistoricalMarketPrice(ident[0], ident[1], timeStart, timeEnd)
        for item in data:
            day = dateutil.parser.parse(item['d']).date()
            if self.holdingPrices.filter(closingDate__exact=day).exists():
                continue
            price = float(item['v'])
            self.holdingPrices.create(price=price, closeDate=day)

    def fillPrices(self):
        """
        If the Holding is new, fills all of its price fields for
        the past three years. Otherwise, fills all price fields since
        its last update till now.
        """
        if(self.updatedAt is None or self.updatedAt < datetime.now() - timedelta(years=3)):
            startDate = datetime.now() - timedelta(years=3)
        else:
            startDate = self.updatedAt - timedelta(days=1)
        self.createPrices(startDate, datetime.now())

    def updateExpenses(self):
        """
        Gets the most recent Expense Ratio for this fund from Morningstar, if they
        don't match, creates a new HoldingExpenseRatio with the most recent date.
        """
        ident = self.getIdentifier()
        data = ms.getProspectusFees(ident[0], ident[1])
        value = float(data['NetExpenseRatio'])
        try:
            mostRecVal = self.expenseRatios.latest('createdAt')
            if np.isclose(mostRecVal, value):
                return
            self.expenseRatios.create(expense=value)
        except HoldingExpenseRatio.DoesNotExist:
            self.expenseRatios.create(expense=value)

    def updateBreakdown(self):
        # TODO: REQUIRES MORNINGSTAR
        pass


class UserCurrentHolding(models.Model):
    """
    This model represents the user's current holdings, updated daily.
    This does not necessarily reflect the holdings presented on the
    user's dashboard, but are the most recent holdings collected from
    a call to the Quovo API.
    """
    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('dashboard.QuovoUser', related_name="userCurrentHoldings")
    value = models.FloatField()
    quantity = models.FloatField()

    class Meta:
        verbose_name = "UserCurrentHolding"
        verbose_name_plural = "UserCurrentHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class UserDisplayHolding(models.Model):
    """
    This model represents the user's current holdings to be displayed
    on their dashboard. This is updated with the values of the UserCurrentHolding
    should all UserCurrentHoldings be identified.
    """
    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('dashboard.QuovoUser', related_name="userDisplayHoldings")
    value = models.FloatField()
    quantity = models.FloatField()

    class Meta:
        verbose_name = "UserDisplayHolding"
        verbose_name_plural = "UserDisplayHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class UserHistoricalHolding(models.Model):
    """
    This model represents the user's past UserDisplayHoldings for
    archiving purposes to see how their portfolios have changed. Each
    HistoricalHolding comes with a timestamp to identify when it was
    archived. More importantly, it has its portfolioIndex. This refers
    to WHICH historical portfolio this HistoricalHolding refers to.

    For example, a user could have been invested in stocks A,B, and C.
    But after time, decides to drop stock C. HistoricalHoldings would
    be created for A, B, and C with an index of 0. After the portfolio's
    next change, HistoricalHoldings will be created for A and B with
    an index of 1. This process continues for every change.
    """
    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('dashboard.QuovoUser', related_name="userHistoricalHoldings")
    value = models.FloatField()
    quantity = models.FloatField()
    archivedAt = models.DateTimeField()
    portfolioIndex = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "UserHistoricalHolding"
        verbose_name_plural = "UserHistoricalHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class HoldingPrice(models.Model):

    price = models.FloatField()
    holding = models.ForeignKey('Holding', related_name="holdingPrices")
    closingDate = models.DateField()

    class Meta:
        verbose_name = "HoldingPrice"
        verbose_name_plural = "HoldingPrices"
        unique_together = ("holding", "closeDate")

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.price, self.closingDate)


class HoldingExpenseRatio(models.Model):

    expense = models.FloatField()
    holding = models.ForeignKey('Holding', related_name="expenseRatios")
    createdAt = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "HoldingExpenseRatio"
        verbose_name_plural = "HoldingExpenseRatios"

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.expense, self.createdAt)


class HoldingAssetBreakdown(models.Model):

    asset = models.CharField(max_length=50)
    percentage = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="assetBreakdown")
    createdAt = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "HoldingAssetBreakdown"
        verbose_name_plural = "HoldingAssetBreakdowns"

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.expense, self.createdAt)


class UserReturns(models.Model):
    """
    This model represents the responses for the UserReturns module. It
    contains three float fields, each containing the returns from date
    to today, where the date ranges from three years ago to one year ago.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    oneYearReturns = models.FloatField()
    twoYearReturns = models.FloatField()
    threeYearReturns = models.FloatField()
    quovoUser = models.ForeignKey("dashboard.QuovoUser", related_name="userReturns")

    class Meta:
        verbose_name = "UserReturn"
        verbose_name_plural = "UserReturns"

    def __str__(self):
        up = self.quovoUser.userProfile
        return up.firstName + " " + up.lastName + ": " + str(self.createdAt)
