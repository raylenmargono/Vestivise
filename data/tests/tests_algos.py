import datetime

from django.test import TestCase
from helpers.test_factory import TestFactory
from helpers.quant_tools import calculate_returns_in_period


class TestAlgos(TestCase):
    def test_calculate_returns_in_period(self):
        # create holding
        holding = TestFactory.create_holding("name", "MUTF", ticker=None, cusip=None, morning_star_id=None, sector=None)
        # create price_dates list     price_dates(price, date)
        price_dates = []
        today = (60, datetime.datetime.strptime('07062017', "%d%m%Y").date())
        price_dates.append(today)
        one_month = (50, datetime.datetime.strptime('07052017', "%d%m%Y").date())
        price_dates.append(one_month)
        three_months = (60, datetime.datetime.strptime('07032017', "%d%m%Y").date())
        price_dates.append(three_months)
        one_year = (100, datetime.datetime.strptime('07062016', "%d%m%Y").date())
        price_dates.append(one_year)
        two_years = (20, datetime.datetime.strptime('07062015', "%d%m%Y").date())
        price_dates.append(two_years)
        three_years = (40, datetime.datetime.strptime('07062014', "%d%m%Y").date())
        price_dates.append(three_years)
        # create prices for holding
        # prices is a list of HoldingPrice objects for all the price_dates
        prices = TestFactory.create_holding_prices(holding, price_dates)
        # pass in calculate_returns_in_period
        initial_price = 50
        returns = []
        for holdingPrice in prices:
            returns.append(calculate_returns_in_period(initial_price, holdingPrice.price))
        expected_returns = [0.2, 0, 0.2, 1, -0.6, -0.2]
        # assert expected value
        self.assertEqual(returns, expected_returns)
        pass
