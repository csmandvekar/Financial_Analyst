from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict
from packages.contracts.financials import FinancialSchema
from packages.contracts.forecast import ForecastSchema
from packages.contracts.market_data import MarketDataSchema
from packages.contracts.news import NewsSummarySchema
from packages.contracts.report import ReportSchema
from packages.contracts.risk import RiskSchema
from packages.contracts.sector import SectorSchema
from packages.contracts.sentiment import SentimentSchema


class OrchestratorState(TypedDict, total=False):
    # Job context
    job_id: str
    ticker: str
    analysis_type: str
    requested_by: str
    started_at: datetime

    # Agent outputs
    market_data: Optional[MarketDataSchema]
    financials: Optional[FinancialSchema]
    news: Optional[NewsSummarySchema]
    sentiment: Optional[SentimentSchema]
    sector: Optional[SectorSchema]
    risk: Optional[RiskSchema]
    forecast: Optional[ForecastSchema]
    report: Optional[ReportSchema]

    # Signal breakdown
    fundamental_signal: float
    sentiment_signal: float
    sector_signal: float
    market_signal: float

    # System & traceability state
    degraded_sources: List[str]
    agent_statuses: Dict[str, str]
    errors: List[str]
    is_completed: bool
