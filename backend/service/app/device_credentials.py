"""Read-only device credential lookup; never returns secret material."""
from __future__ import annotations

import base64
import binascii
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ActiveDeviceCredential:
    device_id: int
    public_key_raw: bytes


def load_active_device_credential(
    connection_factory: Callable[[], Any], key_id: str
) -> ActiveDeviceCredential | None:
    """Return an active device ID and raw Ed25519 key, or None on any invalid state."""
    connection = connection_factory()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT dc.device_id, dc.public_key_base64
                  FROM device_credentials AS dc
                  JOIN devices AS d ON d.id = dc.device_id
                 WHERE dc.key_id = %s
                   AND dc.credential_status = 'active'
                   AND d.lifecycle_status = 'active'
                 LIMIT 1
                """,
                (key_id,),
            )
            row = cursor.fetchone()
        if not row:
            return None
        if isinstance(row, dict):
            device_id = row.get("device_id")
            encoded = row.get("public_key_base64")
        else:
            device_id, encoded = row[0], row[1]
        if not isinstance(device_id, int) or device_id <= 0 or not encoded:
            return None
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            return None
        if len(raw) != 32:
            return None
        return ActiveDeviceCredential(device_id=device_id, public_key_raw=raw)
    finally:
        connection.close()
