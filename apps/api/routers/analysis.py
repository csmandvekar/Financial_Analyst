from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from packages.contracts.report import ReportSchema
from packages.infra.db.models import AnalysisJob, Report
from packages.infra.db.session import AsyncSessionLocal
from packages.orchestrator.graph import run_analysis_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analysis"])


class AnalysisRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, json_schema_extra={"example": "AAPL"})
    analysis_type: str = Field(default="quarterly_outlook", json_schema_extra={"example": "quarterly_outlook"})
    requested_by: Optional[str] = Field(default="user_analyst")


class AnalysisResponse(BaseModel):
    job_id: str
    ticker: str
    analysis_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    degraded_sources: List[str]
    report: Optional[Dict[str, Any]] = None


@router.post(
    "/analysis",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit and execute a multi-agent financial analysis",
)
async def submit_analysis(request: AnalysisRequest):
    """
    Submits a ticker for analysis. In Phase 1, executes the full LangGraph DAG
    synchronously and returns the completed job and ReportSchema.
    """
    ticker = request.ticker.strip().upper()
    analysis_type = request.analysis_type
    requested_by = request.requested_by or "system"
    now = datetime.now(timezone.utc)

    # 1. Create Job record
    job = AnalysisJob(
        ticker=ticker,
        analysis_type=analysis_type,
        status="running",
        requested_by=requested_by,
        created_at=now,
    )
    async with AsyncSessionLocal() as session:
        session.add(job)
        await session.commit()
        await session.refresh(job)
        job_id = job.id

    # 2. Synchronous pipeline execution
    try:
        report_schema: ReportSchema = await run_analysis_pipeline(
            ticker=ticker,
            analysis_type=analysis_type,
            job_id=job_id,
            requested_by=requested_by,
        )

        # Refresh job row
        async with AsyncSessionLocal() as session:
            stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
            res = await session.execute(stmt)
            updated_job = res.scalar_one()

            return AnalysisResponse(
                job_id=updated_job.id,
                ticker=updated_job.ticker,
                analysis_type=updated_job.analysis_type,
                status=updated_job.status,
                created_at=updated_job.created_at,
                completed_at=updated_job.completed_at,
                degraded_sources=updated_job.degraded_sources or [],
                report=report_schema.model_dump(),
            )
    except Exception as exc:
        logger.error("Analysis pipeline failed for job_id=%s: %s", job_id, exc, exc_info=True)
        async with AsyncSessionLocal() as session:
            stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
            res = await session.execute(stmt)
            failed_job = res.scalar_one_or_none()
            if failed_job:
                failed_job.status = "failed"
                failed_job.error = str(exc)
                failed_job.completed_at = datetime.now(timezone.utc)
                await session.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis execution failed: {str(exc)}",
        )


@router.get(
    "/analysis/{job_id}",
    response_model=AnalysisResponse,
    summary="Get analysis job status and result",
)
async def get_analysis(job_id: str):
    """Fetches job metadata and associated report."""
    async with AsyncSessionLocal() as session:
        stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
        res = await session.execute(stmt)
        job = res.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=404, detail=f"Analysis job '{job_id}' not found")

        # Fetch report
        report_stmt = select(Report).where(Report.job_id == job_id)
        rep_res = await session.execute(report_stmt)
        report_row = rep_res.scalar_one_or_none()

        return AnalysisResponse(
            job_id=job.id,
            ticker=job.ticker,
            analysis_type=job.analysis_type,
            status=job.status,
            created_at=job.created_at,
            completed_at=job.completed_at,
            degraded_sources=job.degraded_sources or [],
            report=report_row.payload if report_row else None,
        )
