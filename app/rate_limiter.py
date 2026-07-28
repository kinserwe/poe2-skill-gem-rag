import math
import time
from collections.abc import Callable
from typing import NamedTuple

from app.config import settings


class RateLimitResult(NamedTuple):
    allowed: bool
    retry_after: int = 0


class RateLimiter:
    def __init__(
        self,
        capacity: int = settings.ASK_CAPACITY,
        rate_per_minute: int = settings.ASK_RATE_PER_MINUTE,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.capacity = capacity
        self.tokens_per_second = rate_per_minute / 60
        self.clock = clock
        self.users = {}

    def check(self, key: str) -> RateLimitResult:
        now = self.clock()
        if key not in self.users:
            self.users[key] = (self.capacity, now)

        tokens, last_seen = self.users[key]
        elapsed = now - last_seen
        tokens = min(self.capacity, tokens + elapsed * self.tokens_per_second)
        if tokens >= 1:
            self.users[key] = (tokens - 1, now)
            return RateLimitResult(allowed=True)

        retry_after = math.ceil((1 - tokens) / self.tokens_per_second)
        return RateLimitResult(allowed=False, retry_after=retry_after)


_limiter = RateLimiter()


def get_limiter() -> RateLimiter:
    return _limiter
