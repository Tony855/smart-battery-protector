import pytest

from app.audit import write_audit_event


class Cursor:
    def __init__(self):
        self.statement = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, statement, params):
        self.statement, self.params = statement, params


class Connection:
    def __init__(self):
        self.cursor_instance = Cursor()
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_audit_event_uses_bound_parameters_and_commits():
    conn = Connection()
    write_audit_event(
        lambda: conn, actor_type="device", actor_id="dev-1",
        action="device.auth", target_type="device", target_id="dev-1",
        result="accepted",
    )
    assert conn.committed and conn.closed
    assert "%s" in conn.cursor_instance.statement
    assert conn.cursor_instance.params == (
        "device", "dev-1", "device.auth", "device", "dev-1", "accepted"
    )


def test_invalid_audit_classification_is_rejected_before_db_access():
    with pytest.raises(ValueError):
        write_audit_event(
            lambda: None, actor_type="unknown", actor_id="x",
            action="x", target_type="device", target_id="x", result="accepted",
        )
