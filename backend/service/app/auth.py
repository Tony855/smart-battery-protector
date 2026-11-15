"""Verify user access tokens using a configured OIDC JWKS endpoint."""
from __future__ import annotations

import os
from functools import lru_cache

import jwt
from jwt import PyJWKClient


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    url = os.getenv("SBP_JWT_JWKS_URL")
    if not url:
        raise RuntimeError("jwt_jwks_configuration_missing")
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300, timeout=3)


def verify_user_token(token: str) -> str | None:
    issuer = os.getenv("SBP_JWT_ISSUER")
    audience = os.getenv("SBP_JWT_AUDIENCE")
    if not issuer or not audience or not token:
        return None
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            issuer=issuer,
            audience=audience,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            leeway=30,
        )
        subject = claims.get("sub")
        return subject if isinstance(subject, str) and 1 <= len(subject) <= 191 else None
    except (jwt.PyJWTError, Exception) as exc:
        # Do not leak token validation or upstream JWKS details.
        return None


def require_user_subject(authorization: str | None) -> str:
    from fastapi import HTTPException

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="user_authentication_required")
    subject = verify_user_token(authorization[7:].strip())
    if subject is None:
        raise HTTPException(status_code=401, detail="invalid_user_token")
    return subject
