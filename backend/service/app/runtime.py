"""Runtime factories for PostgreSQL and Redis with remote transport security."""
from __future__ import annotations

import os
from functools import lru_cache
from urllib.parse import urlsplit

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
import redis

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _host_is_remote(value: str | None) -> bool:
    if not value:
        return False
    for item in value.split(","):
        host = item.strip().strip("[]").lower()
        if not host or host in _LOCAL_HOSTS or host.startswith("/"):
            continue
        return True
    return False


def _dsn_is_remote(params: dict[str, str]) -> bool:
    return (
        _host_is_remote(params.get("host"))
        or _host_is_remote(params.get("hostaddr"))
        or bool(params.get("service"))
    )


def database_connection():
    """Open PostgreSQL; remote hosts must use certificate- and hostname-verified TLS."""
    dsn = os.getenv("SBP_DATABASE_URL")
    if dsn:
        params = conninfo_to_dict(dsn)
        if _dsn_is_remote(params) and params.get("sslmode", "prefer").lower() != "verify-full":
            raise RuntimeError("remote_database_requires_sslmode_verify_full")
        return psycopg.connect(dsn, connect_timeout=3, row_factory=dict_row)

    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    if any(not os.getenv(key) for key in required):
        raise RuntimeError("database_configuration_missing")
    host = os.environ["SBP_DB_HOST"]
    remote = _host_is_remote(host)
    sslmode = os.getenv("SBP_DB_SSLMODE", "verify-full" if remote else "prefer").lower()
    if remote and sslmode != "verify-full":
        raise RuntimeError("remote_database_requires_sslmode_verify_full")
    return psycopg.connect(
        host=host,
        port=int(os.getenv("SBP_DB_PORT", "5432")),
        dbname=os.environ["SBP_DB_NAME"],
        user=os.environ["SBP_DB_USER"],
        password=os.environ["SBP_DB_PASSWORD"],
        connect_timeout=3,
        sslmode=sslmode,
        row_factory=dict_row,
    )


@lru_cache(maxsize=1)
def redis_client():
    url = os.getenv("SBP_REDIS_URL")
    if not url:
        raise RuntimeError("redis_configuration_missing")
    parsed = urlsplit(url)
    if parsed.scheme == "unix":
        if not parsed.path.startswith("/"):
            raise RuntimeError("redis_unix_socket_path_must_be_absolute")
        tls_options = {}
    elif parsed.scheme in {"redis", "rediss"} and parsed.hostname:
        remote = parsed.hostname.lower() not in _LOCAL_HOSTS
        if remote and parsed.scheme != "rediss":
            raise RuntimeError("remote_redis_requires_rediss")
        tls_options = (
            {"ssl_cert_reqs": "required", "ssl_check_hostname": True}
            if parsed.scheme == "rediss" else {}
        )
    else:
        raise RuntimeError("unsupported_redis_url")
    return redis.Redis.from_url(
        url,
        socket_connect_timeout=3,
        socket_timeout=3,
        health_check_interval=30,
        decode_responses=True,
        **tls_options,
    )
