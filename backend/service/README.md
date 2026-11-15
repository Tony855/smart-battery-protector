# SBP API service scaffold

## Local run
```bash
cd backend/service
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
uvicorn app.main:app --reload
pytest
```

- Liveness: `GET /health/live`
- Readiness: `GET /health/ready` (intentionally returns 503 until real dependencies are configured)
- OpenAPI UI: `/docs`

## Safety and security boundary
No device command route is implemented. Do not expose this scaffold as a production API. Before enabling device/user routes, implement JWT issuer/audience/signature validation, authorization on every device binding, rate limits, audit logging, database transactions, MQTT ACL integration, secrets management and integration tests. Device-local interlocks remain authoritative.

## User authentication and device ownership

Configure a trusted OIDC provider before using account endpoints:

- `SBP_JWT_JWKS_URL`
- `SBP_JWT_ISSUER`
- `SBP_JWT_AUDIENCE`

The API verifies RS256/ES256 access tokens against the provider's JWKS. Do not use self-issued client tokens. Account routes:

- `GET /api/v1/me/devices`
- `POST /api/v1/me/devices/bind`

Apply migrations 001 through 004 in order. The one-time claim-code digest must be provisioned by a trusted manufacturing/provisioning process. The raw claim code must never be logged or stored. These routes do not enable remote power control.

## Device claim-code provisioning

From the service directory, run the trusted provisioning station command with database credentials supplied via environment variables:

```sh
python scripts/provision_claim_code.py --serial SBP-000001 --ttl-hours 24
```

The command invalidates previous unused claim codes for that device, stores only the SHA-256 digest, and prints the new high-entropy code once. Deliver it to the device owner over a protected channel. Never capture terminal output in CI logs, shell transcripts, support tickets or application logs.

## Telemetry

- Device-signed `POST /api/v1/device/telemetry`
- Owner-scoped `GET /api/v1/me/devices/{serial_number}/telemetry?limit=100`
- Migrations 001 through 005 must be applied in order.
- Measurements use integer base units: millivolts, milliamps and centi-degrees Celsius.
- Telemetry is observational only; it cannot trigger relay/contactor switching.
