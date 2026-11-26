"""Ensure locked/deleted user accounts cannot access bound-device APIs."""
from fastapi import HTTPException
import pytest

from app.account import _require_device_role, list_my_devices
from app.device_data import _authorized_device


class Cursor:
    def __init__(self, row=None):
        self.row = row
        self.query = ""

    def execute(self, query, params):
        self.query = query

    def fetchone(self):
        return self.row

    def fetchall(self):
        return []


class Connection:
    def __init__(self, cursor):
        self.cur = cursor
        self.closed = False

    def cursor(self):
        return self.cur

    def close(self):
        self.closed = True


def test_device_data_authorization_requires_active_user_status():
    cursor = Cursor(row=None)
    with pytest.raises(HTTPException) as exc:
        _authorized_device(cursor, "locked-subject", "SBP-000001")
    assert exc.value.status_code == 404
    assert "u.status='active'" in cursor.query


def test_member_management_role_lookup_requires_active_user_status():
    cursor = Cursor(row=None)
    with pytest.raises(HTTPException) as exc:
        _require_device_role(cursor, "locked-subject", "SBP-000001", ("owner", "admin"))
    assert exc.value.status_code == 404
    assert "u.status='active'" in cursor.query


def test_list_my_devices_filters_inactive_users(monkeypatch):
    import app.account as account

    cursor = Cursor()
    connection = Connection(cursor)
    monkeypatch.setattr(account, "require_user_subject", lambda authorization: "locked-subject")
    monkeypatch.setattr(account, "database_connection", lambda: connection)
    assert list_my_devices(authorization="Bearer test") == {"devices": []}
    assert "u.status='active'" in cursor.query
    assert connection.closed
