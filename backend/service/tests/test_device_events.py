import asyncio
import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from starlette.requests import Request

import app.device_events as device_events
from app.device_events import DeviceEvent


def test_device_event_requires_timezone_and_rejects_unknown_fields():
    event = DeviceEvent(
        event_uuid=uuid4(),
        event_type="protection.trip",
        occurred_at=datetime.now(timezone.utc),
    )
    assert event.occurred_at.tzinfo is not None
    with pytest.raises(ValidationError):
        DeviceEvent(
            event_uuid=uuid4(),
            event_type="Protection Trip",
            occurred_at=datetime.now(timezone.utc),
        )
    with pytest.raises(ValidationError):
        DeviceEvent(
            event_uuid=uuid4(),
            event_type="fault",
            occurred_at=datetime.now(timezone.utc),
            unexpected="value",
        )


def test_event_type_pattern_and_length_are_enforced():
    with pytest.raises(ValidationError):
        DeviceEvent(
            event_uuid=uuid4(),
            event_type="UPPERCASE",
            occurred_at=datetime.now(timezone.utc),
        )


class _FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params=None):
        self.connection.statements.append((query, params))
        if "INSERT INTO device_events" in query:
            self.rowcount = 1


class _FakeConnection:
    def __init__(self):
        self.statements = []
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return _FakeCursor(self)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class _AllowLimiter:
    def __init__(self, redis):
        self.redis = redis

    def allow(self, key, *, limit, window_seconds):
        return True


def _event_request():
    payload = {
        "event_uuid": str(uuid4()),
        "event_type": "protection.trip",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps(payload).encode("utf-8")
    messages = [{"type": "http.request", "body": body, "more_body": False}]

    async def receive():
        if messages:
            return messages.pop(0)
        return {"type": "http.disconnect"}

    headers = [
        (b"content-type", b"application/json"),
        (b"x-sbp-key-id", b"device-key-1"),
        (b"x-sbp-timestamp", b"1795600000"),
        (b"x-sbp-nonce", b"0123456789abcdef"),
        (b"x-sbp-signature", b"A" * 86),
    ]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/api/v1/device/events",
        "raw_path": b"/api/v1/device/events",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("test", 443),
    }
    return Request(scope, receive)


def _patch_event_route(monkeypatch, connection):
    monkeypatch.setattr(device_events, "redis_client", lambda: object())
    monkeypatch.setattr(device_events, "RedisFixedWindowLimiter", _AllowLimiter)
    monkeypatch.setattr(device_events, "rate_limit_source", lambda host: "test-source")
    monkeypatch.setattr(device_events, "authenticate_device_request", lambda **kwargs: 7)
    monkeypatch.setattr(device_events, "database_connection", lambda: connection)


def test_event_and_audit_row_commit_in_same_transaction(monkeypatch):
    connection = _FakeConnection()
    _patch_event_route(monkeypatch, connection)

    result = asyncio.run(device_events.ingest_device_event(_event_request()))

    assert result == {"accepted": True, "duplicate": False}
    statements = [query for query, _ in connection.statements]
    event_index = next(i for i, query in enumerate(statements) if "INSERT INTO device_events" in query)
    audit_index = next(i for i, query in enumerate(statements) if "INSERT INTO audit_events" in query)
    assert event_index < audit_index
    assert connection.committed
    assert not connection.rolled_back
    assert connection.closed


def test_audit_insert_failure_rolls_back_event_and_last_seen(monkeypatch):
    connection = _FakeConnection()
    _patch_event_route(monkeypatch, connection)

    def fail_audit(*args, **kwargs):
        raise RuntimeError("simulated audit storage failure")

    monkeypatch.setattr(device_events, "insert_audit_event", fail_audit)

    with pytest.raises(HTTPException) as error:
        asyncio.run(device_events.ingest_device_event(_event_request()))

    assert error.value.status_code == 503
    assert not connection.committed
    assert connection.rolled_back
    assert connection.closed
