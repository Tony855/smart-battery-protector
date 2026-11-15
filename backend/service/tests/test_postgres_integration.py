"""Live PostgreSQL migration/schema integration test (enabled in CI)."""
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from app.migrate import apply_migrations


@pytest.mark.skipif(not os.getenv("SBP_TEST_DATABASE_URL"), reason="PostgreSQL integration DSN not configured")
def test_all_postgresql_migrations_apply_and_telemetry_units_are_correct():
    dsn = os.environ["SBP_TEST_DATABASE_URL"]
    schema = "sbp_test_" + uuid4().hex
    migrations = Path(__file__).resolve().parents[2] / "db" / "postgresql" / "migrations"
    with psycopg.connect(dsn) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        connection.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
        try:
            applied = apply_migrations(connection, migrations)
            assert applied == [
                "001_initial_schema.sql",
                "002_device_credentials.sql",
                "003_device_ed25519_public_keys.sql",
                "004_device_claim_codes.sql",
                "005_device_telemetry.sql",
                "006_device_presence.sql",
            ]
            rows = connection.execute(
                """
                SELECT column_name, data_type, numeric_precision, numeric_scale
                  FROM information_schema.columns
                 WHERE table_schema=%s AND table_name='device_telemetry'
                """,
                (schema,),
            ).fetchall()
            columns = {row[0]: row[1:] for row in rows}
            assert columns["battery_voltage_v"] == ("numeric", 6, 3)
            assert columns["battery_current_a"] == ("numeric", 9, 3)
            assert columns["temperature_deci_c"][0] == "smallint"
            assert "last_seen_at" in {
                row[0] for row in connection.execute(
                    "SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name='devices'",
                    (schema,),
                ).fetchall()
            }
            connection.execute(
                "INSERT INTO product_models (model_id, family, connectivity, voltage_capability) "
                "VALUES ('ci-model', 'aux', ARRAY['ble']::varchar(16)[], ARRAY['12v']::varchar(8)[])"
            )
            device_id = connection.execute(
                "INSERT INTO devices (serial_number, model_id) VALUES ('CI-SBP-1', 'ci-model') RETURNING id"
            ).fetchone()[0]
            sample_id = uuid4()
            connection.execute(
                """
                INSERT INTO device_telemetry
                  (device_id, sample_uuid, observed_at, battery_voltage_v,
                   battery_current_a, temperature_deci_c, state_code, engine_running)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (device_id, sample_id, datetime.now(timezone.utc),
                 Decimal("12.800"), Decimal("-1.200"), 253, "normal", "no"),
            )
            stored = connection.execute(
                "SELECT sample_uuid, battery_voltage_v, battery_current_a, temperature_deci_c "
                "FROM device_telemetry WHERE device_id=%s AND sample_uuid=%s",
                (device_id, sample_id),
            ).fetchone()
            assert stored == (sample_id, Decimal("12.800"), Decimal("-1.200"), 253)
        finally:
            connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
