import numpy as np


def calculate_returns_in_period(start_price, end_price):
    return (end_price - start_price)/start_price


def calculate_sharpe_ratio(returns, t_bill, years):
    for i in range(12 * years):
        returns[i] = returns[i] - t_bill[i]
    return np.sqrt(12) * np.mean(returns)/np.std(returns)


def calculate_bottom_line(holding):
    pass
