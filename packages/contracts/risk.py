from typing import List
from pydantic import BaseModel, Field
from packages.contracts.base import ContractBase


class StressScenario(BaseModel):
    name: str = Field(..., min_length=1, description="Scenario label, e.g. 'rate_hike_100bps'")
    estimated_price_impact_pct: float = Field(..., description="Estimated percentage return impact under stress scenario")


class RiskSchema(ContractBase):
    schema_version: str = "1.0.0"
    volatility_band_low: float = Field(..., description="Lower annualized volatility forecast band")
    volatility_band_high: float = Field(..., description="Upper annualized volatility forecast band")
    beta_vs_sector: float = Field(..., description="Calculated beta against sector/peer benchmark")
    macro_exposure_flags: List[str] = Field(default_factory=list, description="Flags like ['rate_sensitive', 'high_debt_load']")
    stress_scenarios: List[StressScenario] = Field(default_factory=list)
