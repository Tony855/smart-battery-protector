# Implementation Batch 03

## Delivered in this batch
- Initial logical schema for users, product models, devices, bindings, versioned configurations, events, firmware releases and audit events. The original MariaDB-specific draft has since been retired and replaced by PostgreSQL 15+ migrations.
- OpenAPI 3.1 draft for device listing/details/events, control requests and firmware metadata.
- Host-buildable C safety-gate helper and unit tests for engine-running/unknown-state, invalid sensors, overtemperature, overcurrent and latched faults.
- GitHub Actions workflow to build and run host safety-gate tests on relevant changes.

## Important limitations
- Host tests validate only a small pure decision helper. They do not prove functional safety or vehicle suitability.
- No GPIO, relay, contactor, MOSFET or power-stage actuation is implemented.
- The current supported database is PostgreSQL 15+; canonical DDL and migrations are in backend/db/postgresql/.
- OpenAPI server hostname is intentionally non-routable placeholder and must be configured per deployment.
- CI must run in GitHub before any passing status can be claimed.
