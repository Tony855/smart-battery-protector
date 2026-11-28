# Implementation Batch 42 — Enforce Active User Status for Device Access

Date: 2026-11-26

## Finding
The users table defines active, locked and deleted account states. The device list, device data authorization and device member-management role lookup previously checked membership and role but did not consistently filter the requesting user's account status. A locked or deleted account with an otherwise active binding could retain read or management access through these paths.

## Remediation
- Filter account device-list queries to active users.
- Filter device status/event authorization to active users.
- Filter device member-management authorization to active users.
- Preserve the existing 404 response for missing membership so account state is not exposed through these authorization paths.

## Regression coverage
Host unit tests assert the active-status predicate in each authorization query and the denial path when the authorization lookup returns no active row. These are SQL/query-shape tests, not a live PostgreSQL integration or deployment test.

## Verification boundary
Run Backend CI on the current branch head. No production database, credentials, or migration was touched.
