import jwt

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
            "sub": "user-123",
            "iss": "https://identity.example.test/",
            "aud": "sbp-api",
            "iat": 1700000000,
            "exp": 1800000000,
        },
    )
    assert verify_user_token("signed-token") == "user-123"


def test_user_token_fails_closed_without_configuration(monkeypatch):
    monkeypatch.delenv("SBP_JWT_ISSUER", raising=False)
    monkeypatch.delenv("SBP_JWT_AUDIENCE", raising=False)
    assert verify_user_token("token") is None
