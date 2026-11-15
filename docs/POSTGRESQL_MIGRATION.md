# MariaDB to PostgreSQL transition

## New target
The backend runtime database is PostgreSQL 15 or newer. New deployments must use the PostgreSQL migration set in backend/db/postgresql/migrations/. The former MariaDB migration set is retired and must never be executed against PostgreSQL.

## Fresh installation
1. Provision PostgreSQL 15+ and a dedicated database/user. Use a strong password and TLS for remote connections.
2. Configure SBP_DATABASE_URL, for example postgresql://sbp_user:REDACTED@db-host:5432/sbp?sslmode=verify-full.
3. Install the API package: pip install -e 'backend/service'.
4. Run the explicit migration command from backend/service: python -m app.migrate.
5. Verify schema_migrations contains migrations 001 through 006 and verify GET /health/ready.
6. Deploy the API only after PostgreSQL and Redis are reachable. API startup does not mutate the schema.

For local development, set SBP_POSTGRES_DB, SBP_POSTGRES_USER and SBP_POSTGRES_PASSWORD, then run docker compose -f backend/docker-compose.yml up -d. The compose ports bind to loopback only.

## Existing MariaDB data
The repository scaffold has no confirmed production database endpoint or production data snapshot. Do not assume that changing the driver migrates existing rows. Before moving a populated MariaDB database:
- Take and verify a restorable MariaDB backup.
- Freeze writes or use a controlled dual-write/CDC cutover plan.
- Export parent tables before child tables and preserve primary/foreign-key IDs.
- Convert telemetry values during export/import:
  - battery_voltage_v = battery_voltage_mv / 1000.0
  - battery_current_a = battery_current_ma / 1000.0
  - temperature_deci_c = ROUND(temperature_centi_c / 10.0)
- The old centi-degree integer is converted to tenths of a degree by dividing by 10; e.g. 2534 becomes 253.
- Import JSON fields as JSONB, timestamps as TIMESTAMPTZ, and UUID fields as PostgreSQL UUID.
- Reset identity sequences to at least the maximum imported ID for every identity-backed table.
- Reconcile row counts, foreign keys, duplicate sample/event IDs, nullability and telemetry ranges before cutover.
- Keep the source backup read-only until application-level and business-level reconciliation is signed off.

Do not point the PostgreSQL service at the MariaDB data directory. PostgreSQL and MariaDB data files are not interchangeable. Do not use a blind pgloader run for telemetry without applying the unit conversions above.

## Telemetry contract after cutover
- JSON/API field battery_voltage_v is in volts (V), decimal.
- JSON/API field battery_current_a is in amperes (A), decimal.
- JSON/API field temperature_deci_c is an integer count of 0.1°C. A value of 253 means 25.3°C.
- PostgreSQL columns are NUMERIC(6,3), NUMERIC(9,3), and SMALLINT respectively.
