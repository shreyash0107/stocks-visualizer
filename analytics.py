import numpy as np
import pandas as pd

TRADING_DAYS = 252

def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()

def equal_weights(n: int):
    return np.array([1.0/n]*n)

def portfolio_daily(returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    return returns.mul(weights, axis=1).sum(axis=1)

def cumulative_index(series: pd.Series, base=100.0) -> pd.Series:
    return (1.0 + series).cumprod() * base

def portfolio_metrics(port_daily: pd.Series, rf: float = 0.03) -> dict:
    mu = float(port_daily.mean() * TRADING_DAYS)
    sigma = float(port_daily.std() * (TRADING_DAYS ** 0.5))
    sharpe = float((mu - rf) / sigma) if sigma != 0 else 0.0
    return {"expected_return": mu, "volatility": sigma, "sharpe": sharpe}
