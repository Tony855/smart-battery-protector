"""Composition layer for device authentication; intentionally not a route."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.device_auth import ReplayStore, verify_device_request
from app.device_credentials import ActiveDeviceCredential, load_active_device_credential


def authenticate_device_request(
    *,
    connection_factory: Callable[[], Any],
    replay_store: ReplayStore,
    key_id: str,
    timestamp: str,
    nonce: str,
    method: str,
    path: str,
    body: bytes,
    signature: str,
    now: float | None = None,
) -> int | None:
    """Return the authenticated device ID; None means reject.

    Infrastructure errors (database/Redis unavailable) deliberately propagate so
    the future HTTP adapter can return 503 rather than silently bypassing checks.
    """
    credential: ActiveDeviceCredential | None = load_active_device_credential(
        connection_factory, key_id
    )
    if credential is None:
        return None
    accepted = verify_device_request(
        key_id=key_id,
        timestamp=timestamp,
        nonce=nonce,
        method=method,
        path=path,
        body=body,
        signature=signature,
        public_key_raw=credential.public_key_raw,
        replay_store=replay_store,
        now=now,
    )
    return credential.device_id if accepted else None
