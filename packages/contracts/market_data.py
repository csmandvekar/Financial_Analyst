from datetime import datetime
from typing import List, Tuple
from pydantic import BaseModel, Field, model_validator
from packages.contracts.base import ContractBase


class TechnicalIndicators(BaseModel):
    sma_20: float = Field(..., description="20-day Simple Moving Average")
    sma_50: float = Field(..., description="50-day Simple Moving Average")
    rsi_14: float = Field(..., ge=0.0, le=100.0, description="14-day Relative Strength Index [0, 100]")
    volatility_30d: float = Field(..., ge=0.0, description="Annualized standard deviation of 30-day daily returns")


class MarketDataSchema(ContractBase):
    schema_version: str = "1.0.0"
    current_price: float = Field(..., gt=0.0, description="Current market price")
    volume: int = Field(..., ge=0, description="Trading volume")
    market_cap: float = Field(..., gt=0.0, description="Total market capitalization")
    fifty_two_week_high: float = Field(..., gt=0.0, description="52-week high price")
    fifty_two_week_low: float = Field(..., gt=0.0, description="52-week low price")
    indicators: TechnicalIndicators
    price_history: List[Tuple[datetime, float]] = Field(
        default_factory=list,
        description="Historical (date, close) price pairs bounded to lookback window"
    )

    @model_validator(mode="after")
    def validate_high_gte_low(self) -> "MarketDataSchema":
        if self.fifty_two_week_high < self.fifty_two_week_low:
            raise ValueError(
                f"52-week high ({self.fifty_two_week_high}) cannot be less than 52-week low ({self.fifty_two_week_low})"
            )
        return self
