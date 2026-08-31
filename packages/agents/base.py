from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import json
import logging
import time
from typing import Any, Generic, Optional, TypeVar
from packages.infra.db.models import AgentRun
from packages.infra.db.session import AsyncSessionLocal
from packages.infra.observability.metrics import (
    AGENT_EXECUTION_DURATION_SECONDS,
    AGENT_EXECUTION_TOTAL,
)
from packages.infra.observability.tracer import start_agent_span

logger = logging.getLogger(__name__)

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Abstract base class for all 8 agents with tracing, metrics, and audit logging."""
    name: str = "base_agent"
    version: str = "1.0.0"

    @abstractmethod
    async def run(self, input_data: InputT) -> OutputT:
        """Core agent business logic. Never called directly by orchestrator."""
        pass

    async def execute(
        self,
        input_data: InputT,
        job_id: Optional[str] = None,
        persist_run: bool = True,
    ) -> OutputT:
        """
        Wraps run() with timing, OpenTelemetry tracing, Prometheus metrics,
        audit logging, and exception capture.
        """
        start_time = time.perf_counter()
        started_at = datetime.now(timezone.utc)
        status = "success"
        error_msg: Optional[str] = None
        output: Optional[OutputT] = None

        # Compute hash of input for provenance & auditability
        input_str = str(input_data)
        input_hash = hashlib.sha256(input_str.encode("utf-8")).hexdigest()[:16]

        logger.info(
            "Starting agent [%s v%s] for job_id=%s (input_hash=%s)",
            self.name,
            self.version,
            job_id,
            input_hash,
        )

        with start_agent_span(
            agent_name=self.name,
            version=self.version,
            job_id=job_id,
            input_hash=input_hash,
        ):
            try:
                output = await self.run(input_data)
                return output
            except Exception as exc:
                status = "failed"
                error_msg = f"{type(exc).__name__}: {str(exc)}"
                logger.error(
                    "Agent [%s] failed during execution: %s",
                    self.name,
                    error_msg,
                    exc_info=True,
                )
                raise exc
            finally:
                finished_at = datetime.now(timezone.utc)
                duration_s = time.perf_counter() - start_time
                duration_ms = duration_s * 1000.0

                # Record Prometheus metrics
                try:
                    AGENT_EXECUTION_DURATION_SECONDS.labels(
                        agent_name=self.name, status=status
                    ).observe(duration_s)
                    AGENT_EXECUTION_TOTAL.labels(
                        agent_name=self.name, status=status
                    ).inc()
                except Exception as m_err:
                    logger.debug("Metric recording skipped: %s", m_err)

                logger.info(
                    "Finished agent [%s] status=%s duration=%.2fms",
                    self.name,
                    status,
                    duration_ms,
                )

                if persist_run and job_id:
                    await self._persist_agent_run(
                        job_id=job_id,
                        status=status,
                        started_at=started_at,
                        finished_at=finished_at,
                        duration_ms=duration_ms,
                        error=error_msg,
                        input_hash=input_hash,
                    )

    async def _persist_agent_run(
        self,
        job_id: str,
        status: str,
        started_at: datetime,
        finished_at: datetime,
        duration_ms: float,
        error: Optional[str],
        input_hash: str,
    ) -> None:
        try:
            async with AsyncSessionLocal() as session:
                agent_run = AgentRun(
                    job_id=job_id,
                    agent_name=self.name,
                    agent_version=self.version,
                    status=status,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                    error=error,
                    input_hash=input_hash,
                )
                session.add(agent_run)
                await session.commit()
        except Exception as e:
            logger.warning("Failed to persist AgentRun for [%s]: %s", self.name, e)
