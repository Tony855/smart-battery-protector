# Implementation Batch 20 — Python cryptographic dependency remediation

Date: 2026-11-21

## Finding

The latest backend CI dependency audit at PR head `f57325f942d609b46afe845de6ed06fd8638b47a` failed before unit tests ran. The job log identified 13 vulnerability advisories affecting the resolved `cryptography 45.0.7` package. The audit listed remediation versions including 46.0.5, 46.0.6, 46.0.7, 48.0.1, 49.0.0 and 50.0.0, depending on the advisory.

## Remediation

- Raised the direct dependency constraint from `cryptography>=42,<46` to `cryptography>=50,<51`, avoiding the affected 45.x resolution while retaining a bounded major-version range.
- Kept `pip-audit --strict` as a required CI step; the workflow must not suppress or allow-list these findings.
- No secret material or production configuration was changed.

## Verification

- Host safety gate and ESP-IDF firmware workflow were green at the previous PR head `f57325f942d609b46afe845de6ed06fd8638b47a`.
- Backend dependency audit was red on that previous head due to the resolved `cryptography 45.0.7` vulnerabilities.
- A new backend CI run is required on this remediation commit. Unit tests, PostgreSQL migration integration, OpenAPI validation and container build are not claimed passed until that run completes.

## Remaining release gates

No physical switching, HIL, vehicle testing, production OTA, Secure Boot, encryption enablement, eFuse provisioning, or certification was performed. Those remain explicit engineering release gates.
