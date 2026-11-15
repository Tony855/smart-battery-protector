"""Read-only device credential lookup; never returns secret material."""
from __future__ import annotations

import base64
import binascii
from collections.abc import Callable
from typing import Any


def load_active_device_key(connection_factory: Callable[[], Any], key_id: str) -> bytes | None:
    """Return a raw Ed25519 public key only for an active credential and device."""
    connection = connection_factory()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT dc.public_key_base64
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
        encoded = row.get("public_key_base64") if isinstance(row, dict) else row[0]
        if not encoded:
            return None
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            return None
        return raw if len(raw) == 32 else None
    finally:
        connection.close()
