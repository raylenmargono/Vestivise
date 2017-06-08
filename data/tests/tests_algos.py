import datetime, decimal
from data.models import HoldingPrice
from django.test import TestCase
from helpers.test_factory import TestFactory
from helpers.quant_tools import calculate_returns_in_period


class TestAlgos(TestCase):
    def test_calculate_returns_in_period(self):
        # create holding
        holding = TestFactory.create_holding("foo", "MUTF", ticker=None, cusip=None, morning_star_id=None, sector=None)

        # create price_dates list     price_dates(price, date)
        price_dates = []
        today = (60, datetime.date(2017, 6, 7))
        one_month = (50, datetime.date(2017, 5, 7))
        three_months = (60, datetime.date(2017, 3, 7))
        one_year = (100, datetime.date(2016, 6, 7))
        two_years = (20, datetime.date(2015, 6, 7))
        three_years = (40, datetime.date(2014, 6, 7))

        # append to price_dates
        price_dates.append(today)
        price_dates.append(one_month)
        price_dates.append(three_months)
        price_dates.append(one_year)
        price_dates.append(two_years)
        price_dates.append(three_years)
        # create prices for holding
        TestFactory.create_holding_prices(holding, price_dates)
        closing_price_today = HoldingPrice.objects.get(closing_date=datetime.date(2017, 6, 7)).price
        closing_price_one_month = HoldingPrice.objects.get(closing_date=datetime.date(2017, 5, 7)).price
        closing_price_three_months = HoldingPrice.objects.get(closing_date=datetime.date(2017, 3, 7)).price
        closing_price_one_year = HoldingPrice.objects.get(closing_date=datetime.date(2016, 6, 7)).price
        closing_price_two_years = HoldingPrice.objects.get(closing_date=datetime.date(2015, 6, 7)).price
        closing_price_three_years = HoldingPrice.objects.get(closing_date=datetime.date(2014, 6, 7)).price

        # pass in calculate_returns_in_period
        initial_price = 43
        returns = []
        returns.append(round(calculate_returns_in_period(initial_price, closing_price_today), 3))
        returns.append(round(calculate_returns_in_period(initial_price, closing_price_one_month), 3))
        returns.append(round(calculate_returns_in_period(initial_price, closing_price_three_months), 3))
        returns.append(round(calculate_returns_in_period(initial_price, closing_price_one_year), 3))
        returns.append(round(calculate_returns_in_period(initial_price, closing_price_two_years), 3))
        returns.append(round(calculate_returns_in_period(initial_price, closing_price_three_years), 3))

        expected_returns = [0.395, 0.163, 0.395, 1.326, -0.535, -0.07]
        # assert expected value
        self.assertEqual(returns, expected_returns)