"""PostgreSQL connectivity probe. Credentials are supplied only through environment variables."""
from __future__ import annotations

import os

import psycopg


def _dsn() -> str | None:
    dsn = os.getenv("SBP_DATABASE_URL")
    if dsn:
        return dsn
    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    if any(not os.getenv(key) for key in required):
        return None
    return (
        f"host={os.environ['SBP_DB_HOST']} "
        f"port={os.getenv('SBP_DB_PORT', '5432')} "
        f"dbname={os.environ['SBP_DB_NAME']} "
        f"user={os.environ['SBP_DB_USER']} "
        f"password={os.environ['SBP_DB_PASSWORD']} connect_timeout=3"
    )


def ping_database() -> bool:
    dsn = _dsn()
    if not dsn:
        return False
    try:
        with psycopg.connect(dsn, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS alive")
                row = cursor.fetchone()
                return bool(row and row[0] == 1)
    except (psycopg.Error, ValueError):
        return False
