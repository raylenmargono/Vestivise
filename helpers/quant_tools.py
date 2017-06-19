import numpy as np


def calculate_returns_in_period(start_price, end_price):
    returns = (end_price - start_price)/start_price
    return round(returns, 3)


def calculate_sharpe_ratio(returns, t_bill):
    risk_free_returns = []
    for i in range(len(returns)):
        risk_free_returns.append(round(returns[i] - t_bill[i], 3))

    sharpe = np.sqrt(12) * np.average(risk_free_returns) / np.std(risk_free_returns, ddof=1)
    return round(sharpe, 3)


def calculate_bottom_line(starting_value, return_rate, years):
    savings = [starting_value]
    for i in range(1, years+1):
        savings.append(round(savings[i-1]*(1+return_rate), 3))
    return savings
