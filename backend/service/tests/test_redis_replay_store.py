from app.redis_replay_store import RedisReplayStore


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.calls = []

    def set(self, name, value, *, nx, ex):
        self.calls.append((name, value, nx, ex))
        if nx and name in self.values:
            return None
        self.values[name] = value
        return True


def test_nonce_claim_is_atomic_and_repeat_is_rejected():
    redis = FakeRedis()
    store = RedisReplayStore(redis)
    assert store.claim("device-1:nonce-123", 601) is True
    assert store.claim("device-1:nonce-123", 601) is False
    assert redis.calls[0][2:] == (True, 601)
    assert redis.calls[0][0].startswith("sbp:device-nonce:")


def test_invalid_ttl_or_key_is_rejected():
    store = RedisReplayStore(FakeRedis())
    assert store.claim("", 10) is False
    assert store.claim("k", 0) is False
