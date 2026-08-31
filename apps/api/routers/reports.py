from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from packages.infra.db.models import Report
from packages.infra.db.session import AsyncSessionLocal

router = APIRouter(tags=["Reports"])


@router.get("/reports/{report_or_job_id}", summary="Get financial intelligence report alone")
async def get_report(report_or_job_id: str):
    """Retrieves full serialized ReportSchema by either Report ID or Job ID."""
    async with AsyncSessionLocal() as session:
        stmt = select(Report).where(
            (Report.id == report_or_job_id) | (Report.job_id == report_or_job_id)
        )
        res = await session.execute(stmt)
        report = res.scalar_one_or_none()

        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"Report with ID or Job ID '{report_or_job_id}' not found",
            )

        return {
            "id": report.id,
            "job_id": report.job_id,
            "ticker": report.ticker,
            "version": report.version,
            "created_at": report.created_at,
            "confidence_score": report.confidence_score,
            "payload": report.payload,
        }
