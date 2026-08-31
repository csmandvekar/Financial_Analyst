import logging
from typing import Any, Callable, TypeVar
import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


def is_retryable_exception(exc: BaseException) -> bool:
    """Determines whether an exception is transient and should be retried."""
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        # Retry 5xx server errors and 429 rate limits, but not 4xx client errors
        return exc.response.status_code in (429, 500, 502, 503, 504)
    if isinstance(exc, ConnectionError):
        return True
    return False


def log_retry_attempt(retry_state: RetryCallState) -> None:
    fn_name = retry_state.fn.__name__ if retry_state.fn else "unnamed_callable"
    logger.warning(
        "Retry attempt %d for %s failed with exception: %s. Next attempt in %.2fs...",
        retry_state.attempt_number,
        fn_name,
        retry_state.outcome.exception() if retry_state.outcome else "unknown",
        retry_state.next_action.sleep if retry_state.next_action else 0.0,
    )


async def execute_with_retry(
    func: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    min_wait: float = 0.5,
    max_wait: float = 4.0,
    **kwargs: Any,
) -> Any:
    """Executes an async callable with exponential backoff, jitter, and selective retry."""
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(multiplier=min_wait, max=max_wait),
        retry=retry_if_exception(is_retryable_exception),
        before_sleep=log_retry_attempt,
        reraise=True,
    ):
        with attempt:
            return await func(*args, **kwargs)
