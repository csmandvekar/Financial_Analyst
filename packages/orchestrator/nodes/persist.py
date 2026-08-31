from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict
from sqlalchemy import select
from packages.infra.cache.redis_client import cache_client
from packages.infra.db.models import (
    AnalysisJob,
    AuditLog,
    FinancialDataModel,
    Forecast,
    MarketDataModel,
    NewsDataModel,
    Report,
    SectorDataModel,
    SentimentDataModel,
)
from packages.infra.db.session import AsyncSessionLocal
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)


async def persist_node(state: OrchestratorState) -> Dict[str, Any]:
    """Persists all outputs to PostgreSQL and Redis cache."""
    job_id = state.get("job_id")
    ticker = state["ticker"]
    now = datetime.now(timezone.utc)
    degraded_sources = state.get("degraded_sources", [])
    status = "degraded" if degraded_sources else "completed"

    report_schema = state["report"]
    forecast_schema = state["forecast"]
    market_schema = state["market_data"]
    fin_schema = state["financials"]
    news_schema = state["news"]
    sent_schema = state["sentiment"]
    sec_schema = state["sector"]

    # 1. Update Database
    if job_id:
        try:
            async with AsyncSessionLocal() as session:
                # Update AnalysisJob
                stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
                res = await session.execute(stmt)
                job = res.scalar_one_or_none()
                if job:
                    job.status = status
                    job.completed_at = now
                    job.degraded_sources = degraded_sources

                # Insert Report
                report_row = Report(
                    job_id=job_id,
                    ticker=ticker,
                    version=report_schema.schema_version,
                    executive_summary=report_schema.executive_summary,
                    bull_case=report_schema.bull_case,
                    bear_case=report_schema.bear_case,
                    confidence_score=report_schema.confidence,
                    payload=json.loads(report_schema.model_dump_json()),
                )
                session.add(report_row)

                # Insert Forecasts (one per horizon)
                for h in forecast_schema.horizons:
                    fc_row = Forecast(
                        job_id=job_id,
                        ticker=ticker,
                        horizon=h.horizon,
                        bull_prob=h.bull_probability,
                        bear_prob=h.bear_probability,
                        neutral_prob=h.neutral_probability,
                        expected_vol=h.expected_volatility,
                        price_range_low=h.expected_price_low,
                        price_range_high=h.expected_price_high,
                        confidence=h.confidence,
                        source="forecast_agent",
                        version=forecast_schema.schema_version,
                    )
                    session.add(fc_row)

                # Insert Raw Data Snapshots
                if market_schema:
                    session.add(
                        MarketDataModel(
                            ticker=ticker,
                            as_of=market_schema.generated_at,
                            payload=json.loads(market_schema.model_dump_json()),
                            source=market_schema.provenance[0].source,
                            confidence=market_schema.confidence,
                        )
                    )
                if fin_schema:
                    session.add(
                        FinancialDataModel(
                            ticker=ticker,
                            period="latest_quarterly",
                            payload=json.loads(fin_schema.model_dump_json()),
                            source=fin_schema.provenance[0].source,
                            confidence=fin_schema.confidence,
                        )
                    )
                if news_schema:
                    session.add(
                        NewsDataModel(
                            ticker=ticker,
                            payload=json.loads(news_schema.model_dump_json()),
                            source=news_schema.provenance[0].source,
                            confidence=news_schema.confidence,
                        )
                    )
                if sent_schema:
                    session.add(
                        SentimentDataModel(
                            ticker=ticker,
                            payload=json.loads(sent_schema.model_dump_json()),
                            source=sent_schema.provenance[0].source,
                            confidence=sent_schema.confidence,
                        )
                    )
                if sec_schema:
                    session.add(
                        SectorDataModel(
                            ticker=ticker,
                            payload=json.loads(sec_schema.model_dump_json()),
                            source=sec_schema.provenance[0].source,
                            confidence=sec_schema.confidence,
                        )
                    )

                # Insert Audit Log
                session.add(
                    AuditLog(
                        actor=state.get("requested_by", "system"),
                        action="generate_analysis_report",
                        entity_type="report",
                        entity_id=job_id,
                        metadata_json={
                            "ticker": ticker,
                            "analysis_type": state.get("analysis_type"),
                            "status": status,
                            "degraded_sources": degraded_sources,
                            "duration_ms": (now - state["started_at"]).total_seconds() * 1000.0,
                        },
                    )
                )

                await session.commit()
                logger.info("Persisted all report entities for job_id=%s to database", job_id)
        except Exception as e:
            logger.error("Failed to persist report to database: %s", e, exc_info=True)

    # 2. Update Cache
    cache_key = cache_client.build_key(
        source="report",
        ticker=ticker,
        params={"analysis_type": state.get("analysis_type", "quarterly_outlook")},
    )
    await cache_client.set(cache_key, report_schema, source="report")

    return {"is_completed": True}
