from dateutil.parser import parse

from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date

from data.models import Holding, Account, Portfolio, Transaction, UserCurrentHolding, HoldingPrice, HoldingExpenseRatio, \
    HoldingDividends
from sources.quovo import QuovoSource
from sources.morningstar import MorningstarSource
from dashboard.models import UserProfile, QuovoUser


class TestFactory:

    @staticmethod
    def get_quovo_source():
        return QuovoSource(use_test_account=True)

    @staticmethod
    def get_morning_star_source():
        return MorningstarSource()

    @staticmethod
    def create_user(quovo, email, password, birthday):
        user = get_user_model().objects.create_user(
            password=password,
            email=email
        )
        user_profile = UserProfile.objects.create(
            birthday=parse(birthday).date(),
            user=user
        )
        quovo_user_data = quovo.create_user(email)
        QuovoUser.objects.create(
            quovo_id=quovo_user_data['user']['id'],
            user_profile=user_profile
        )
        return user

    @staticmethod
    def create_holding(secname, category, ticker=None, cusip=None, morning_star_id=None, sector=None):
        return Holding.objects.create(
            secname=secname,
            category=category,
            ticker=ticker,
            cusip=cusip,
            morning_star_id=morning_star_id,
            sectory=sector
        )

    @staticmethod
    def create_holding_prices(holding, price_dates):
        # price_dates (price, date)
        if not price_dates:
            raise Exception("Missing param price_dates - list of (price, date)")
        result = []
        for price_date in price_dates:
            result.append(
                HoldingPrice.objects.create(
                    price=price_date[0],
                    closing_date=price_dates[1],
                    holding=holding
                )
            )
        return result

    @staticmethod
    def create_holding_expense_ratio(holding, ratio):
        return HoldingExpenseRatio.objects.create(
            expense=ratio,
            holding=holding
        )

    @staticmethod
    def create_holding_dividend(holding, value, date):
        return HoldingDividends.objects.create(
            holding=holding,
            value=value,
            date=date
        )

    @staticmethod
    def create_account(quovo, user):
        quovo_user = user.profile.quovo_user
        account_data = quovo.create_account(quovo_user.quovo_id, 21534, 'testusername', 'testpassword')
        account = Account.objects.create(
            quovo_user=quovo_user,
            brokerage_name="Test Brokerage",
            quovo_id=account_data['account']['id']
        )
        quovo.sync_account(account.quovo_id)
        is_done_syncing = False
        while not is_done_syncing:
            is_done_syncing = quovo.get_sync_status(account.quovo_id)['sync']['status'] == "good"
        return account

    @staticmethod
    def create_portfolios(quovo, user):
        quovo_user = user.profile.quovo_user
        portfolios = quovo.get_user_portfolios(quovo_user.quovo_id)
        print portfolios
        result = []
        for portfolio in portfolios.get("portfolios"):
            portfolio_id = portfolio.get("id")
            p = Portfolio.objects.create(
                quovo_user=quovo_user,
                description=portfolio.get("description"),
                is_taxable=portfolio.get("is_taxable"),
                quovo_id=portfolio_id,
                nickname=portfolio.get("nickname"),
                owner_type=portfolio.get("owner_type"),
                portfolio_name=portfolio.get("portfolio_name"),
                portfolio_type=portfolio.get("portfolio_type"),
                account_id=portfolio.get("account"),
            )
            result.append(p)
        return result

    @staticmethod
    def create_transactions(quovo, user):
        quovo_user = user.profile.quovo_user
        latest_history = quovo.get_user_history(quovo_user.quovo_id)
        result = []
        for transaction in latest_history.get('history'):
            t = Transaction.objects.update_or_create(
                quovo_user=quovo_user,
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
            result.append(t)
        return result

    @staticmethod
    def create_positions_from_portfolio(quovo, user, portfolio):
        quovo_user = user.profile.quovo_user
        positions_data = quovo.get_portfolio_positions(portfolio.quovo_id)
        positions = positions_data["positions"]
        result = []
        for position in positions:
            hold = UserCurrentHolding()
            hold.quovo_user = quovo_user
            hold.quantity = position["quantity"]
            hold.value = position["value"]
            hold.quovo_cusip = position["cusip"]
            hold.quovo_ticker = position["ticker"]
            hold.account_id = position["account"]
            hold.portfolio_id = position["portfolio"]
            hold.holding = Holding.get_holding_by_position_dict(position)
            result.append(hold.save())
        return result
