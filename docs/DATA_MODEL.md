# Initial Data Model v0.1

Logical model only; database DDL and migration scripts are not yet implemented.

## Entities
- users: id, login_identity, status, created_at
- devices: id, serial_number, model_id, hw_revision, fw_version, lifecycle_status
- device_bindings: user_id, device_id, role, bound_at, revoked_at
- product_models: model_id, product_family, voltage_capability, connectivity_capability, config_schema_version
- device_configurations: device_id, revision, profile_id, payload, updated_at
- telemetry_samples: device_id, measured_at, voltage_mv, current_ma, temperature_dc, state
- device_events: device_id, event_id, event_type, fault_code, occurred_at, details
- firmware_releases: release_id, model_id, version, artifact_digest, signature_metadata, rollout_state
- audit_events: actor_id, action, target_id, occurred_at, result

## Constraints
- Serial number unique.
- Binding ownership and role changes are auditable.
- Configuration has revision and schema version.
- Commands carry request ID, expiry and authorization context.
- Firmware artifacts are immutable and signature-verified.
- Telemetry retention and access policy must be defined before production deployment.
