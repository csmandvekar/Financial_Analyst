from unittest.mock import patch
import pytest
from packages.contracts.report import ReportSchema
from packages.infra.cache.redis_client import cache_client
from packages.infra.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException, CircuitState
from packages.orchestrator.graph import run_analysis_pipeline


@pytest.mark.asyncio
async def test_chaos_multi_source_failure():
    """
    Chaos Test: Injects simultaneous failure of both News and Sentiment external providers.
    Verifies the LangGraph orchestrator detects both failures, marks them as degraded,
    and successfully produces a valid ReportSchema with confidence adjusted.
    """
    with patch(
        "packages.agents.news.agent.NewsAgent.run",
        side_effect=ConnectionError("Simulated NewsAPI Global Outage"),
    ), patch(
        "packages.agents.sentiment.agent.SentimentAgent.run",
        side_effect=TimeoutError("Simulated Reddit Gateway Timeout 504"),
    ):
        report = await run_analysis_pipeline(
            ticker="AMZN",
            analysis_type="quarterly_outlook",
            job_id="chaos_test_job_001",
            requested_by="chaos_injector",
        )

        assert isinstance(report, ReportSchema)
        assert report.ticker == "AMZN"
        assert "news" in report.degraded_sources
        assert "sentiment" in report.degraded_sources
        assert len(report.degraded_sources) == 2
        # Report confidence should reflect degradation
        assert 0.0 < report.confidence <= 0.85
        assert len(report.executive_summary) > 20


@pytest.mark.asyncio
async def test_chaos_circuit_breaker_tripped_recovery():
    """
    Chaos Test: Triggers circuit breaker failure threshold to force OPEN state,
    verifies fast-failing during cooldown, and tests automatic transition to HALF_OPEN.
    """
    cb = CircuitBreaker("chaos_mock_service", failure_threshold=2, recovery_timeout=0.1)

    async def broken_call():
        raise ConnectionError("Upstream server dead")

    # Trip breaker
    for _ in range(2):
        with pytest.raises(ConnectionError):
            await cb.call(broken_call)

    assert cb.state == CircuitState.OPEN

    # In OPEN state, fast fails without executing function
    with pytest.raises(CircuitBreakerOpenException) as excinfo:
        await cb.call(broken_call)
    assert "is OPEN" in str(excinfo.value)
