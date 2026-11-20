"""Explicit PostgreSQL schema migration runner; never runs during API startup."""
from __future__ import annotations

import hashlib
from pathlib import Path

from app.runtime import database_connection


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


def _connect_database():
    """Use the same remote TLS verification policy as all application DB access."""
    try:
        return database_connection()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc


def main() -> int:
    connection = _connect_database()
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
