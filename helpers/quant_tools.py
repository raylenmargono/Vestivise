import numpy as np
import pandas as pd


def calculate_returns_in_period(start_price, end_price):
    # get_returns_in_period in models Holding.get_returns_in_period
    return (end_price - start_price)/start_price


def calculate_sharpe_ratio(returns, t_bill, years):
    # returns is an array of monthly returns
    # return (np.average(returns)-rfr/100)/np.std(returns)
    for i in range(12 * years):
        returns[i] = returns[i] - t_bill[i]
    return np.sqrt(12) * np.mean(returns)/np.std(returns)


def calculate_bottom_line(holding):
    pass
