import pytest
from pydantic import ValidationError

from app.account import BindDeviceRequest


def test_bind_request_validates_serial_and_claim_code():
    request = BindDeviceRequest(serial_number="SBP-000001", claim_code="A1b2C3d4E5f6G7h8")
    assert request.serial_number == "SBP-000001"


@pytest.mark.parametrize("payload", [
    {"serial_number": "bad serial", "claim_code": "A1b2C3d4E5f6G7h8"},
    {"serial_number": "SBP-000001", "claim_code": "short"},
    {"serial_number": "SBP-000001", "claim_code": "A1b2C3d4E5f6G7h8", "role": "owner"},
])
def test_bind_request_rejects_invalid_or_extra_fields(payload):
    with pytest.raises(ValidationError):
        BindDeviceRequest(**payload)

from fastapi.testclient import TestClient


def test_device_list_requires_user_bearer_token():
    from app.main import app

    response = TestClient(app).get("/api/v1/me/devices")
    assert response.status_code == 401
    assert response.json()["detail"] == "user_authentication_required"


from app.account import AddMemberRequest


def test_member_role_allowlist():
    assert AddMemberRequest(auth_subject="subject-1", role="viewer").role == "viewer"
    assert AddMemberRequest(auth_subject="subject-2", role="admin").role == "admin"


@pytest.mark.parametrize("role", ["owner", "root", "device-control", ""])
def test_member_role_rejects_escalation(role):
    with pytest.raises(ValidationError):
        AddMemberRequest(auth_subject="subject-1", role=role)
