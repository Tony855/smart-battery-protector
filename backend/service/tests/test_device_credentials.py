import base64

from app.device_credentials import load_active_device_key


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


def test_active_device_public_key_is_decoded_and_connection_closed():
    raw = bytes(range(32))
    conn = Connection({"public_key_base64": base64.b64encode(raw).decode()})
    assert load_active_device_key(lambda: conn, "key-1") == raw
    assert conn.closed
    assert conn.cursor_instance.params == ("key-1",)
    assert "d.lifecycle_status = 'active'" in conn.cursor_instance.sql


def test_missing_or_invalid_key_fails_closed():
    missing = Connection(None)
    malformed = Connection({"public_key_base64": "not-base64"})
    wrong_length = Connection({"public_key_base64": base64.b64encode(b"short").decode()})
    assert load_active_device_key(lambda: missing, "missing") is None
    assert load_active_device_key(lambda: malformed, "bad") is None
    assert load_active_device_key(lambda: wrong_length, "short") is None
    assert missing.closed and malformed.closed and wrong_length.closed
