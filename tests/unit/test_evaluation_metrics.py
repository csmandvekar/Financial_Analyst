import math
import pytest
from packages.evaluation.metrics import (
    calculate_brier_score,
    calculate_directional_accuracy,
    calculate_price_forecast_metrics,
    calculate_volatility_mae,
)


def test_directional_accuracy():
    # 3 out of 4 correct -> 0.75
    preds = ["bullish", "bearish", "neutral", "bullish"]
    actuals = ["bullish", "bearish", "bullish", "bullish"]
    acc = calculate_directional_accuracy(preds, actuals)
    assert acc == 0.75

    # 100% correct
    assert calculate_directional_accuracy(["bullish", "bearish"], ["bullish", "bearish"]) == 1.0

    # Empty
    assert calculate_directional_accuracy([], []) == 0.0


def test_brier_score():
    # Perfect predictions: prob=1.0 when outcome=1, prob=0.0 when outcome=0 -> Brier score = 0.0
    perfect_probs = [1.0, 0.0, 1.0]
    perfect_actuals = [1, 0, 1]
    assert calculate_brier_score(perfect_probs, perfect_actuals) == 0.0

    # Completely wrong: prob=1.0 when outcome=0 -> Brier score = 1.0
    wrong_probs = [1.0, 1.0]
    wrong_actuals = [0, 0]
    assert calculate_brier_score(wrong_probs, wrong_actuals) == 1.0

    # 50/50 uniform uninformative -> (0.5 - 1)^2 = 0.25
    uninformative_probs = [0.5, 0.5]
    uninformative_actuals = [1, 0]
    assert calculate_brier_score(uninformative_probs, uninformative_actuals) == 0.25


def test_volatility_mae():
    pred_vols = [0.20, 0.25, 0.30]
    real_vols = [0.22, 0.23, 0.35]
    # Errors: 0.02, 0.02, 0.05 -> Mean = 0.03
    mae = calculate_volatility_mae(pred_vols, real_vols)
    assert round(mae, 4) == 0.03


def test_price_forecast_metrics():
    # 2 predictions:
    # Range 1: [90, 110] (mid=100), actual=105 -> err = 5, within interval
    # Range 2: [180, 220] (mid=200), actual=210 -> err = 10, within interval
    ranges = [(90.0, 110.0), (180.0, 220.0)]
    actuals = [105.0, 210.0]

    metrics = calculate_price_forecast_metrics(ranges, actuals)
    assert metrics["mae"] == 7.5
    assert metrics["interval_coverage"] == 1.0
    assert metrics["rmse"] == round(math.sqrt((25 + 100) / 2.0), 2)
