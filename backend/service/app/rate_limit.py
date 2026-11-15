"""Atomic fixed-window rate limiting backed by Redis."""
from __future__ import annotations

import hashlib
from typing import Protocol


_INCREMENT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


class RedisEvalLike(Protocol):
    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int: ...


class RedisFixedWindowLimiter:
    """Fixed-window limiter; Redis errors propagate so callers can fail closed."""

    def __init__(self, client: RedisEvalLike, namespace: str = "sbp:rate"):
        self._client = client
        self._namespace = namespace.rstrip(":")

    def allow(self, subject: str, *, limit: int, window_seconds: int) -> bool:
        if not subject or limit < 1 or window_seconds < 1:
            return False
        digest = hashlib.sha256(subject.encode("utf-8")).hexdigest()
        count = self._client.eval(
            _INCREMENT_SCRIPT, 1,
            f"{self._namespace}:{digest}", str(window_seconds),
        )
        return int(count) <= limit
