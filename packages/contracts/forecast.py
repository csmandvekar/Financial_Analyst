import math
from typing import Dict, List, Literal
from pydantic import BaseModel, Field, model_validator
from packages.contracts.base import ContractBase


class HorizonForecast(BaseModel):
    horizon: Literal["3m", "6m", "1y"] = Field(..., description="Forecast time horizon")
    bull_probability: float = Field(..., ge=0.0, le=1.0, description="Bullish outcome probability")
    bear_probability: float = Field(..., ge=0.0, le=1.0, description="Bearish outcome probability")
    neutral_probability: float = Field(..., ge=0.0, le=1.0, description="Neutral outcome probability")
    expected_volatility: float = Field(..., ge=0.0, description="Forecasted annualized volatility")
    expected_price_low: float = Field(..., gt=0.0, description="Expected price range low")
    expected_price_high: float = Field(..., gt=0.0, description="Expected price range high")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Horizon confidence score")

    @model_validator(mode="after")
    def validate_probabilities_and_prices(self) -> "HorizonForecast":
        total_prob = self.bull_probability + self.bear_probability + self.neutral_probability
        if not math.isclose(total_prob, 1.0, abs_tol=0.05):
            raise ValueError(f"Probabilities must sum to ~1.0 (got {total_prob:.4f})")
        if self.expected_price_high < self.expected_price_low:
            raise ValueError(
                f"expected_price_high ({self.expected_price_high}) cannot be less than "
                f"expected_price_low ({self.expected_price_low})"
            )
        return self


class SignalBreakdown(BaseModel):
    fundamental_signal: float = Field(..., ge=-1.0, le=1.0, description="Fundamental health score [-1.0, 1.0]")
    sentiment_signal: float = Field(..., ge=-1.0, le=1.0, description="Social & news sentiment score [-1.0, 1.0]")
    sector_signal: float = Field(..., ge=-1.0, le=1.0, description="Sector momentum score [-1.0, 1.0]")
    market_signal: float = Field(..., ge=-1.0, le=1.0, description="Technical market momentum score [-1.0, 1.0]")
    weights_used: Dict[str, float] = Field(..., description="Weight per factor; sum must be ~1.0")

    @model_validator(mode="after")
    def validate_weights(self) -> "SignalBreakdown":
        total_weight = sum(self.weights_used.values())
        if not math.isclose(total_weight, 1.0, abs_tol=0.05):
            raise ValueError(f"Signal weights must sum to 1.0 (got {total_weight:.4f})")
        return self


class ForecastSchema(ContractBase):
    schema_version: str = "1.0.0"
    horizons: List[HorizonForecast] = Field(..., min_length=1, description="Forecasts across horizons (3m, 6m, 1y)")
    signal_breakdown: SignalBreakdown
