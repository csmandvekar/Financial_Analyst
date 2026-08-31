import logging
from typing import Any, Dict
from packages.agents.report import ReportAgent, ReportInput
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)
report_agent = ReportAgent()


async def report_node(state: OrchestratorState) -> Dict[str, Any]:
    """Report Node: Synthesizes final report narrative strictly grounded in upstream data."""
    job_id = state.get("job_id")
    agent_statuses = dict(state.get("agent_statuses", {}))

    try:
        report_output = await report_agent.execute(
            ReportInput(
                analysis_type=state.get("analysis_type", "quarterly_outlook"),
                market_data=state["market_data"],
                financials=state["financials"],
                news=state["news"],
                sentiment=state["sentiment"],
                sector=state["sector"],
                risk=state["risk"],
                forecast=state["forecast"],
                degraded_sources=state.get("degraded_sources", []),
                agent_statuses=agent_statuses,
            ),
            job_id=job_id,
        )
        agent_statuses["report_agent"] = "success"
    except Exception as e:
        logger.error("Report agent execution failed: %s. Using direct fallback.", e)
        agent_statuses["report_agent"] = "degraded"
        report_output = await report_agent.run(
            ReportInput(
                analysis_type=state.get("analysis_type", "quarterly_outlook"),
                market_data=state["market_data"],
                financials=state["financials"],
                news=state["news"],
                sentiment=state["sentiment"],
                sector=state["sector"],
                risk=state["risk"],
                forecast=state["forecast"],
                degraded_sources=state.get("degraded_sources", []),
                agent_statuses=agent_statuses,
            )
        )

    return {
        "report": report_output,
        "agent_statuses": agent_statuses,
    }
