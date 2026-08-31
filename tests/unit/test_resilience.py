import asyncio
import pytest
from packages.infra.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException,
    CircuitState,
)
from packages.infra.resilience.rate_limiter import TokenBucketRateLimiter
from packages.infra.resilience.retry import execute_with_retry, is_retryable_exception
import httpx


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    cb = CircuitBreaker("test_service", failure_threshold=2, recovery_timeout=0.1)

    assert cb.state == CircuitState.CLOSED

    # Trigger failure 1
    async def fail_call():
        raise ConnectionError("Network failure")

    with pytest.raises(ConnectionError):
        await cb.call(fail_call)
    assert cb.state == CircuitState.CLOSED

    # Trigger failure 2 -> reaches threshold -> transitions to OPEN
    with pytest.raises(ConnectionError):
        await cb.call(fail_call)
    assert cb.state == CircuitState.OPEN

    # Calling when OPEN raises CircuitBreakerOpenException immediately without calling func
    with pytest.raises(CircuitBreakerOpenException):
        await cb.call(fail_call)

    # Wait for recovery cooldown
    await asyncio.sleep(0.15)
    assert cb.state == CircuitState.HALF_OPEN

    # Success in HALF_OPEN transitions back to CLOSED
    async def success_call():
        return "ok"

    res1 = await cb.call(success_call)
    res2 = await cb.call(success_call)
    assert res1 == "ok" and res2 == "ok"
    assert cb.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = TokenBucketRateLimiter(rate_limit=10.0, time_period=1.0, burst=2)
    # Fast acquire within burst
    await limiter.acquire(1.0)
    await limiter.acquire(1.0)
    assert True


@pytest.mark.asyncio
async def test_retry_success():
    attempts = 0

    async def flaky_call():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ConnectionError("Temporary blip")
        return "success"

    result = await execute_with_retry(flaky_call, max_attempts=3, min_wait=0.01, max_wait=0.05)
    assert result == "success"
    assert attempts == 2
