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
