import asyncio
from enum import Enum
import logging
import time
from typing import Callable, Optional, Type

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenException(Exception):
    def __init__(self, service_name: str, reset_timeout_remaining: float):
        super().__init__(
            f"Circuit breaker for '{service_name}' is OPEN. "
            f"Recovery cooldown: {reset_timeout_remaining:.1f}s remaining."
        )
        self.service_name = service_name
        self.reset_timeout_remaining = reset_timeout_remaining


class CircuitBreaker:
    """Production circuit breaker supporting failure thresholds, cooldowns, and half-open testing."""

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_trials: int = 2,
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_trials = half_open_max_trials

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._half_open_successes = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                logger.info("Circuit breaker [%s] transitioning OPEN -> HALF_OPEN", self.service_name)
                self._state = CircuitState.HALF_OPEN
                self._half_open_successes = 0
        return self._state

    async def call(self, func: Callable, *args, **kwargs):
        async with self._lock:
            current_state = self.state
            if current_state == CircuitState.OPEN:
                remaining = self.recovery_timeout - (time.time() - self._last_failure_time)
                raise CircuitBreakerOpenException(self.service_name, max(0.0, remaining))

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            async with self._lock:
                self._on_success()
            return result
        except Exception as e:
            async with self._lock:
                self._on_failure(e)
            raise

    def _on_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_successes += 1
            if self._half_open_successes >= self.half_open_max_trials:
                logger.info("Circuit breaker [%s] transitioning HALF_OPEN -> CLOSED (healthy)", self.service_name)
                self._state = CircuitState.CLOSED
                self._failure_count = 0
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0

    def _on_failure(self, exception: Exception) -> None:
        self._failure_count += 1
        self._last_failure_time = time.time()
        logger.warning(
            "Circuit breaker [%s] recorded failure (%s). Total consecutive failures: %d",
            self.service_name,
            exception,
            self._failure_count,
        )

        if self._state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            if self._failure_count >= self.failure_threshold or self._state == CircuitState.HALF_OPEN:
                logger.error(
                    "Circuit breaker [%s] threshold reached. Transitioning to OPEN for %.1fs",
                    self.service_name,
                    self.recovery_timeout,
                )
                self._state = CircuitState.OPEN
