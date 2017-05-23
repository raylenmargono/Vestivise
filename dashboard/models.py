from __future__ import unicode_literals
import random
import string
from uuid import uuid4
from dateutil.relativedelta import relativedelta
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils.dateparse import parse_date
from django.db import IntegrityError, models

import numpy as np
import pandas as pd

from data.models import (Holding, UserCurrentHolding, UserHistoricalHolding, UserDisplayHolding, Account, Portfolio,
                         Transaction, UserSharpe, UserBondEquity, AccountReturns, UserFee, TreasuryBondValue)
from Vestivise import settings, Vestivise
from sources import mailchimp
from sources.quovo import Quovo


class UserProfile(models.Model):
    birthday = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    company = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def get_quovo_user(self):
        if hasattr(self, 'quovo_user'):
            return self.quovo_user
        return None

    def get_age(self):
        return relativedelta(datetime.now(), self.birthday).years

    def save(self, *args, **kwargs):
        should_create_progress = False
        if self.pk is None:
            should_create_progress = True
        super(UserProfile, self).save(*args, **kwargs)
        if should_create_progress:
            ProgressTracker.objects.create(profile=self)

    def __str__(self):
        return "%s" % (self.user.email,)


@receiver(post_save, sender=UserProfile, dispatch_uid="send_email_creation")
def send_email_creation(sender, instance, created, **kwargs):
    if created:
        mailchimp.user_creation(instance.user.email)


class ProgressTracker(models.Model):
    did_link = models.BooleanField(default=False)
    complete_identification = models.BooleanField(default=False)
    did_open_dashboard = models.BooleanField(default=False)
    dashboard_data_shown = models.BooleanField(default=False)
    annotation_view_count = models.IntegerField(default=0)
    hover_module_count = models.IntegerField(default=0)
    total_dashboard_view_time = models.FloatField(default=0)
    total_filters = models.IntegerField(default=0)
    tutorial_time = models.IntegerField(default=0)
    profile = models.OneToOneField("UserProfile", related_name="progress")
    last_dashboard_view = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def track_progress(user, track_info):
        pt = user.profile.progress
        track_id = track_info.get("track_id")
        track_data = track_info.get("track_data")

        if track_id == "did_link":
            pt.did_link = True
        if track_id == "complete_identification":
            pt.complete_identification = track_data
        if track_id == "did_open_dashboard":
            pt.did_open_dashboard = track_data
        if track_id == "dashboard_data_shown":
            pt.dashboard_data_shown = track_data
        if track_id == "annotation_view_count":
            pt.annotation_view_count += 1
        if track_id == "hover_module_count":
            pt.hover_module_count += 1
        if track_id == "total_dashboard_view_time":
            pt.total_dashboard_view_time += track_data
        if track_id == "total_filters":
            pt.total_filters += 1
        if track_id == "tutorial_time":
            pt.tutorial_time += track_data
        if track_id == "module_view":
            for i in track_data.get("modules"):
                ptmv, did_create = ProgressTrackerModuleView.get_module_view_model(i.get("id"), pt)
                ptmv.views += i.get("time")
                ptmv.save()
        pt.save()

    class Meta:
        verbose_name = "ProgressTracker"
        verbose_name_plural = "ProgressTrackers"


class UserTracking(models.Model):
    count = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "UserTracking"
        verbose_name_plural = "UserTrackings"

    def __str__(self):
        return "{} {}".format(self.created_at, self.count)


class ProgressTrackerModuleView(models.Model):
    module_name = models.CharField(max_length=100)
    views = models.IntegerField(default=0)
    tracker = models.ForeignKey("ProgressTracker", related_name="moduleViews")

    @staticmethod
    def get_module_view_model(module_name, tracker):
        return ProgressTrackerModuleView.objects.get_or_create(module_name=module_name, tracker=tracker)

    class Meta:
        verbose_name = "ProgressTrackerModuleView"
        verbose_name_plural = "ProgressTrackerModuleViews"


class RecoveryLink(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recovery_links')
    link = models.CharField(max_length=100)

    class Meta:
        verbose_name = "RecoveryLink"
        verbose_name_plural = "RecoveryLinks"

    def save(self, *args, **kwargs):
        if self.id:
            super(RecoveryLink, self).save(*args, **kwargs)
            return

        unique = False
        while not unique:
            try:
                self.id = uuid4().hex
                self.link = RecoveryLink.generate_link()
                super(RecoveryLink, self).save(*args, **kwargs)
            except IntegrityError:
                self.id = uuid4().hex
            else:
                unique = True

    def activate(self):
        self.is_active = True
        self.save()

    @staticmethod
    def generate_link(stop=0, length=15):
        result = ''.join(random.choice(string.letters + string.digits) for _ in range(length))
        if RecoveryLink.objects.filter(link=result).exists() and stop != 5:
            result = RecoveryLink.generateLink(stop=stop + 1)
        return result


class Module(models.Model):
    categories = (
        ('Risk', 'Risk'),
        ('Return', 'Return'),
        ('Asset', 'Asset'),
        ('Cost', 'Cost'),
        ('Other', 'Other')
    )

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=categories)
    endpoint = models.CharField(max_length=50)
    module_id = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return self.name


class QuovoUser(models.Model):
    quovo_id = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    user_profile = models.OneToOneField('UserProfile', related_name='quovo_user')
    current_historical_index = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "QuovoUser"
        verbose_name_plural = "QuovoUsers"

    def __str__(self):
        return str(self.quovo_id)

    def has_completed_user_holdings(self):
        """
        Returns if the user has completed holdings for their current holdings
        :return: Boolean if the user's holdings for this account are all identified
                and completed.
        """
        if hasattr(self, "user_current_holdings"):
            current_holdings = self.user_current_holdings.exclude(holding__category__in=['FOFF', 'IGNO'])
            fund_of_funds = self.user_current_holdings.filter(holding__category__exact="FOFF")
            if len(current_holdings) == 0 and len(fund_of_funds) == 0:
                return False
            for current_holding in current_holdings:
                if not current_holding.holding.is_identified() or not current_holding.holding.is_completed():
                    return False

            for fund in fund_of_funds:
                for hold in fund.holding.child_joiner.all():
                    if not hold.child_holding.is_identified() or not hold.child_holding.is_completed():
                        return False
        else:
            return False
        return True

    def get_new_holdings(self):
        """
        Gathers the new holdings JSON from a call to the Quovo API.
        :return: A Json of the user's most recent holdings.
        """
        try:
            positions = Quovo.get_user_positions(self.quovo_id)
            if not positions:
                return None
            return positions
        except Vestivise.QuovoRequestError:
            return None

    def get_display_holdings(self, acct_ignore=None):
        """
        Returns DisplayHoldings that aren't ignored, and should be
        used in different computations.
        :return: List of DisplayHoldings.
        """
        if not acct_ignore:
            acct_ignore = []
        holds = self.user_display_holdings.exclude(holding__category__exact="IGNO")\
                    .exclude(account__quovo_id__in=acct_ignore)
        res = []
        for hold in holds:
            if hold.holding.category == "FOFF":
                for joiner in hold.holding.child_joiner.all():
                    temp = UserDisplayHolding(holding=joiner.child_holding,
                                              quovo_user=self,
                                              value=hold.value * joiner.composite_percent/100,
                                              quantity=hold.quantity * joiner.composite_percent/100,
                                              quovo_cusip=hold.quovo_cusip,
                                              quovo_ticker=hold.quovo_ticker)
                    res.append(temp)
            else:
                res.append(hold)
        return res

    def get_current_holdings(self, acct_ignore=None, exclude_holdings=None, show_ignore=False):
        if not acct_ignore:
            acct_ignore = []

        if show_ignore:
            holds = self.user_current_holdings.exclude(account__quovo_id__in=acct_ignore)
        else:
            holds = self.user_current_holdings.exclude(holding__category__exact="IGNO").exclude(
                                                       account__quovo_id__in=acct_ignore)
        if exclude_holdings:
            holds = holds.exclude(holding_id__in=exclude_holdings)
        res = []
        for hold in holds:
            if hold.holding.category == "FOFF":
                for joiner in hold.holding.child_joiner.all():
                    temp = UserDisplayHolding(holding=joiner.child_holding,
                                              quovo_user=self,
                                              value=hold.value * joiner.composite_percent / 100,
                                              quantity=hold.quantity * joiner.composite_percent / 100,
                                              quovo_cusip=hold.quovo_cusip,
                                              quovo_ticker=hold.quovo_ticker)
                    res.append(temp)
            else:
                res.append(hold)
        return res

    def set_current_holdings(self, new_holdings):
        """
        Accepts a Json of new holdings and sets the UserCurrentHoldings
        of this user to contain the values of the newHoldings. This then
        deletes the old UserCurrentHoldings.
        :param: newHoldings The Json of new holdings to overwrite the
                UserCurrentHoldings
        """

        # Get rid of all the old UserCurrentHoldings
        for hold in self.user_current_holdings.all():
            hold.delete()

        # For each new position in Json response, create
        # a new UserCurrentHolding with its data.
        # Search for the Holding by its name. If it isn't present,
        # create a new one.
        positions = new_holdings["positions"]

        for position in positions:
            hold = UserCurrentHolding()
            hold.quovo_user = self
            hold.quantity = position["quantity"]
            hold.value = position["value"]
            hold.quovo_cusip = position["cusip"]
            hold.quovo_ticker = position["ticker"]
            hold.account_id = position["account"]
            hold.portfolio_id = position["portfolio"]
            hold.holding = Holding.get_holding_by_position_dict(position)
            hold.save()

    def update_display_holdings(self):
        """
        Copies the values of the UserCurrentHoldings to the
        UserDisplayHoldings. This will move the old UserDisplayHoldings
        to UserHistoricalHoldings.
        """
        # Collect a time to organize the UserHistoricalHoldings
        timestamp = timezone.now()
        # Transfer all current display Holdings to historical
        # holdings, then delete the old disp Holding.
        for display_holding in self.user_display_holdings.all():
            UserHistoricalHolding.objects.create(
                quovo_user=self,
                quantity=display_holding.quantity,
                value=display_holding.quantity,
                holding=display_holding.holding,
                archived_at=timestamp,
                portfolio_index=self.current_historical_index,
                quovo_cusip=display_holding.quovo_cusip,
                quovo_ticker=display_holding.quovo_ticker,
                account=display_holding.account,
                portfolio=display_holding.portfolio,

            )
            display_holding.delete()

        # Create a new UserDisplayHolding for each
        # currentHolding.
        for current_holding in self.user_current_holdings.all():
            is_identified = current_holding.holding.is_identified()
            is_completed = current_holding.holding.is_completed()
            if is_identified and is_completed:
                UserDisplayHolding.objects.create(
                    quovo_user=self,
                    quantity=current_holding.quantity,
                    value=current_holding.value,
                    holding=current_holding.holding,
                    quovo_cusip=current_holding.quovo_cusip,
                    quovo_ticker=current_holding.quovo_ticker,
                    account=current_holding.account,
                    portfolio=current_holding.portfolio,
                )
        self.current_historical_index += 1
        self.save()

    def current_holdings_equal_holding_json(self, holding_json):
        """
        Determines whether or not the user's current holdings
        possess the same assets as a holding JSON from Quovo.
        :param holding_json: The json of holding names to be compared against.
        :return: Boolean value denoting whether or not the UserCurrentHolding possesses
        the same assets as the Json.
        """
        # Get the current user holds in touples of secname, to the
        # hold itself.
        user_current_holds = dict((x.holding.secname, x) for x in self.user_current_holdings.all())
        # Fetch the positions from the call.
        positions = holding_json["positions"]
        if len(positions) != self.user_current_holdings.count():
            return False
        for position in positions:
            # Check if the position is currently in the user's holdings, if not
            # return false.
            if position["ticker_name"] in user_current_holds:
                # Check that the user's holdings match (or at least are very close)
                # in terms of value and quantity. If they aren't, return false.
                hold = user_current_holds[position["ticker_name"]]
                if not np.isclose(hold.value, position["value"]):
                    return False
            else:
                return False
        return True

    def get_user_returns(self, acct_ignore=None):
        """
        Creates a UserReturns for the user's most recent portfolio information.
        """
        if not acct_ignore:
            acct_ignore = []
        accounts = self.user_accounts.exclude(quovo_id__in=acct_ignore)
        acct_returns = [account.account_returns for account in accounts]
        weights = np.array(
            [
                sum([display_holding.value for display_holding in account.account_display_holdings.all()])
                for account in accounts
             ]
        )
        weights /= sum(weights)
        return_dict = {}
        return_list = ['one_month_return', 'three_month_return', 'one_year_return',
                       'two_year_return', 'three_year_return', 'year_to_date']
        for key in return_list:
            return_dict[key] = weights.dot([getattr(acct_return, key) for acct_return in acct_returns])
        return return_dict

    def get_user_sharpe(self, acct_ignore=None):
        if not acct_ignore:
            acct_ignore = []
        holds = self.get_display_holdings(acct_ignore=acct_ignore)

        if np.all([hold.holding.category == "CASH" for hold in holds]):
            if acct_ignore:
                return UserSharpe(value=0, acct_ignore=self)
            if self.user_sharpes.exists():
                if np.isclose(self.user_sharpes.latest('created_at').value, 0.0):
                    return
            return self.user_sharpes.create(value=0.0)

        end = datetime.now().date()
        start = end - relativedelta(years=3)
        tmp_returns = []
        for hold in holds:
            monthly_returns = hold.holding.get_monthly_returns(start + relativedelta(months=1), end - relativedelta(months=1))
            tmp_returns.append([0.0]*(36-len(monthly_returns)) + monthly_returns)
        returns = pd.DataFrame(tmp_returns)

        if returns.empty:
            return self.user_sharpes.create(value=0)

        count = TreasuryBondValue.objects.count()
        t_bill = np.array([t_bond_value.value/100 for t_bond_value in TreasuryBondValue.objects.all()[count-37:count-1]])
        returns -= t_bill
        mu = returns.mean(axis=1)
        sigma = returns.T.cov()
        total_value = sum([x.value for x in holds])
        weights = [hold.value / total_value for hold in holds]
        volatility = np.sqrt(sigma.dot(weights).dot(weights))
        ratio = np.sqrt(12)*(mu.dot(weights)) / volatility

        if acct_ignore:
            return UserSharpe(value=ratio, quovo_user=self)

        if self.user_sharpes.exists():
            curr = self.user_sharpes.latest('created_at')
            if np.isclose(curr.value, ratio):
                return curr

        return self.user_sharpes.create(value=ratio)

    def get_user_bond_equity(self, acct_ignore=None):
        if not acct_ignore:
            acct_ignore = []

        holdings = self.get_display_holdings(acct_ignore=acct_ignore)
        total_value = sum([hold.value for hold in holdings])

        break_downs = []
        for holding in holdings:
            asset_breakdowns = holding.holding.asset_breakdown
            for break_down in asset_breakdowns.filter(update_index__exact=holding.holding.current_update_index):
                break_downs.append({break_down.asset:  break_down.percentage * holding.value / total_value})

        stock_agg = 0
        bond_agg = 0
        for break_down in break_downs:
            bs = break_down.get("BondShort", 0.0)
            bl = break_down.get("BondLong", 0.0)
            ss = break_down.get("StockShort", 0.0)
            sl = break_down.get("StockLong", 0.0)

            stock_agg += ss + sl
            bond_agg += bs + bl

        if stock_agg == 0 and bond_agg == 0:
            return self.user_bond_equity.create(bond=0, equity=0)

        stock_total = stock_agg/(stock_agg + bond_agg) * 100
        bond_total = bond_agg/(stock_agg + bond_agg) * 100

        if acct_ignore:
            return UserBondEquity(bond=bond_total, equity=stock_total, quovo_user=self)

        return self.user_bond_equity.create(
            bond=bond_total,
            equity=stock_total
        )

    def get_user_history(self):
        return self.user_transaction.all().order_by('date')

    def get_contributions(self, to_year=3, acct_ignore=None):
        if not acct_ignore:
            acct_ignore = []
        contribution_sym = "B"
        to_date = datetime.today() - relativedelta(years=to_year)
        return self.user_transaction.filter(tran_category=contribution_sym, date__gt=to_date)\
                   .exclude(account__quovo_id__in=acct_ignore)

    def get_withdraws(self, to_year=3, acct_ignore=None):
        if not acct_ignore:
            acct_ignore = []
        withdraw_sym = "S"
        to_date = datetime.today() - relativedelta(years=to_year)
        return self.user_transaction.filter(tran_category=withdraw_sym, date__gt=to_date)\
                   .exclude(account__quovo_id__in=acct_ignore)

    def update_accounts(self):
        try:
            accounts = Quovo.get_accounts(self.quovo_id)
            user_accounts_map = {user_account.quovo_id: user_account for user_account in self.user_accounts.all()}
            current_accounts_id = user_accounts_map.keys()
            for account in accounts.get("accounts"):
                account_id = account.get("id")
                if account_id in current_accounts_id:
                    current_accounts_id.remove(account_id)
                    user_account = user_accounts_map.get(account_id)
                    if not user_account.active:
                        user_account.active = True
                        user_account.save()
                else:
                    Account.objects.create(
                        quovo_user=self,
                        brokerage_name=account.get("brokerage_name"),
                        nickname=account.get("nickname"),
                        quovo_id=account_id
                    )
            for i in current_accounts_id:
                a = user_accounts_map.get(i)
                a.active = False
                a.save()
        except Exception as e:
            raise Vestivise.NightlyProcessException(e.message)

    def update_portfolios(self):
        try:
            portfolios = Quovo.get_user_portfolios(self.quovo_id)
            user_portfolio_map = {user_portfolio.quovo_id: user_portfolio
                                  for user_portfolio in self.user_portfolios.all()}
            current_portfolio_ids = user_portfolio_map.keys()
            for portfolio in portfolios.get("portfolios"):
                portfolio_id = portfolio.get("id")
                if portfolio_id in current_portfolio_ids:
                    current_portfolio_ids.remove(portfolio_id)
                    user_portfolio = user_portfolio_map.get(portfolio_id)
                    if not user_portfolio.active:
                        user_portfolio.active = True
                        user_portfolio.save()
                else:
                    Portfolio.objects.create(
                        quovo_user=self,
                        description=portfolio.get("description"),
                        is_taxable=portfolio.get("is_taxable"),
                        quovo_id=portfolio_id,
                        nickname=portfolio.get("nickname"),
                        owner_type=portfolio.get("owner_type"),
                        portfolio_name=portfolio.get("portfolio_name"),
                        portfolio_type=portfolio.get("portfolio_type"),
                        account_id=portfolio.get("account"),
                    )
            for current_portfolio_id in current_portfolio_ids:
                portfolio = user_portfolio_map.get(current_portfolio_id)
                portfolio.active = False
                portfolio.save()
        except Exception as e:
            raise Vestivise.NightlyProcessException(e.message)

    def update_transactions(self):
        history = self.get_user_history()
        last_id = None
        if history:
            last_id = history.last().quovo_id
        latest_history = Quovo.get_user_history(self.quovo_id, start_id=last_id)
        for transaction in latest_history.get('history'):
            try:
                Transaction.objects.update_or_create(
                    quovo_user=self,
                    quovo_id=transaction.get('id'),
                    date=parse_date(transaction.get('date')),
                    fees=transaction.get('fees'),
                    value=transaction.get('value'),
                    price=transaction.get('price'),
                    quantity=transaction.get('quantity'),
                    cusip=transaction.get('cusip'),
                    expense_category=transaction.get('expense_category'),
                    ticker=transaction.get('ticker'),
                    ticker_name=transaction.get('ticker_name'),
                    tran_category=transaction.get('tran_category'),
                    tran_type=transaction.get('tran_type'),
                    memo=transaction.get('memo'),
                    account_id=transaction.get('account')
                )
                cusip_exist = Holding.objects.filter(cusip=transaction.get('cusip')).exists()
                ticker_exist = Holding.objects.filter(ticker=transaction.get('ticker')).exists()
                secname_exist = Holding.objects.filter(secname=transaction.get('ticker_name')).exists()
                if not cusip_exist and not ticker_exist and not secname_exist:
                    mailchimp.alert_identify_holdings(transaction.get('ticker_name'))
                    Holding.objects.create(secname=transaction.get('ticker_name'))
            except Exception as e:
                raise Vestivise.NightlyProcessException(e.message)

    def update_fees(self):
        holds = self.get_display_holdings()
        total_value = sum([hold.value for hold in holds])
        weights = [hold.value / total_value for hold in holds]
        costs = np.dot(weights, [hold.holding.expense_ratios.latest('created_at').expense for hold in holds])
        should_create = True
        index = 1
        if self.fees.exists():
            latest_fee = self.fees.all().latest('change_index')
            if latest_fee.value == costs:
                should_create = False
                index = latest_fee.change_index + 1
        if should_create:
            UserFee.objects.create(quovo_user=self, value=costs, change_index=index)


@receiver(post_delete, sender=QuovoUser)
def quovo_user_delete(sender, instance, **kwargs):
    Quovo.delete_user(instance.quovo_id)
