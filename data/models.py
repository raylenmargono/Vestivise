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


class UserCurrentHolding(models.Model):

    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('QuovoUser', related_name="currHoldings")

    class Meta:
        verbose_name = "UserCurrentHolding"
        verbose_name_plural = "UserCurrentHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)

    def equalsHoldingJson(self, holdingJson):
        """
        Determines whether or not the user's current holdings
        possess the same assets as a holding JSON from Quovo.
        :param holdingJson: The json of holding names to be compared against.
        :return: Boolean value denoting whether or not the UserCurrentHolding possesses
        the same assets as the Json.
        """
        pass


class UserDisplayHolding(models.Model):

    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('QuovoUser', related_name="dispHoldings")

    class Meta:
        verbose_name = "UserDisplayHolding"
        verbose_name_plural = "UserDisplayHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class HoldingPrice(models.Model):

    price = models.FloatField()
    holding = models.ForeignKey('Holding')
    closingDate = models.DateField()

    class Meta:
        verbose_name = "HoldingPrice"
        verbose_name_plural = "HoldingPrices"

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.price, self.closingDate)


class HoldingExpenseRatio(models.Model):

    expense = models.FloatField()
    holding = models.ForeignKey('Holding')
    createdAt = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "HoldingExpenseRatio"
        verbose_name_plural = "HoldingExpenseRatios"

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.expense, self.createdAt)


class HoldingAssetBreakdown(models.Model):

    asset = models.CharField(max_length=50)
    percentage = models.FloatField()
    holding = models.ForeignKey("Holding")
    createdAt = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "HoldingAssetBreakdown"
        verbose_name_plural = "HoldingAssetBreakdowns"

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.expense, self.createdAt)
