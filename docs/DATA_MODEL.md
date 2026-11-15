# Data Model v0.2

The backend runtime database is PostgreSQL 15+. Canonical DDL is maintained in backend/db/postgresql/migrations/ and the schema snapshot in backend/db/schema.sql.

## Entities
- users: identity subject, status, created_at
- devices: serial number, model, hardware/firmware revisions, lifecycle and last_seen_at
- device_bindings: user/device membership, role, bound_at, revoked_at
- product_models: family, connectivity and 12V/24V capabilities
- device_configurations: versioned JSONB configuration payload
- device_telemetry: timestamped electrical and temperature measurements
- device_events: timestamped events and JSONB diagnostic details
- firmware_releases: immutable artifact digest, signature reference and rollout state
- audit_events: actor, action, target, result and JSONB metadata

## Telemetry wire/database units
- battery_voltage_v: decimal volts (V), stored as NUMERIC(6,3).
- battery_current_a: signed decimal amperes (A), stored as NUMERIC(9,3).
- temperature_deci_c: integer units of 0.1°C; 253 represents 25.3°C, stored as SMALLINT.
- Existing legacy telemetry conversion, if any, must divide old mV by 1000, old mA by 1000, and old centi-degrees Celsius by 10 before inserting into the new columns.

## Constraints
- Serial number and per-device event/sample identifiers are unique.
- Membership roles are constrained to owner/admin/viewer.
- Configuration has revision and schema version.
- Commands carry request ID, expiry and authorization context.
- Firmware artifacts are immutable and signature-verified.
- Telemetry retention and access policy must be defined before production deployment.
