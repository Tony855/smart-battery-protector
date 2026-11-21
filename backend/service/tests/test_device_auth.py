import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.device_auth import (
    InMemoryReplayStore,
    canonical_request,
    canonical_request_target,
    verify_device_request,
)


def make_keypair():
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private, public


def test_valid_signature_is_accepted_once_and_replay_is_rejected():
    private, public = make_keypair()
    store = InMemoryReplayStore()
    args = dict(key_id="dev-key-01", timestamp="1700000000",
                nonce="abcdefghijklmnop", method="post",
                path="/api/v1/device/events", body=b'{"ok":true}')
    signature = base64.urlsafe_b64encode(private.sign(canonical_request(**args))).decode().rstrip("=")
    verify_args = dict(args, signature=signature, public_key_raw=public, replay_store=store, now=1700000000)
    assert verify_device_request(**verify_args) is True
    assert verify_device_request(**verify_args) is False


def test_tampered_body_or_invalid_signature_is_rejected():
    private, public = make_keypair()
    args = dict(key_id="dev-key-01", timestamp="1700000000",
                nonce="abcdefghijklmnop", method="POST",
                path="/api/v1/device/events", body=b"original")
    signature = base64.urlsafe_b64encode(private.sign(canonical_request(**args))).decode().rstrip("=")
    assert verify_device_request(
        **dict(args, body=b"tampered", signature=signature, public_key_raw=public,
               replay_store=InMemoryReplayStore(), now=1700000000)
    ) is False


def test_expired_timestamp_is_rejected_before_nonce_claim():
    _, public = make_keypair()
    store = InMemoryReplayStore()
    assert verify_device_request(
        key_id="dev-key-01", timestamp="1699999000", nonce="abcdefghijklmnop",
        method="POST", path="/x", body=b"", signature="invalid",
        public_key_raw=public, replay_store=store, now=1700000000,
    ) is False
    assert store.claim("dev-key-01:abcdefghijklmnop", 30) is True


def test_signature_encoding_must_be_canonical_unpadded_base64url():
    private, public = make_keypair()
    args = dict(key_id="dev-key-01", timestamp="1700000000", nonce="abcdefghijklmnop",
                method="POST", path="/api/v1/device/events", body=b"{}")
    signature = base64.urlsafe_b64encode(private.sign(canonical_request(**args))).decode("ascii").rstrip("=")
    common = dict(args, public_key_raw=public, replay_store=InMemoryReplayStore(), now=1700000000)
    assert verify_device_request(**common, signature=signature) is True
    assert verify_device_request(**common, signature=signature + "=") is False
    assert verify_device_request(**common, signature=signature[:-1] + "!") is False


def test_canonical_request_target_includes_raw_query_string():
    assert canonical_request_target("/api/v1/device/telemetry", "source=vehicle&v=1") == (
        "/api/v1/device/telemetry?source=vehicle&v=1"
    )
    assert canonical_request_target("/api/v1/device/telemetry") == "/api/v1/device/telemetry"
