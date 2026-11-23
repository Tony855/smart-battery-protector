"""User identity and device ownership APIs."""
from __future__ import annotations

import hashlib
import hmac
import json

import psycopg
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.auth import require_user_subject
from app.runtime import database_connection

router = APIRouter(prefix="/api/v1/me", tags=["account"])


class BindDeviceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    serial_number: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    claim_code: str = Field(min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")


class AddMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    auth_subject: str = Field(min_length=1, max_length=191)
    role: str = Field(pattern=r"^(admin|viewer)$")




def _write_account_audit(cursor, actor_subject: str, action: str,
                         serial_number: str, metadata: dict) -> None:
    """Insert an account/device action audit row in the caller's transaction."""
    cursor.execute(
        """
        INSERT INTO audit_events
          (actor_type, actor_id, action, target_type, target_id, result, metadata)
        VALUES ('user', %s, %s, 'device', %s, 'accepted', %s::jsonb)
        """,
        (actor_subject[:128], action[:96], serial_number[:128],
         json.dumps(metadata, separators=(",", ":"))),
    )



def _user_id(cursor, subject: str) -> int:
    cursor.execute(
        """
        INSERT INTO users (auth_subject) VALUES (%s)
        ON CONFLICT (auth_subject) DO UPDATE SET auth_subject=EXCLUDED.auth_subject
        RETURNING id
        """,
        (subject,),
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=503, detail="user_account_lookup_failed")
    user_id = int(user["id"])
    cursor.execute("SELECT status FROM users WHERE id=%s LIMIT 1", (user_id,))
    status = cursor.fetchone()
    if not status or status["status"] != "active":
        raise HTTPException(status_code=403, detail="user_account_inactive")
    return user_id


@router.get("/devices")
def list_my_devices(authorization: str | None = Header(default=None)):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.serial_number, d.model_id, d.hw_revision, d.fw_version,
                       d.lifecycle_status, d.last_seen_at,
                       CASE WHEN d.last_seen_at >= CURRENT_TIMESTAMP - INTERVAL '90 seconds'
                            THEN 'online' ELSE 'offline' END AS connection_status,
                       b.role, b.bound_at
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
                 WHERE device_id=%s AND used_at IS NULL AND expires_at > CURRENT_TIMESTAMP
                 ORDER BY created_at DESC LIMIT 1 FOR UPDATE
                """,
                (device["id"],),
            )
            claim = cursor.fetchone()
            if not claim or not hmac.compare_digest(claim["code_hash"], code_hash):
                raise HTTPException(status_code=400, detail="invalid_or_expired_claim_code")
            cursor.execute(
                "UPDATE device_claim_codes SET used_at=CURRENT_TIMESTAMP WHERE id=%s AND used_at IS NULL",
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
            _write_account_audit(
                cursor, subject, "device.claim", payload.serial_number,
                {"device_id": int(device["id"]), "role": "owner"},
            )
        connection.commit()
        return {"bound": True, "serial_number": payload.serial_number, "role": "owner"}
    except HTTPException:
        connection.rollback()
        raise
    except psycopg.errors.UniqueViolation as exc:
        connection.rollback()
        raise HTTPException(status_code=409, detail="device_already_claimed") from exc
    except Exception as exc:
        connection.rollback()
        raise HTTPException(status_code=503, detail="device_binding_service_unavailable") from exc
    finally:
        connection.close()


def _require_device_role(cursor, subject: str, serial_number: str, allowed: tuple[str, ...]):
    cursor.execute(
        """
        SELECT d.id AS device_id, b.role
          FROM devices d
          JOIN device_bindings b ON b.device_id=d.id AND b.revoked_at IS NULL
          JOIN users u ON u.id=b.user_id
         WHERE d.serial_number=%s AND u.auth_subject=%s
         LIMIT 1 FOR UPDATE
        """,
        (serial_number, subject),
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="device_or_membership_not_found")
    if row["role"] not in allowed:
        raise HTTPException(status_code=403, detail="insufficient_device_role")
    return int(row["device_id"]), row["role"]


@router.get("/devices/{serial_number}/members")
def list_device_members(serial_number: str, authorization: str | None = Header(default=None)):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            _require_device_role(cursor, subject, serial_number, ("owner", "admin"))
            cursor.execute(
                """
                SELECT u.auth_subject, b.role, b.bound_at
                  FROM device_bindings b
                  JOIN devices d ON d.id=b.device_id
                  JOIN users u ON u.id=b.user_id
                 WHERE d.serial_number=%s AND b.revoked_at IS NULL
                 ORDER BY CASE b.role WHEN 'owner' THEN 0 WHEN 'admin' THEN 1 ELSE 2 END,
                          b.bound_at
                """,
                (serial_number,),
            )
            rows = cursor.fetchall()
        return {"members": rows}
    finally:
        connection.close()


@router.post("/devices/{serial_number}/members", status_code=201)
def add_device_member(
    serial_number: str,
    payload: AddMemberRequest,
    authorization: str | None = Header(default=None),
):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            device_id, actor_role = _require_device_role(
                cursor, subject, serial_number, ("owner", "admin")
            )
            if actor_role == "admin" and payload.role != "viewer":
                raise HTTPException(status_code=403, detail="admin_can_only_add_viewers")
            target_id = _user_id(cursor, payload.auth_subject)
            cursor.execute(
                "SELECT id FROM device_bindings WHERE device_id=%s AND user_id=%s AND revoked_at IS NULL FOR UPDATE",
                (device_id, target_id),
            )
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="user_already_bound")
            cursor.execute(
                "INSERT INTO device_bindings (device_id,user_id,role) VALUES (%s,%s,%s)",
                (device_id, target_id, payload.role),
            )
            _write_account_audit(
                cursor, subject, "device.member.add", serial_number,
                {"device_id": device_id, "member_subject": payload.auth_subject,
                 "role": payload.role},
            )
        connection.commit()
        return {"added": True, "auth_subject": payload.auth_subject, "role": payload.role}
    except HTTPException:
        connection.rollback()
        raise
    except psycopg.errors.UniqueViolation as exc:
        connection.rollback()
        raise HTTPException(status_code=409, detail="user_already_bound") from exc
    except Exception as exc:
        connection.rollback()
        raise HTTPException(status_code=503, detail="device_member_service_unavailable") from exc
    finally:
        connection.close()


@router.delete("/devices/{serial_number}/members/{member_subject}", status_code=200)
def revoke_device_member(
    serial_number: str,
    member_subject: str,
    authorization: str | None = Header(default=None),
):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            device_id, actor_role = _require_device_role(
                cursor, subject, serial_number, ("owner", "admin")
            )
            cursor.execute(
                """
                SELECT b.id, b.role, u.auth_subject
                  FROM device_bindings b
                  JOIN users u ON u.id=b.user_id
                 WHERE b.device_id=%s AND u.auth_subject=%s AND b.revoked_at IS NULL
                 LIMIT 1 FOR UPDATE
                """,
                (device_id, member_subject),
            )
            target = cursor.fetchone()
            if not target:
                raise HTTPException(status_code=404, detail="active_member_not_found")
            if target["role"] == "owner":
                raise HTTPException(status_code=403, detail="owner_binding_cannot_be_revoked")
            if actor_role == "admin" and target["role"] != "viewer":
                raise HTTPException(status_code=403, detail="admin_can_only_remove_viewers")
            cursor.execute(
                "UPDATE device_bindings SET revoked_at=CURRENT_TIMESTAMP WHERE id=%s AND revoked_at IS NULL",
                (target["id"],),
            )
            _write_account_audit(
                cursor, subject, "device.member.revoke", serial_number,
                {"device_id": device_id, "member_subject": member_subject,
                 "role": target["role"]},
            )
        connection.commit()
        return {"revoked": True, "auth_subject": member_subject}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as exc:
        connection.rollback()
        raise HTTPException(status_code=503, detail="device_member_service_unavailable") from exc
    finally:
        connection.close()
