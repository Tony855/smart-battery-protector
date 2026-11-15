"""Runtime factories for PostgreSQL and Redis; no network connection at import time."""
from __future__ import annotations

import os
from functools import lru_cache

import psycopg
from psycopg.rows import dict_row
import redis


def database_connection():
    """Open a PostgreSQL connection; configure TLS with sslmode in SBP_DATABASE_URL."""
    dsn = os.getenv("SBP_DATABASE_URL")
    if not dsn:
        required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
        if any(not os.getenv(key) for key in required):
            raise RuntimeError("database_configuration_missing")
        dsn = (
            f"host={os.environ['SBP_DB_HOST']} "
            f"port={os.getenv('SBP_DB_PORT', '5432')} "
            f"dbname={os.environ['SBP_DB_NAME']} "
            f"user={os.environ['SBP_DB_USER']} "
            f"password={os.environ['SBP_DB_PASSWORD']} "
            f"connect_timeout=3"
        )
    return psycopg.connect(dsn, connect_timeout=3, row_factory=dict_row)


@lru_cache(maxsize=1)
def redis_client():
    url = os.getenv("SBP_REDIS_URL")
    if not url:
        raise RuntimeError("redis_configuration_missing")
    return redis.Redis.from_url(
        url, socket_connect_timeout=3, socket_timeout=3,
        health_check_interval=30, decode_responses=True,
    )
