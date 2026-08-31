from typing import List, Optional
from pydantic import BaseModel, Field
from packages.contracts.base import ContractBase


class PeerComparison(BaseModel):
    ticker: str = Field(..., min_length=1)
    market_cap: float = Field(..., gt=0.0)
    price_change_30d: float = Field(..., description="30-day percentage price change")
    pe_ratio: Optional[float] = Field(default=None, description="Trailing or forward P/E ratio")


class SectorSchema(ContractBase):
    schema_version: str = "1.0.0"
    sector_name: str = Field(..., min_length=1)
    sector_price_change_30d: float = Field(..., description="Sector average 30-day percentage price change")
    peers: List[PeerComparison] = Field(default_factory=list)
    relative_performance: float = Field(..., description="Target ticker 30d return minus sector benchmark")
