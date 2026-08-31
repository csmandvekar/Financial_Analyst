from datetime import datetime
from typing import Dict, List, Literal
from pydantic import BaseModel, Field
from packages.contracts.base import ContractBase
from packages.contracts.forecast import ForecastSchema
from packages.contracts.risk import RiskSchema


class ReasoningFactor(BaseModel):
    factor: str = Field(..., min_length=1, description="Driver description")
    weight: float = Field(..., ge=0.0, le=1.0, description="Relative importance [0.0, 1.0]")
    direction: Literal["bullish", "bearish", "neutral"] = Field(..., description="Impact direction")


class AgentContribution(BaseModel):
    agent_name: str = Field(..., min_length=1)
    agent_version: str = Field(..., min_length=1)
    status: Literal["success", "degraded", "failed"] = Field(...)


class ReportSchema(ContractBase):
    schema_version: str = "1.0.0"
    analysis_type: str = Field(..., description="e.g. quarterly_outlook, deep_dive")
    executive_summary: str = Field(..., min_length=10, description="High-level executive thesis")
    bull_case: str = Field(..., min_length=10, description="Upside scenarios and catalysts")
    bear_case: str = Field(..., min_length=10, description="Downside risks and vulnerabilities")
    forecast: ForecastSchema
    risk: RiskSchema
    reasoning_factors: List[ReasoningFactor] = Field(default_factory=list)
    agent_contributions: List[AgentContribution] = Field(default_factory=list)
    degraded_sources: List[str] = Field(default_factory=list, description="List of degraded or unavailable sources")
    data_freshness: Dict[str, datetime] = Field(default_factory=dict, description="As-of timestamps per source")
