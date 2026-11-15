"""Minimal security audit writer. Never pass credentials, signatures or raw payloads."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


def write_audit_event(
    connection_factory: Callable[[], Any],
    *,
    actor_type: str,
    actor_id: str,
    action: str,
    target_type: str,
    target_id: str,
    result: str,
) -> None:
    allowed_actor = {"user", "device", "admin", "system"}
    allowed_result = {"accepted", "rejected", "failed"}
    if actor_type not in allowed_actor or result not in allowed_result:
        raise ValueError("invalid audit classification")
    connection = connection_factory()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO audit_events
                  (actor_type, actor_id, action, target_type, target_id, result)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (actor_type, actor_id[:128], action[:96], target_type[:48],
                 target_id[:128], result),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
