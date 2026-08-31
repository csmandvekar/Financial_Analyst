from contextlib import contextmanager
import logging
from typing import Any, Dict, Generator, Optional
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)

# Initialize OTel Tracer Provider
resource = Resource.create({"service.name": "financial-intel-platform", "service.version": "1.0.0"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("financial-intel-platform", "1.0.0")


def get_current_trace_id() -> Optional[str]:
    """Returns the current active trace_id in hex format if available."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return f"{span.get_span_context().trace_id:032x}"
    return None


@contextmanager
def start_agent_span(
    agent_name: str,
    version: str = "1.0.0",
    job_id: Optional[str] = None,
    input_hash: Optional[str] = None,
) -> Generator[trace.Span, None, None]:
    """Opens a child span for an agent run, tagging with job_id and input metadata."""
    with tracer.start_as_current_span(
        f"agent.{agent_name}",
        attributes={
            "agent.name": agent_name,
            "agent.version": version,
            "job.id": job_id or "unassigned",
            "agent.input_hash": input_hash or "none",
        },
    ) as span:
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise


@contextmanager
def start_job_span(job_id: str, ticker: str, analysis_type: str) -> Generator[trace.Span, None, None]:
    """Opens a root span for an analysis job run."""
    with tracer.start_as_current_span(
        "analysis_job",
        attributes={
            "job.id": job_id,
            "ticker": ticker,
            "analysis.type": analysis_type,
        },
    ) as span:
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
