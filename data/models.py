from django.db import models
from datetime import timedelta
from django.utils.datetime_safe import datetime as dj_datetime
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from Vestivise.morningstar import Morningstar as ms, Morningstar
import copy
from Vestivise.Vestivise import UnidentifiedHoldingException
import dateutil.parser
from dateutil.relativedelta import relativedelta
import numpy as np
from Vestivise import mailchimp
import logging

nplog = logging.getLogger('nightly_process')

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
    ticker_name = models.CharField(max_length=150, null=True, blank=True)
    tran_category = models.CharField(max_length=50, null=True, blank=True)
    # https://api.quovo.com/docs/agg/#transaction-types
    tran_type = models.CharField(max_length=50, null=True, blank=True)
    memo = models.TextField(blank=True, null=True)
    account = models.ForeignKey("Account", related_name="accountTransaction", to_field="quovoID", null=True, blank=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return "{0}: {1} {2}".format(self.quovoUser, self.tran_type, self.date)

    def get_full_transaction_name(self):
        map = {
            'B': 'Buy',
            'S': 'Sell',
            'T': 'Transfer',
            'I': 'Dividends/Interest/Fees',
            'C': 'Cash'
        }
        return map.get(self.tran_category)


class HoldingJoin(models.Model):
    parentHolding = models.ForeignKey("Holding", related_name="childJoiner")
    childHolding = models.ForeignKey("Holding", related_name="parentJoiner")
    compositePercent = models.FloatField()

    class Meta:
        verbose_name = "HoldingJoin"
        verbose_name_plural = "HoldingJoins"

    def __str__(self):
        return "%s: %s" % (self.parentHolding, self.childHolding)


class Holding(models.Model):
    """
    Various categorizations:
    MUTF - Mutual Fund
    CASH - Cash
    STOC - Stock/Equity
    FOFF - Fund of Funds.
    BOND - Bond
    """
    secname = models.CharField(max_length=200, null=True, blank=True, unique=True)
    cusip = models.CharField(max_length=9, null=True, blank=True)
    ticker = models.CharField(max_length=5, null=True, blank=True)
    mstarid = models.CharField(max_length=15, null=True, blank=True)
    updatedAt = models.DateTimeField(null=True, blank=True)
    currentUpdateIndex = models.PositiveIntegerField(default=0)
    sector = models.CharField(max_length=22, null=True, blank=True, default="")
    MUTUAL_FUND = "MUTF"
    CASH = "CASH"
    STOCK = "STOC" #Also stands for Equity
    FUND_OF_FUNDS = "FOFF"
    IGNORE = "IGNO" #Also stands for unidentifiable.
    BOND = "BOND"

    CATEGORY_CHOICES = (
        (MUTUAL_FUND, "Mutual Fund"),
        (CASH, "Cash"),
        (STOCK, "Stock"),
        (FUND_OF_FUNDS, "Fund of Funds"),
        (IGNORE, "Should Ignore"),
        (BOND, "Bond")
    )
    category = models.CharField(
        max_length=4,
        choices=CATEGORY_CHOICES,
        default="IGNO"
    )

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
            if (posDict["cusip"] is not None and posDict["cusip"] != ""):
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

        secDict = {"Basic Materials": "Materials", "Consumer Cyclical": "ConsumerCyclic",
                 "Financial Services": "Financial", "Real Estate": "RealEstate",
                 "Consumer Defensive": "ConsumerDefense", "Healthcare": "Healthcare",
                 "Utilities": "Utilities", "Communication Services": "Communication",
                 "Energy": "Energy", "Industrials": "Industrials", "Technology": "Technology",
                 "Congolmerates": "Conglomerates", "Consumer Goods": "ConsumerDefense",
                 "Services": "Services", "Other": "Other"}

        st_map = {
            "Bond": "BOND",
            "Cash": "CASH",
            "Closed-End Fund": "MUTF",
            "Equity": "STOC",
            "ETF": "MUTF",
            "Foreign Equity": "STOC",
            "Hedge Fund": "MUTF",
            "Index": "MUTF",
            "Mutual Fund": "MUTF",
            "Other Equity": "STOC",
            "Preferred Stock" : "STOC"
        }
        qst = posDict["security_type"]

        st = st_map.get(qst, "IGNO")

        ticker = posDict["ticker"]

        if posDict.get("proxy_ticker") and posDict.get("proxy_confidence") > 0.95:
            ticker = posDict.get("proxy_ticker")

        startDate = dj_datetime.now() - timedelta(weeks=1)

        res = None

        try:
            if st == "BOND":
                pass
            elif st == "MUTF":
                res = Morningstar.getHistoricalNAV(ticker, "ticker", startDate, dj_datetime.now())
            elif st == "STOC":
                res = Morningstar.getHistoricalMarketPrice(ticker, "ticker", startDate, dj_datetime.now())
            if not res:
                ticker = None
        except:
            ticker = None
        sector = posDict.get('sector', 'Other') if posDict.get('sector', "Other") is not None else "Other"
        internal_sector = secDict[sector]
        return Holding.objects.create(
            secname=posDict["ticker_name"],
            cusip=posDict["cusip"],
            ticker=ticker,
            category=st,
            sector=internal_sector
        )

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
        if self.ticker is not None and self.ticker != "":
            return (self.ticker, 'ticker')
        elif self.cusip is not None and self.cusip != "":
            return (self.cusip, 'cusip')
        elif self.mstarid is not None and self.mstarid != "":
            return (self.mstarid, 'mstarid')
        else:
            raise UnidentifiedHoldingException("Holding id: {0}, secname: {1}, is unidentified!".format(
                self.id, self.secname
            ))

    def isIdentified(self):
        """
        Returns True if the holding is identified - cusip is filled or ric
        :return: Boolean if the holding is identified
        """
        return (self.ticker != "" and self.ticker is not None) or \
               (self.cusip != "" and self.cusip is not None) or \
               (self.mstarid != "" and self.mstarid is not None) or \
               (self.category == "FOFF") or \
               (self.category == "CASH")

    def isCompleted(self):
        """
        Returns True if the holding is completed - has asset breakdown and holding price and expense ratio
        :return: Boolean if the holding is completed
        """
        if self.category == "MUTF":
            return hasattr(self, 'assetBreakdowns') and self.assetBreakdowns.exists()\
                and hasattr(self, 'holdingPrices') and self.holdingPrices.exists()\
                and hasattr(self, 'expenseRatios') and self.expenseRatios.exists()\
                and hasattr(self, 'returns') and self.returns.exists()

        elif self.category == "STOC":
            return hasattr(self, 'assetBreakdowns') and self.assetBreakdowns.exists()\
                and hasattr(self, 'holdingPrices') and self.holdingPrices.exists()\
                and hasattr(self, 'expenseRatios') and self.expenseRatios.exists()\
                and hasattr(self, 'returns') and self.returns.exists()

        elif self.category == "CASH":
            return hasattr(self, 'assetBreakdowns') and self.assetBreakdowns.exists()\
                and hasattr(self, 'expenseRatios') and self.expenseRatios.exists()\
                and hasattr(self, 'returns') and self.returns.exists()

    def createPrices(self, timeStart, timeEnd):
        """
        Creates HoldingPrice objects associated with each available day in the
        the provided timespan, including the timeStart and the timeEnd if they are available.
        :param timeStart: The beginning time from which data will be collected.
        :param timeEnd: The findal day from which data will be collected.
        """
        ident = self.getIdentifier()
        if self.category == "MUTF":
            data = ms.getHistoricalNAV(ident[0], ident[1], timeStart, timeEnd)
            for item in data:
                day = dateutil.parser.parse(item['d']).date()
                try:
                    price = float(item['v'])
                    self.holdingPrices.create(price=price, closingDate=day)
                except (ValidationError, IntegrityError):
                    pass
        elif self.category == "STOC":
            data = ms.getHistoricalMarketPrice(ident[0], ident[1], timeStart, timeEnd)
            for item in data:
                day = dateutil.parser.parse(item['Date']).date()
                try:
                    price = float(item['ClosePrice'])
                    self.holdingPrices.create(price=price, closingDate=day)
                except (ValidationError, IntegrityError):
                    pass


    def fillPrices(self):
        """
        If the Holding is new, fills all of its price fields for
        the past three years. Otherwise, fills all price fields since
        its last update till now.
        """
        if(self.category not in ['MUTF', 'STOC']):
            return
        if (self.updatedAt is None or
                not self.holdingPrices.exists() or
                    self.holdingPrices.latest('closingDate').closingDate < (
                    dj_datetime.now() - timedelta(weeks=3 * 52 + 6)).date()):

            startDate = dj_datetime.now() - timedelta(weeks=3 * 52 + 6)
        else:
            startDate = self.holdingPrices.latest('closingDate').closingDate - timedelta(days=1)
        self.createPrices(startDate, dj_datetime.now())

    def updateExpenses(self):
        """
        Gets the most recent Expense Ratio for this fund from Morningstar, if they
        don't match, creates a new HoldingExpenseRatio with the most recent ratio.
        """
        if(self.category == 'MUTF'):
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
        else:
            try:
                self.expenseRatios.latest('createdAt')
            except HoldingExpenseRatio.DoesNotExist:
                self.expenseRatios.create(
                    expense=0.0
                )

    def updateReturns(self):
        """
        Gets the most recent returns for this holding from Morningstar. If they
        don't match, creates a new HoldingReturns with the most recent info.
        """
        if self.category == "MUTF" or self.category == "STOC":
            begin = dj_datetime.now().replace(day=1, month=1)
            now = dj_datetime.now()
            yeartodate = self.getReturnsInPeriod(begin, now)*100
            now = now.replace(day=1)
            ret1mo = self.getReturnsInPeriod(now - relativedelta(months=1), now)*100
            ret3mo = self.getReturnsInPeriod(now - relativedelta(months=3), now)*100
            now = now.replace(month=1)
            ret1ye = self.getReturnsInPeriod(now - relativedelta(years=1), now)*100
            ret2ye = self.getReturnsInPeriod(now - relativedelta(years=2), now - relativedelta(years=1))*100
            ret3ye = self.getReturnsInPeriod(now - relativedelta(years=3), now - relativedelta(years=2))*100

            try:
                mostRecRets = self.returns.latest('createdAt')
                if (np.isclose(ret1ye, mostRecRets.oneYearReturns)
                    and np.isclose(ret2ye, mostRecRets.twoYearReturns)
                    and np.isclose(ret3ye, mostRecRets.threeYearReturns)
                    and np.isclose(ret1mo, mostRecRets.oneMonthReturns)
                    and np.isclose(ret3mo, mostRecRets.threeMonthReturns)
                    and np.isclose(yeartodate, mostRecRets.yearToDate)):
                    return
            except HoldingReturns.DoesNotExist:
                pass
            self.returns.create(oneYearReturns=ret1ye,
                                twoYearReturns=ret2ye,
                                threeYearReturns=ret3ye,
                                oneMonthReturns=ret1mo,
                                threeMonthReturns=ret3mo,
                                yearToDate=yeartodate)
        else:
            try:
                self.returns.latest('createdAt')
            except HoldingReturns.DoesNotExist :
                self.returns.create(
                    oneMonthReturns=0.0,
                    threeMonthReturns=0.0,
                    oneYearReturns=0.0,
                    twoYearReturns=0.0,
                    threeYearReturns=0.0,
                    yearToDate=0.0
                )

    def getReturnsInPeriod(self, startDate, endDate):
        """
        Determines the returns in a period of time for this specific holding.
        :param: startDate: Date to start determining returns.
        :param: endDate: Date to stop determining returns.
        :return: Float of returns in that period.
        """
        if(self.category == 'MUTF' or self.category == 'STOC'):
            try:
                end_val = self.holdingPrices.filter(closingDate__lte=endDate).latest('closingDate')
                end_val = end_val.price
                begin_val = self.holdingPrices.filter(closingDate__lte=startDate).latest('closingDate')
                begin_val = begin_val.price
                for x in self.dividends.filter(date__gte=startDate, date__lte=endDate):
                    end_val += x.value
                return (end_val - begin_val)/begin_val
            except HoldingPrice.DoesNotExist:
                return 0.0
        # TODO : HANDLE BOND POSITIONS AND MAYBE CASH POSITIONS
        return 0.0

    def updateDividends(self):
        """
        Obtains the dividends for the security, and ensures that they're filled
        up to three years ago from the present date.
        """
        if self.category == "MUTF":
            try:
                start = self.dividends.latest('date').date + relativedelta(days=1)
            except HoldingDividends.DoesNotExist:
                start = dj_datetime.now().date() - relativedelta(years=3)
            if (start < dj_datetime.now().date() - relativedelta(years=3)):
                start = dj_datetime.now().date() - relativedelta(years=3)
            end = dj_datetime.now().date()

            ident = self.getIdentifier()

            dividends = ms.getHistoricalDistributions(ident[0], ident[1], start, end)

            if dividends.get("DividendDetail"):
                for d in dividends['DividendDetail']:
                    try:
                        self.dividends.create(
                            date=dateutil.parser.parse(d['ExcludingDate']),
                            value=d['TotalDividend']
                        )
                    except KeyError:
                        nplog.error("Could not update dividend on holding pk: ", self.pk, " had following values: ", str(d))
            if dividends.get('CapitalGainDetail'):
                for d in dividends.get('CapitalGainDetail'):
                    try:
                        self.dividends.create(
                            date=dateutil.parser.parse(d['ExcludingDate']),
                            value=d['TotalCapitalGain']
                        )
                    except KeyError:
                        nplog.error("Could not update dividend on holding pk: ", self.pk, " had following values: ", str(d))

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
                if item in data:
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
        if(self.category == "MUTF"):
            assetBreakdownResponse = self._updateGenericBreakdown("assetBreakdowns",
                {"StockLong": "AssetAllocEquityLong", "StockShort": "AssetAllocEquityShort",
                 "BondLong": "AssetAllocBondLong", "BondShort": "AssetAllocBondShort",
                 "CashLong": "AssetAllocCashLong", "CashShort": "AssetAllocCashShort",
                 "OtherLong": "OtherLong", "OtherShort": "OtherShort"})

            bondBreakdownResponse = self._updateGenericBreakdown("bondBreakdowns",
                {"Government": "SuperSectorGovernment", "Municipal": "SuperSectorMunicipal",
                 "Corporate": "SuperSectorCorporate", "Securitized": "SuperSectorSecuritized",
                 "Cash": "SuperSectorCash", "Derivatives": "SuperSectorDerivative"})

            equityBreakdownResponse = self._updateGenericBreakdown("equityBreakdowns",
                {"Materials": "BasicMaterials", "ConsumerCyclic": "ConsumerCyclical",
                 "Financial": "FinancialServices", "RealEstate": "RealEstate",
                 "ConsumerDefense": "ConsumerDefensive", "Healthcare": "Healthcare",
                 "Utilities": "Utilities", "Communication": "CommunicationServices",
                 "Energy": "Energy", "Industrials": "Industrials", "Technology": "Technology"})

            if (not assetBreakdownResponse and not bondBreakdownResponse and not equityBreakdownResponse):
                return

            if (not assetBreakdownResponse):
                self._copyGenericBreakdown("assetBreakdowns")
            if (not bondBreakdownResponse):
                self._copyGenericBreakdown("bondBreakdowns")
            if (not equityBreakdownResponse):
                self._copyGenericBreakdown("equityBreakdowns")

            self.currentUpdateIndex += 1
            self.save()
        elif(self.category == "STOC"):
            try:
                self.assetBreakdowns.latest('createdAt')
            except HoldingAssetBreakdown.DoesNotExist:
                self.assetBreakdowns.create(
                    asset="StockLong",
                    percentage=100,
                    updateIndex=0
                )
            try:
                self.equityBreakdowns.latest('createdAt')
            except HoldingEquityBreakdown.DoesNotExist:
                self.equityBreakdowns.create(
                    category=self.sector if self.sector is not None else "Other",
                    percentage=100,
                    updateIndex=0
                )
        elif(self.category == "CASH"):
            try:
                self.assetBreakdowns.latest('createdAt')
            except HoldingAssetBreakdown.DoesNotExist:
                self.assetBreakdowns.create(
                    asset="CashLong",
                    percentage=100,
                    updateIndex=0
                )


    #TODO : TINKER WITH THIS
    def getMonthlyReturns(self, startDate, endDate):
        """
        Returns an array of returns made in each month, including the month of the
        start date, and the month of the end date. If not enough data is available for
        either month, throws an exception.
        :param startDate: Beginning date of the returns. Datetime.date object.
        :param endDate: Ending date of the returns. Datetime.date object.
        :return: Array of returns corresponding to each month.
        """
        endDate = (endDate + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        values = []
        toadd = [0]
        dateIter = copy.deepcopy(startDate).replace(day=1) - relativedelta(days=1)
        try:
            values.append(self.holdingPrices.filter(closingDate__lte=dateIter).order_by('-closingDate')[0].price)
            while(dateIter <= endDate):
                dateIter = (dateIter + relativedelta(months=2)).replace(day=1) - relativedelta(days=1)
                val = self.holdingPrices.filter(closingDate__lte=dateIter).order_by('-closingDate')[0].price
                divThisMonth = 0
                for divid in self.dividends.filter(date__lte=dateIter, date__gte=dateIter.replace(day=1)):
                    divThisMonth += divid.value
                values.append(val)
                toadd.append(divThisMonth)
        except (IndexError, HoldingPrice.DoesNotExist, HoldingDividends.DoesNotExist) as e:
            return[(values[i] + toadd[i] - values[i-1])/values[i-1] for i in range(1, len(values))]
        return [(values[i] + toadd[i] - values[i-1])/values[i-1] for i in range(1, len(values))]


class TreasuryBondValue(models.Model):
    """
    This represents the given rate of return of a 90 day treasury bond
    given on a certain day.
    """
    date = models.DateField()
    value = models.FloatField()

    class Meta:
        verbose_name = "TreasuryBondValue"
        verbose_name_plural = "TreasuryBondValues"

    def __str__(self):
        return "%s: %s rate" % (self.date, self.value)


class UserCurrentHolding(models.Model):
    """
    This model represents the user's current holdings, updated daily.
    This does not necessarily reflect the holdings presented on the
    user's dashboard, but are the most recent holdings collected from
    a call to the Quovo API.
    """
    holding = models.ForeignKey('Holding', related_name="currentHoldingChild")
    quovoUser = models.ForeignKey('dashboard.QuovoUser', related_name="userCurrentHoldings")
    value = models.FloatField()
    quantity = models.FloatField()
    quovoCusip = models.CharField(max_length=20, null=True, blank=True)
    quovoTicker = models.CharField(max_length=20, null=True, blank=True)
    account = models.ForeignKey("Account", related_name="accountCurrentHoldings", to_field="quovoID", null=True, blank=True)
    portfolio = models.ForeignKey("Portfolio", related_name="portfolioCurrentHoldings", to_field="quovoID", null=True, blank=True)

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
    holding = models.ForeignKey('Holding', related_name="displayHoldingChild")
    quovoUser = models.ForeignKey('dashboard.QuovoUser', related_name="userDisplayHoldings")
    value = models.FloatField()
    quantity = models.FloatField()
    quovoCusip = models.CharField(max_length=20, null=True, blank=True)
    quovoTicker = models.CharField(max_length=20, null=True, blank=True)
    account = models.ForeignKey("Account", related_name="accountDisplayHoldings", to_field="quovoID", null=True, blank=True)
    portfolio = models.ForeignKey("Portfolio", related_name="portfolioDisplayHoldings", to_field="quovoID", null=True, blank=True)

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
    account = models.ForeignKey("Account", related_name="accountHistoricalHoldings", to_field="quovoID", null=True, blank=True)
    portfolio = models.ForeignKey("Portfolio", related_name="portfolioHistoricalHoldings", to_field="quovoID", null=True, blank=True)

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
    yearToDate = models.FloatField()
    oneYearReturns = models.FloatField()
    twoYearReturns = models.FloatField()
    threeYearReturns = models.FloatField()
    oneMonthReturns = models.FloatField()
    threeMonthReturns = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="returns")

    class Meta:
        verbose_name = "HoldingReturn"
        verbose_name_plural = "HoldingReturns"

    def __str__(self):
        return "%s returns at %s" % (self.holding, self.createdAt)


class HoldingDividends(models.Model):
    """
    This model represents the dividends provided by a certain fund
    on a given day.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    value = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="dividends")

    class Meta:
        verbose_name = "HoldingDividend"
        verbose_name_plural = "HoldingDividends"


class AccountReturns(models.Model):
    """
    This model represents the returns made by some account corresponding to certain
    time intervals.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    yearToDate = models.FloatField()
    oneYearReturns = models.FloatField()
    twoYearReturns = models.FloatField()
    threeYearReturns = models.FloatField()
    oneMonthReturns = models.FloatField()
    threeMonthReturns = models.FloatField()
    account = models.OneToOneField("Account", related_name="accountReturns")

    class Meta:
        verbose_name = "AccountReturn"
        verbose_name_plural = "AccountReturns"

    def __str__(self):
        up = self.account.quovoUser.userProfile
        return "%s %s, acct %d" % (up.firstName, up.lastName, self.account.quovoID)


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

class UserBondEquity(models.Model):
    """
    This model represents the responses for the risk-age module.
    It contains the bond-equity breakdown of a user's portfolio on a given day.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    bond = models.FloatField()
    equity = models.FloatField()
    quovoUser = models.ForeignKey("dashboard.QuovoUser", related_name="userBondEquity")


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
    yearToDate = models.FloatField()
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



class AverageUserFee(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    avgFees = models.FloatField()

    class Meta:
        verbose_name = "AverageUserFees"
        verbose_name_plural = "AverageUserFees"

    def __str__(self):
        return "Avg User Fees on " + str(self.createdAt.date())

class AverageUserBondEquity(models.Model):
    """
    This model represents the average of many user Bond Equity breakdowns in a given day.
    There should be eight of these each day, following a similar age group construction
    as detailed above.
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    ageGroup = models.PositiveSmallIntegerField()
    bond = models.FloatField()
    equity = models.FloatField()

    class Meta:
        verbose_name = "AverageUserBondEquity"
        verbose_name_plural = "AverageUserBondEquities"

    def __str__(self):
        return "Avg User BondEquity on " + str(self.createdAt.date())


class Account(models.Model):
    quovoUser = models.ForeignKey("dashboard.QuovoUser", related_name="userAccounts")
    brokerage_name = models.CharField(blank=True, null=True, max_length=100)
    nickname = models.CharField(blank=True, null=True, max_length=100)
    quovoID = models.IntegerField(unique=True)
    # if user no longer has this account - we want to save the existence of this account
    # if the user relinks the account we can show the account because we have the past holding info
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return "%s %s" % (self.quovoUser, self.brokerage_name)

    def getAccountReturns(self):
        """
        Creates and returns the most recent instance of the account's AccountReturn
        model.
        """
        begin = dj_datetime.now().replace(day=1, month=1)
        now = datetime.now()
        yeartodate = self.getReturnsInPeriod(begin, now)
        now = now.replace(day=1)
        ret1mo = self.getReturnsInPeriod(now - relativedelta(months=1), now)
        ret3mo = self.getReturnsInPeriod(now - relativedelta(months=3), now)
        now = now.replace(month=1)
        ret1ye = self.getReturnsInPeriod(now - relativedelta(years=1), now)
        ret2ye = self.getReturnsInPeriod(now - relativedelta(years=2), now - relativedelta(years=1))
        ret3ye = self.getReturnsInPeriod(now - relativedelta(years=3), now - relativedelta(years=2))
        if not hasattr(self, 'accountReturns'):
            ar = AccountReturns(oneMonthReturns=ret1mo,
                                threeMonthReturns=ret3mo,
                                oneYearReturns=ret1ye,
                                twoYearReturns=ret2ye,
                                threeYearReturns=ret3ye,
                                yearToDate=yeartodate,
                                account=self)
            ar.save()
            return ar
        ar = self.accountReturns
        ar.oneMonthReturns = ret1mo
        ar.threeMonthReturns = ret3mo
        ar.oneYearReturns = ret1ye
        ar.twoYearReturns = ret2ye
        ar.threeYearReturns = ret3ye
        ar.yearToDate = yeartodate
        ar.save()
        return ar

    @staticmethod
    def _applyReverseTransaction(holds, transaction):
        """
        Private method intended only for use in getReturnsInPeriod
        Applies a transaction to a list of UserDisplayHoldings.
        :param holds: UserDisplayHoldings to be modified.
        :param transaction: Transaction to be applied.
        """
        if(len(holds)) == 0: return
        for i in range(len(holds)):
            hold = holds[i].holding
            if hold.ticker == transaction.ticker or hold.cusip == transaction.cusip:
                if transaction.tran_category == "B":
                    holds[i].value += abs(transaction.value)
                if transaction.tran_category == "S":
                    holds[i].value -= abs(transaction.value)
                return
        newhold = None
        if transaction.ticker != "" and UserDisplayHolding.objects.filter(quovoTicker=transaction.ticker).exists():
            newhold = UserDisplayHolding.objects.filter(quovoTicker=transaction.ticker)[0].holding
        elif transaction.ticker != "" and Holding.objects.filter(ticker=transaction.ticker).exists():
            newhold = Holding.objects.filter(ticker=transaction.ticker)[0]
        elif transaction.cusip != "" and Holding.objects.filter(cusip=transaction.cusip).exists():
            newhold = Holding.objects.filter(cusip=transaction.cusip)[0]
        elif transaction.ticker_name != "" and Holding.objects.filter(secname__exact=transaction.ticker_name).exists():
            newhold = Holding.objects.filter(secname__exact=transaction.ticker_name)[0]
        if newhold is not None:
            if transaction.tran_category == "B":
                val = abs(transaction.value)
            elif transaction.tran_category == "S":
                val = -abs(transaction.value)
            else:
                return
            usr = holds[0].quovoUser
            temphold = UserDisplayHolding(holding=newhold,
                                          quovoUser=usr,
                                          value=val,
                                          quantity=0)
            holds.append(temphold)

    def getReturnsInPeriod(self, startDate, endDate):
        if type(startDate) is datetime or type(startDate) is dj_datetime:
            startDate = startDate.date()
        if type(endDate) is datetime or type(startDate) is dj_datetime:
            endDate = endDate.date()

        if self.accountTransaction.exists and self.accountTransaction.earliest('date').date > startDate:
            startDate = self.accountTransaction.earliest('date').date

        if endDate <= startDate:
            return 0.0

        return_product = 1.0
        # Set and end to the query at today.
        query_end = datetime.now().date()
        # Compile a list of the account's present holdings.
        # Then compile a weight vector.
        holds = list(self.accountDisplayHoldings.all())
        s = sum([x.value for x in holds])
        weight = [x.value/s for x in holds]

        # Strategy: Take the current portfolio, and attempt to reverse its performance.
        # Take each transaction. For each interval between each transaction, find the
        # returns of each asset. Reverse these returns on the value of the asset.
        # If this time interval falls within our startdate and enddate, then we
        # multiply a running product against the dot product of the weight vector along
        # a vector representing the returns of those assets in that period.
        for t in self.accountTransaction.filter(date__gte=startDate, date__lte=query_end).order_by('-date'):
            return_in_period = [x.holding.getReturnsInPeriod(t.date, query_end) for x in holds]
            for i in range(len(holds)):
                holds[i].value /= (1 + return_in_period[i])
            if t.date <= endDate <= query_end:
                ret_prime = [x.holding.getReturnsInPeriod(t.date, endDate) for x in holds]
                return_product *= (1 + np.dot(ret_prime, weight))
            elif startDate <= t.date <= endDate and startDate <= query_end <= endDate:
                return_product *= (1 + np.dot(return_in_period, weight))
            Account._applyReverseTransaction(holds, t)
            s = sum([x.value for x in holds])
            weight = [x.value/s for x in holds]
            query_end = t.date
        try:
            return_in_period = [x.holding.getReturnsInPeriod(startDate, t.date) for x in holds]
        except NameError:
            return_in_period = [x.holding.getReturnsInPeriod(startDate, endDate) for x in holds]
        return_product *= (1 + np.dot(weight, return_in_period))
        return (return_product - 1)*100


class Portfolio(models.Model):

    quovoUser = models.ForeignKey("dashboard.QuovoUser", related_name="userPortfolios")
    quovoID = models.IntegerField(unique=True)
    description = models.CharField(blank=True, null=True, max_length=100)
    is_taxable = models.BooleanField()
    nickname = models.CharField(blank=True, null=True, max_length=100)
    owner_type = models.CharField(blank=True, null=True, max_length=100)
    portfolio_name = models.CharField(blank=True, null=True, max_length=100)
    portfolio_type = models.CharField(blank=True, null=True, max_length=100)
    account = models.ForeignKey("Account", related_name="portfolios", to_field="quovoID")
    # if user no longer has this portfolio - we want to save the existence of this portfolio
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return "%s %s" % (self.quovoUser, self.portfolio_name)