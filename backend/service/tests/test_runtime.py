import pytest

import app.runtime as runtime


def test_remote_postgres_dsn_requires_verify_full(monkeypatch):
    monkeypatch.setenv("SBP_DATABASE_URL", "postgresql://user:pass@db.example.test/sbp")
    called = []
    monkeypatch.setattr(runtime.psycopg, "connect", lambda *args, **kwargs: called.append((args, kwargs)))
    with pytest.raises(RuntimeError, match="remote_database_requires_sslmode_verify_full"):
        runtime.database_connection()
    assert called == []


def test_remote_postgres_dsn_accepts_verify_full(monkeypatch):
    monkeypatch.setenv(
        "SBP_DATABASE_URL",
        "postgresql://user:pass@db.example.test/sbp?sslmode=verify-full",
    )
    sentinel = object()
    monkeypatch.setattr(runtime.psycopg, "connect", lambda *args, **kwargs: sentinel)
    assert runtime.database_connection() is sentinel


def test_loopback_postgres_dsn_keeps_local_development_compatibility(monkeypatch):
    monkeypatch.setenv("SBP_DATABASE_URL", "postgresql://user:pass@localhost/sbp")
    sentinel = object()
    monkeypatch.setattr(runtime.psycopg, "connect", lambda *args, **kwargs: sentinel)
    assert runtime.database_connection() is sentinel


def test_separate_remote_postgres_settings_default_to_verify_full(monkeypatch):
    monkeypatch.delenv("SBP_DATABASE_URL", raising=False)
    monkeypatch.setenv("SBP_DB_HOST", "db.example.test")
    monkeypatch.setenv("SBP_DB_USER", "sbp")
    monkeypatch.setenv("SBP_DB_PASSWORD", "test-only")
    monkeypatch.setenv("SBP_DB_NAME", "sbp")
    calls = []
    monkeypatch.setattr(runtime.psycopg, "connect", lambda *args, **kwargs: calls.append(kwargs) or object())
    runtime.database_connection()
    assert calls[0]["sslmode"] == "verify-full"


def test_separate_remote_postgres_rejects_weaker_sslmode(monkeypatch):
    monkeypatch.delenv("SBP_DATABASE_URL", raising=False)
    monkeypatch.setenv("SBP_DB_HOST", "db.example.test")
    monkeypatch.setenv("SBP_DB_USER", "sbp")
    monkeypatch.setenv("SBP_DB_PASSWORD", "test-only")
    monkeypatch.setenv("SBP_DB_NAME", "sbp")
    monkeypatch.setenv("SBP_DB_SSLMODE", "prefer")
    with pytest.raises(RuntimeError, match="remote_database_requires_sslmode_verify_full"):
        runtime.database_connection()


def test_remote_redis_requires_rediss(monkeypatch):
    runtime.redis_client.cache_clear()
    monkeypatch.setenv("SBP_REDIS_URL", "redis://cache.example.test:6379/0")
    with pytest.raises(RuntimeError, match="remote_redis_requires_rediss"):
        runtime.redis_client()
    runtime.redis_client.cache_clear()


def test_remote_rediss_enables_certificate_and_hostname_verification(monkeypatch):
    runtime.redis_client.cache_clear()
    monkeypatch.setenv("SBP_REDIS_URL", "rediss://cache.example.test:6380/0")
    calls = []

    def fake_from_url(cls, url, **kwargs):
        calls.append((url, kwargs))
        return "redis-client"

    monkeypatch.setattr(runtime.redis.Redis, "from_url", classmethod(fake_from_url))
    try:
        assert runtime.redis_client() == "redis-client"
        assert calls[0][1]["ssl_cert_reqs"] == "required"
        assert calls[0][1]["ssl_check_hostname"] is True
    finally:
        runtime.redis_client.cache_clear()


def test_loopback_redis_url_remains_available_for_local_development(monkeypatch):
    runtime.redis_client.cache_clear()
    monkeypatch.setenv("SBP_REDIS_URL", "redis://localhost:6379/0")
    calls = []

    def fake_from_url(cls, url, **kwargs):
        calls.append((url, kwargs))
        return "local-redis"

    monkeypatch.setattr(runtime.redis.Redis, "from_url", classmethod(fake_from_url))
    try:
        assert runtime.redis_client() == "local-redis"
        assert "ssl_cert_reqs" not in calls[0][1]
    finally:
        runtime.redis_client.cache_clear()
