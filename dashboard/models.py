from __future__ import unicode_literals
import random
import string
from dateutil.relativedelta import relativedelta
from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
import numpy as np
import pandas as pd

from Vestivise import mailchimp
from Vestivise import settings
from Vestivise.Vestivise import NightlyProcessException
from Vestivise.quovo import Quovo
from django.db import models
from data.models import Holding, UserCurrentHolding, UserHistoricalHolding, UserDisplayHolding, UserReturns, Account, Portfolio, \
    Transaction, UserSharpe, UserBondEquity
from data.models import TreasuryBondValue
from django.utils.timezone import datetime
from django.utils.dateparse import parse_date
from uuid import uuid4
from django.db import IntegrityError

class UserProfile(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    birthday = models.DateField()
    state = models.CharField(max_length=5)
    createdAt = models.DateField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    company = models.CharField(max_length=50, null=True, blank=True)
    zipCode = models.CharField(max_length=5)

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def get_quovo_user(self):
        if hasattr(self, 'quovoUser'):
            return self.quovoUser
        return None

    def get_full_name(self):
        return "%s %s" % (self.firstName, self.lastName)

    def get_age(self):
        return datetime.today().year - self.birthday.year

    def save(self, *args, **kwargs):
        should_create_progress = False
        if self.pk is None:
            should_create_progress = True
        super(UserProfile, self).save(*args, **kwargs)
        if should_create_progress:
            ProgressTracker.objects.create(profile=self)

    def __str__(self):
        return "%s" % (self.user.email,)


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

    @staticmethod
    def track_progress(user, track_info):
        pt = user.profile.progress
        track_id = track_info.get("track_id")
        track_data = track_info.get("track_data")

        if track_id == "did_link":
            pt.did_link = True
        if track_id == "complete_identification":
            pt.complete_identification = True
        if track_id == "did_open_dashboard":
            pt.did_open_dashboard = True
        if track_id == "dashboard_data_shown":
            pt.dashboard_data_shown = True
        if track_id == "annotation_view_count":
            pt.annotation_view_count += 1
        if track_id == "hover_module_count":
            pt.hover_module_count += 1
        if track_id == "total_dashboard_view_time":
            pt.total_dashboard_view_time += track_data
        if track_id == "total_filters":
            pt.total_filters += 1
        if track_id == "tutorial_time":
            pt.tutorial_time += 1
        if track_id == "module_view":
            ptmv = ProgressTrackerModuleView.get_module_view_model(track_data, pt)
            ptmv.views += 1
            ptmv.save()
        pt.save()

    class Meta:
        verbose_name = "ProgressTracker"
        verbose_name_plural = "ProgressTrackers"


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recoveryLinks')
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
                self.link = RecoveryLink.generateLink()
                super(RecoveryLink, self).save(*args, **kwargs)
            except IntegrityError:
                self.id = uuid4().hex
            else:
                unique = True

    def activate(self):
        self.is_active = True
        self.save()

    @staticmethod
    def generateLink(stop=0, length=15):
        '''
        Generates random string for magic link
        '''
        result = ''.join(random.choice(string.letters + string.digits) for i in range(length))
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
    moduleID = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return self.name

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
            current_holdings = self.userCurrentHoldings.exclude(holding__category__in=['FOFF', 'IGNO'])
            fundOfFunds = self.userCurrentHoldings.filter(holding__category__exact="FOFF")
            if len(current_holdings) == 0 and len(fundOfFunds) == 0:
                return False
            for current_holding in current_holdings:
                if not current_holding.holding.isIdentified() or not current_holding.holding.isCompleted():
                    return False

            for fund in fundOfFunds:
                for hold in fund.holding.childJoiner.all():
                    if not hold.childHolding.isIdentified() or not hold.childHolding.isCompleted():
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

    def getDisplayHoldings(self, acctIgnore=[]):
        """
        Returns DisplayHoldings that aren't ignored, and should be
        used in different computations.
        :return: List of DisplayHoldings.
        """
        holds = self.userDisplayHoldings.exclude(holding__category__exact="IGNO").exclude(account__quovoID__in=acctIgnore)
        res = []
        for h in holds:
            if h.holding.category=="FOFF":
                for toAdd in h.holding.childJoiner.all():
                    temp = UserDisplayHolding(holding=toAdd.childHolding,
                                              quovoUser=self,
                                              value=h.value*toAdd.compositePercent/100,
                                              quantity=h.quantity*toAdd.compositePercent/100,
                                              quovoCusip=h.quovoCusip,
                                              quovoTicker=h.quovoTicker)
                    res.append(temp)
            else:
                res.append(h)
        return res

    def getCurrentHoldings(self, acctIgnore=[], exclude_holdings=None):
        holds = self.userCurrentHoldings.exclude(holding__category__exact="IGNO").exclude(
            account__quovoID__in=acctIgnore)
        if exclude_holdings:
            holds = holds.exclude(holding_id__in=exclude_holdings)
        res = []
        for h in holds:
            if h.holding.category == "FOFF":
                for toAdd in h.holding.childJoiner.all():
                    temp = UserDisplayHolding(holding=toAdd.childHolding,
                                              quovoUser=self,
                                              value=h.value * toAdd.compositePercent / 100,
                                              quantity=h.quantity * toAdd.compositePercent / 100,
                                              quovoCusip=h.quovoCusip,
                                              quovoTicker=h.quovoTicker)
                    res.append(temp)
            else:
                res.append(h)
        return res

    def setCurrentHoldings(self, newHoldings):
        """
        Accepts a Json of new holdings and sets the UserCurrentHoldings
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
            hold.quovoCusip = position["cusip"]
            hold.quovoTicker = position["ticker"]
            hold.account_id = position["account"]
            hold.portfolio_id = position["portfolio"]
            hold.holding = Holding.getHoldingByPositionDict(position)
            hold.save()

    def updateDisplayHoldings(self):
        """
        Copies the values of the UserCurrentHoldings to the
        UserDisplayHoldings. This will move the old UserDisplayHoldings
        to UserHistoricalHoldings.
        """
        # Collect a time to organize the UserHistoricalHoldings
        timestamp = timezone.now()
        # Transfer all current display Holdings to historical
        # holdings, then delete the old disp Holding.
        for dispHold in self.userDisplayHoldings.all():
            UserHistoricalHolding.objects.create(
                quovoUser=self,
                quantity=dispHold.quantity,
                value=dispHold.quantity,
                holding=dispHold.holding,
                archivedAt=timestamp,
                portfolioIndex=self.currentHistoricalIndex,
                quovoCusip=dispHold.quovoCusip,
                quovoTicker=dispHold.quovoTicker,
                account=dispHold.account,
                portfolio=dispHold.portfolio,

            )
            dispHold.delete()

        # Create a new UserDisplayHolding for each
        # currentHolding.
        for currHold in self.userCurrentHoldings.all():
            is_identified = currHold.holding.isIdentified()
            is_completed = currHold.holding.isCompleted()
            if is_identified and is_completed:
                UserDisplayHolding.objects.create(
                    quovoUser=self,
                    quantity=currHold.quantity,
                    value=currHold.value,
                    holding=currHold.holding,
                    quovoCusip=currHold.quovoCusip,
                    quovoTicker=currHold.quovoTicker,
                    account=currHold.account,
                    portfolio=currHold.portfolio,
                )

        self.currentHistoricalIndex += 1

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
        if len(positions) != self.userCurrentHoldings.count():
            return False
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

    def getUserReturns(self, acctIgnore=[]):
        """
        Creates a UserReturns for the user's most recent portfolio information.
        """
        begin = datetime.now().replace(day=1, month=1)
        now = datetime.now()
        yeartodate = self.getReturnsInPeriod(begin, now)
        now = now.replace(day=1)
        ret1mo = self.getReturnsInPeriod(now - relativedelta(months=1), now)
        ret3mo = self.getReturnsInPeriod(now - relativedelta(months=3), now)
        now = now.replace(month=1)
        ret1ye = self.getReturnsInPeriod(now - relativedelta(years=1), now)
        ret2ye = self.getReturnsInPeriod(now - relativedelta(years=2), now - relativedelta(years=1))
        ret3ye = self.getReturnsInPeriod(now - relativedelta(years=3), now - relativedelta(years=2))
        if acctIgnore:
            return UserReturns(oneMonthReturns=ret1mo,
                               threeMonthReturns=ret3mo,
                               oneYearReturns=ret1ye,
                               twoYearReturns=ret2ye,
                               threeYearReturns=ret3ye,
                               yearToDate=yeartodate)
        return self.userReturns.create(oneMonthReturns=ret1mo,
                                       threeMonthReturns=ret3mo,
                                       oneYearReturns=ret1ye,
                                       twoYearReturns=ret2ye,
                                       threeYearReturns=ret3ye,
                                       yearToDate=yeartodate)

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
                    holds[i].value -= abs(transaction.value)
                if transaction.tran_category == "S":
                    holds[i].value += abs(transaction.value)
                break
        newhold = None
        if transaction.ticker != "" and Holding.objects.filter(ticker=transaction.ticker).exists():
            newhold = Holding.objects.filter(ticker=transaction.ticker)[0]
        elif newhold is not None and transaction.cusip != "" and Holding.objects.filter(cusip=transaction.cusip).exists():
            newhold = Holding.objects.filter(cusip=transaction.cusip)[0]
        if newhold is not None:
            if transaction.tran_category == "B":
                val = -abs(transaction.value)
            elif transaction.tran_category == "S":
                val = abs(transaction.value)
            else:
                return
            usr = holds[0].quovoUser
            temphold = UserDisplayHolding(holding=newhold,
                                          quovoUser=usr,
                                          value=val,
                                          quantity=0)
            holds.append(temphold)

    def getReturnsInPeriod(self, startDate, endDate, acctIgnore=[]):
        """
        Determines the returns in a period of time for this specific user.
        :param startDate: Date to start determining returns.
        :param endDate: Date to stop determining returns.
        :return: Float of returns in that period.
        """
        if type(startDate) is datetime:
            startDate = startDate.date()
        if type(endDate) is datetime:
            endDate = endDate.date()

        return_product = 1.0
        query_end = datetime.now().date()
        holds = self.getDisplayHoldings(acctIgnore=acctIgnore)
        s = sum([x.value for x in holds])
        weight = [x.value/s for x in holds]
        for t in self.userTransaction.filter(date__gte=startDate, date__lte=query_end).order_by('-date'):
            return_in_period = [x.holding.getReturnsInPeriod(t.date, query_end) for x in holds]
            for i in range(len(holds)):
                holds[i].value /= (1 + return_in_period[i])
            if t.date <= endDate <= query_end:
                ret_prime = [x.holding.getReturnsInPeriod(t.date, endDate) for x in holds]
                return_product *= (1 + np.dot(ret_prime, weight))
            elif startDate <= t.date <= endDate and startDate <= query_end <= endDate:
                return_product *= (1 + np.dot(return_in_period, weight))
            QuovoUser._applyReverseTransaction(holds, t)
            s = sum([x.value for x in holds])
            weight = [x.value/s for x in holds]
            query_end = t.date
        try:
            return_in_period = [x.holding.getReturnsInPeriod(startDate, t.date) for x in holds]
        except NameError:
            return_in_period = [x.holding.getReturnsInPeriod(startDate, endDate) for x in holds]
        return_product *= (1 + np.dot(weight, return_in_period))
        return (return_product - 1)*100

    def getUserSharpe(self, acctIgnore=[]):
        holds = self.getDisplayHoldings(acctIgnore=acctIgnore)
        end = datetime.now().date()
        start = end - relativedelta(years=3)
        tmpRets = []
        for hold in holds:
            toadd = hold.holding.getMonthlyReturns(start+relativedelta(months=1), end-relativedelta(months=1))
            tmpRets.append([0.0]*(36-len(toadd)) + toadd)
        returns = pd.DataFrame(tmpRets)

        if returns.empty:
            return self.userSharpes.create(
                value=0
            )

        count = TreasuryBondValue.objects.count()
        tbill = np.array([x.value/100 for x in TreasuryBondValue.objects.all()[count-37:count-1]])
        returns -= tbill
        mu = returns.mean(axis=1)
        sigma = (returns).T.cov()
        totVal = sum([x.value for x in holds])
        weights = [x.value / totVal for x in holds]
        denom = np.sqrt(sigma.dot(weights).dot(weights))
        rfrr = np.mean(tbill)
        ratio = np.sqrt(12)*(mu.dot(weights)) / denom

        if acctIgnore:
            return UserSharpe(value=ratio, quovoUser=self)

        return self.userSharpes.create(
            value=ratio
        )

    def getUserBondEquity(self, acctIgnore=[]):
        holds = self.getDisplayHoldings(acctIgnore=acctIgnore)
        totalVal = sum([x.value for x in holds])
        breakDowns = [dict([(x.asset, x.percentage * h.value / totalVal) for x in h.holding.assetBreakdowns.filter(updateIndex__exact=h.holding.currentUpdateIndex)]) for h in holds]
        totPerc = sum([sum(x.itervalues()) for x in breakDowns])
        stock_agg = 0
        bond_agg = 0
        for breakDown in breakDowns:
            bs = breakDown.get("BondShort", 0.0)
            bl = breakDown.get("BondLong", 0.0)
            ss = breakDown.get("StockShort", 0.0)
            sl = breakDown.get("StockLong", 0.0)

            stock_agg += ss + sl
            bond_agg += bs + bl
        if stock_agg == 0 and bond_agg == 0:
            return self.userBondEquity.create(
                bond=0,
                equity=0
            )

        stock_total = stock_agg/(stock_agg + bond_agg) * 100
        bond_total = bond_agg/(stock_agg + bond_agg) * 100

        if acctIgnore:
            return UserBondEquity(
                bond=bond_total,
                equity=stock_total,
                quovoUser=self
            )

        return self.userBondEquity.create(
            bond=bond_total,
            equity=stock_total
        )

    def getUserHistory(self):
        return self.userTransaction.all().order_by('date')

    def getContributions(self, to_year=3, acctIgnore=[]):
        contribution_sym = "B"
        to_date = datetime.today() - relativedelta(years=to_year)
        return self.userTransaction.filter(tran_category=contribution_sym, date__gt=to_date).exclude(quovoID__in=acctIgnore)

    def getWithdraws(self, to_year=3, acctIgnore=[]):
        withdraw_sym = "S"
        to_date = datetime.today() - relativedelta(years=to_year)
        return self.userTransaction.filter(tran_category=withdraw_sym, date__gt=to_date).exclude(quovoID__in=acctIgnore)

    def updateAccounts(self):
        try:
            accounts = Quovo.get_accounts(self.quovoID)
            user_accounts_map = {x.quovoID : x for x in self.userAccounts.all()}
            current_accounts_id = user_accounts_map.keys()
            for a in accounts.get("accounts"):
                id = a.get("id")
                if id in current_accounts_id:
                    current_accounts_id.remove(id)
                    a = user_accounts_map.get(id)
                    if not a.active:
                        a.active = True
                        a.save()
                else:
                    Account.objects.create(
                        quovoUser=self,
                        brokerage_name=a.get("brokerage_name"),
                        nickname=a.get("nickname"),
                        quovoID=id
                    )
            for i in current_accounts_id:
                a = user_accounts_map.get(i)
                a.active = False
                a.save()
        except Exception as e:
            raise NightlyProcessException(e.message)

    def updatePortfolios(self):
        try:
            portfolios = Quovo.get_user_portfolios(self.quovoID)
            user_portfolio_map = {x.quovoID: x for x in self.userPortfolios.all()}
            current_portfolios_id = user_portfolio_map.keys()
            for p in portfolios.get("portfolios"):
                id = p.get("id")
                if id in current_portfolios_id:
                    current_portfolios_id.remove(id)
                    a = user_portfolio_map.get(id)
                    if not a.active:
                        a.active = True
                        a.save()
                else:
                    Portfolio.objects.create(
                        quovoUser=self,
                        description=p.get("description"),
                        is_taxable=p.get("is_taxable"),
                        quovoID=id,
                        nickname=p.get("nickname"),
                        owner_type=p.get("owner_type"),
                        portfolio_name=p.get("portfolio_name"),
                        portfolio_type=p.get("portfolio_type"),
                        account_id=p.get("account"),
                    )
            for i in current_portfolios_id:
                a = user_portfolio_map.get(i)
                a.active = False
                a.save()
        except Exception as e:
            raise NightlyProcessException(e.message)

    def updateTransactions(self):
        history = self.getUserHistory()
        last_id = None
        if history:
            last_id = history.last().quovoID
        latest_history = Quovo.get_user_history(self.quovoID, start_id=last_id)
        for transaction in latest_history.get('history'):
            try:
                t = Transaction.objects.update_or_create(
                    quovoUser=self,
                    quovoID=transaction.get('id'),
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
                    mailchimp.alertIdentifyHoldings(transaction.get('ticker_name'))
                    Holding.objects.create(secname=transaction.get('ticker_name'))
            except Exception as e:
                raise NightlyProcessException(e.message)



@receiver(post_delete, sender=QuovoUser)
def _QuovoUser_delete(sender, instance, **kwargs):
    Quovo.delete_user(instance.quovoID)

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month) + delta-1) / 12
    if not m: m = 12
    return date.replace(month=m, year=y)