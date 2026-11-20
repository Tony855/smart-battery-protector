"""Authenticated device telemetry ingestion and owner-scoped history."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from typing import Literal

from fastapi import APIRouter, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.auth import require_user_subject
from app.device_auth import canonical_request_target
from app.device_auth_service import authenticate_device_request
from app.rate_limit import RedisFixedWindowLimiter, rate_limit_source
from app.redis_replay_store import RedisReplayStore
from app.request_body import read_limited_body
from app.runtime import database_connection, redis_client

router = APIRouter(tags=["telemetry"])
MAX_BODY = 8 * 1024


class TelemetrySample(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sample_uuid: UUID
    observed_at: datetime
    battery_voltage_v: Decimal = Field(ge=Decimal("0"), le=Decimal("60"), max_digits=6, decimal_places=3)
    battery_current_a: Decimal | None = Field(default=None, ge=Decimal("-1000"), le=Decimal("1000"), max_digits=9, decimal_places=3)
    # TMP117 valid measurement envelope: -55.0°C to +150.0°C, in 0.1°C units.
    temperature_deci_c: int | None = Field(default=None, ge=-550, le=1500)
    system_voltage_class: Literal[12, 24] | None = None
    state_code: str = Field(pattern=r"^(normal|charging|discharging|protected|fault|unknown)$")
    engine_running: str = Field(default="unknown", pattern=r"^(yes|no|unknown)$")


@router.post("/api/v1/device/telemetry", status_code=202)
async def ingest_telemetry(request: Request):
    try:
        redis = redis_client()
        limiter = RedisFixedWindowLimiter(redis)
        # Do not derive pre-auth Redis keys from the caller-controlled key-id.
        source = rate_limit_source(request.client.host if request.client else None)
        if not limiter.allow(f"device-source:{source}", limit=6000, window_seconds=60):
            raise HTTPException(status_code=429, detail="rate_limit_exceeded")

        raw = await read_limited_body(
            request, max_bytes=MAX_BODY, too_large_detail="telemetry_body_too_large"
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
        if not limiter.allow(f"device-telemetry:{device_id}", limit=60, window_seconds=60):
            raise HTTPException(status_code=429, detail="rate_limit_exceeded")

        try:
            sample = TelemetrySample.model_validate_json(raw)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail="invalid_telemetry_sample") from exc
        if sample.observed_at.tzinfo is None:
            raise HTTPException(status_code=422, detail="observed_at_timezone_required")

        connection = database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO device_telemetry
                      (device_id, sample_uuid, observed_at, battery_voltage_v,
                       battery_current_a, temperature_deci_c, system_voltage_class, state_code, engine_running)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (device_id, sample_uuid) DO NOTHING
                    """,
                    (
                        device_id, sample.sample_uuid, sample.observed_at.astimezone(timezone.utc),
                        sample.battery_voltage_v, sample.battery_current_a, sample.temperature_deci_c,
                        sample.system_voltage_class, sample.state_code, sample.engine_running,
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
        return {"accepted": True, "duplicate": not created}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="telemetry_service_unavailable") from exc


@router.get("/api/v1/me/devices/{serial_number}/telemetry")
def get_device_telemetry(
    serial_number: str,
    authorization: str | None = Header(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    subject = require_user_subject(authorization)
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT t.observed_at, t.battery_voltage_v, t.battery_current_a,
                       t.temperature_deci_c, t.system_voltage_class, t.state_code, t.engine_running
                  FROM device_telemetry t
                  JOIN devices d ON d.id=t.device_id
                  JOIN device_bindings b ON b.device_id=d.id AND b.revoked_at IS NULL
                  JOIN users u ON u.id=b.user_id
                 WHERE d.serial_number=%s AND u.auth_subject=%s
                 ORDER BY t.observed_at DESC LIMIT %s
                """,
                (serial_number, subject, limit),
            )
            rows = cursor.fetchall()
        return {"samples": rows}
    finally:
        connection.close()
