#!/usr/bin/env python3
"""Generate and persist a one-time device claim code; print it exactly once."""
from __future__ import annotations

import argparse
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.runtime import database_connection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--ttl-hours", type=int, default=24)
    args = parser.parse_args()
    if not 1 <= args.ttl_hours <= 168:
        parser.error("--ttl-hours must be between 1 and 168")

    try:
        connection = database_connection()
    except RuntimeError as exc:
        parser.error(str(exc))

    code = secrets.token_urlsafe(24)
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(hours=args.ttl_hours)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, lifecycle_status FROM devices WHERE serial_number=%s FOR UPDATE",
                (args.serial,),
            )
            device = cursor.fetchone()
            if not device or device["lifecycle_status"] != "provisioning":
                raise SystemExit("device_not_found_or_not_in_provisioning_state")
            cursor.execute(
                "UPDATE device_claim_codes SET used_at=CURRENT_TIMESTAMP "
                "WHERE device_id=%s AND used_at IS NULL",
                (device["id"],),
            )
            cursor.execute(
                "INSERT INTO device_claim_codes (device_id, code_hash, expires_at) "
                "VALUES (%s, %s, %s)",
                (device["id"], digest, expires),
            )
    connection.close()

    print("ONE-TIME DEVICE CLAIM CODE (displayed once; store securely):")
    print(code)
    print(f"Expires after {args.ttl_hours} hour(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
