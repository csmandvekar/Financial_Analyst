import logging
from typing import Any, Dict
from packages.agents.forecast import ForecastAgent, ForecastInput
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)
forecast_agent = ForecastAgent()


async def forecast_node(state: OrchestratorState) -> Dict[str, Any]:
    """Forecast Node: Synthesizes multi-factor ensemble into multi-horizon forecasts."""
    job_id = state.get("job_id")
    market_data = state["market_data"]
    fund_sig = state["fundamental_signal"]
    sent_sig = state["sentiment_signal"]
    sec_sig = state["sector_signal"]
    mkt_sig = state["market_signal"]
    agent_statuses = dict(state.get("agent_statuses", {}))

    try:
        forecast_output = await forecast_agent.execute(
            ForecastInput(
                market_data=market_data,
                fundamental_signal=fund_sig,
                sentiment_signal=sent_sig,
                sector_signal=sec_sig,
                market_signal=mkt_sig,
            ),
            job_id=job_id,
        )
        agent_statuses["forecast_agent"] = "success"
    except Exception as e:
        logger.error("Forecast agent failed: %s. Using internal fallback.", e)
        agent_statuses["forecast_agent"] = "degraded"
        forecast_output = await forecast_agent.run(
            ForecastInput(
                market_data=market_data,
                fundamental_signal=fund_sig,
                sentiment_signal=sent_sig,
                sector_signal=sec_sig,
                market_signal=mkt_sig,
            )
        )

    return {
        "forecast": forecast_output,
        "agent_statuses": agent_statuses,
    }
