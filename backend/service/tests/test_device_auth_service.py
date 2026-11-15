import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.device_auth import InMemoryReplayStore, canonical_request
from app.device_auth_service import authenticate_device_request
from app.device_credentials import ActiveDeviceCredential


def test_authentication_returns_device_id_only_after_signature_and_nonce_checks(monkeypatch):
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    monkeypatch.setattr(
        "app.device_auth_service.load_active_device_credential",
        lambda factory, key_id: ActiveDeviceCredential(17, public),
    )
    args = dict(
        key_id="device-key-17",
        timestamp="1700000000",
        nonce="abcdefghijklmnop",
        method="POST",
        path="/api/v1/device/telemetry",
        body=b'{"voltage_mv":12500}',
    )
    signature = base64.urlsafe_b64encode(
        private.sign(canonical_request(**args))
    ).decode().rstrip("=")
    kwargs = dict(
        connection_factory=lambda: None,
        replay_store=InMemoryReplayStore(),
        **args,
        signature=signature,
        now=1700000000,
    )
    assert authenticate_device_request(**kwargs) == 17
    assert authenticate_device_request(**kwargs) is None


def test_invalid_signature_does_not_authenticate(monkeypatch):
    monkeypatch.setattr(
        "app.device_auth_service.load_active_device_credential",
        lambda factory, key_id: ActiveDeviceCredential(18, bytes(32)),
    )
    assert authenticate_device_request(
        connection_factory=lambda: None,
        replay_store=InMemoryReplayStore(),
        key_id="device-key-18",
        timestamp="1700000000",
        nonce="abcdefghijklmnop",
        method="POST",
        path="/api/v1/device/telemetry",
        body=b"",
        signature="invalid",
        now=1700000000,
    ) is None
