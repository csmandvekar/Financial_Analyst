from unittest.mock import patch
import pytest
from packages.contracts.report import ReportSchema
from packages.orchestrator.graph import run_analysis_pipeline


@pytest.mark.asyncio
async def test_pipeline_with_degraded_news_source():
    """
    Simulates external news provider outage.
    Verifies the pipeline completes gracefully, marks news as degraded,
    and produces a valid ReportSchema with degraded_sources listed.
    """
    with patch("packages.agents.news.agent.NewsAgent.run", side_effect=ConnectionError("NewsAPI Gateway Timeout 504")):
        report = await run_analysis_pipeline(
            ticker="NVDA",
            analysis_type="quarterly_outlook",
            job_id="test_degraded_job_002",
            requested_by="chaos_test_runner",
        )

        assert isinstance(report, ReportSchema)
        assert report.ticker == "NVDA"
        assert "news" in report.degraded_sources
        assert any(c.agent_name == "news_intelligence_agent" and c.status == "degraded" for c in report.agent_contributions)
        assert report.confidence > 0.0
