#!/usr/bin/env python3
"""Generate and persist a one-time device claim code; print it exactly once."""
from __future__ import annotations

import argparse
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import pymysql


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--ttl-hours", type=int, default=24)
    args = parser.parse_args()
    if not 1 <= args.ttl_hours <= 168:
        parser.error("--ttl-hours must be between 1 and 168")

    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    import os
    if any(not os.getenv(name) for name in required):
        parser.error("database environment variables are incomplete")

    code = secrets.token_urlsafe(24)
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=args.ttl_hours)
    connection = pymysql.connect(
        host=os.environ["SBP_DB_HOST"],
        port=int(os.getenv("SBP_DB_PORT", "3306")),
        user=os.environ["SBP_DB_USER"],
        password=os.environ["SBP_DB_PASSWORD"],
        database=os.environ["SBP_DB_NAME"],
        connect_timeout=3,
        read_timeout=3,
        write_timeout=3,
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, lifecycle_status FROM devices WHERE serial_number=%s FOR UPDATE",
                (args.serial,),
            )
            device = cursor.fetchone()
            if not device or device["lifecycle_status"] != "provisioning":
                raise SystemExit("device_not_found_or_not_in_provisioning_state")
            cursor.execute(
                "UPDATE device_claim_codes SET used_at=UTC_TIMESTAMP(3) "
                "WHERE device_id=%s AND used_at IS NULL",
                (device["id"],),
            )
            cursor.execute(
                "INSERT INTO device_claim_codes (device_id, code_hash, expires_at) "
                "VALUES (%s, %s, %s)",
                (device["id"], digest, expires),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print("ONE-TIME DEVICE CLAIM CODE (displayed once; store securely):")
    print(code)
    print(f"Expires after {args.ttl_hours} hour(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
