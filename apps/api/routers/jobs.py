from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from packages.infra.db.models import AgentRun, AnalysisJob
from packages.infra.db.session import AsyncSessionLocal

router = APIRouter(tags=["Jobs"])


@router.get("/jobs/{job_id}", summary="Get job execution trace and per-agent metrics")
async def get_job_trace(job_id: str):
    """
    Returns analysis job status and full execution audit trace across all 8 agents.
    Supplies the backend data for the Agent Trace Viewer UI.
    """
    async with AsyncSessionLocal() as session:
        job_stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
        job_res = await session.execute(job_stmt)
        job = job_res.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

        runs_stmt = select(AgentRun).where(AgentRun.job_id == job_id).order_by(AgentRun.started_at)
        runs_res = await session.execute(runs_stmt)
        runs = runs_res.scalars().all()

        agent_traces: List[Dict[str, Any]] = [
            {
                "id": r.id,
                "agent_name": r.agent_name,
                "agent_version": r.agent_version,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "duration_ms": r.duration_ms,
                "error": r.error,
                "input_hash": r.input_hash,
            }
            for r in runs
        ]

        total_duration_ms = (
            (job.completed_at - job.created_at).total_seconds() * 1000.0
            if job.completed_at
            else sum((r.duration_ms or 0.0) for r in runs)
        )

        return {
            "job_id": job.id,
            "ticker": job.ticker,
            "analysis_type": job.analysis_type,
            "status": job.status,
            "requested_by": job.requested_by,
            "degraded_sources": job.degraded_sources or [],
            "error": job.error,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "total_duration_ms": total_duration_ms,
            "agent_runs": agent_traces,
        }
