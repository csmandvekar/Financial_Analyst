from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from packages.contracts.base import ContractBase


class NewsArticleRef(BaseModel):
    title: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    published_at: datetime
    source_name: str = Field(..., min_length=1)


class NewsSummarySchema(ContractBase):
    schema_version: str = "1.0.0"
    company_summary: str = Field(..., description="LLM/Synthesized company news summary, traceable to articles")
    sector_summary: str = Field(..., description="Sector developments and trends")
    macro_summary: str = Field(..., description="Macroeconomic environment highlights")
    articles_referenced: List[NewsArticleRef] = Field(default_factory=list, description="Direct citations")
    sentiment_lean: float = Field(..., ge=-1.0, le=1.0, description="Coarse news sentiment polarity [-1.0, 1.0]")
