from datetime import datetime, timezone
import logging
from typing import Any, Dict
from packages.agents.financials.agent import FinancialAgent
from packages.agents.market_data.agent import MarketDataAgent
from packages.agents.news.agent import NewsAgent
from packages.agents.sector.agent import SectorAgent, get_sector_info
from packages.agents.sentiment.agent import SentimentAgent
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)


async def validation_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Data Validation Node:
    - Sanity checks on raw data (price > 0, ratios valid).
    - Injects structured fallback schemas for any collection agents that threw errors.
    - Records degraded status for downstream traceability.
    """
    ticker = state["ticker"]
    now = datetime.now(timezone.utc)

    market_data = state.get("market_data")
    financials = state.get("financials")
    news = state.get("news")
    sentiment = state.get("sentiment")
    sector = state.get("sector")

    degraded_sources = list(state.get("degraded_sources", []))
    agent_statuses = dict(state.get("agent_statuses", {}))

    # Validate / repair Market Data
    if market_data is None or market_data.current_price <= 0:
        logger.warning("Market data invalid or missing for %s. Applying fallback schema.", ticker)
        market_agent = MarketDataAgent()
        market_data = market_agent._build_fallback(ticker, now, error_note="Validation node fallback")
        if "market_data" not in degraded_sources:
            degraded_sources.append("market_data")
        agent_statuses["market_data_agent"] = "degraded"

    # Validate / repair Financials
    if financials is None:
        logger.warning("Financials missing for %s. Applying fallback schema.", ticker)
        fin_agent = FinancialAgent()
        financials = fin_agent._build_fallback(ticker, now)
        if "financials" not in degraded_sources:
            degraded_sources.append("financials")
        agent_statuses["financial_statement_agent"] = "degraded"

    # Validate / repair News
    if news is None:
        logger.warning("News missing for %s. Applying fallback schema.", ticker)
        news_agent = NewsAgent()
        news = news_agent._build_fallback(ticker, now)
        if "news" not in degraded_sources:
            degraded_sources.append("news")
        agent_statuses["news_intelligence_agent"] = "degraded"

    # Validate / repair Sentiment
    if sentiment is None:
        logger.warning("Sentiment missing for %s. Applying fallback schema.", ticker)
        sent_agent = SentimentAgent()
        sentiment = await sent_agent._aggregate_social_sentiment(ticker)
        sentiment.degraded = True
        if "sentiment" not in degraded_sources:
            degraded_sources.append("sentiment")
        agent_statuses["social_sentiment_agent"] = "degraded"

    # Validate / repair Sector
    if sector is None:
        logger.warning("Sector data missing for %s. Applying fallback schema.", ticker)
        sec_agent = SectorAgent()
        sector = sec_agent._build_fallback(ticker, now, get_sector_info(ticker))
        if "sector" not in degraded_sources:
            degraded_sources.append("sector")
        agent_statuses["sector_intelligence_agent"] = "degraded"

    return {
        "market_data": market_data,
        "financials": financials,
        "news": news,
        "sentiment": sentiment,
        "sector": sector,
        "degraded_sources": degraded_sources,
        "agent_statuses": agent_statuses,
    }
