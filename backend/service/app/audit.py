"""Minimal security audit writer. Never pass credentials, signatures or raw payloads."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


def insert_audit_event(
    cursor: Any,
    *,
    actor_type: str,
    actor_id: str,
    action: str,
    target_type: str,
    target_id: str,
    result: str,
) -> None:
    """Insert an audit row using the caller's cursor and transaction."""
    allowed_actor = {"user", "device", "admin", "system"}
    allowed_result = {"accepted", "rejected", "failed"}
    if actor_type not in allowed_actor or result not in allowed_result:
        raise ValueError("invalid audit classification")
    cursor.execute(
        """
        INSERT INTO audit_events
          (actor_type, actor_id, action, target_type, target_id, result)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (actor_type, actor_id[:128], action[:96], target_type[:48],
         target_id[:128], result),
    )


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
    """Write a standalone audit event when no business transaction is active."""
    connection = connection_factory()
    try:
        with connection.cursor() as cursor:
            insert_audit_event(
                cursor, actor_type=actor_type, actor_id=actor_id, action=action,
                target_type=target_type, target_id=target_id, result=result,
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
