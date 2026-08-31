import asyncio
import os
from datetime import datetime, timezone
import pytest
from httpx import ASGITransport, AsyncClient
from packages.infra.config import settings

# Configure test environment before importing app or session
TEST_DB_PATH = "./test_financial.db"
settings.ENVIRONMENT = "test"
settings.DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
settings.USE_SQLITE_FALLBACK = True
settings.DEBUG = False

from apps.api.main import app
from packages.infra.cache.redis_client import cache_client
from packages.infra.db.session import init_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_test_infrastructure():
    """Initializes test database and cache before each test run."""
    await init_db()
    await cache_client.connect()
    yield
    await cache_client.close()


@pytest.fixture
async def async_client():
    """FastAPI async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
