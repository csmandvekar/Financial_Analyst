from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from packages.evaluation.backfill import backfill_forecast_outcomes
from packages.evaluation.backtest import BacktestRunner
from packages.evaluation.metrics import (
    calculate_brier_score,
    calculate_directional_accuracy,
    calculate_price_forecast_metrics,
    calculate_volatility_mae,
)
from packages.infra.db.models import ForecastOutcome
from packages.infra.db.session import AsyncSessionLocal

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Backtesting"])


class BacktestRequest(BaseModel):
    tickers: Optional[List[str]] = Field(default=None, json_schema_extra={"example": ["AAPL", "MSFT", "NVDA"]})
    lookback_days: int = Field(default=180, ge=30, le=720)
    horizon: str = Field(default="3m", json_schema_extra={"example": "3m"})


@router.post("/backtest", summary="Run offline historical backtest evaluation")
async def trigger_backtest(request: BacktestRequest):
    """
    Executes backtesting simulation over historical price data,
    evaluating directional accuracy, Brier score, and forecast error.
    """
    runner = BacktestRunner(tickers=request.tickers)
    try:
        summary = await runner.run_backtest(
            lookback_days=request.lookback_days,
            horizon=request.horizon,
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest execution failed: {str(e)}")


@router.get("/metrics", summary="Get aggregated forecast evaluation metrics")
async def get_evaluation_metrics(horizon: Optional[str] = Query(None, description="Filter by horizon (3m, 6m, 1y)")):
    """
    Retrieves global forecast accuracy metrics across all evaluated forecast outcomes:
    - Directional Accuracy (%)
    - Brier Calibration Score
    - Volatility MAE
    - Price RMSE & MAE
    - Interval Coverage
    """
    async with AsyncSessionLocal() as session:
        stmt = select(ForecastOutcome)
        if horizon:
            stmt = stmt.where(ForecastOutcome.horizon == horizon)
        res = await session.execute(stmt)
        outcomes = res.scalars().all()

        if not outcomes:
            return {
                "sample_size": 0,
                "metrics": {
                    "directional_accuracy": 0.0,
                    "brier_calibration_score": 0.25,
                    "volatility_mae": 0.0,
                    "price_mae": 0.0,
                    "price_rmse": 0.0,
                    "interval_coverage": 0.0,
                },
            }

        pred_dirs = [o.predicted_direction for o in outcomes]
        act_dirs = [o.actual_direction for o in outcomes]
        conf_probs = [o.predicted_confidence for o in outcomes]
        act_bins = [1 if o.is_direction_correct else 0 for o in outcomes]
        ranges = [(o.predicted_price_low, o.predicted_price_high) for o in outcomes]
        actual_prices = [o.actual_price for o in outcomes]

        dir_acc = calculate_directional_accuracy(pred_dirs, act_dirs)
        brier = calculate_brier_score(conf_probs, act_bins)
        price_metrics = calculate_price_forecast_metrics(ranges, actual_prices)

        return {
            "sample_size": len(outcomes),
            "horizon_filter": horizon or "all",
            "metrics": {
                "directional_accuracy": dir_acc,
                "brier_calibration_score": brier,
                "price_mae": price_metrics["mae"],
                "price_rmse": price_metrics["rmse"],
                "interval_coverage": price_metrics["interval_coverage"],
            },
        }


@router.get("/outcomes", summary="List historical forecast evaluation outcomes")
async def list_outcomes(limit: int = Query(50, le=200)):
    """Lists recent individual forecast evaluation records."""
    async with AsyncSessionLocal() as session:
        stmt = select(ForecastOutcome).order_by(ForecastOutcome.evaluated_at.desc()).limit(limit)
        res = await session.execute(stmt)
        outcomes = res.scalars().all()

        return [
            {
                "id": o.id,
                "ticker": o.ticker,
                "horizon": o.horizon,
                "prediction_date": o.prediction_date,
                "predicted_direction": o.predicted_direction,
                "actual_direction": o.actual_direction,
                "is_direction_correct": o.is_direction_correct,
                "predicted_price_low": o.predicted_price_low,
                "predicted_price_high": o.predicted_price_high,
                "actual_price": o.actual_price,
                "price_error_abs": o.price_error_abs,
                "evaluated_at": o.evaluated_at,
            }
            for o in outcomes
        ]


@router.post("/backfill", summary="Trigger outcome backfill for matured forecasts")
async def trigger_backfill():
    """Checks for completed forecasts whose horizons have passed and evaluates outcomes."""
    res = await backfill_forecast_outcomes()
    return res
