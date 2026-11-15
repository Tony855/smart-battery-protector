"""User identity and device ownership APIs."""
from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.auth import require_user_subject
from app.runtime import database_connection

router = APIRouter(prefix="/api/v1/me", tags=["account"])


class BindDeviceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    serial_number: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    claim_code: str = Field(min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")


def _user_id(cursor, subject: str) -> int:
    cursor.execute(
        "INSERT INTO users (auth_subject) VALUES (%s) "
        "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
        (subject,),
    )
    cursor.execute("SELECT id, status FROM users WHERE auth_subject=%s LIMIT 1", (subject,))
    user = cursor.fetchone()
    if not user or user["status"] != "active":
        raise HTTPException(status_code=403, detail="user_account_inactive")
    return int(user["id"])


@router.get("/devices")
def list_my_devices(authorization: str | None = Header(default=None)):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.serial_number, d.model_id, d.hw_revision, d.fw_version,
                       d.lifecycle_status, b.role, b.bound_at
                  FROM device_bindings b
                  JOIN devices d ON d.id=b.device_id
                  JOIN users u ON u.id=b.user_id
                 WHERE u.auth_subject=%s AND b.revoked_at IS NULL
                 ORDER BY b.bound_at DESC
                """,
                (subject,),
            )
            rows = cursor.fetchall()
        return {"devices": rows}
    finally:
        connection.close()


@router.post("/devices/bind", status_code=201)
def bind_device(payload: BindDeviceRequest, authorization: str | None = Header(default=None)):
    subject = require_user_subject(authorization)
    code_hash = hashlib.sha256(payload.claim_code.encode("utf-8")).hexdigest()
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            user_id = _user_id(cursor, subject)
            cursor.execute(
                "SELECT id, lifecycle_status FROM devices WHERE serial_number=%s FOR UPDATE",
                (payload.serial_number,),
            )
            device = cursor.fetchone()
            if not device:
                raise HTTPException(status_code=404, detail="device_not_found")
            if device["lifecycle_status"] != "provisioning":
                raise HTTPException(status_code=409, detail="device_not_available_for_claim")
            cursor.execute(
                """
                SELECT id, code_hash FROM device_claim_codes
                 WHERE device_id=%s AND used_at IS NULL AND expires_at > UTC_TIMESTAMP(3)
                 ORDER BY created_at DESC LIMIT 1 FOR UPDATE
                """,
                (device["id"],),
            )
            claim = cursor.fetchone()
            if not claim or not hmac.compare_digest(claim["code_hash"], code_hash):
                raise HTTPException(status_code=400, detail="invalid_or_expired_claim_code")
            cursor.execute(
                "UPDATE device_claim_codes SET used_at=UTC_TIMESTAMP(3) WHERE id=%s AND used_at IS NULL",
                (claim["id"],),
            )
            if cursor.rowcount != 1:
                raise HTTPException(status_code=409, detail="claim_code_already_used")
            cursor.execute(
                "UPDATE devices SET lifecycle_status='active' WHERE id=%s AND lifecycle_status='provisioning'",
                (device["id"],),
            )
            if cursor.rowcount != 1:
                raise HTTPException(status_code=409, detail="device_claim_conflict")
            cursor.execute(
                "INSERT INTO device_bindings (device_id, user_id, role) VALUES (%s, %s, 'owner')",
                (device["id"], user_id),
            )
        connection.commit()
        return {"bound": True, "serial_number": payload.serial_number, "role": "owner"}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as exc:
        connection.rollback()
        raise HTTPException(status_code=503, detail="device_binding_service_unavailable") from exc
    finally:
        connection.close()
