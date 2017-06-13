import datetime, numpy as np
from data.models import HoldingPrice, TreasuryBondValue
from django.test import TestCase
from helpers.test_factory import TestFactory
from helpers.quant_tools import calculate_returns_in_period, calculate_sharpe_ratio
from dateutil.relativedelta import relativedelta


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

    def test_calculate_sharpe_ratio(self):
        # create holding
        holding = TestFactory.create_holding("foo", "MUTF", ticker=None, cusip=None, morning_star_id=None, sector=None)

        # create list of closing prices
        prices = [60, 54, 53, 50, 53, 55, 60, 65, 43, 54, 66, 70,
                  76, 80, 67, 63, 60, 58, 50, 46, 42, 40, 38, 46,
                  60, 78, 80, 89, 92, 100, 123, 121, 102, 98, 86, 80]

        # create list of risk-free rates (%)
        rates = [2, 6, 6, 7, 7, 5, 7, 9, 7, 11, 13, 4,
                 5, 8, 8, 5, 2, 3, 2, 4, 2, 11, 5, 2,
                 4, 5, 2, 3, 4, 8, 9, 10, 6, 2, 7, 4]

        initial_price = 43
        start_date = datetime.date(2014, 5, 13)  # three years ago
        price_dates = []
        risk_free_rates = []

        for i in range(0, 36):
            price_dates.append((prices[i], start_date + relativedelta(months=i)))
            risk_free_rates.append((rates[i], start_date + relativedelta(months=i)))

        # create prices for holding
        TestFactory.create_holding_prices(holding, price_dates)
        # create treasury bonds with above rates
        TestFactory.create_treasury_bond_rates(risk_free_rates)

        # get returns and risk-free rates
        returns = []
        t_bill = []

        for i in range(0,36):
            holding = HoldingPrice.objects.get(closing_date=(start_date + relativedelta(months=i)))
            returns.append(round(calculate_returns_in_period(initial_price, holding.price), 3))
            t_bond = TreasuryBondValue.objects.get(date=(start_date + relativedelta(months=i)))
            t_bill.append(t_bond.value/100)

        # calculate sharpe ratio
        sharpe = round(calculate_sharpe_ratio(returns, t_bill, 3), 3)

        # expected_returns = [0.395, 0.256, 0.233, 0.163, 0.233, 0.279, 0.395, 0.512, 0, 0.256, 0.535, 0.628,
        #                     0.767, 0.86, 0.558, 0.465, 0.395, 0.349, 0.163, 0.07, -0.023, -0.07, -0.116, 0.07,
        #                     0.395, 0.814, 0.86, 1.07, 1.14, 1.326, 1.86, 1.814, 1.372, 1.279, 1, 0.86]

        # expected_returns_minus_rfr = [0.375, 0.196, 0.173, 0.093, 0.163, 0.229, 0.325, 0.422, -0.07, 0.146, 0.405, 0.588,
        #                               0.717, 0.78, 0.478, 0.415, 0.375, 0.319, 0.143, 0.03, -0.043, -0.18, -0.166, 0.05,
        #                               0.355, 0.764, 0.84, 1.04, 1.1, 1.246, 1.77, 1.714, 1.312, 1.259, 0.93, 0.82]

        # mean = 0.531
        # std = 0.5
        expected_sharpe = 3.68

        # assert expected value
        self.assertEqual(sharpe, expected_sharpe)
        pass
