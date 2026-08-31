import math
from typing import List, Tuple
import numpy as np


def compute_sma(prices: List[float], window: int) -> float:
    """Calculates Simple Moving Average over window size."""
    if not prices or len(prices) < window:
        return float(np.mean(prices)) if prices else 0.0
    return float(np.mean(prices[-window:]))


def compute_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculates Relative Strength Index (RSI) using standard Wilder's smoothing.
    Returns float between 0.0 and 100.0.
    """
    if len(prices) < period + 1:
        return 50.0  # Neutral fallback for short history

    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return float(np.clip(rsi, 0.0, 100.0))


def compute_annualized_volatility(prices: List[float], window: int = 30) -> float:
    """
    Calculates annualized volatility from daily log returns over the lookback window.
    Assumes 252 trading days per year.
    """
    if len(prices) < 2:
        return 0.20  # Default market vol ~20%

    sub_prices = prices[-window:] if len(prices) >= window else prices
    returns = np.diff(sub_prices) / sub_prices[:-1]
    daily_std = float(np.std(returns, ddof=1)) if len(returns) > 1 else 0.01
    annualized_vol = daily_std * math.sqrt(252)
    return float(max(0.01, annualized_vol))
