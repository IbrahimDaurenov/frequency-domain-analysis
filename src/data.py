"""Adjusted prices and daily log returns."""
import numpy as np
import yfinance as yf


def download_prices(ticker, start, end):
    """Download adjusted daily close; end is exclusive."""
    table = yf.download(ticker, start=start, end=end, auto_adjust=True,
                        multi_level_index=False, progress=False)
    prices = table['Close'].rename(ticker)
    prices.index.name = 'date'
    return prices


def compute_log_returns(prices):
    """r[t] = log(P[t]) - log(P[t-1])."""
    assert prices.index.is_monotonic_increasing and prices.index.is_unique
    assert len(prices) > 2 and prices.notna().all() and (prices > 0).all()
    returns = np.log(prices).diff()
    return returns.iloc[1:]
