"""A real signal, its Fourier coefficients, and three period bands."""
import numpy as np


def compute_spectrum(returns):
    """Return x, X, frequencies, periods, and |X|²."""
    values = np.asarray(returns, dtype=float)
    assert values.ndim == 1 and len(values) >= 4
    assert np.isfinite(values).all()
    x = values - values.mean()
    X = np.fft.rfft(x)
    frequencies = np.fft.rfftfreq(len(x), d=1)
    periods = np.full(len(frequencies), np.inf)
    periods[1:] = 1 / frequencies[1:]
    power = np.abs(X) ** 2
    return x, X, frequencies, periods, power


def make_frequency_masks(periods, low_period=60, high_period=10):
    """Low: T>60; mid: 10<T<=60; high: 2<=T<=10 by default."""
    assert 2 < high_period < low_period
    nonzero = np.isfinite(periods)
    low_mask = nonzero & (periods > low_period)
    mid_mask = (periods > high_period) & (periods <= low_period)
    high_mask = (periods >= 2) & (periods <= high_period)
    return low_mask, mid_mask, high_mask
