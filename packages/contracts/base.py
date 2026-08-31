from datetime import datetime, timezone
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator


class SourceReliability(str, Enum):
    HIGH = "high"       # primary source, e.g. SEC filing, exchange feed
    MEDIUM = "medium"   # reputable secondary source, e.g. news aggregator
    LOW = "low"         # unverified, e.g. social media


class DataProvenance(BaseModel):
    source: str                      # e.g. "sec_edgar", "yfinance", "praw_reddit"
    reliability: SourceReliability
    fetched_at: datetime
    is_degraded: bool = False        # true if this came from a fallback/cache due to upstream failure

    @field_validator("fetched_at")
    @classmethod
    def validate_not_future(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        target = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if target > now:
            # Allow a small 60s clock skew tolerance
            if (target - now).total_seconds() > 60:
                raise ValueError(f"fetched_at cannot be in the future: {v}")
        return v


class ContractBase(BaseModel):
    """Every agent output schema inherits this."""
    schema_version: str = Field(..., description="Semver, e.g. '1.0.0'")
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    generated_at: datetime
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    provenance: List[DataProvenance] = Field(..., min_length=1, description="Data provenance chain")

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("generated_at")
    @classmethod
    def validate_generated_at(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        target = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if target > now and (target - now).total_seconds() > 60:
            raise ValueError(f"generated_at cannot be in the future: {v}")
        return v
