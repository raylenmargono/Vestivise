from django.db import models
from datetime import timedelta
from django.utils.datetime_safe import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from Vestivise.morningstar import Morningstar as ms
from Vestivise.Vestivise import UnidentifiedHoldingException
import dateutil.parser
import numpy as np
from Vestivise import mailchimp


class Transaction(models.Model):

    quovoUser = models.ForeignKey('dashboard.QuovoUser', related_name="userTransaction")

    quovoID = models.IntegerField(unique=True)

    date = models.DateField(null=True, blank=True)
    value = models.FloatField()
    fees = models.FloatField()
    value = models.FloatField()
    price = models.FloatField()
    quantity = models.FloatField()

    cusip = models.CharField(max_length=30, null=True, blank=True)
    expense_category = models.CharField(max_length=30, null=True, blank=True)
    ticker = models.CharField(max_length=30, null=True, blank=True)
    ticker_name = models.CharField(max_length=50, null=True, blank=True)
    tran_category = models.CharField(max_length=50, null=True, blank=True)
    # https://api.quovo.com/docs/agg/#transaction-types
    tran_type = models.CharField(max_length=50, null=True, blank=True)
    memo = models.CharField(max_length=250, null=True, blank=True)


    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return "{0}: {1} {2}".format(self.quovoUser, self.tran_type, self.date)

    def get_full_transaction_name(self):
        map = {
            'B' : 'Buy',
            'S' : 'Sell',
            'T' : 'Transfer',
            'I' : 'Dividends/Interest/Fees',
            'C' : 'Cash'
        }
        return map.get(self.tran_category)


class HoldingJoin(models.Model):

    parentHolding = models.ForeignKey("Holding", related_name="childJoiner")
    childHolding = models.ForeignKey("Holding", related_name="parentJoiner")
    compositePercent = models.FloatField()

    class Meta:
        verbose_name = "HoldingJoin"
        verbose_name_plural = "HoldingJoins"


class Holding(models.Model):

    secname = models.CharField(max_length=200, null=True, blank=True, unique=True)
    cusip = models.CharField(max_length=9, null=True, blank=True)
    ticker = models.CharField(max_length=5, null=True, blank=True)
    updatedAt = models.DateTimeField(null=True, blank=True)
    currentUpdateIndex = models.PositiveIntegerField(default=0)
    isNAVValued = models.BooleanField(default=True)
    shouldIgnore = models.BooleanField(default=False)
    isFundOfFunds = models.BooleanField(default=False)


    class Meta:
        verbose_name = "Holding"
        verbose_name_plural = "Holdings"

    def __str__(self):
        return self.secname

    @staticmethod
    def isIdentifiedHolding(secname):
        return Holding.objects.filter(secname=secname).exists()

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
        try:
            mailchimp.alertIdentifyHoldings(posDict["ticker_name"])
        except:
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
            mailchimp.alertIdentifyHoldings(sname)
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
        return (self.ticker != "" and self.ticker is not None) or (self.cusip != "" and not (self.cusip is None))

    def isCompleted(self):
        """
        Returns True if the holding is completed - has asset breakdown and holding price and expense ratio
        :return: Boolean if the holding is completed
        """
        return hasattr(self, 'assetBreakdowns') and hasattr(self, 'holdingPrices') and hasattr(self, 'expenseRatios')

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
            try:
                price = float(item['v'])
                self.holdingPrices.create(price=price, closingDate=day)
            except (ValidationError, IntegrityError):
                continue

    def fillPrices(self):
        """
        If the Holding is new, fills all of its price fields for
        the past three years. Otherwise, fills all price fields since
        its last update till now.
        """
        if(self.updatedAt is None or
           not self.holdingPrices.exists() or
           self.holdingPrices.latest('closingDate').closingDate < (datetime.now() - timedelta(weeks=3*52)).date()):

            startDate = datetime.now() - timedelta(weeks=3*52)
        else:
            startDate = self.holdingPrices.latest('closingDate').closingDate - timedelta(days=1)
        self.createPrices(startDate, datetime.now())

    def updateExpenses(self):
        """
        Gets the most recent Expense Ratio for this fund from Morningstar, if they
        don't match, creates a new HoldingExpenseRatio with the most recent ratio.
        """
        ident = self.getIdentifier()
        data = ms.getProspectusFees(ident[0], ident[1])
        value = float(data['NetExpenseRatio'])
        try:
            mostRecVal = self.expenseRatios.latest('createdAt').expense
            if np.isclose(mostRecVal, value):
                return
            self.expenseRatios.create(expense=value)
        except (HoldingExpenseRatio.DoesNotExist):
            self.expenseRatios.create(expense=value)

    def updateReturns(self):
        """
        Gets the most recent returns for this holding from Morningstar. If they
        don't match, creates a new HoldingReturns with the most recent info.
        """
        ident = self.getIdentifier()
        data = ms.getAssetReturns(ident[0], ident[1])
        try:
            ret1 = float(data['Return1Yr'])
        except KeyError:
            ret1 = 0.0
        try:
            ret2 = float(data['Return2Yr'])
        except KeyError:
            ret2 = 0.0
        try:
            ret3 = float(data['Return3Yr'])
        except KeyError:
            ret3 = 0.0
        try:
            ret1mo = float(data['Return1Mth'])
        except KeyError:
            ret1mo = 0.0
        try:
            ret3mo = float(data['Return3Mth'])
        except KeyError:
            ret3mo = 0.0
        try:
            mostRecRets = self.returns.latest('createdAt')
            if(np.isclose(ret1, mostRecRets.oneYearReturns)
               and np.isclose(ret2, mostRecRets.twoYearReturns)
               and np.isclose(ret3, mostRecRets.threeYearReturns)
               and np.isclose(ret1mo, mostRecRets.oneMonthReturns)
               and np.isclose(ret3mo, mostRecRets.threeMonthReturns)):
                return
        except(HoldingReturns.DoesNotExist):
            pass
        self.returns.create(oneYearReturns=ret1,
                            twoYearReturns=ret2,
                            threeYearReturns=ret3,
                            oneMonthReturns=ret1mo,
                            threeMonthReturns=ret3mo)

    def _updateGenericBreakdown(self, modelType, nameDict):
        ident = self.getIdentifier()

        if modelType == "assetBreakdowns":
            data = ms.getAssetAllocation(ident[0], ident[1])
            form = HoldingAssetBreakdown
        elif modelType == "equityBreakdowns":
            data = ms.getEquityBreakdown(ident[0], ident[1])
            form = HoldingEquityBreakdown
        elif modelType == "bondBreakdowns":
            data = ms.getBondBreakdown(ident[0], ident[1])
            form = HoldingBondBreakdown
        else:
            raise ValueError("The input {0} wasn't one of the approved types!"
                             "\n(assetBreakdowns, equityBreakdowns, or bondBreakdowns".format(modelType))
        shouldUpdate = False
        try:
            current = getattr(self, modelType).filter(updateIndex__exact=self.currentUpdateIndex)
            if modelType == "assetBreakdowns":
                current = dict([(item.asset, item.percentage) for item in current])
            else:
                current = dict([(item.category, item.percentage) for item in current])
        except (HoldingAssetBreakdown.DoesNotExist, HoldingEquityBreakdown.DoesNotExist,
                HoldingBondBreakdown.DoesNotExist):
            shouldUpdate = True
            for asstype in nameDict.keys():
                try:
                    percentage = float(data[nameDict[asstype]])
                except KeyError:
                    percentage = 0.0
                if modelType == "assetBreakdowns":
                    form.objects.create(
                        asset=asstype,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.currentUpdateIndex + 1
                    )
                else:
                    form.objects.create(
                        category=asstype,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.currentUpdateIndex + 1
                    )
            return True

        if current:
            for item in current:
                try:
                    if not np.isclose(current[item], float(data[nameDict[item]])):
                        shouldUpdate = True
                        break
                except KeyError:
                    shouldUpdate = True
                    break
        else:
            shouldUpdate = True

        if shouldUpdate:
            for asstype in nameDict.keys():
                try:
                    percentage = float(data[nameDict[asstype]])
                except KeyError:
                    percentage = 0.0
                if modelType == "assetBreakdowns":
                    form.objects.create(
                        asset=asstype,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.currentUpdateIndex + 1
                    )
                else:
                    form.objects.create(
                        category=asstype,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.currentUpdateIndex + 1
                    )
            return True
        return False

    def _copyGenericBreakdown(self, modelType):
        if (modelType != "assetBreakdowns" and
            modelType != "equityBreakdowns" and
            modelType != "bondBreakdowns"):
                raise ValueError("The input {0} wasn't one of the approved types!"
                            "\n(assetBreakdowns, equityBreakdowns, or bondBreakdowns".format(modelType))
        current = getattr(self, modelType).filter(updateIndex__exact=self.currentUpdateIndex)
        for item in current:
            temp = item
            temp.updateIndex += 1
            temp.pk = None
            temp.save()

    def updateAllBreakdowns(self):
        assetBreakdownResponse = self._updateGenericBreakdown("assetBreakdowns",
                    {"StockLong": "AssetAllocEquityLong", "StockShort": "AssetAllocEquityShort",
                    "BondLong": "AssetAllocBondLong", "BondShort": "AssetAllocBondShort",
                    "CashLong": "AssetAllocCashLong", "CashShort": "AssetAllocCashShort",
                    "OtherLong": "OtherLong", "OtherShort": "OtherShort"})

        bondBreakdownResponse = self._updateGenericBreakdown("bondBreakdowns",
                    {"Government": "SuperSectorGovernment", "Municipal": "SuperSectorMunicipal",
                     "Corporate": "SuperSectorCorporate", "Securitized": "SuperSectorSecuritized",
                     "Cash": "SuperSectorCash"})

        equityBreakdownResponse = self._updateGenericBreakdown("equityBreakdowns",
                    {"Materials": "BasicMaterials", "ConsumerCyclic" : "ConsumerCyclical",
                     "Financial" : "FinancialServices", "RealEstate": "RealEstate",
                     "ConsumerDefense": "ConsumerDefensive", "Healthcare" : "HealthCare",
                     "Utilities": "Utilities", "Communication": "CommunicationServices",
                     "Energy": "Energy", "Industrials": "Industrials", "Technology": "Technology"})

        if(not assetBreakdownResponse and not bondBreakdownResponse and not equityBreakdownResponse):
            return

        if(not assetBreakdownResponse):
            self._copyGenericBreakdown("assetBreakdowns")
        if(not bondBreakdownResponse):
            self._copyGenericBreakdown("bondBreakdowns")
        if(not equityBreakdownResponse):
            self._copyGenericBreakdown("equityBreakdowns")

        self.currentUpdateIndex += 1
        self.save()


    def updateBreakdown(self):
        """
        Gets the most recent Asset Breakdown for this fund from Morningstar, if they
        don't match, creates a new set of HoldingAssetBreakdowns with the most recent
        breakdown.
        """
        ident = self.getIdentifier()
        data = ms.getAssetAllocation(ident[0], ident[1])
        shouldUpdate = False
        nameDict = {"StockLong": "AssetAllocEquityLong", "StockShort": "AssetAllocEquityShort",
                    "BondLong": "AssetAllocBondLong", "BondShort": "AssetAllocBondShort",
                    "CashLong": "AssetAllocCashLong", "CashShort": "AssetAllocCashShort",
                    "OtherLong": "OtherLong", "OtherShort": "OtherShort"}
        try:
            current = self.assetBreakdowns.filter(updateIndex__exact=self.currentUpdateIndex)
            current = dict([(item.asset, item.percentage) for item in current])
        except HoldingAssetBreakdown.DoesNotExist:
            self.currentUpdateIndex += 1
            for asstype in ["StockLong", "StockShort", "BondLong", "BondShort",
                            "CashLong", "CashShort", "OtherLong", "OtherShort"]:
                try:
                    percentage = float(data[nameDict[asstype]])
                except KeyError:
                    percentage = 0.0

                HoldingAssetBreakdown.objects.create(
                    asset=asstype,
                    percentage=percentage,
                    holding=self,
                    updateIndex=self.currentUpdateIndex
                )
            self.save()
            return
        if current:
            for item in current:
                try:
                    if not np.isclose(current[item], float(data[nameDict[item]])):
                        shouldUpdate = True
                except KeyError:
                    shouldUpdate = True
        else:
            shouldUpdate = True

        if shouldUpdate:
            self.currentUpdateIndex += 1
            for asstype in ["StockLong", "StockShort", "BondLong", "BondShort",
                            "CashLong", "CashShort", "OtherLong", "OtherShort"]:
                try:
                    percentage = float(data[nameDict[asstype]])
                except KeyError:
                    percentage = 0.0

                HoldingAssetBreakdown.objects.create(
                    asset=asstype,
                    percentage=percentage,
                    holding=self,
                    updateIndex=self.currentUpdateIndex
                )
            self.save()


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
    quovoCusip = models.CharField(max_length=20, null=True, blank=True)
    quovoTicker = models.CharField(max_length=20, null=True, blank=True)

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
    quovoCusip = models.CharField(max_length=20, null=True, blank=True)
    quovoTicker = models.CharField(max_length=20, null=True, blank=True)

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
    be created for A, B, and C with an index of 1. After the portfolio's
    next change, HistoricalHoldings will be created for A and B with
    an index of 2. This process continues for every change.
    """
    holding = models.ForeignKey('Holding')
    quovoUser = models.ForeignKey('dashboard.QuovoUser', related_name="userHistoricalHoldings")
    value = models.FloatField()
    quantity = models.FloatField()
    archivedAt = models.DateTimeField()
    portfolioIndex = models.PositiveIntegerField()
    quovoCusip = models.CharField(max_length=20, null=True, blank=True)
    quovoTicker = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "UserHistoricalHolding"
        verbose_name_plural = "UserHistoricalHoldings"

    def __str__(self):
        return "%s: %s" % (self.quovoUser, self.holding)


class HoldingPrice(models.Model):
    """
    This model represents the closing price of a holding
    on a given day. Note that this is market price if the item is not
    NAV valued, and its NAV on that day if it is.
    """
    price = models.FloatField()
    holding = models.ForeignKey('Holding', related_name="holdingPrices")
    closingDate = models.DateField()

    class Meta:
        verbose_name = "HoldingPrice"
        verbose_name_plural = "HoldingPrices"
        unique_together = ("holding", "closingDate")

    def __str__(self):
        return "%s: %f - %s" % (self.holding, self.price, self.closingDate)


class HoldingExpenseRatio(models.Model):
    """
    The net expense ratio of a fund or security, assuming it has one.
    """
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
    holding = models.ForeignKey("Holding", related_name="assetBreakdowns")
    createdAt = models.DateField(auto_now_add=True)
    updateIndex = models.PositiveIntegerField()

    class Meta:
        verbose_name = "HoldingAssetBreakdown"
        verbose_name_plural = "HoldingAssetBreakdowns"

    def __str__(self):
        return "%s: %s - %s" % (self.holding, self.asset, self.createdAt)


class HoldingEquityBreakdown(models.Model):
    category = models.CharField(max_length=30)
    percentage = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="equityBreakdowns")
    createdAt = models.DateField(auto_now_add=True)
    updateIndex = models.PositiveIntegerField()

    class Meta:
        verbose_name = "HoldingEquityBreakdown"
        verbose_name_plural = "HoldingEquityBreakdowns"

    def __str__(self):
        return "%s: %s - %s" % (self.holding, self.category, self.createdAt)


class HoldingBondBreakdown(models.Model):
    category = models.CharField(max_length=30)
    percentage = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="bondBreakdowns")
    createdAt = models.DateField(auto_now_add=True)
    updateIndex = models.PositiveIntegerField()

    class Meta:
        verbose_name = "HoldingBondBreakdown"
        verbose_name_plural = "HoldingBondBreakdowns"

    def __str__(self):
        return "%s: %s - %s" % (self.holding, self.category, self.createdAt)


class HoldingReturns(models.Model):
    """
    This model represents the one year, two year, and three year
    returns for any single holding, according to Morningstar.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    oneYearReturns = models.FloatField()
    twoYearReturns = models.FloatField()
    threeYearReturns = models.FloatField()
    oneMonthReturns = models.FloatField()
    threeMonthReturns = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="returns")

    class Meta:
        verbose_name = "HoldingReturn"
        verbose_name_plural = "HoldingReturns"


class UserReturns(models.Model):
    """
    This model represents the responses for the UserReturns module. It
    contains five float fields, each corresponding to the returns from some
    period ago to today.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    oneYearReturns = models.FloatField()
    twoYearReturns = models.FloatField()
    threeYearReturns = models.FloatField()
    oneMonthReturns = models.FloatField()
    threeMonthReturns = models.FloatField()
    quovoUser = models.ForeignKey("dashboard.QuovoUser", related_name="userReturns")

    class Meta:
        verbose_name = "UserReturn"
        verbose_name_plural = "UserReturns"

    def __str__(self):
        up = self.quovoUser.userProfile
        return up.firstName + " " + up.lastName + ": " + str(self.createdAt)


class UserSharpe(models.Model):
    """
    This model represents the responses for the riskReturnProfile module.
    It contains the sharpe ratio of a user's portfolio on a given day.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    quovoUser = models.ForeignKey("dashboard.QuovoUser", related_name="userSharpes")

    class Meta:
        verbose_name = "UserSharpe"
        verbose_name_plural = "UserSharpes"

    def __str__(self):
        up = self.quovoUser.userProfile
        return up.firstName + " " + up.lastName + ": " + str(self.createdAt)


class AverageUserReturns(models.Model):
    """
    This model represents the average of many UserReturns accounts in a given day.
    Note that on each day, there should be seven of these, one for each age group.
    Age groups are coded in the following way:
    20 : 20-25
    30 : 26-35
    40 : 36-45
    n  : n-4 - n+5
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    ageGroup = models.PositiveSmallIntegerField()
    oneYearReturns = models.FloatField()
    twoYearReturns = models.FloatField()
    threeYearReturns = models.FloatField()
    oneMonthReturns = models.FloatField()
    threeMonthReturns = models.FloatField()

    class Meta:
        verbose_name = "AverageUserReturn"
        verbose_name_plural = "AverageUserReturns"

    def __str__(self):
        return "Avg User Returns on " + str(self.createdAt.date())


class AverageUserSharpe(models.Model):
    """
    This model represents the average of many user Sharpe Ratios in a given day.
    There should be eight of these each day, following a similar age group construction
    as detailed above.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    ageGroup = models.PositiveSmallIntegerField()
    mean = models.FloatField(null=True)
    std = models.FloatField(null=True)

    class Meta:
        verbose_name = "AverageUserSharpe"
        verbose_name_plural = "AverageUserSharpes"

    def __str__(self):
        return "Avg User Sharpes on " + str(self.createdAt.date())



