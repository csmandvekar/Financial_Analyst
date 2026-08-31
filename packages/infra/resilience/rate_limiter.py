import asyncio
import time


class TokenBucketRateLimiter:
    """Async Token Bucket Rate Limiter for respecting external API rate limits."""

    def __init__(self, rate_limit: float, time_period: float = 1.0, burst: int = 5):
        """
        rate_limit: number of requests allowed
        time_period: time window in seconds (e.g. 1.0s or 60.0s)
        burst: maximum burst bucket capacity
        """
        self.rate = rate_limit / time_period
        self.capacity = float(burst)
        self.tokens = float(burst)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            # Add newly replenished tokens
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

            if self.tokens < tokens:
                needed = tokens - self.tokens
                wait_time = needed / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0.0
                self.last_update = time.monotonic()
            else:
                self.tokens -= tokens
