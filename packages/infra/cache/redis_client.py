import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional
import redis.asyncio as redis
from packages.infra.config import settings
from packages.infra.observability.metrics import CACHE_HIT_TOTAL, CACHE_MISS_TOTAL

logger = logging.getLogger(__name__)

# Standard TTL table (in seconds)
CACHE_TTLS = {
    "market_data": 900,       # 15 min
    "sentiment": 1800,        # 30 min
    "news": 3600,             # 1 hour
    "report": 21600,          # 6 hours
    "financials": 86400,      # 24 hours
    "sector": 3600,           # 1 hour
}


class CacheClient:
    """Redis cache client with key convention {source}:{ticker}:{params_hash} and metric tracking."""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._memory_cache: Dict[str, tuple[float, str]] = {}
        self._connected = False

    async def connect(self) -> None:
        try:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            await self._redis.ping()
            self._connected = True
            logger.info("Connected to Redis at %s", settings.REDIS_URL)
        except Exception as e:
            self._connected = False
            logger.warning(
                "Redis connection failed (%s). Using in-memory fallback cache.", e
            )

    async def close(self) -> None:
        if self._redis and self._connected:
            await self._redis.close()
            self._connected = False

    def build_key(self, source: str, ticker: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Constructs standardized cache key: {source}:{ticker}:{params_hash}"""
        params_str = json.dumps(params or {}, sort_keys=True)
        params_hash = hashlib.sha256(params_str.encode("utf-8")).hexdigest()[:12]
        return f"{source.lower()}:{ticker.upper()}:{params_hash}"

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        prefix = key.split(":")[0] if ":" in key else "unknown"
        if self._connected and self._redis:
            try:
                val = await self._redis.get(key)
                if val:
                    try:
                        CACHE_HIT_TOTAL.labels(cache_key_prefix=prefix).inc()
                    except Exception:
                        pass
                    return json.loads(val)
                try:
                    CACHE_MISS_TOTAL.labels(cache_key_prefix=prefix).inc()
                except Exception:
                    pass
                return None
            except Exception as e:
                logger.warning("Redis GET error (%s). Falling back to memory cache.", e)

        # In-memory fallback
        if key in self._memory_cache:
            expires_at, val_str = self._memory_cache[key]
            if time.time() < expires_at:
                try:
                    CACHE_HIT_TOTAL.labels(cache_key_prefix=prefix).inc()
                except Exception:
                    pass
                return json.loads(val_str)
            else:
                del self._memory_cache[key]

        try:
            CACHE_MISS_TOTAL.labels(cache_key_prefix=prefix).inc()
        except Exception:
            pass
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        source: Optional[str] = None,
    ) -> None:
        if ttl_seconds is None and source and source in CACHE_TTLS:
            ttl_seconds = CACHE_TTLS[source]
        ttl_seconds = ttl_seconds or 3600

        # Handle Pydantic models or dicts
        if hasattr(value, "model_dump_json"):
            val_str = value.model_dump_json()
        elif hasattr(value, "dict"):
            val_str = json.dumps(value.dict(), default=str)
        else:
            val_str = json.dumps(value, default=str)

        if self._connected and self._redis:
            try:
                await self._redis.set(key, val_str, ex=ttl_seconds)
                return
            except Exception as e:
                logger.warning("Redis SET error (%s). Using memory cache.", e)

        # In-memory fallback
        self._memory_cache[key] = (time.time() + ttl_seconds, val_str)


# Global singleton instance
cache_client = CacheClient()
