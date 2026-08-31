import logging
from typing import Any, Dict
from packages.agents.risk import RiskAgent, RiskInput
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)
risk_agent = RiskAgent()


async def risk_node(state: OrchestratorState) -> Dict[str, Any]:
    """Risk Node: Executes quantitative risk calculations."""
    job_id = state.get("job_id")
    market_data = state["market_data"]
    financials = state["financials"]
    agent_statuses = dict(state.get("agent_statuses", {}))

    try:
        risk_output = await risk_agent.execute(
            RiskInput(market_data=market_data, financials=financials),
            job_id=job_id,
        )
        agent_statuses["risk_agent"] = "success"
    except Exception as e:
        logger.error("Risk agent failed: %s. Using internal fallback.", e)
        agent_statuses["risk_agent"] = "degraded"
        risk_output = await risk_agent.run(RiskInput(market_data=market_data, financials=financials))

    return {
        "risk": risk_output,
        "agent_statuses": agent_statuses,
    }
