"""Device request signature verification primitives.

This module is deliberately not wired to routes yet. Production must inject a
shared atomic nonce store (for example Redis SET NX with expiry) and load the
device public key from the credential repository.
"""
from __future__ import annotations

import base64
import hashlib
import re
import threading
import time
from collections.abc import Callable
from typing import Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_KEY_ID = re.compile(r"^[A-Za-z0-9._-]{1,96}$")
_NONCE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")


class ReplayStore(Protocol):
    def claim(self, key: str, ttl_seconds: int) -> bool: ...


class InMemoryReplayStore:
    """Single-process test/development store; not safe for multi-worker production."""
    def __init__(self, clock: Callable[[], float] = time.time):
        self._clock = clock
        self._items: dict[str, float] = {}
        self._lock = threading.Lock()

    def claim(self, key: str, ttl_seconds: int) -> bool:
        now = self._clock()
        with self._lock:
            expired = [item for item, expiry in self._items.items() if expiry <= now]
            for item in expired:
                del self._items[item]
            if key in self._items:
                return False
            self._items[key] = now + ttl_seconds
            return True


def canonical_request(key_id: str, timestamp: str, nonce: str,
                      method: str, path: str, body: bytes) -> bytes:
    body_digest = hashlib.sha256(body).hexdigest()
    fields = (key_id, timestamp, nonce, method.upper(), path, body_digest)
    if any("\n" in field or "\r" in field for field in fields):
        raise ValueError("invalid canonical request field")
    return "\n".join(fields).encode("utf-8")


def verify_device_request(*, key_id: str, timestamp: str, nonce: str,
                           method: str, path: str, body: bytes, signature: str,
                           public_key_raw: bytes, replay_store: ReplayStore,
                           now: float | None = None, max_skew_seconds: int = 300) -> bool:
    """Verify Ed25519 signature and claim nonce only after signature validation."""
    if not _KEY_ID.fullmatch(key_id) or not _NONCE.fullmatch(nonce):
        return False
    if not timestamp.isdigit() or len(timestamp) > 12:
        return False
    current = time.time() if now is None else now
    issued = int(timestamp)
    if abs(current - issued) > max_skew_seconds:
        return False
    try:
        if len(public_key_raw) != 32:
            return False
        sig = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        if len(sig) != 64:
            return False
        message = canonical_request(key_id, timestamp, nonce, method, path, body)
        Ed25519PublicKey.from_public_bytes(public_key_raw).verify(sig, message)
    except (ValueError, InvalidSignature, TypeError):
        return False
    return replay_store.claim(f"{key_id}:{nonce}", max_skew_seconds * 2 + 1)
