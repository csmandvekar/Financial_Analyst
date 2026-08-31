from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict
from packages.infra.observability.tracer import get_current_trace_id


class JSONStructuredFormatter(logging.Formatter):
    """Custom logging formatter that produces JSON structured logs for production observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Embed OpenTelemetry trace_id if available
        trace_id = getattr(record, "trace_id", None) or get_current_trace_id()
        if trace_id:
            log_obj["trace_id"] = trace_id

        # Embed contextual fields if present
        for field in ("job_id", "agent_name", "ticker", "duration_ms", "status"):
            if hasattr(record, field):
                log_obj[field] = getattr(record, field)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def configure_structured_logging(level: str = "INFO") -> None:
    """Configures root and app loggers with JSON structured formatter."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONStructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
