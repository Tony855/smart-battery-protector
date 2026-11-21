"""Authenticated device event ingestion endpoint."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pydantic import ValidationError
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.audit import write_audit_event
from app.device_auth import canonical_request_target
from app.device_auth_service import authenticate_device_request
from app.rate_limit import RedisFixedWindowLimiter, rate_limit_source
from app.redis_replay_store import RedisReplayStore
from app.request_body import read_limited_body
from app.runtime import database_connection, redis_client

router = APIRouter(prefix="/api/v1/device", tags=["device"])
MAX_EVENT_BODY = 16 * 1024


class DeviceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_uuid: UUID
    event_type: str = Field(min_length=1, max_length=48, pattern=r"^[a-z][a-z0-9_.-]*$")
    fault_code: str | None = Field(default=None, max_length=48)
    occurred_at: datetime
    details: dict | None = None


@router.post("/events", status_code=202)
async def ingest_device_event(request: Request):
    try:
        redis = redis_client()
        limiter = RedisFixedWindowLimiter(redis)
        # The source key is derived from the socket peer, not an untrusted key-id
        # header. IPv6 addresses are grouped by /64 to limit key churn.
        source = rate_limit_source(request.client.host if request.client else None)
        if not limiter.allow(f"device-source:{source}", limit=6000, window_seconds=60):
            raise HTTPException(status_code=429, detail="rate_limit_exceeded")

        raw = await read_limited_body(
            request, max_bytes=MAX_EVENT_BODY, too_large_detail="event_body_too_large"
        )
        key_id = request.headers.get("x-sbp-key-id", "")
        timestamp = request.headers.get("x-sbp-timestamp", "")
        nonce = request.headers.get("x-sbp-nonce", "")
        signature = request.headers.get("x-sbp-signature", "")
        if not all((key_id, timestamp, nonce, signature)):
            raise HTTPException(status_code=401, detail="device_authentication_required")

        device_id = authenticate_device_request(
            connection_factory=database_connection,
            replay_store=RedisReplayStore(redis),
            key_id=key_id,
            timestamp=timestamp,
            nonce=nonce,
            method=request.method,
            path=canonical_request_target(request.url.path, request.url.query),
            body=raw,
            signature=signature,
        )
        if device_id is None:
            raise HTTPException(status_code=401, detail="device_authentication_failed")
        if not limiter.allow(f"device-event:{device_id}", limit=30, window_seconds=60):
            raise HTTPException(status_code=429, detail="rate_limit_exceeded")

        try:
            event = DeviceEvent.model_validate_json(raw)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail="invalid_device_event") from exc
        if event.occurred_at.tzinfo is None:
            raise HTTPException(status_code=422, detail="occurred_at_timezone_required")

        connection = database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO device_events
                      (device_id, event_uuid, event_type, fault_code, occurred_at, details)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (device_id, event_uuid) DO NOTHING
                    """,
                    (
                        device_id, event.event_uuid, event.event_type,
                        event.fault_code, event.occurred_at.astimezone(timezone.utc),
                        json.dumps(event.details, separators=(",", ":")) if event.details is not None else None,
                    ),
                )
                created = cursor.rowcount == 1
            with connection.cursor() as cursor:
                cursor.execute("UPDATE devices SET last_seen_at=CURRENT_TIMESTAMP WHERE id=%s", (device_id,))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        write_audit_event(
            database_connection, actor_type="device", actor_id=str(device_id),
            action="device.event.ingest", target_type="device",
            target_id=str(device_id), result="accepted",
        )
        return {"accepted": True, "duplicate": not created}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="device_event_service_unavailable") from exc
