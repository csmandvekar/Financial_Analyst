from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional
from packages.agents.base import BaseAgent
from packages.contracts.base import DataProvenance, SourceReliability
from packages.contracts.financials import FinancialSchema
from packages.contracts.forecast import ForecastSchema
from packages.contracts.market_data import MarketDataSchema
from packages.contracts.news import NewsSummarySchema
from packages.contracts.report import AgentContribution, ReasoningFactor, ReportSchema
from packages.contracts.risk import RiskSchema
from packages.contracts.sector import SectorSchema
from packages.contracts.sentiment import SentimentSchema

logger = logging.getLogger(__name__)


class ReportInput:
    def __init__(
        self,
        analysis_type: str,
        market_data: MarketDataSchema,
        financials: FinancialSchema,
        news: NewsSummarySchema,
        sentiment: SentimentSchema,
        sector: SectorSchema,
        risk: RiskSchema,
        forecast: ForecastSchema,
        degraded_sources: Optional[List[str]] = None,
        agent_statuses: Optional[Dict[str, str]] = None,
    ):
        self.analysis_type = analysis_type
        self.market_data = market_data
        self.financials = financials
        self.news = news
        self.sentiment = sentiment
        self.sector = sector
        self.risk = risk
        self.forecast = forecast
        self.degraded_sources = degraded_sources or []
        self.agent_statuses = agent_statuses or {}

    def __str__(self) -> str:
        return f"ReportInput(ticker={self.market_data.ticker}, type={self.analysis_type})"


class ReportAgent(BaseAgent[ReportInput, ReportSchema]):
    name = "report_agent"
    version = "1.0.0"

    async def run(self, input_data: ReportInput) -> ReportSchema:
        now = datetime.now(timezone.utc)
        m = input_data.market_data
        f = input_data.financials
        n = input_data.news
        s = input_data.sentiment
        sec = input_data.sector
        r = input_data.risk
        fc = input_data.forecast
        ticker = m.ticker

        provenance = [
            DataProvenance(
                source="report_synthesis_engine",
                reliability=SourceReliability.HIGH,
                fetched_at=now,
                is_degraded=len(input_data.degraded_sources) > 0,
            )
        ]

        # Determine prevailing sentiment/direction
        fund_sig = fc.signal_breakdown.fundamental_signal
        mkt_sig = fc.signal_breakdown.market_signal
        sent_sig = fc.signal_breakdown.sentiment_signal
        sec_sig = fc.signal_breakdown.sector_signal

        h_3m = next((h for h in fc.horizons if h.horizon == "3m"), fc.horizons[0])
        h_1y = next((h for h in fc.horizons if h.horizon == "1y"), fc.horizons[-1])

        # Synthesize Executive Summary
        bias = "bullish" if h_3m.bull_probability > h_3m.bear_probability else "bearish"
        if abs(h_3m.bull_probability - h_3m.bear_probability) < 0.10:
            bias = "balanced/neutral"

        exec_summary = (
            f"Comprehensive {input_data.analysis_type.replace('_', ' ').title()} for {ticker}: "
            f"Trading at ${m.current_price:.2f} (52W range: ${m.fifty_two_week_low:.2f} - ${m.fifty_two_week_high:.2f}). "
            f"The quantitative multi-factor model indicates a {bias} outlook with a 3-month bull probability of "
            f"{h_3m.bull_probability * 100:.1f}% vs bear probability of {h_3m.bear_probability * 100:.1f}%. "
            f"Key fundamentals reflect a net margin of {f.ratios.net_margin * 100:.1f}%, debt-to-equity ratio of {f.ratios.debt_to_equity:.2f}, "
            f"and relative sector performance of {sec.relative_performance:+.2f}% vs peer benchmark '{sec.sector_name}'. "
            f"Expected 1-year trading channel spans ${h_1y.expected_price_low:.2f} to ${h_1y.expected_price_high:.2f}."
        )

        # Bull Case
        bull_points = [
            f"Strong margin profile with net margin of {f.ratios.net_margin * 100:.1f}% and healthy gross margin of {f.ratios.gross_margin * 100:.1f}%.",
            f"Favorable sector momentum outperforming '{sec.sector_name}' peers by {sec.relative_performance:+.2f}%.",
            f"Constructive community sentiment (+{s.aggregate_sentiment:.2f}) with active social engagement of {s.aggregate_mention_volume:,} mentions.",
            f"Technical momentum holding above moving averages (SMA20: ${m.indicators.sma_20:.2f}, SMA50: ${m.indicators.sma_50:.2f}, RSI14: {m.indicators.rsi_14:.1f}).",
        ]
        bull_case = " ".join(bull_points)

        # Bear Case
        bear_points = [
            f"Macro and rate sensitivity flagged with estimated beta of {r.beta_vs_sector:.2f} vs sector.",
            f"Downside stress test: a 100bps rate increase is projected to cause an estimated price impact of {next((sc.estimated_price_impact_pct for sc in r.stress_scenarios if 'rate_hike' in sc.name), -5.0):+.1f}%.",
            f"30-day realized annualized volatility of {m.indicators.volatility_30d * 100:.1f}% exposes position to short-term market drawdowns.",
            f"Active risk tags identified: {', '.join(r.macro_exposure_flags)}.",
        ]
        bear_case = " ".join(bear_points)

        # Reasoning Factors
        reasoning_factors = [
            ReasoningFactor(
                factor="Fundamental Margins & Balance Sheet Quality",
                weight=fc.signal_breakdown.weights_used.get("fundamental", 0.35),
                direction="bullish" if fund_sig >= 0 else "bearish",
            ),
            ReasoningFactor(
                factor="Sector Relative Strength & Peer Momentum",
                weight=fc.signal_breakdown.weights_used.get("sector", 0.25),
                direction="bullish" if sec_sig >= 0 else "bearish",
            ),
            ReasoningFactor(
                factor="Technical Trend & Volatility Structure",
                weight=fc.signal_breakdown.weights_used.get("market", 0.25),
                direction="bullish" if mkt_sig >= 0 else "bearish",
            ),
            ReasoningFactor(
                factor="News Flow & Social Media Sentiment",
                weight=fc.signal_breakdown.weights_used.get("sentiment", 0.15),
                direction="bullish" if sent_sig >= 0 else "bearish",
            ),
        ]

        # Agent contributions
        agent_names = [
            "market_data_agent",
            "financial_statement_agent",
            "news_intelligence_agent",
            "social_sentiment_agent",
            "sector_intelligence_agent",
            "risk_agent",
            "forecast_agent",
            "report_agent",
        ]
        agent_contributions = []
        for a_name in agent_names:
            status_val = input_data.agent_statuses.get(a_name, "success")
            if any(deg in a_name for deg in input_data.degraded_sources):
                status_val = "degraded"
            agent_contributions.append(
                AgentContribution(
                    agent_name=a_name,
                    agent_version=self.version,
                    status=status_val,
                )
            )

        # Data freshness
        data_freshness = {
            "market_data": m.generated_at,
            "financials": f.generated_at,
            "news": n.generated_at,
            "sentiment": s.generated_at,
            "sector": sec.generated_at,
            "risk": r.generated_at,
            "forecast": fc.generated_at,
        }

        # Overall confidence is weighted upstream confidence
        overall_conf = float(
            round(
                (m.confidence * 0.25 + f.confidence * 0.25 + fc.confidence * 0.30 + r.confidence * 0.20)
                * (0.85 if input_data.degraded_sources else 1.0),
                2,
            )
        )

        return ReportSchema(
            schema_version=self.version,
            ticker=ticker,
            generated_at=now,
            confidence=min(1.0, max(0.0, overall_conf)),
            provenance=provenance,
            analysis_type=input_data.analysis_type,
            executive_summary=exec_summary,
            bull_case=bull_case,
            bear_case=bear_case,
            forecast=fc,
            risk=r,
            reasoning_factors=reasoning_factors,
            agent_contributions=agent_contributions,
            degraded_sources=input_data.degraded_sources,
            data_freshness=data_freshness,
        )
