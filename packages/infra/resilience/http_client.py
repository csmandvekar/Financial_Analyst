import logging
from typing import Any, Dict, Optional
import httpx
from packages.infra.config import settings
from packages.infra.resilience.circuit_breaker import CircuitBreaker
from packages.infra.resilience.rate_limiter import TokenBucketRateLimiter
from packages.infra.resilience.retry import execute_with_retry

logger = logging.getLogger(__name__)


class ResilientHttpClient:
    """HTTP Client with per-source Circuit Breaker, Rate Limiter, Timeout, and Retry."""

    _circuit_breakers: Dict[str, CircuitBreaker] = {}
    _rate_limiters: Dict[str, TokenBucketRateLimiter] = {}

    def __init__(self, service_name: str, requests_per_second: float = 5.0, burst: int = 10):
        self.service_name = service_name
        if service_name not in self._circuit_breakers:
            self._circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name,
                failure_threshold=settings.CIRCUIT_BREAKER_FAIL_THRESHOLD,
                recovery_timeout=settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            )
        if service_name not in self._rate_limiters:
            self._rate_limiters[service_name] = TokenBucketRateLimiter(
                rate_limit=requests_per_second,
                time_period=1.0,
                burst=burst,
            )

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        return self._circuit_breakers[self.service_name]

    @property
    def rate_limiter(self) -> TokenBucketRateLimiter:
        return self._rate_limiters[self.service_name]

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        max_attempts: int = 3,
    ) -> httpx.Response:
        timeout_val = timeout or settings.DEFAULT_TIMEOUT_SECONDS

        async def _call_http():
            await self.rate_limiter.acquire()
            async with httpx.AsyncClient(timeout=timeout_val) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response

        async def _protected_call():
            return await self.circuit_breaker.call(_call_http)

        return await execute_with_retry(_protected_call, max_attempts=max_attempts)

    async def post(
        self,
        url: str,
        json_data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        max_attempts: int = 3,
    ) -> httpx.Response:
        timeout_val = timeout or settings.DEFAULT_TIMEOUT_SECONDS

        async def _call_http():
            await self.rate_limiter.acquire()
            async with httpx.AsyncClient(timeout=timeout_val) as client:
                response = await client.post(url, json=json_data, headers=headers)
                response.raise_for_status()
                return response

        async def _protected_call():
            return await self.circuit_breaker.call(_call_http)

        return await execute_with_retry(_protected_call, max_attempts=max_attempts)
