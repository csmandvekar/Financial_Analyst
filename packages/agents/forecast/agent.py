from datetime import datetime, timezone
import logging
import math
from typing import Dict, List, Optional
from packages.agents.base import BaseAgent
from packages.contracts.base import DataProvenance, SourceReliability
from packages.contracts.forecast import ForecastSchema, HorizonForecast, SignalBreakdown
from packages.contracts.market_data import MarketDataSchema
from packages.infra.config import settings

logger = logging.getLogger(__name__)


class ForecastInput:
    def __init__(
        self,
        market_data: MarketDataSchema,
        fundamental_signal: float,
        sentiment_signal: float,
        sector_signal: float,
        market_signal: float,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.market_data = market_data
        self.fundamental_signal = max(-1.0, min(1.0, fundamental_signal))
        self.sentiment_signal = max(-1.0, min(1.0, sentiment_signal))
        self.sector_signal = max(-1.0, min(1.0, sector_signal))
        self.market_signal = max(-1.0, min(1.0, market_signal))
        self.weights = weights or settings.forecast_weights

    def __str__(self) -> str:
        return f"ForecastInput(ticker={self.market_data.ticker})"


class ForecastAgent(BaseAgent[ForecastInput, ForecastSchema]):
    name = "forecast_agent"
    version = "1.0.0"

    async def run(self, input_data: ForecastInput) -> ForecastSchema:
        now = datetime.now(timezone.utc)
        ticker = input_data.market_data.ticker
        current_price = input_data.market_data.current_price
        base_vol = input_data.market_data.indicators.volatility_30d

        provenance = [
            DataProvenance(
                source="ensemble_forecast_engine",
                reliability=SourceReliability.HIGH,
                fetched_at=now,
                is_degraded=False,
            )
        ]

        # Normalize weights to ensure exact sum = 1.0
        raw_weights = input_data.weights
        total_w = sum(raw_weights.values())
        norm_weights = {k: float(round(v / total_w, 4)) for k, v in raw_weights.items()}
        # Correct any minor float rounding difference on the largest weight
        diff = 1.0 - sum(norm_weights.values())
        if abs(diff) > 1e-6:
            max_k = max(norm_weights, key=norm_weights.get)
            norm_weights[max_k] = float(round(norm_weights[max_k] + diff, 4))

        # Composite score in [-1.0, 1.0]
        composite_score = (
            norm_weights["fundamental"] * input_data.fundamental_signal
            + norm_weights["sentiment"] * input_data.sentiment_signal
            + norm_weights["sector"] * input_data.sector_signal
            + norm_weights["market"] * input_data.market_signal
        )
        composite_score = max(-1.0, min(1.0, composite_score))

        signal_breakdown = SignalBreakdown(
            fundamental_signal=float(round(input_data.fundamental_signal, 3)),
            sentiment_signal=float(round(input_data.sentiment_signal, 3)),
            sector_signal=float(round(input_data.sector_signal, 3)),
            market_signal=float(round(input_data.market_signal, 3)),
            weights_used=norm_weights,
        )

        horizons: List[HorizonForecast] = []
        horizon_params = [
            ("3m", 0.25, 0.85),
            ("6m", 0.50, 0.80),
            ("1y", 1.00, 0.75),
        ]

        for h_label, t_factor, conf_base in horizon_params:
            # Probability calculation based on composite score
            # A score > 0 increases bull prob, < 0 increases bear prob
            score_magnitude = abs(composite_score)
            if composite_score >= 0:
                bull_p = 0.33 + (score_magnitude * 0.42)
                bear_p = max(0.08, 0.33 - (score_magnitude * 0.25))
            else:
                bear_p = 0.33 + (score_magnitude * 0.42)
                bull_p = max(0.08, 0.33 - (score_magnitude * 0.25))

            neutral_p = max(0.10, 1.0 - (bull_p + bear_p))
            # Normalize triple to sum exactly to 1.0
            sum_p = bull_p + bear_p + neutral_p
            bull_p = float(round(bull_p / sum_p, 4))
            bear_p = float(round(bear_p / sum_p, 4))
            neutral_p = float(round(1.0 - (bull_p + bear_p), 4))

            # Volatility scaling with horizon
            exp_vol = float(round(base_vol * math.sqrt(t_factor), 4))

            # Expected price boundaries based on volatility and direction
            drift = composite_score * 0.15 * t_factor
            vol_range = current_price * exp_vol * 1.645  # ~90% confidence range
            expected_low = float(round(max(1.0, current_price * (1.0 + drift) - vol_range), 2))
            expected_high = float(round(current_price * (1.0 + drift) + vol_range, 2))

            horizons.append(
                HorizonForecast(
                    horizon=h_label,
                    bull_probability=bull_p,
                    bear_probability=bear_p,
                    neutral_probability=neutral_p,
                    expected_volatility=exp_vol,
                    expected_price_low=expected_low,
                    expected_price_high=expected_high,
                    confidence=float(round(conf_base * (1.0 - 0.2 * base_vol), 2)),
                )
            )

        return ForecastSchema(
            schema_version=self.version,
            ticker=ticker,
            generated_at=now,
            confidence=0.88,
            provenance=provenance,
            horizons=horizons,
            signal_breakdown=signal_breakdown,
        )
