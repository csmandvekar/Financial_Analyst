import math
import pytest
from packages.agents.market_data.indicators import (
    compute_annualized_volatility,
    compute_rsi,
    compute_sma,
)


def test_compute_sma():
    prices = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert compute_sma(prices, 3) == 40.0
    assert compute_sma(prices, 5) == 30.0
    assert compute_sma([], 5) == 0.0
    assert compute_sma([15.0], 5) == 15.0


def test_compute_rsi():
    # Monotonically increasing prices -> RSI should be high (>70)
    up_prices = [100.0 + i * 2.0 for i in range(25)]
    rsi_up = compute_rsi(up_prices, period=14)
    assert 70.0 <= rsi_up <= 100.0

    # Monotonically decreasing prices -> RSI should be low (<30)
    down_prices = [200.0 - i * 2.0 for i in range(25)]
    rsi_down = compute_rsi(down_prices, period=14)
    assert 0.0 <= rsi_down <= 30.0

    # Short history fallback
    short_prices = [100.0, 101.0, 102.0]
    assert compute_rsi(short_prices, period=14) == 50.0


def test_compute_annualized_volatility():
    # Constant prices -> zero or floor volatility
    flat_prices = [100.0] * 30
    vol_flat = compute_annualized_volatility(flat_prices, window=30)
    assert vol_flat == 0.01

    # Volatile prices
    volatile_prices = [100.0, 105.0, 98.0, 104.0, 95.0, 102.0] * 5
    vol = compute_annualized_volatility(volatile_prices, window=30)
    assert vol > 0.10
