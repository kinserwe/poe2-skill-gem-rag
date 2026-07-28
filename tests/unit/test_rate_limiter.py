import pytest

from app.rate_limiter import RateLimiter

_LIMITER_KEY = "127.0.0.1"


class ClockHelper:
    def __init__(self, now: float = 0.0):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def make_limiter():
    def _make_limiter(capacity: int) -> RateLimiter:
        clock = ClockHelper()
        return RateLimiter(capacity=capacity, rate_per_minute=10, clock=clock)

    return _make_limiter


class TestRateLimiter:
    def test_denied_when_exhausted(self, make_limiter):
        limiter = make_limiter(2)
        for _ in range(2):
            assert limiter.check(_LIMITER_KEY).allowed
        assert not limiter.check(_LIMITER_KEY).allowed

    def test_refills_over_time(self, make_limiter):
        limiter = make_limiter(2)
        for _ in range(2):
            assert limiter.check(_LIMITER_KEY).allowed
        limiter.clock.advance(3600)
        for _ in range(2):
            assert limiter.check(_LIMITER_KEY).allowed
        assert not limiter.check(_LIMITER_KEY).allowed

    def test_retry_after(self, make_limiter):
        limiter = make_limiter(2)
        for _ in range(2):
            assert limiter.check(_LIMITER_KEY).allowed
        not_allowed = limiter.check(_LIMITER_KEY)
        assert not not_allowed.allowed
        assert not_allowed.retry_after == 6

    def test_keys_are_independent(self, make_limiter):
        limiter = make_limiter(1)
        assert limiter.check(_LIMITER_KEY).allowed
        assert limiter.check("127.0.0.2").allowed
