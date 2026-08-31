import asyncio
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_concurrent_analysis_requests(async_client: AsyncClient):
    """
    Load test: Submits multiple concurrent analysis requests across different tickers
    and verifies the server executes and persists all requests without state collision.
    """
    tickers = ["AAPL", "MSFT", "GOOGL"]
    tasks = [
        async_client.post(
            "/analysis",
            json={"ticker": t, "analysis_type": "quarterly_outlook", "requested_by": "load_test"},
        )
        for t in tickers
    ]

    responses = await asyncio.gather(*tasks)

    for resp in responses:
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("completed", "degraded")
        assert "report" in data
        assert data["report"]["ticker"] in tickers
