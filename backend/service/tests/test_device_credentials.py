import base64

from app.device_credentials import load_active_device_credential


class Cursor:
    def __init__(self, row):
        self.row = row
        self.sql = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params):
        self.sql, self.params = sql, params

    def fetchone(self):
        return self.row


class Connection:
    def __init__(self, row):
        self.cursor_instance = Cursor(row)
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def close(self):
        self.closed = True


def test_active_device_public_key_and_identity_are_returned():
    raw = bytes(range(32))
    conn = Connection({"device_id": 42, "public_key_base64": base64.b64encode(raw).decode()})
    credential = load_active_device_credential(lambda: conn, "key-1")
    assert credential.device_id == 42
    assert credential.public_key_raw == raw
    assert conn.closed
    assert conn.cursor_instance.params == ("key-1",)
    assert "d.lifecycle_status = 'active'" in conn.cursor_instance.sql
    assert "dc.public_key_algorithm = 'ed25519'" in conn.cursor_instance.sql
    assert "dc.signature_algorithm = 'ed25519'" in conn.cursor_instance.sql


def test_missing_or_invalid_key_fails_closed():
    missing = Connection(None)
    malformed = Connection({"device_id": 7, "public_key_base64": "not-base64"})
    wrong_length = Connection({"device_id": 7, "public_key_base64": base64.b64encode(b"short").decode()})
    invalid_id = Connection({"device_id": 0, "public_key_base64": base64.b64encode(bytes(32)).decode()})
    assert load_active_device_credential(lambda: missing, "missing") is None
    assert load_active_device_credential(lambda: malformed, "bad") is None
    assert load_active_device_credential(lambda: wrong_length, "short") is None
    assert load_active_device_credential(lambda: invalid_id, "zero") is None
    assert missing.closed and malformed.closed and wrong_length.closed and invalid_id.closed
