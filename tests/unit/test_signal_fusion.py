from packages.orchestrator.nodes.signal import (
    calculate_fundamental_signal,
    calculate_market_signal,
)


def test_calculate_fundamental_signal():
    # Strong fundamentals
    sig_strong = calculate_fundamental_signal(
        net_margin=0.25,
        gross_margin=0.50,
        debt_to_equity=0.30,
        current_ratio=2.0,
    )
    assert 0.5 <= sig_strong <= 1.0

    # Weak fundamentals
    sig_weak = calculate_fundamental_signal(
        net_margin=-0.05,
        gross_margin=0.15,
        debt_to_equity=2.5,
        current_ratio=0.8,
    )
    assert -1.0 <= sig_weak <= -0.4


def test_calculate_market_signal():
    # Bullish technicals: Price above moving averages, strong RSI
    sig_bull = calculate_market_signal(
        current_price=150.0,
        sma_20=140.0,
        sma_50=130.0,
        rsi_14=65.0,
    )
    assert 0.4 <= sig_bull <= 1.0

    # Bearish technicals: Price below moving averages, oversold RSI
    sig_bear = calculate_market_signal(
        current_price=100.0,
        sma_20=115.0,
        sma_50=125.0,
        rsi_14=32.0,
    )
    assert -1.0 <= sig_bear <= -0.3
