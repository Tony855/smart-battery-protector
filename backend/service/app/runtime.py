"""Runtime factories for PostgreSQL and Redis; no network connection at import time."""
from __future__ import annotations

import os
from functools import lru_cache

import psycopg
from psycopg.rows import dict_row
import redis


def database_connection():
    """Open PostgreSQL; configure remote TLS through sslmode in SBP_DATABASE_URL."""
    dsn = os.getenv("SBP_DATABASE_URL")
    if dsn:
        return psycopg.connect(dsn, connect_timeout=3, row_factory=dict_row)
    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    if any(not os.getenv(key) for key in required):
        raise RuntimeError("database_configuration_missing")
    return psycopg.connect(
        host=os.environ["SBP_DB_HOST"],
        port=int(os.getenv("SBP_DB_PORT", "5432")),
        dbname=os.environ["SBP_DB_NAME"],
        user=os.environ["SBP_DB_USER"],
        password=os.environ["SBP_DB_PASSWORD"],
        connect_timeout=3,
        row_factory=dict_row,
    )


@lru_cache(maxsize=1)
def redis_client():
    url = os.getenv("SBP_REDIS_URL")
    if not url:
        raise RuntimeError("redis_configuration_missing")
    return redis.Redis.from_url(
        url, socket_connect_timeout=3, socket_timeout=3,
        health_check_interval=30, decode_responses=True,
    )
