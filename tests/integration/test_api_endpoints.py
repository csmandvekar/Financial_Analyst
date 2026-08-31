import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Financial Intelligence Platform"


@pytest.mark.asyncio
async def test_ticker_snapshot_endpoint(async_client: AsyncClient):
    response = await async_client.get("/ticker/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "current_price" in data
    assert "indicators" in data
    assert data["indicators"]["rsi_14"] >= 0


@pytest.mark.asyncio
async def test_submit_analysis_and_retrieve(async_client: AsyncClient):
    # 1. Submit POST /analysis
    post_res = await async_client.post(
        "/analysis",
        json={"ticker": "MSFT", "analysis_type": "quarterly_outlook", "requested_by": "api_test"},
    )
    assert post_res.status_code == 200
    post_data = post_res.json()

    job_id = post_data["job_id"]
    assert post_data["ticker"] == "MSFT"
    assert post_data["status"] in ("completed", "degraded")
    assert "report" in post_data
    assert post_data["report"]["ticker"] == "MSFT"

    # 2. Query GET /analysis/{job_id}
    get_res = await async_client.get(f"/analysis/{job_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["job_id"] == job_id
    assert get_data["status"] in ("completed", "degraded")

    # 3. Query GET /reports/{job_id}
    rep_res = await async_client.get(f"/reports/{job_id}")
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    assert rep_data["ticker"] == "MSFT"
    assert "payload" in rep_data

    # 4. Query GET /jobs/{job_id} (Agent Trace Viewer)
    trace_res = await async_client.get(f"/jobs/{job_id}")
    assert trace_res.status_code == 200
    trace_data = trace_res.json()
    assert trace_data["job_id"] == job_id
    assert len(trace_data["agent_runs"]) > 0
    # Every agent run has duration_ms, agent_name, status
    first_run = trace_data["agent_runs"][0]
    assert "agent_name" in first_run
    assert "duration_ms" in first_run
    assert "status" in first_run
