"""PostgreSQL connectivity probe using the same TLS policy as application queries."""
from __future__ import annotations

import psycopg

from app.runtime import database_connection


def ping_database() -> bool:
    try:
        connection = database_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS alive")
                row = cursor.fetchone()
                return bool(row and row["alive"] == 1)
    except (psycopg.Error, RuntimeError, ValueError):
        return False
