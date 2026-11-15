"""MariaDB connectivity probe. Credentials are supplied only through environment variables."""
import os
import pymysql

def ping_database() -> bool:
    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    if any(not os.getenv(key) for key in required):
        return False
    connection = None
    try:
        connection = pymysql.connect(
            host=os.environ["SBP_DB_HOST"],
            port=int(os.getenv("SBP_DB_PORT", "3306")),
            user=os.environ["SBP_DB_USER"],
            password=os.environ["SBP_DB_PASSWORD"],
            database=os.environ["SBP_DB_NAME"],
            connect_timeout=3,
            read_timeout=3,
            write_timeout=3,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS alive")
            row = cursor.fetchone()
            return bool(row and row.get("alive") == 1)
    except (pymysql.MySQLError, ValueError):
        return False
    finally:
        if connection is not None:
            connection.close()
