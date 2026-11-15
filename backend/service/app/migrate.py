"""Explicit MariaDB schema migration runner.

DDL in MariaDB may implicitly commit. Each migration must therefore be restart-safe
and use idempotent DDL where possible. Migrations are never run at API startup.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Iterable


def split_sql_statements(source: str) -> list[str]:
    """Split this project's simple SQL migrations on semicolons.

    Deliberately does not support stored procedures, delimiter directives, or
    semicolons inside quoted strings. Keep migration files within this subset.
    """
    cleaned = []
    for line in source.splitlines():
        if line.lstrip().startswith("--"):
            continue
        cleaned.append(line)
    return [part.strip() for part in "\n".join(cleaned).split(";") if part.strip()]


def checksum(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def migration_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("[0-9][0-9][0-9]_*.sql"))


def apply_migrations(connection, directory: Path) -> list[str]:
    applied_now: list[str] = []
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(128) NOT NULL PRIMARY KEY,
                checksum CHAR(64) NOT NULL,
                applied_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
            ) ENGINE=InnoDB"""
        )
        for path in migration_files(directory):
            version = path.name
            source = path.read_text(encoding="utf-8")
            digest = checksum(source)
            cursor.execute(
                "SELECT checksum FROM schema_migrations WHERE version = %s",
                (version,),
            )
            row = cursor.fetchone()
            if row:
                recorded = row[0] if not isinstance(row, dict) else row["checksum"]
                if recorded != digest:
                    raise RuntimeError(f"Applied migration was modified: {version}")
                continue
            for statement in split_sql_statements(source):
                cursor.execute(statement)
            cursor.execute(
                "INSERT INTO schema_migrations (version, checksum) VALUES (%s, %s)",
                (version, digest),
            )
            applied_now.append(version)
    connection.commit()
    return applied_now


def main() -> int:
    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise SystemExit("Missing database settings: " + ", ".join(missing))

    import pymysql

    connection = pymysql.connect(
        host=os.environ["SBP_DB_HOST"],
        port=int(os.getenv("SBP_DB_PORT", "3306")),
        user=os.environ["SBP_DB_USER"],
        password=os.environ["SBP_DB_PASSWORD"],
        database=os.environ["SBP_DB_NAME"],
        charset="utf8mb4",
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=False,
    )
    directory = Path(
        os.getenv(
            "SBP_MIGRATIONS_DIR",
            str(Path(__file__).resolve().parents[2] / "db" / "migrations"),
        )
    )
    try:
        applied = apply_migrations(connection, directory)
        print("Applied: " + (", ".join(applied) if applied else "no pending migrations"))
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
