"""Cross-worker replay protection backed by Redis SET NX with expiry."""
from __future__ import annotations

import hashlib
from typing import Protocol


class RedisLike(Protocol):
    def set(self, name: str, value: str, *, nx: bool, ex: int) -> bool | None: ...


class RedisReplayStore:
    """Production replay store. Redis errors intentionally propagate (fail closed)."""

    def __init__(self, client: RedisLike, namespace: str = "sbp:device-nonce"):
        self._client = client
        self._namespace = namespace.rstrip(":")

    def claim(self, key: str, ttl_seconds: int) -> bool:
        if not key or ttl_seconds < 1:
            return False
        # Hash the caller-provided key so identifiers/nonces are not exposed in Redis key names.
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        result = self._client.set(
            f"{self._namespace}:{digest}", "1", nx=True, ex=ttl_seconds
        )
        return result is True
