import math
from typing import Any, Dict, List, Tuple
import numpy as np


def calculate_directional_accuracy(predicted_directions: List[str], actual_directions: List[str]) -> float:
    """
    Computes percentage of forecasts where predicted direction matched actual outcome.
    Returns float in [0.0, 1.0].
    """
    if not predicted_directions or len(predicted_directions) != len(actual_directions):
        return 0.0

    matches = sum(
        1 for p, a in zip(predicted_directions, actual_directions)
        if p.strip().lower() == a.strip().lower()
    )
    return float(round(matches / len(predicted_directions), 4))


def calculate_brier_score(forecast_probabilities: List[float], actual_outcomes: List[int]) -> float:
    """
    Computes Brier Score: Mean Squared Error of probability forecast against binary outcome.
    BS = (1/N) * sum((prob - actual)^2).
    A score of 0.0 is perfect calibration, 0.25 is random/uninformative, >0.25 is miscalibrated.
    """
    if not forecast_probabilities or len(forecast_probabilities) != len(actual_outcomes):
        return 0.25

    n = len(forecast_probabilities)
    sq_errs = [(p - a) ** 2 for p, a in zip(forecast_probabilities, actual_outcomes)]
    return float(round(sum(sq_errs) / n, 4))


def calculate_volatility_mae(predicted_vols: List[float], realized_vols: List[float]) -> float:
    """Computes Mean Absolute Error between predicted annualized volatility and realized volatility."""
    if not predicted_vols or len(predicted_vols) != len(realized_vols):
        return 0.0

    n = len(predicted_vols)
    errors = [abs(p - r) for p, r in zip(predicted_vols, realized_vols)]
    return float(round(sum(errors) / n, 4))


def calculate_price_forecast_metrics(
    predicted_ranges: List[Tuple[float, float]],
    actual_prices: List[float],
) -> Dict[str, float]:
    """
    Computes:
    - MAE: Mean absolute error of range midpoint vs actual price
    - RMSE: Root mean squared error
    - Interval Coverage: Percentage of actual prices falling within [expected_low, expected_high]
    """
    if not predicted_ranges or len(predicted_ranges) != len(actual_prices):
        return {"mae": 0.0, "rmse": 0.0, "interval_coverage": 0.0}

    n = len(predicted_ranges)
    abs_errors = []
    sq_errors = []
    within_interval = 0

    for (p_low, p_high), actual in zip(predicted_ranges, actual_prices):
        midpoint = (p_low + p_high) / 2.0
        err = actual - midpoint
        abs_errors.append(abs(err))
        sq_errors.append(err ** 2)
        if p_low <= actual <= p_high:
            within_interval += 1

    mae = float(round(sum(abs_errors) / n, 2))
    rmse = float(round(math.sqrt(sum(sq_errors) / n), 2))
    coverage = float(round(within_interval / n, 4))

    return {
        "mae": mae,
        "rmse": rmse,
        "interval_coverage": coverage,
    }
