from django.db import models
from dashboard.models import UserProfile, QuovoUser


class Holding(models.Model):

    secname = models.CharField(max_length=200)
    cusip = models.CharField(max_length=9, null=True, blank=True)
    ric = models.CharField(max_length=9, null=True, blank=True)
    ticker = models.CharField(max_length=5, null=True, blank=True)
    updatedAt = models.DateTimeField(null=True, blank=True)

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
        if(self.cusip!= ""):
            return (self.cusip, "Cusip")
        elif(self.ric != ""):
            return (self.ric, "Ric")
        else:
            return None

    def isIdentified(self):
        """
        Returns True if the holding is identified - cusip is filled or ric
        :return: Boolean if the holding is identified
        """
        return self.cusip != "" or self.ric != ""

    def isCompleted(self):
        """
        Returns True if the holding is completed - has asset breakdown and holding price and expense ratio
        :return: Boolean if the holding is completed
        """
        return hasattr(self, 'assetBreakdown') and hasattr(self, 'holdingPrice') and hasattr(self, 'expenseRatio')


class UserCurrentHolding(models.Model):

    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('QuovoUser', related_name="userCurrentHoldings")
    value = models.FloatField()
    quantity = models.FloatField()

    class Meta:
        verbose_name = "UserCurrentHolding"
        verbose_name_plural = "UserCurrentHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class UserDisplayHolding(models.Model):

    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('QuovoUser', related_name="userDisplayHoldings")
    value = models.FloatField()
    quantity = models.FloatField()

    class Meta:
        verbose_name = "UserDisplayHolding"
        verbose_name_plural = "UserDisplayHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class UserHistoricalHolding(models.Model):

    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('QuovoUser', related_name="userHistoricalHoldings")
    value = models.FloatField()
    quantity = models.FloatField()
    archivedAt = models.DateTimeField()

    class Meta:
        verbose_name = "UserHistoricalHolding"
        verbose_name_plural = "UserHistoricalHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class HoldingPrice(models.Model):

    price = models.FloatField()
    holding = models.ForeignKey('Holding', related_name="holdingPrice")
    closingDate = models.DateField()

    class Meta:
        verbose_name = "HoldingPrice"
        verbose_name_plural = "HoldingPrices"

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.price, self.closingDate)


class HoldingExpenseRatio(models.Model):

    expense = models.FloatField()
    holding = models.ForeignKey('Holding', related_name="expenseRatio")
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
