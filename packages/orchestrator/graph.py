from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional
from langgraph.graph import END, START, StateGraph
from packages.contracts.report import ReportSchema
from packages.orchestrator.nodes.collection import collection_node
from packages.orchestrator.nodes.forecast_node import forecast_node
from packages.orchestrator.nodes.persist import persist_node
from packages.orchestrator.nodes.report_node import report_node
from packages.orchestrator.nodes.risk_node import risk_node
from packages.orchestrator.nodes.signal import signal_node
from packages.orchestrator.nodes.validation import validation_node
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)


def build_analysis_graph() -> StateGraph:
    """Builds and compiles the LangGraph StateGraph DAG for multi-agent financial analysis."""
    builder = StateGraph(OrchestratorState)

    # Register DAG nodes
    builder.add_node("collection", collection_node)
    builder.add_node("validation", validation_node)
    builder.add_node("signal", signal_node)
    builder.add_node("risk", risk_node)
    builder.add_node("forecast", forecast_node)
    builder.add_node("report", report_node)
    builder.add_node("persist", persist_node)

    # Wire DAG edges
    builder.add_edge(START, "collection")
    builder.add_edge("collection", "validation")
    builder.add_edge("validation", "signal")
    builder.add_edge("signal", "risk")
    builder.add_edge("risk", "forecast")
    builder.add_edge("forecast", "report")
    builder.add_edge("report", "persist")
    builder.add_edge("persist", END)

    return builder.compile()


analysis_graph = build_analysis_graph()


async def run_analysis_pipeline(
    ticker: str,
    analysis_type: str = "quarterly_outlook",
    job_id: Optional[str] = None,
    requested_by: str = "system",
) -> ReportSchema:
    """Entrypoint to execute the analysis graph synchronously."""
    initial_state: OrchestratorState = {
        "job_id": job_id or "local_test_job",
        "ticker": ticker.upper(),
        "analysis_type": analysis_type,
        "requested_by": requested_by,
        "started_at": datetime.now(timezone.utc),
        "degraded_sources": [],
        "agent_statuses": {},
        "errors": [],
        "is_completed": False,
    }

    logger.info("Starting pipeline execution for %s (job_id=%s)", ticker, job_id)
    final_state = await analysis_graph.ainvoke(initial_state)

    report = final_state.get("report")
    if not report:
        raise RuntimeError(f"Pipeline finished without producing a ReportSchema for {ticker}")

    return report
