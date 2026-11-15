"""Explicit PostgreSQL schema migration runner; never runs during API startup."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


def split_sql_statements(source: str) -> list[str]:
    """Split project migration files on semicolons.

    Stored procedures, delimiter directives, and semicolons inside quoted strings
    are intentionally unsupported. Keep migration files within this subset.
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
        cursor.execute("SELECT pg_advisory_xact_lock(hashtext('smart_battery_protector_schema'))")
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(128) PRIMARY KEY,
                checksum CHAR(64) NOT NULL,
                applied_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        for path in migration_files(directory):
            version = path.name
            source = path.read_text(encoding="utf-8")
            digest = checksum(source)
            cursor.execute("SELECT checksum FROM schema_migrations WHERE version = %s", (version,))
            row = cursor.fetchone()
            if row:
                recorded = row["checksum"] if isinstance(row, dict) else row[0]
                if recorded.strip() != digest:
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


def _database_dsn() -> str:
    dsn = os.getenv("SBP_DATABASE_URL")
    if dsn:
        return dsn
    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise SystemExit("Missing PostgreSQL settings: " + ", ".join(missing))
    return (
        f"host={os.environ['SBP_DB_HOST']} "
        f"port={os.getenv('SBP_DB_PORT', '5432')} "
        f"dbname={os.environ['SBP_DB_NAME']} "
        f"user={os.environ['SBP_DB_USER']} "
        f"password={os.environ['SBP_DB_PASSWORD']} connect_timeout=5"
    )


def main() -> int:
    connection = psycopg.connect(_database_dsn(), connect_timeout=5, row_factory=dict_row)
    directory = Path(os.getenv(
        "SBP_MIGRATIONS_DIR",
        str(Path(__file__).resolve().parents[2] / "db" / "postgresql" / "migrations"),
    ))
    try:
        applied = apply_migrations(connection, directory)
        print("Applied: " + (", ".join(applied) if applied else "no pending migrations"))
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
