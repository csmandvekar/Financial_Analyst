import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_evaluation_backtest_and_metrics(async_client: AsyncClient):
    # 1. Trigger POST /evaluation/backtest
    backtest_res = await async_client.post(
        "/evaluation/backtest",
        json={"tickers": ["AAPL", "MSFT"], "lookback_days": 180, "horizon": "3m"},
    )
    assert backtest_res.status_code == 200
    b_data = backtest_res.json()
    assert b_data["sample_size"] >= 2
    assert "metrics" in b_data
    assert 0.0 <= b_data["metrics"]["directional_accuracy"] <= 1.0
    assert 0.0 <= b_data["metrics"]["brier_calibration_score"] <= 1.0

    # 2. Query GET /evaluation/metrics
    metrics_res = await async_client.get("/evaluation/metrics")
    assert metrics_res.status_code == 200
    m_data = metrics_res.json()
    assert m_data["sample_size"] >= 2
    assert "directional_accuracy" in m_data["metrics"]

    # 3. Query GET /evaluation/outcomes
    outcomes_res = await async_client.get("/evaluation/outcomes")
    assert outcomes_res.status_code == 200
    o_data = outcomes_res.json()
    assert len(o_data) >= 2
    assert "ticker" in o_data[0]
    assert "is_direction_correct" in o_data[0]


@pytest.mark.asyncio
async def test_metrics_prometheus_scrape(async_client: AsyncClient):
    """Verifies that Prometheus /metrics scrape returns properly formatted metrics."""
    res = await async_client.get("/metrics")
    assert res.status_code == 200
    text_content = res.text
    assert "http_request_duration_seconds" in text_content
    assert "agent_execution_total" in text_content
