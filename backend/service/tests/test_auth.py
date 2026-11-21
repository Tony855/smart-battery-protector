import jwt
import pytest

import app.auth as auth
from app.auth import verify_user_token


def test_user_token_requires_issuer_audience_and_subject(monkeypatch):
    monkeypatch.setenv("SBP_JWT_ISSUER", "https://identity.example.test/")
    monkeypatch.setenv("SBP_JWT_AUDIENCE", "sbp-api")
    monkeypatch.setenv("SBP_JWT_JWKS_URL", "https://identity.example.test/.well-known/jwks.json")

    class SigningKey:
        key = object()

    class Client:
        def get_signing_key_from_jwt(self, token):
            assert token == "signed-token"
            return SigningKey()

    monkeypatch.setattr("app.auth._jwks_client", lambda: Client())
    monkeypatch.setattr(
        jwt, "decode",
        lambda *args, **kwargs: {
            "sub": "user-123", "iss": "https://identity.example.test/",
            "aud": "sbp-api", "iat": 1700000000, "exp": 1800000000,
        },
    )
    assert verify_user_token("signed-token") == "user-123"


def test_user_token_fails_closed_without_configuration(monkeypatch):
    monkeypatch.delenv("SBP_JWT_ISSUER", raising=False)
    monkeypatch.delenv("SBP_JWT_AUDIENCE", raising=False)
    assert verify_user_token("token") is None


def test_remote_jwks_requires_https(monkeypatch):
    monkeypatch.setenv("SBP_JWT_JWKS_URL", "http://identity.example.test/jwks")
    auth._jwks_client.cache_clear()
    with pytest.raises(RuntimeError, match="remote_jwks_requires_https"):
        auth._jwks_client()
    auth._jwks_client.cache_clear()


def test_loopback_http_jwks_is_allowed_for_local_development(monkeypatch):
    class FakeJwksClient:
        def __init__(self, url, **kwargs):
            self.url = url
            self.kwargs = kwargs

    monkeypatch.setattr(auth, "PyJWKClient", FakeJwksClient)
    monkeypatch.setenv("SBP_JWT_JWKS_URL", "http://127.0.0.1:8080/jwks")
    auth._jwks_client.cache_clear()
    try:
        client = auth._jwks_client()
        assert client.url == "http://127.0.0.1:8080/jwks"
        assert client.kwargs["timeout"] == 3
    finally:
        auth._jwks_client.cache_clear()
