# Implementation Batch 03

## Delivered in this batch
- Initial MariaDB schema for users, product models, devices, bindings, versioned configurations, events, firmware releases and audit events.
- OpenAPI 3.1 draft for device listing/details/events, control requests and firmware metadata.
- Host-buildable C safety-gate helper and unit tests for engine-running/unknown-state, invalid sensors, overtemperature, overcurrent and latched faults.
- GitHub Actions workflow to build and run host safety-gate tests on relevant changes.

## Important limitations
- Host tests validate only a small pure decision helper. They do not prove functional safety or vehicle suitability.
- No GPIO, relay, contactor, MOSFET or power-stage actuation is implemented.
- SQL is an initial logical schema, not a production migration package; authentication, tenant authorization, retention and operational hardening remain.
- OpenAPI server hostname is intentionally non-routable placeholder and must be configured per deployment.
- CI must run in GitHub before any passing status can be claimed.
