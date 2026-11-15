# Implementation Batch 05

## Delivered
- Python 3.12 / FastAPI service scaffold.
- Liveness endpoint and fail-closed readiness endpoint.
- Automated API bootstrap tests.
- Container image definition with non-root runtime user.
- GitHub Actions workflow for backend tests.

## Explicitly not enabled
- No login or token validation.
- No device ownership/tenant authorization.
- No database or MQTT connectivity.
- No remote power-control endpoint.
- No production deployment claim.

Readiness returns HTTP 503 by design until dependency checks are implemented. This avoids advertising an unconfigured service as ready.
