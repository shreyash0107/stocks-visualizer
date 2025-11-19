import numpy as np
import pandas as pd

def simulate_paths(initial_value: float, mu: float, sigma: float,
                   days: int = 252, sims: int = 300, seed: int | None = None) -> pd.DataFrame:
    """
    Geometric Brownian Motion simulation for portfolio value.
    Returns a DataFrame: rows=days+1, cols=sims
    """
    rng = np.random.default_rng(seed)
    dt = 1/252
    drift = (mu - 0.5*(sigma**2)) * dt
    shocks = sigma * (dt ** 0.5) * rng.standard_normal((days, sims))
    log_returns = drift + shocks
    paths = initial_value * np.exp(log_returns.cumsum(axis=0))
    paths = np.vstack([np.full((1, sims), initial_value), paths])  # include day 0
    return pd.DataFrame(paths)

def percentiles(paths: pd.DataFrame, q=(5, 50, 95)) -> pd.DataFrame:
    return paths.quantile([x/100 for x in q], axis=1).T
