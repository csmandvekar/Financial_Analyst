import pytest
from packages.contracts.report import ReportSchema
from packages.orchestrator.graph import run_analysis_pipeline


@pytest.mark.asyncio
async def test_run_analysis_pipeline_success():
    """Tests end-to-end multi-agent pipeline for ticker AAPL."""
    report = await run_analysis_pipeline(
        ticker="AAPL",
        analysis_type="quarterly_outlook",
        job_id="test_pipeline_job_001",
        requested_by="unit_test_runner",
    )

    assert isinstance(report, ReportSchema)
    assert report.ticker == "AAPL"
    assert len(report.executive_summary) > 20
    assert len(report.bull_case) > 20
    assert len(report.bear_case) > 20
    assert len(report.forecast.horizons) == 3
    assert report.risk.volatility_band_low > 0
    assert report.risk.volatility_band_high >= report.risk.volatility_band_low
    assert len(report.reasoning_factors) >= 3
    assert len(report.agent_contributions) == 8
    assert 0.0 <= report.confidence <= 1.0
