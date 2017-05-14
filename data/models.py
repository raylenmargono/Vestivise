import re
import copy
import logging
import dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime

from django.db import models, IntegrityError
from django.utils.datetime_safe import datetime as dj_datetime
from django.core.exceptions import ValidationError
import numpy as np

from Vestivise.Vestivise import UnidentifiedHoldingException
from sources import mailchimp
from sources.morningstar import Morningstar

nplog = logging.getLogger('nightly_process')


class Transaction(models.Model):
    quovo_user = models.ForeignKey('dashboard.QuovoUser', related_name="user_transaction")
    quovo_id = models.IntegerField(unique=True)
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
    account = models.ForeignKey(
        "Account",
        related_name="account_transaction",
        to_field="quovo_id", null=True, blank=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return "{}: {} {}".format(self.quovo_user, self.tran_type, self.date)

    def get_full_transaction_name(self):
        transaction_map = {
            'B': 'Buy',
            'S': 'Sell',
            'T': 'Transfer',
            'I': 'Dividends/Interest/Fees',
            'C': 'Cash'
        }
        return transaction_map.get(self.tran_category)


class HoldingJoin(models.Model):
    parent_holding = models.ForeignKey("Holding", related_name="child_joiner")
    child_holding = models.ForeignKey("Holding", related_name="parent_joiner")
    composite_percent = models.FloatField()

    class Meta:
        verbose_name = "HoldingJoin"
        verbose_name_plural = "HoldingJoins"

    def __str__(self):
        return "{}: {}".format(self.parent_holding, self.child_holding)


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
    morning_star_id = models.CharField(max_length=15, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    current_update_index = models.PositiveIntegerField(default=0)
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
        if self.secname:
            return self.secname
        elif self.cusip:
            return self.cusip
        elif self.ticker:
            return self.ticker
        return ""


    @staticmethod
    def is_identified_holding(secname):
        return Holding.objects.filter(secname=secname).exists()


    @staticmethod
    def get_holding_by_position_dict(position_dict):
        """
        Queries Holdings by the security name, cusip, and
        ticker, organized in the format of a position from
        the Quovo API. If no such holding exists, it will create
        a new one using the information from this Json.
        :param position_dict: Position Dictionary to be used in query/creation
        :return: A reference to the desired Holding.
        """
        try:
            if position_dict["cusip"] is not None and position_dict["cusip"] != "":
                return Holding.objects.get(cusip=position_dict["cusip"])
        except (Holding.DoesNotExist, KeyError):
            pass
        try:
            return Holding.objects.get(secname=position_dict["ticker_name"])
        except (Holding.DoesNotExist, KeyError):
            pass
        try:
            mailchimp.alert_identify_holdings(position_dict["ticker_name"])
        except:
            pass

        security_dict = {
            "Basic Materials": "Materials", "Consumer Cyclical": "ConsumerCyclic",
            "Financial Services": "Financial", "Real Estate": "RealEstate",
            "Consumer Defensive": "ConsumerDefense", "Healthcare": "Healthcare",
            "Utilities": "Utilities", "Communication Services": "Communication",
            "Energy": "Energy", "Industrials": "Industrials", "Technology": "Technology",
            "Congolmerates": "Conglomerates", "Consumer Goods": "ConsumerDefense",
            "Services": "Services", "Other": "Other"
        }

        security_type_map = {
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
        quovo_security_type = position_dict["security_type"]
        ticker = position_dict["ticker"]

        ticker_special_case = re.match("FI:[A-Za-z]+-([A-Za-z]+)\/?", ticker)
        if ticker_special_case and len(ticker_special_case.groups()) > 0:
            ticker = ticker_special_case.groups()[0]

        if position_dict.get("proxy_ticker") and position_dict.get("proxy_confidence") > 0.95:
            ticker = position_dict.get("proxy_ticker")

        start_date = dj_datetime.now() - timedelta(weeks=1)

        res = None

        security_type = security_type_map.get(quovo_security_type, "IGNO")
        try:
            if security_type == "BOND":
                pass
            elif security_type == "MUTF":
                res = Morningstar.getHistoricalNAV(ticker, "ticker", start_date, dj_datetime.now())
            elif security_type == "STOC":
                res = Morningstar.getHistoricalMarketPrice(ticker, "ticker", start_date, dj_datetime.now())
            if not res:
                ticker = None
        except:
            ticker = None

        sector = position_dict.get('sector', 'Other') if position_dict.get('sector', "Other") is not None else "Other"
        internal_sector = security_dict[sector]
        return Holding.objects.create(
            secname=position_dict["ticker_name"],
            cusip=position_dict["cusip"],
            ticker=ticker,
            category=security_type,
            sector=internal_sector
        )

    @staticmethod
    def get_holding_by_secname(secname):
        """
        Queries Holdings by the security name, and returns its
        reference. If it doesn't exit, it will create a Holding
        with that secname, and return its reference.
        :param sname: Holding name to be queried.
        :return: Reference to the desired Holding.
        """
        try:
            return Holding.objects.get(secname=secname)
        except Holding.DoesNotExist:
            mailchimp.alert_identify_holdings(secname)
            return Holding.objects.create(secname=secname)

    def get_identifier(self):
        """
        Gets the identifier for the Holding for use in TR calls.
        If there is no proper identifier, returns a None type.
        :return: ( identifier, identifierType) or None.
        """
        if self.ticker is not None and self.ticker != "":
            return self.ticker, 'ticker'
        elif self.cusip is not None and self.cusip != "":
            return self.cusip, 'cusip'
        elif self.morning_star_id is not None and self.morning_star_id != "":
            return self.morning_star_id, 'mstarid'
        else:
            raise UnidentifiedHoldingException("Holding id: {}, secname: {}, is unidentified!".format(
                self.id, self.secname
            ))

    def is_identified(self):
        """
        Returns True if the holding is identified - cusip is filled or ric
        :return: Boolean if the holding is identified
        """
        return (self.ticker != "" and self.ticker is not None) or \
               (self.cusip != "" and self.cusip is not None) or \
               (self.morning_star_id != "" and self.morning_star_id is not None) or \
               (self.category == "FOFF") or \
               (self.category == "CASH")

    def is_completed(self):
        """
        Returns True if the holding is completed - has asset breakdown and holding price and expense ratio
        :return: Boolean if the holding is completed
        """
        if self.category == "MUTF":
            return hasattr(self, 'asset_breakdown') and self.asset_breakdown.exists()\
                and hasattr(self, 'holdingPrices') and self.holdingPrices.exists()\
                and hasattr(self, 'expense_ratios') and self.expense_ratios.exists()\
                and hasattr(self, 'returns') and self.returns.exists()

        elif self.category == "STOC":
            return hasattr(self, 'asset_breakdown') and self.asset_breakdown.exists()\
                and hasattr(self, 'holdingPrices') and self.holdingPrices.exists()\
                and hasattr(self, 'expense_ratios') and self.expense_ratios.exists()\
                and hasattr(self, 'returns') and self.returns.exists()

        elif self.category == "CASH":
            return hasattr(self, 'asset_breakdown') and self.asset_breakdown.exists()\
                and hasattr(self, 'expense_ratios') and self.expense_ratios.exists()\
                and hasattr(self, 'returns') and self.returns.exists()

        elif self.category == "FOFF":
            return hasattr(self, 'childJoiner') and self.childJoiner.exists()

    def create_prices(self, time_start, time_end):
        """
        Creates HoldingPrice objects associated with each available day in the
        the provided timespan, including the timeStart and the timeEnd if they are available.
        :param time_start: The beginning time from which data will be collected.
        :param time_end: The findal day from which data will be collected.
        """
        identifier = self.get_identifier()
        if self.category == "MUTF":
            data = Morningstar.get_historical_nav(identifier[0], identifier[1], time_start, time_end)
            for item in data:
                day = dateutil.parser.parse(item['d']).date()
                try:
                    price = float(item['v'])
                    self.holdingPrices.create(price=price, closingDate=day)
                except (ValidationError, IntegrityError):
                    pass
        elif self.category == "STOC":
            data = Morningstar.getHistoricalMarketPrice(identifier[0], identifier[1], time_start, time_end)
            for item in data:
                day = dateutil.parser.parse(item['Date']).date()
                try:
                    price = float(item['ClosePrice'])
                    self.holdingPrices.create(price=price, closingDate=day)
                except (ValidationError, IntegrityError):
                    pass

    def fill_prices(self):
        """
        If the Holding is new, fills all of its price fields for
        the past three years. Otherwise, fills all price fields since
        its last update till now.
        """
        if self.category not in ['MUTF', 'STOC']:
            return

        closing_date = self.holdingPrices.latest('closingDate').closingDate

        start_date = closing_date - timedelta(days=1)

        has_unfilled_prices = closing_date < (dj_datetime.now() - timedelta(weeks=3 * 52 + 6)).date()

        if self.updatedAt is None or not self.holdingPrices.exists() or has_unfilled_prices:
            start_date = dj_datetime.now() - timedelta(weeks=3 * 52 + 6)
        self.create_prices(start_date, dj_datetime.now())

    def update_expenses(self):
        """
        Gets the most recent Expense Ratio for this fund from Morningstar, if they
        don't match, creates a new HoldingExpenseRatio with the most recent ratio.
        """
        if self.category == 'MUTF':
            identifier = self.get_identifier()
            data = Morningstar.getProspectusFees(identifier[0], identifier[1])
            value = float(data['NetExpenseRatio'])
            try:
                recent_expense_value = self.expense_ratios.latest('createdAt').expense
                if np.isclose(recent_expense_value, value):
                    return
                self.expense_ratios.create(expense=value)
            except HoldingExpenseRatio.DoesNotExist:
                self.expense_ratios.create(expense=value)
        elif self.category == "FOFF":
            expense = [
                child_joiner.childHolding.expense_ratios.latest('createdAt').expense
                for child_joiner in self.child_joiner.all()
            ]
            weight = [child_joiner.compositePercent/100 for child_joiner in self.child_joiner.all()]
            self.expense_ratios.create(expense=np.dot(expense, weight))
        else:
            try:
                self.expense_ratios.latest('createdAt')
            except HoldingExpenseRatio.DoesNotExist:
                self.expense_ratios.create(
                    expense=0.0
                )

    def update_returns(self):
        """
        Gets the most recent returns for this holding from Morningstar. If they
        don't match, creates a new HoldingReturns with the most recent info.
        """
        if self.category == "MUTF" or self.category == "STOC":
            begin = dj_datetime.now().replace(day=1, month=1)
            now = dj_datetime.now()
            year_to_date = self.get_returns_in_period(begin, now) * 100
            now = now.replace(day=1)
            returns_1_month = self.get_returns_in_period(now - relativedelta(months=1), now) * 100
            returns_3_month = self.get_returns_in_period(now - relativedelta(months=3), now) * 100
            now = now.replace(month=1)
            returns_1_year = self.get_returns_in_period(now - relativedelta(years=1), now) * 100
            returns_2_year = self.get_returns_in_period(now - relativedelta(years=2), now - relativedelta(years=1)) * 100
            returns_3_year = self.get_returns_in_period(now - relativedelta(years=3), now - relativedelta(years=2)) * 100

            try:
                most_recent_returns = self.returns.latest('createdAt')
                if np.isclose(returns_1_year, most_recent_returns.oneYearReturns)\
                   and np.isclose(returns_2_year, most_recent_returns.twoYearReturns)\
                   and np.isclose(returns_3_year, most_recent_returns.threeYearReturns)\
                   and np.isclose(returns_1_month, most_recent_returns.oneMonthReturns)\
                   and np.isclose(returns_3_month, most_recent_returns.threeMonthReturns)\
                   and np.isclose(year_to_date, most_recent_returns.yearToDate):
                    return
            except HoldingReturns.DoesNotExist:
                pass
            self.returns.create(oneYearReturns=returns_1_year,
                                twoYearReturns=returns_2_year,
                                threeYearReturns=returns_3_year,
                                oneMonthReturns=returns_1_month,
                                threeMonthReturns=returns_3_month,
                                yearToDate=year_to_date)

        elif self.category == "FOFF":
            returns = {'oneYearReturns': 0, 'twoYearReturns': 0, 'threeYearReturns': 0, 'oneMonthReturns': 0, 'threeMonthReturns': 0, 'yearToDate': 0}
            for joint in self.childJoiner.all():
                child = joint.childHolding
                for key in returns:
                    returns[key] += getattr(child.returns.latest('createdAt'), key)*joint.compositePercent/100
            self.returns.create(oneYearReturns=returns['oneYearReturns'],
                                twoYearReturns=returns['twoYearReturns'],
                                threeYearReturns=returns['threeYearReturns'],
                                oneMonthReturns=returns['oneMonthReturns'],
                                threeMonthReturns=returns['threeMonthReturns'],
                                yearToDate=returns['yearToDate'])
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

    def get_returns_in_period(self, start_date, end_date):
        """
        Determines the returns in a period of time for this specific holding.
        :param: startDate: Date to start determining returns.
        :param: endDate: Date to stop determining returns.
        :return: Float of returns in that period.
        """
        if self.category == 'MUTF' or self.category == 'STOC':
            try:
                end_val = self.holdingPrices.filter(closingDate__lte=end_date).latest('closingDate')
                end_val = end_val.price
                begin_val = self.holdingPrices.filter(closingDate__lte=start_date).latest('closingDate')
                begin_val = begin_val.price
                for x in self.dividends.filter(date__gte=start_date, date__lte=end_date):
                    end_val += x.value
                return (end_val - begin_val)/begin_val
            except HoldingPrice.DoesNotExist:
                return 0.0
        # TODO : HANDLE BOND POSITIONS AND MAYBE CASH POSITIONS
        elif self.category == "FOFF":
            returns = [
                child_joiner.childHolding.get_returns_in_period(start_date, end_date)
                for child_joiner in self.child_joiner.all()
            ]
            weights = [child_joiner.compositePercent/100 for child_joiner in self.child_joiner.all()]
            return np.dot(returns, weights)
        return 0.0

    def update_dividends(self):
        """
        Obtains the dividends for the security, and ensures that they're filled
        up to three years ago from the present date.
        """
        if self.category == "MUTF":
            try:
                start = self.dividends.latest('date').date + relativedelta(days=1)
            except HoldingDividends.DoesNotExist:
                start = dj_datetime.now().date() - relativedelta(years=3)
            if start < dj_datetime.now().date() - relativedelta(years=3):
                start = dj_datetime.now().date() - relativedelta(years=3)
            end = dj_datetime.now().date()

            identifier = self.get_identifier()

            dividends = Morningstar.get_historical_distributions(identifier[0], identifier[1], start, end)

            if dividends.get("DividendDetail"):
                for dividend in dividends['DividendDetail']:
                    try:
                        self.dividends.create(
                            date=dateutil.parser.parse(dividend['ExcludingDate']),
                            value=dividend['TotalDividend']
                        )
                    except KeyError:
                        error_msg = "Could not update dividend on holding pk: {} had following values: {}"
                        nplog.error(error_msg.format(self.pk, str(dividend)))
            if dividends.get('CapitalGainDetail'):
                for dividend in dividends.get('CapitalGainDetail'):
                    try:
                        self.dividends.create(
                            date=dateutil.parser.parse(dividend['ExcludingDate']),
                            value=dividend['TotalCapitalGain']
                        )
                    except KeyError:
                        error_msg = "Could not update dividend on holding pk: {} had following values: {}"
                        nplog.error(error_msg.format(self.pk, str(dividend)))

    def _update_generic_breakdown(self, model_type, name_dict):
        identifier = self.get_identifier()
        if model_type == "asset_breakdown":
            data = Morningstar.getAssetAllocation(identifier[0], identifier[1])
            form = HoldingAssetBreakdown
        elif model_type == "equity_breakdown":
            data = Morningstar.getEquityBreakdown(identifier[0], identifier[1])
            form = HoldingEquityBreakdown
        elif model_type == "bond_breakdown":
            data = Morningstar.getBondBreakdown(identifier[0], identifier[1])
            form = HoldingBondBreakdown
        else:
            raise ValueError("The input {} wasn't one of the approved types!"
                             "\n(asset_breakdown, equity_breakdown, or bond_breakdown".format(model_type))
        should_update = False
        try:
            current = getattr(self, model_type).filter(updateIndex__exact=self.current_update_index)
            if model_type == "asset_breakdown":
                current = dict([(item.asset, item.percentage) for item in current])
            else:
                current = dict([(item.category, item.percentage) for item in current])
        except (HoldingAssetBreakdown.DoesNotExist, HoldingEquityBreakdown.DoesNotExist,
                HoldingBondBreakdown.DoesNotExist):

            should_update = True

            for asset_type in name_dict.keys():
                try:
                    percentage = float(data[name_dict[asset_type]])
                except KeyError:
                    percentage = 0.0
                if model_type == "asset_breakdown":
                    form.objects.create(
                        asset=asset_type,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.currentUpdateIndex + 1
                    )
                else:
                    form.objects.create(
                        category=asset_type,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.currentUpdateIndex + 1
                    )
            return True

        if current:
            for item in current:
                if item in data:
                    try:
                        if not np.isclose(current[item], float(data[name_dict[item]])):
                            should_update = True
                            break
                    except KeyError:
                        should_update = True
                        break
        else:
            should_update = True

        if should_update:
            for asset_type in name_dict.keys():
                try:
                    percentage = float(data[name_dict[asset_type]])
                except KeyError:
                    percentage = 0.0
                if model_type == "asset_breakdown":
                    form.objects.create(
                        asset=asset_type,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.current_update_index + 1
                    )
                else:
                    form.objects.create(
                        category=asset_type,
                        percentage=percentage,
                        holding=self,
                        updateIndex=self.current_update_index + 1
                    )
            return True
        return False

    def _copy_generic_breakdown(self, model_type):
        if model_type != "asset_breakdown" and \
           model_type != "equity_breakdown" and \
           model_type != "bond_breakdown":
            raise ValueError("The input {0} wasn't one of the approved types!"
                             "\n(asset_breakdown, equity_breakdown, or bond_breakdown".format(model_type))
        current = getattr(self, model_type).filter(updateIndex__exact=self.current_update_index)
        for item in current:
            item.updateIndex += 1
            item.pk = None
            item.save()

    def update_all_breakdowns(self):
        if self.category == "MUTF":
            asset_breakdown_response = self._update_generic_breakdown("asset_breakdown", {
                "StockLong": "AssetAllocEquityLong", 
                "StockShort": "AssetAllocEquityShort",
                "BondLong": "AssetAllocBondLong", 
                "BondShort": "AssetAllocBondShort",
                "CashLong": "AssetAllocCashLong", 
                "CashShort": "AssetAllocCashShort",
                "OtherLong": "OtherLong", 
                "OtherShort": "OtherShort"
            })

            bond_breakdown_response = self._update_generic_breakdown("bond_breakdown", {
                "Government": "SuperSectorGovernment", 
                "Municipal": "SuperSectorMunicipal",
                "Corporate": "SuperSectorCorporate", 
                "Securitized": "SuperSectorSecuritized",
                "Cash": "SuperSectorCash", 
                "Derivatives": "SuperSectorDerivative"
            })

            equity_breakdown_response = self._update_generic_breakdown("equity_breakdown", {
                "Materials": "BasicMaterials", 
                "ConsumerCyclic": "ConsumerCyclical",
                "Financial": "FinancialServices", 
                "RealEstate": "RealEstate",
                "ConsumerDefense": "ConsumerDefensive", 
                "Healthcare": "Healthcare",
                "Utilities": "Utilities", 
                "Communication": "CommunicationServices",
                "Energy": "Energy", 
                "Industrials": "Industrials", "Technology": "Technology"
            })

            if not asset_breakdown_response and not bond_breakdown_response and not equity_breakdown_response:
                return

            if not asset_breakdown_response:
                self._copy_generic_breakdown("asset_breakdown")
            if not bond_breakdown_response:
                self._copy_generic_breakdown("bond_breakdown")
            if not equity_breakdown_response:
                self._copy_generic_breakdown("equity_breakdown")

            self.currentUpdateIndex += 1
            self.save()

        elif self.category == "STOC":
            try:
                self.asset_breakdown.latest('created_at')
            except HoldingAssetBreakdown.DoesNotExist:
                self.asset_breakdown.create(
                    asset="StockLong",
                    percentage=100,
                    updateIndex=0
                )
            try:
                self.equity_breakdown.latest('created_at')
            except HoldingEquityBreakdown.DoesNotExist:
                self.equity_breakdown.create(
                    category=self.sector if self.sector is not None else "Other",
                    percentage=100,
                    updateIndex=0
                )
        elif self.category == "CASH":
            try:
                self.asset_breakdown.latest('createdAt')
            except HoldingAssetBreakdown.DoesNotExist:
                self.asset_breakdown.create(
                    asset="CashLong",
                    percentage=100,
                    updateIndex=0
                )


    #TODO : TINKER WITH THIS
    def get_monthly_returns(self, start_date, end_date):
        """
        Returns an array of returns made in each month, including the month of the
        start date, and the month of the end date. If not enough data is available for
        either month, throws an exception.
        :param start_date: Beginning date of the returns. Datetime.date object.
        :param end_date: Ending date of the returns. Datetime.date object.
        :return: Array of returns corresponding to each month.
        """
        adjusted_date_date = (end_date + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        values = []
        to_add = [0]
        date_iteration = copy.deepcopy(start_date).replace(day=1) - relativedelta(days=1)
        try:
            values.append(self.holdingPrices.filter(closingDate__lte=date_iteration).order_by('-closingDate')[0].price)
            while date_iteration <= adjusted_date_date:
                date_iteration = (date_iteration + relativedelta(months=2)).replace(day=1) - relativedelta(days=1)
                val = self.holdingPrices.filter(closingDate__lte=date_iteration).order_by('-closingDate')[0].price
                dividend_this_month = 0
                dividends = self.dividends.filter(date__lte=date_iteration, date__gte=date_iteration.replace(day=1))
                for dividend in dividends:
                    dividend_this_month += dividend.value
                values.append(val)
                to_add.append(dividend_this_month)
        except (IndexError, HoldingPrice.DoesNotExist, HoldingDividends.DoesNotExist):
            return[(values[i] + to_add[i] - values[i-1])/values[i-1] for i in range(1, len(values))]
        return [(values[i] + to_add[i] - values[i-1])/values[i-1] for i in range(1, len(values))]


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
        return "{}: {} rate".format(self.date, self.value)


class UserCurrentHolding(models.Model):
    """
    This model represents the user's current holdings, updated daily.
    This does not necessarily reflect the holdings presented on the
    user's dashboard, but are the most recent holdings collected from
    a call to the Quovo API.
    """
    holding = models.ForeignKey('Holding', related_name="current_holding_child")
    quovo_user = models.ForeignKey('dashboard.QuovoUser', related_name="user_current_holdings")
    value = models.FloatField()
    quantity = models.FloatField()
    quovo_cusip = models.CharField(max_length=20, null=True, blank=True)
    quovo_ticker = models.CharField(max_length=20, null=True, blank=True)
    account = models.ForeignKey("Account",
                                related_name="account_current_holdings",
                                to_field="quovo_id",
                                null=True,
                                blank=True)
    portfolio = models.ForeignKey("Portfolio",
                                  related_name="portfolio_current_holdings",
                                  to_field="quovo_id",
                                  null=True,
                                  blank=True)

    class Meta:
        verbose_name = "UserCurrentHolding"
        verbose_name_plural = "UserCurrentHoldings"

    def __str__(self):
        return "{}: {}".format(self.quovo_user, self.holding)


class UserDisplayHolding(models.Model):
    """
    This model represents the user's current holdings to be displayed
    on their dashboard. This is updated with the values of the UserCurrentHolding
    should all UserCurrentHoldings be identified.
    """
    holding = models.ForeignKey('Holding', related_name="displayHoldingChild")
    quovo_user = models.ForeignKey('dashboard.QuovoUser', related_name="userDisplayHoldings")
    value = models.FloatField()
    quantity = models.FloatField()
    quovo_cusip = models.CharField(max_length=20, null=True, blank=True)
    quovo_ticker = models.CharField(max_length=20, null=True, blank=True)
    account = models.ForeignKey("Account",
                                related_name="account_display_holdings",
                                to_field="quovo_id",
                                null=True,
                                blank=True)
    portfolio = models.ForeignKey("Portfolio",
                                  related_name="portfolio_display_holdings",
                                  to_field="quovo_id",
                                  null=True,
                                  blank=True)

    class Meta:
        verbose_name = "UserDisplayHolding"
        verbose_name_plural = "UserDisplayHoldings"

    def __str__(self):
        return "{}: {}".format(self.quovo_user, self.holding)


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
    quovo_user = models.ForeignKey('dashboard.QuovoUser', related_name="user_historical_holdings")
    value = models.FloatField()
    quantity = models.FloatField()
    archived_at = models.DateTimeField()
    portfolio_index = models.PositiveIntegerField()
    quovo_cusip = models.CharField(max_length=20, null=True, blank=True)
    quovo_ticker = models.CharField(max_length=20, null=True, blank=True)
    account = models.ForeignKey("Account",
                                related_name="account_historical_holdings",
                                to_field="quovo_id", null=True, blank=True)
    portfolio = models.ForeignKey("Portfolio",
                                  related_name="portfolio_historical_holdings",
                                  to_field="quovo_id", null=True, blank=True)

    class Meta:
        verbose_name = "UserHistoricalHolding"
        verbose_name_plural = "UserHistoricalHoldings"

    def __str__(self):
        return "{}: {}".format(self.quovo_user, self.holding)


class HoldingPrice(models.Model):
    """
    This model represents the closing price of a holding
    on a given day. Note that this is market price if the item is not
    NAV valued, and its NAV on that day if it is.
    """
    price = models.FloatField()
    holding = models.ForeignKey('Holding', related_name="holdingPrices")
    closing_date = models.DateField()

    class Meta:
        verbose_name = "HoldingPrice"
        verbose_name_plural = "HoldingPrices"
        unique_together = ("holding", "closing_date")

    def __str__(self):
        return "{}: {} - {}".format(self.holding, self.price, self.closing_date)


class HoldingExpenseRatio(models.Model):
    """
    The net expense ratio of a fund or security, assuming it has one.
    """
    expense = models.FloatField()
    holding = models.ForeignKey('Holding', related_name="expense_ratios")
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "HoldingExpenseRatio"
        verbose_name_plural = "HoldingExpenseRatios"

    def __str__(self):
        return "{}: {} - {}".format(self.holding, self.expense, self.created_at)


class HoldingAssetBreakdown(models.Model):
    asset = models.CharField(max_length=50)
    percentage = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="asset_breakdown")
    created_at = models.DateField(auto_now_add=True)
    update_index = models.PositiveIntegerField()

    class Meta:
        verbose_name = "HoldingAssetBreakdown"
        verbose_name_plural = "HoldingAssetBreakdowns"

    def __str__(self):
        return "{}: {} - {}".format(self.holding, self.asset, self.created_at)


class HoldingEquityBreakdown(models.Model):
    category = models.CharField(max_length=30)
    percentage = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="equity_breakdown")
    created_at = models.DateField(auto_now_add=True)
    update_index = models.PositiveIntegerField()

    class Meta:
        verbose_name = "HoldingEquityBreakdown"
        verbose_name_plural = "HoldingEquityBreakdowns"

    def __str__(self):
        return "{}: {} - {}".format(self.holding, self.category, self.created_at)


class HoldingBondBreakdown(models.Model):
    category = models.CharField(max_length=30)
    percentage = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="bond_breakdown")
    created_at = models.DateField(auto_now_add=True)
    update_index = models.PositiveIntegerField()

    class Meta:
        verbose_name = "HoldingBondBreakdown"
        verbose_name_plural = "HoldingBondBreakdowns"

    def __str__(self):
        return "{}: {} - {}".format(self.holding, self.category, self.created_at)


# todo rename to HoldingReturnMeta
class HoldingReturns(models.Model):
    """
    This model represents the one year, two year, and three year
    returns for any single holding, according to Morningstar.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    year_to_date = models.FloatField()
    one_year_return = models.FloatField()
    two_year_return = models.FloatField()
    three_year_return = models.FloatField()
    one_month_return = models.FloatField()
    threeMonthReturns = models.FloatField()
    three_month_return = models.ForeignKey("Holding", related_name="returns")

    class Meta:
        verbose_name = "HoldingReturn"
        verbose_name_plural = "HoldingReturns"

    def __str__(self):
        return "{} returns at {}".format(self.holding, self.createdAt)


# todo rename to HoldingDividendMeta
class HoldingDividends(models.Model):
    """
    This model represents the dividends provided by a certain fund
    on a given day.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    value = models.FloatField()
    holding = models.ForeignKey("Holding", related_name="dividends")

    class Meta:
        verbose_name = "HoldingDividend"
        verbose_name_plural = "HoldingDividends"


# todo rename to AccountReturnMeta
class AccountReturns(models.Model):
    """
    This model represents the returns made by some account corresponding to certain
    time intervals.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    year_to_date = models.FloatField()
    one_year_return = models.FloatField()
    two_year_return = models.FloatField()
    three_year_return = models.FloatField()
    one_month_return = models.FloatField()
    three_month_return = models.FloatField()
    account = models.OneToOneField("Account", related_name="account_returns")

    class Meta:
        verbose_name = "AccountReturn"
        verbose_name_plural = "AccountReturns"

    def __str__(self):
        return "acct {}".format(self.account.quovo_id)


class UserSharpe(models.Model):
    """
    This model represents the responses for the riskReturnProfile module.
    It contains the sharpe ratio of a user's portfolio on a given day.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    quovo_user = models.ForeignKey("dashboard.QuovoUser", related_name="user_sharpes")

    class Meta:
        verbose_name = "UserSharpe"
        verbose_name_plural = "UserSharpes"

    def __str__(self):
        up = self.quovo_user.user_profile
        return "{} {}: {}".format(up.first_name, up.last_name, str(self.created_at))


class UserBondEquity(models.Model):
    """
    This model represents the responses for the risk-age module.
    It contains the bond-equity breakdown of a user's portfolio on a given day.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    bond = models.FloatField()
    equity = models.FloatField()
    quovo_user = models.ForeignKey("dashboard.QuovoUser", related_name="userBondEquity")


# todo rename to AverageUserReturnMeta
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
    created_at = models.DateTimeField(auto_now_add=True)
    age_group = models.PositiveSmallIntegerField()
    year_to_date = models.FloatField()
    one_year_return = models.FloatField()
    two_year_return = models.FloatField()
    three_year_return = models.FloatField()
    one_month_return = models.FloatField()
    three_month_return = models.FloatField()

    class Meta:
        verbose_name = "AverageUserReturn"
        verbose_name_plural = "AverageUserReturns"

    def __str__(self):
        return "Avg User Returns on {}".format(str(self.created_at.date()))


class AverageUserSharpe(models.Model):
    """
    This model represents the average of many user Sharpe Ratios in a given day.
    There should be eight of these each day, following a similar age group construction
    as detailed above.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    age_group = models.PositiveSmallIntegerField()
    mean = models.FloatField(null=True)
    std = models.FloatField(null=True)

    class Meta:
        verbose_name = "AverageUserSharpe"
        verbose_name_plural = "AverageUserSharpes"

    def __str__(self):
        return "Avg User Sharpes on {}".format(str(self.created_at.date()))


class AverageUserFee(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    average_fees = models.FloatField()

    class Meta:
        verbose_name = "AverageUserFees"
        verbose_name_plural = "AverageUserFees"

    def __str__(self):
        return "Avg User Fees on {}".format(str(self.created_at.date()))


class AverageUserBondEquity(models.Model):
    """
    This model represents the average of many user Bond Equity breakdowns in a given day.
    There should be eight of these each day, following a similar age group construction
    as detailed above.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    age_group = models.PositiveSmallIntegerField()
    bond = models.FloatField()
    equity = models.FloatField()

    class Meta:
        verbose_name = "AverageUserBondEquity"
        verbose_name_plural = "AverageUserBondEquities"

    def __str__(self):
        return "Avg User BondEquity on {}".format(str(self.created_at.date()))


class Account(models.Model):
    quovo_user = models.ForeignKey("dashboard.QuovoUser", related_name="user_accounts")
    brokerage_name = models.CharField(blank=True, null=True, max_length=100)
    nickname = models.CharField(blank=True, null=True, max_length=100)
    quovo_id = models.IntegerField(unique=True)
    # if user no longer has this account - we want to save the existence of this account
    # if the user relinks the account we can show the account because we have the past holding info
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return "%s %s" % (self.quovoUser, self.brokerage_name)

    def get_account_returns(self):
        """
        Creates and returns the most recent instance of the account's AccountReturn
        model.
        """
        begin = dj_datetime.now().replace(day=1, month=1)
        now = datetime.now()
        year_to_date = self.get_returns_in_period(begin, now)
        now = now.replace(day=1)
        ret1mo = self.get_returns_in_period(now - relativedelta(months=1), now)
        ret3mo = self.get_returns_in_period(now - relativedelta(months=3), now)
        now = now.replace(month=1)
        ret1ye = self.get_returns_in_period(now - relativedelta(years=1), now)
        ret2ye = self.get_returns_in_period(now - relativedelta(years=2), now - relativedelta(years=1))
        ret3ye = self.get_returns_in_period(now - relativedelta(years=3), now - relativedelta(years=2))

        if not hasattr(self, 'account_returns'):
            ar = AccountReturns(one_month_return=ret1mo,
                                three_month_return=ret3mo,
                                one_year_return=ret1ye,
                                two_year_return=ret2ye,
                                three_year_return=ret3ye,
                                year_to_date=year_to_date,
                                account=self)
            ar.save()
            return ar
        ar = self.account_returns
        ar.one_month_return = ret1mo
        ar.three_month_return = ret3mo
        ar.one_year_return = ret1ye
        ar.two_year_return = ret2ye
        ar.three_year_return = ret3ye
        ar.year_to_date = year_to_date
        ar.save()
        return ar

    def get_returns_in_period(self, start_date, end_date):
        if type(start_date) is datetime or type(start_date) is dj_datetime:
            start_date = start_date.date()
        if type(end_date) is datetime or type(start_date) is dj_datetime:
            end_date = end_date.date()

        if end_date <= start_date:
            return 0.0

        holds = self.account_display_holdings.all()

        total_value = sum([hold.value for hold in holds])
        weight = [hold.value/total_value for hold in holds]

        return_vector = [hold.holding.get_returns_in_period(start_date, end_date) for hold in holds]

        return np.dot(weight, return_vector)*100


class Portfolio(models.Model):
    quovo_user = models.ForeignKey("dashboard.QuovoUser", related_name="user_portfolios")
    quovo_id = models.IntegerField(unique=True)
    description = models.CharField(blank=True, null=True, max_length=100)
    is_taxable = models.BooleanField()
    nickname = models.CharField(blank=True, null=True, max_length=100)
    owner_type = models.CharField(blank=True, null=True, max_length=100)
    portfolio_name = models.CharField(blank=True, null=True, max_length=100)
    portfolio_type = models.CharField(blank=True, null=True, max_length=100)
    account = models.ForeignKey("Account", related_name="portfolios", to_field="quovo_id")
    # if user no longer has this portfolio - we want to save the existence of this portfolio
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return "{} {}".format(self.quovo_user, self.portfolio_name)


class UserFee(models.Model):
    quovo_user = models.ForeignKey("dashboard.QuovoUser", related_name="fees")
    value = models.FloatField(default=0)
    change_index = models.IntegerField(default=1)

    class Meta:
        verbose_name = "UserFee"
        verbose_name_plural = "UserFees"

    def __str__(self):
        return "{} {}".format(self.quovo_user, self.change_index)


class Benchmark(models.Model):
    name = models.CharField(max_length=225)
    age_group = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Benchmark"
        verbose_name_plural = "Benchmarks"

    def __str__(self):
        return self.name

    def get_returns_wrapped(self):
        result = {
            "year_to_date" : 0,
            "one_year" : 0,
            "two_year" : 0
        }
        composites = self.composites.all().prefetch_related("returns")
        count = composites.count()

        if count == 0:
            return result

        for composite in composites:
            returns = composite.returns
            if not returns.exists():
                count -= 1
                continue
            composite_return = returns.latest("createdAt")
            result["year_to_date"] += composite_return.year_to_date
            result["one_year"] += composite_return.one_year_return
            result["two_year"] += composite_return.two_year_return
        result["year_to_date"] /= count
        result["one_year"] /= count
        result["two_year"] /= count
        return result

    def get_stock_bond_split(self):
        result = {
            "stock": 0,
            "bond": 0,
        }
        composites = self.composites.all().prefetch_related("asset_breakdown")
        for composite in composites:
            breakdowns = composite.asset_breakdown\
                        .filter(updateIndex__exact=composite.current_update_index)\
                        .filter(asset__in=["StockLong", "StockShort", "BondLong", "BondShort"])
            for breakdown in breakdowns:
                asset = breakdown.asset
                if asset == "StockLong":
                    result["stock"] += breakdown.percentage
                elif asset == "StockShort":
                    result["stock"] -= breakdown.percentage
                elif asset == "BondLong":
                    result["bond"] += breakdown.percentage
                else:
                    result["bond"] -= breakdown.percentage

        total = result["stock"] + result["bond"]
        for key, value in result.iteritems():
            normalized = "{0:.2f}".format(result.get(key) / total)
            result[key] = float(normalized)
        return result


class BenchmarkComposite(Holding):
    benchmark = models.ForeignKey('Benchmark', related_name="composites")

    class Meta:
        verbose_name = "BenchmarkComposite"
        verbose_name_plural = "BenchmarkComposites"

    def __str__(self):
        return self.secname
