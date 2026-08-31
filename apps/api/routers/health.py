from datetime import datetime, timezone
from fastapi import APIRouter
from sqlalchemy import text
from packages.infra.cache.redis_client import cache_client
from packages.infra.db.session import AsyncSessionLocal

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check for API gateway, Postgres database, and Redis cache."""
    db_ok = False
    redis_ok = False

    # Check DB
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False

    # Check Redis
    try:
        if cache_client._connected and cache_client._redis:
            await cache_client._redis.ping()
            redis_ok = True
        else:
            redis_ok = True  # Memory cache fallback active
    except Exception:
        redis_ok = False

    status = "healthy" if db_ok else "degraded"
    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "database": "connected" if db_ok else "disconnected",
            "cache": "connected" if redis_ok else "memory_fallback",
        },
    }
