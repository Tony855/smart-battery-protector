"""PostgreSQL connectivity probe. Credentials are supplied only through environment variables."""
from __future__ import annotations

import os

import psycopg


def ping_database() -> bool:
    dsn = os.getenv("SBP_DATABASE_URL")
    if not dsn:
        required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
        if any(not os.getenv(key) for key in required):
            return False
    try:
        if dsn:
            connection = psycopg.connect(dsn, connect_timeout=3)
        else:
            connection = psycopg.connect(
                host=os.environ["SBP_DB_HOST"],
                port=int(os.getenv("SBP_DB_PORT", "5432")),
                dbname=os.environ["SBP_DB_NAME"],
                user=os.environ["SBP_DB_USER"],
                password=os.environ["SBP_DB_PASSWORD"],
                connect_timeout=3,
            )
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS alive")
                row = cursor.fetchone()
                return bool(row and row[0] == 1)
    except (psycopg.Error, ValueError):
        return False
