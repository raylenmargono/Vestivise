import numpy as np


def calculate_returns_in_period(start_price, end_price):
    return (end_price - start_price)/start_price


def calculate_sharpe_ratio(returns, t_bill):
    for i in range(len(returns)):
        returns[i] = round(returns[i] - t_bill[i], 3)

    return np.sqrt(12) * np.average(returns) / np.std(returns, ddof=1)


def calculate_bottom_line(holding):
    pass
