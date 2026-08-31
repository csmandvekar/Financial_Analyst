from datetime import datetime, timezone
import logging
from typing import List, Optional
from packages.agents.base import BaseAgent
from packages.contracts.base import DataProvenance, SourceReliability
from packages.contracts.financials import FinancialSchema
from packages.contracts.market_data import MarketDataSchema
from packages.contracts.risk import RiskSchema, StressScenario

logger = logging.getLogger(__name__)


class RiskInput:
    def __init__(self, market_data: MarketDataSchema, financials: FinancialSchema):
        self.market_data = market_data
        self.financials = financials

    def __str__(self) -> str:
        return f"RiskInput(ticker={self.market_data.ticker})"


class RiskAgent(BaseAgent[RiskInput, RiskSchema]):
    name = "risk_agent"
    version = "1.0.0"

    async def run(self, input_data: RiskInput) -> RiskSchema:
        now = datetime.now(timezone.utc)
        m = input_data.market_data
        f = input_data.financials
        ticker = m.ticker

        provenance = [
            DataProvenance(
                source="quantitative_risk_engine",
                reliability=SourceReliability.HIGH,
                fetched_at=now,
                is_degraded=False,
            )
        ]

        vol = m.indicators.volatility_30d
        vol_band_low = float(round(max(0.05, vol * 0.75), 4))
        vol_band_high = float(round(vol * 1.35, 4))

        # Leverage & Beta estimation
        debt_to_equity = f.ratios.debt_to_equity
        net_margin = f.ratios.net_margin
        current_ratio = f.ratios.current_ratio

        # Estimated beta based on volatility scaling against market baseline (0.18)
        base_beta = vol / 0.18
        beta_vs_sector = float(round(max(0.5, min(2.5, base_beta * (1.0 + min(0.3, debt_to_equity * 0.1)))), 2))

        # Macro exposure flags
        macro_flags: List[str] = []
        if debt_to_equity > 1.2:
            macro_flags.append("high_debt_load")
        if debt_to_equity > 0.8 or beta_vs_sector > 1.2:
            macro_flags.append("rate_sensitive")
        if net_margin < 0.10:
            macro_flags.append("margin_compression_risk")
        if current_ratio < 1.1:
            macro_flags.append("short_term_liquidity_watch")
        if not macro_flags:
            macro_flags.append("resilient_balance_sheet")

        # Stress test scenarios
        stress_scenarios = [
            StressScenario(
                name="rate_hike_100bps",
                estimated_price_impact_pct=float(round(-3.5 * (1.0 + min(1.0, debt_to_equity)), 2)),
            ),
            StressScenario(
                name="sector_selloff_20pct",
                estimated_price_impact_pct=float(round(-20.0 * beta_vs_sector, 2)),
            ),
            StressScenario(
                name="earnings_multiple_contraction_15pct",
                estimated_price_impact_pct=float(round(-15.0 * (0.8 + 0.2 * beta_vs_sector), 2)),
            ),
        ]

        return RiskSchema(
            schema_version=self.version,
            ticker=ticker,
            generated_at=now,
            confidence=0.91,
            provenance=provenance,
            volatility_band_low=vol_band_low,
            volatility_band_high=vol_band_high,
            beta_vs_sector=beta_vs_sector,
            macro_exposure_flags=macro_flags,
            stress_scenarios=stress_scenarios,
        )
