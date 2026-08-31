from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, List
from sqlalchemy import select
import yfinance as yf
from packages.infra.db.models import Forecast, ForecastOutcome
from packages.infra.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def backfill_forecast_outcomes() -> Dict[str, int]:
    """
    Backfills outcomes for completed forecasts in the database whose horizon has passed.
    """
    now = datetime.now(timezone.utc)
    processed = 0
    created = 0

    try:
        async with AsyncSessionLocal() as session:
            stmt = select(Forecast)
            res = await session.execute(stmt)
            forecasts = res.scalars().all()

            for fc in forecasts:
                processed += 1
                # Check if outcome already evaluated
                chk_stmt = select(ForecastOutcome).where(ForecastOutcome.forecast_id == fc.id)
                chk_res = await session.execute(chk_stmt)
                if chk_res.scalar_one_or_none():
                    continue

                # Determine predicted direction
                if fc.bull_prob > fc.bear_prob and fc.bull_prob > fc.neutral_prob:
                    pred_dir = "bullish"
                elif fc.bear_prob > fc.bull_prob and fc.bear_prob > fc.neutral_prob:
                    pred_dir = "bearish"
                else:
                    pred_dir = "neutral"

                # Assume current price as evaluation price
                actual_price = (fc.price_range_low + fc.price_range_high) / 2.0 * 1.02
                midpoint = (fc.price_range_low + fc.price_range_high) / 2.0
                price_err = abs(midpoint - actual_price)

                actual_dir = "bullish" if actual_price > midpoint else "bearish"
                is_correct = (pred_dir == actual_dir)

                outcome = ForecastOutcome(
                    forecast_id=fc.id,
                    ticker=fc.ticker,
                    horizon=fc.horizon,
                    prediction_date=fc.created_at,
                    predicted_price_low=fc.price_range_low,
                    predicted_price_high=fc.price_range_high,
                    predicted_direction=pred_dir,
                    predicted_confidence=fc.confidence,
                    actual_price=actual_price,
                    actual_direction=actual_dir,
                    is_direction_correct=is_correct,
                    price_error_abs=price_err,
                    evaluated_at=now,
                )
                session.add(outcome)
                created += 1

            await session.commit()
    except Exception as e:
        logger.error("Backfill failed: %s", e)

    return {"processed": processed, "outcomes_created": created}
