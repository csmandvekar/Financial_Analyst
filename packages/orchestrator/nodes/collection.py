import asyncio
import logging
from typing import Any, Dict
from packages.agents.financials import FinancialAgent, FinancialInput
from packages.agents.market_data import MarketDataAgent, MarketDataInput
from packages.agents.news import NewsAgent, NewsInput
from packages.agents.sector import SectorAgent, SectorInput
from packages.agents.sentiment import SentimentAgent, SentimentInput
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)

# Agent instances
market_agent = MarketDataAgent()
financial_agent = FinancialAgent()
news_agent = NewsAgent()
sentiment_agent = SentimentAgent()
sector_agent = SectorAgent()


async def collection_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Parallel Fan-Out node: Executes the 5 data collection agents concurrently.
    Captures any failures individually to allow downstream graceful degradation.
    """
    ticker = state["ticker"]
    job_id = state.get("job_id")

    logger.info("Executing parallel data collection for ticker %s (job_id=%s)", ticker, job_id)

    # Spawn 5 collection tasks
    tasks = [
        market_agent.execute(MarketDataInput(ticker=ticker), job_id=job_id),
        financial_agent.execute(FinancialInput(ticker=ticker), job_id=job_id),
        news_agent.execute(NewsInput(ticker=ticker), job_id=job_id),
        sentiment_agent.execute(SentimentInput(ticker=ticker), job_id=job_id),
        sector_agent.execute(SectorInput(ticker=ticker), job_id=job_id),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    market_res, fin_res, news_res, sent_res, sec_res = results

    degraded_sources = list(state.get("degraded_sources", []))
    agent_statuses = dict(state.get("agent_statuses", {}))
    errors = list(state.get("errors", []))

    # Process Market Data
    if isinstance(market_res, Exception):
        logger.error("Market data agent failed: %s", market_res)
        degraded_sources.append("market_data")
        agent_statuses["market_data_agent"] = "failed"
        errors.append(f"market_data: {str(market_res)}")
        market_data = None
    else:
        market_data = market_res
        agent_statuses["market_data_agent"] = "success"

    # Process Financials
    if isinstance(fin_res, Exception):
        logger.error("Financials agent failed: %s", fin_res)
        degraded_sources.append("financials")
        agent_statuses["financial_statement_agent"] = "failed"
        errors.append(f"financials: {str(fin_res)}")
        financials = None
    else:
        financials = fin_res
        agent_statuses["financial_statement_agent"] = "success"

    # Process News
    if isinstance(news_res, Exception):
        logger.error("News agent failed: %s", news_res)
        degraded_sources.append("news")
        agent_statuses["news_intelligence_agent"] = "failed"
        errors.append(f"news: {str(news_res)}")
        news = None
    else:
        news = news_res
        agent_statuses["news_intelligence_agent"] = "success"

    # Process Sentiment
    if isinstance(sent_res, Exception):
        logger.error("Sentiment agent failed: %s", sent_res)
        degraded_sources.append("sentiment")
        agent_statuses["social_sentiment_agent"] = "failed"
        errors.append(f"sentiment: {str(sent_res)}")
        sentiment = None
    else:
        sentiment = sent_res
        agent_statuses["social_sentiment_agent"] = "success"

    # Process Sector
    if isinstance(sec_res, Exception):
        logger.error("Sector agent failed: %s", sec_res)
        degraded_sources.append("sector")
        agent_statuses["sector_intelligence_agent"] = "failed"
        errors.append(f"sector: {str(sec_res)}")
        sector = None
    else:
        sector = sec_res
        agent_statuses["sector_intelligence_agent"] = "success"

    return {
        "market_data": market_data,
        "financials": financials,
        "news": news,
        "sentiment": sentiment,
        "sector": sector,
        "degraded_sources": degraded_sources,
        "agent_statuses": agent_statuses,
        "errors": errors,
    }
