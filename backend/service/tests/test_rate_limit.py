from app.rate_limit import RedisFixedWindowLimiter


class FakeRedis:
    def __init__(self):
        self.counts = {}
        self.calls = []

    def eval(self, script, numkeys, *args):
        self.calls.append((script, numkeys, args))
        key, ttl = args
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]


def test_fixed_window_allows_limit_then_rejects():
    redis = FakeRedis()
    limiter = RedisFixedWindowLimiter(redis)
    assert limiter.allow("device:1", limit=2, window_seconds=60) is True
    assert limiter.allow("device:1", limit=2, window_seconds=60) is True
    assert limiter.allow("device:1", limit=2, window_seconds=60) is False
    assert redis.calls[0][1] == 1
    assert redis.calls[0][2][1] == "60"


def test_invalid_rate_limit_parameters_reject():
    limiter = RedisFixedWindowLimiter(FakeRedis())
    assert limiter.allow("", limit=2, window_seconds=60) is False
    assert limiter.allow("x", limit=0, window_seconds=60) is False
