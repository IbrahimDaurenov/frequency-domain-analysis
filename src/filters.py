"""Causal SMA/EMA and their frequency responses."""
import numpy as np
import pandas as pd


def sma_filter(returns, window):
    """Average the current return and previous window-1 returns."""
    return returns.rolling(window=window, min_periods=window).mean()


def ema_filter(returns, alpha):
    """s[t] = alpha*r[t] + (1-alpha)*s[t-1], seeded at r[0]."""
    values = returns.to_numpy()
    filtered = np.empty(len(values))
    filtered[0] = values[0]
    for t in range(1, len(values)):
        filtered[t] = alpha * values[t] + (1 - alpha) * filtered[t - 1]
    return pd.Series(filtered, index=returns.index, name='EMA')


def fir_frequency_response(weights, theta):
    """H(theta) = sum h[n]*exp(+i*theta*n)."""
    response = np.zeros_like(theta, dtype=complex)
    for n, weight in enumerate(weights):
        response += weight * np.exp(1j * theta * n)
    return response


def ema_frequency_response(theta, alpha):
    """H(theta) = alpha / (1 - (1-alpha)*exp(+i*theta))."""
    return alpha / (1 - (1 - alpha) * np.exp(1j * theta))
