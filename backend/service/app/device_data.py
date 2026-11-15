"""Owner/member-scoped device status and fault/event history APIs."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query

from app.auth import require_user_subject
from app.runtime import database_connection

router = APIRouter(prefix="/api/v1/me/devices", tags=["device-data"])


def _authorized_device(cursor, subject: str, serial_number: str) -> int:
    cursor.execute(
        """
        SELECT d.id
          FROM devices d
          JOIN device_bindings b ON b.device_id=d.id AND b.revoked_at IS NULL
          JOIN users u ON u.id=b.user_id
         WHERE d.serial_number=%s AND u.auth_subject=%s
         LIMIT 1
        """,
        (serial_number, subject),
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="device_or_membership_not_found")
    return int(row["id"])


@router.get("/{serial_number}/status")
def get_device_status(serial_number: str, authorization: str | None = Header(default=None)):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            device_id = _authorized_device(cursor, subject, serial_number)
            cursor.execute(
                """
                SELECT d.serial_number, d.model_id, d.hw_revision, d.fw_version,
                       d.lifecycle_status, d.last_seen_at,
                       CASE WHEN d.last_seen_at >= CURRENT_TIMESTAMP - INTERVAL '90 seconds'
                            THEN 'online' ELSE 'offline' END AS connection_status,
                       t.observed_at, t.battery_voltage_v, t.battery_current_a,
                       t.temperature_c, t.state_code, t.engine_running
                  FROM devices d
                  LEFT JOIN device_telemetry t ON t.device_id=d.id
                   AND t.id=(SELECT MAX(t2.id) FROM device_telemetry t2 WHERE t2.device_id=d.id)
                 WHERE d.id=%s
                """,
                (device_id,),
            )
            row = cursor.fetchone()
        return {"device": row}
    finally:
        connection.close()


@router.get("/{serial_number}/events")
def get_device_events(
    serial_number: str,
    authorization: str | None = Header(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    before_id: int | None = Query(default=None, gt=0),
):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            device_id = _authorized_device(cursor, subject, serial_number)
            if before_id is None:
                cursor.execute(
                    """
                    SELECT id, event_uuid, event_type, fault_code, occurred_at,
                           received_at, details
                      FROM device_events
                     WHERE device_id=%s
                     ORDER BY id DESC LIMIT %s
                    """,
                    (device_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, event_uuid, event_type, fault_code, occurred_at,
                           received_at, details
                      FROM device_events
                     WHERE device_id=%s AND id < %s
                     ORDER BY id DESC LIMIT %s
                    """,
                    (device_id, before_id, limit),
                )
            rows = cursor.fetchall()
        return {"events": rows, "next_before_id": rows[-1]["id"] if len(rows) == limit else None}
    finally:
        connection.close()
