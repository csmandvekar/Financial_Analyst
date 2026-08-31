from typing import List
from pydantic import BaseModel, Field
from packages.contracts.base import ContractBase


class PlatformSentiment(BaseModel):
    platform: str = Field(..., description="e.g. reddit, stocktwits, news")
    mention_volume: int = Field(..., ge=0)
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sample_size: int = Field(..., ge=0)


class SentimentSchema(ContractBase):
    schema_version: str = "1.0.0"
    aggregate_sentiment: float = Field(..., ge=-1.0, le=1.0, description="Volume-weighted aggregate sentiment [-1.0, 1.0]")
    aggregate_mention_volume: int = Field(..., ge=0, description="Total mention count across platforms")
    by_platform: List[PlatformSentiment] = Field(default_factory=list)
    degraded: bool = Field(default=False, description="True if one or more platforms failed or fell back to defaults")
