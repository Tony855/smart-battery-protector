# Security Threat Model v0.1

## Assets
Device identity and keys; protection configuration; control authorization; signed firmware; telemetry and user/device binding records.

## Threats
- Unauthorized BLE pairing or control
- Replay of a previously valid command
- Device cloning or identity spoofing
- Malicious or downgraded firmware
- Compromised cloud account issuing unauthorized requests
- MQTT topic/tenant authorization failure
- Debug/test interface abuse during production
- Sensitive telemetry leakage

## Required mitigations
- Unique per-device identity and provisioned credentials; no fleet-wide shared secret.
- Authenticated pairing/binding and explicit ownership transfer.
- Nonce/counter, expiry and request ID for command replay resistance.
- Signed firmware, anti-rollback policy and secure boot where supported.
- TLS for cloud transport; per-device broker ACL and credential rotation/revocation.
- Least-privilege user roles and auditable administrative actions.
- Disable or authenticate production debug interfaces; secure manufacturing key injection.
- Minimize telemetry and define retention/access policies.

## Verification
Perform BLE security tests, API authorization tests, MQTT ACL tests, OTA signature/downgrade tests, credential revocation tests and manufacturing provisioning audit. This draft is not a completed security assessment.
