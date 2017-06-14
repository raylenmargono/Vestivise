import numpy as np


def calculate_returns_in_period(start_price, end_price):
    return (end_price - start_price)/start_price


def calculate_sharpe_ratio(returns, t_bill, years):
    for i in range(12 * years):
        returns[i] = round(returns[i] - t_bill[i], 3)

    annualized_mean = 12 * np.mean(returns)
    annualized_std = np.std(returns, ddof=1) * np.sqrt(12)

    return annualized_mean/annualized_std


def calculate_bottom_line(holding):
    pass
