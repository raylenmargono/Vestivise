import datetime, numpy as np
from data.models import HoldingPrice, TreasuryBondValue
from django.test import TestCase
from helpers.test_factory import TestFactory
from helpers.quant_tools import calculate_returns_in_period, calculate_sharpe_ratio, calculate_bottom_line
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
        returns.append(calculate_returns_in_period(initial_price, closing_price_today))
        returns.append(calculate_returns_in_period(initial_price, closing_price_one_month))
        returns.append(calculate_returns_in_period(initial_price, closing_price_three_months))
        returns.append(calculate_returns_in_period(initial_price, closing_price_one_year))
        returns.append(calculate_returns_in_period(initial_price, closing_price_two_years))
        returns.append(calculate_returns_in_period(initial_price, closing_price_three_years))

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

        holdings = HoldingPrice.objects.filter(closing_date__gte=start_date)
        t_bond_rates = TreasuryBondValue.objects.filter(date__gte=start_date)

        current_holding = holdings[0]
        returns.append(calculate_returns_in_period(initial_price, current_holding.price))
        t_bond = t_bond_rates[0]
        t_bill.append(t_bond.value / 100)

        for i in range(1,36):
            current_holding = holdings[i]
            prev_holding = holdings[i-1]
            returns.append(calculate_returns_in_period(prev_holding.price, current_holding.price))
            t_bond = t_bond_rates[i]
            t_bill.append(t_bond.value/100)

        returns_one_year = [0.055, 0.008, -0.085, 0.104, 0.013, 0.004, 0.008, 0.012, 0.009, 0.011, 0.019, 0.006]
        t_bill_one_year = [0.004, 0.004, 0.004, 0.004, 0.004, 0.004, 0.004, 0.004, 0.004, 0.004, 0.004, 0.004]
        returns_two_years = [2.54, 6.06, -0.75, -6.46, 1.39, 0.21, -0.15, 6.47, -6.23, -1.86, 0.78, 6.01,
                             -0.69, 6.21, -5.04, 3.19, -8.13, 2.06, -6.08, 1.6, -3.23, 0.8, 4.39, -5.81]
        t_bill_two_years = [0.02, 0.06, 0.06, 0.07, 0.07, 0.05, 0.07, 0.09, 0.07, 0.11, 0.13, 0.04,
                            0.05, 0.08, 0.08, 0.05, 0.02, 0.03, 0.02, 0.04, 0.02, 0.11, 0.05, 0.02]

        # calculate sharpe ratio
        sharpe = calculate_sharpe_ratio(returns, t_bill)
        sharpe_one_year = calculate_sharpe_ratio(returns_one_year, t_bill_one_year)
        sharpe_two_years = calculate_sharpe_ratio(returns_two_years, t_bill_two_years)

        expected_sharpe = -0.639
        expected_sharpe_one_year = 0.788
        expected_sharpe_two_years = -0.134

        # assert expected value
        self.assertEqual(sharpe, expected_sharpe)
        self.assertEqual(sharpe_one_year, expected_sharpe_one_year)
        self.assertEqual(sharpe_two_years, expected_sharpe_two_years)

    def test_calculate_bottom_line(self):
        # create holding
        holding = TestFactory.create_holding("foo", "MUTF", ticker=None, cusip=None, morning_star_id=None, sector=None)

        initial_price = 43
        prices = [40, 20, 100, 60]      # create list of closing prices
        price_dates = []        # create price_dates list
        start_date = datetime.date(2014, 6, 19)     # three years ago

        # append to price_dates
        for i in range(0, 4):
            price_dates.append((prices[i], start_date + relativedelta(years=i)))

        # create prices for holding
        TestFactory.create_holding_prices(holding, price_dates)
        holdings = HoldingPrice.objects.filter(closing_date__gte=start_date)

        # get annual returns for last three years
        annual_returns = []
        # current_holding = holdings[0]
        # annual_returns.append(calculate_returns_in_period(initial_price, current_holding.price))
        for i in range(1, 4):
            current_holding = holdings[i]
            prev_holding = holdings[i - 1]
            annual_returns.append(calculate_returns_in_period(prev_holding.price, current_holding.price))

        # get normalized average
        normalized_annual_returns = []
        value_range = max(annual_returns) - min(annual_returns)
        for i in range(0, len(annual_returns)):
            normalized_annual_returns.append(round(((annual_returns[i] - min(annual_returns))/value_range), 3))
        average_annual_return = round(np.mean(normalized_annual_returns), 3)

        print annual_returns
        print normalized_annual_returns
        print average_annual_return
        fees = []
        inflation = 0.019
        starting_value = 100

        return_rate = average_annual_return
        # return_rate_fees = average_annual_return - fees
        # return_rate_fees_inflation = average_annual_return - fees - inflation

        savings = calculate_bottom_line(starting_value, return_rate, years=10)
        # savings_fees = calculate_bottom_line(starting_value, return_rate_fees, years=10)
        # savings_fees_inflation = calculate_bottom_line(starting_value, return_rate_fees_inflation, years=10)

        expected_savings = [100, 134.1, 179.823, 241.149, 323.381, 433.655,
                            581.531, 779.833, 1045.756, 1402.359, 1880.563]
        # expected_savings_fees = []
        # expected_savings_fees_inflation = []

        # assert expected value
        self.assertEqual(savings, expected_savings)
        # self.assertEqual(savings_fees, expected_savings_fees)
        # self.assertEqual(savings_fees_inflation, expected_savings_fees_inflation)
        pass
