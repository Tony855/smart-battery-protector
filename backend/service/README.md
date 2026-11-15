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
