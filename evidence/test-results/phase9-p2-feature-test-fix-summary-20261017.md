# Phase 9 P2 Feature Test Harness Fix — Runtime Evidence

Date: 2026-10-17

## Scope

This gate records runtime evidence for the narrow telemetry feature-test harness
fix. Application runtime source was not changed.

Modified source:

- `backend/laravel/tests/Feature/TelemetryIngestTest.php`

## Root cause

The initial runtime suite executed 14 tests and produced four HTTP 401 failures
in raw-body tests. Those raw tests used Laravel's low-level `call(...)` path
while Authorization had been configured through `withHeader(...)`.

The test-only fix passes Authorization in the low-level call server array as
`HTTP_AUTHORIZATION`.

After that change, authentication succeeded. Three negative validation tests
then returned HTTP 302 because the same low-level raw calls did not explicitly
request JSON responses. The test-only fix therefore also passes
`HTTP_ACCEPT=application/json`.

No authentication middleware, authenticator, controller, validator, service,
migration, or LOCKED requirement was changed.

## Runtime verification

- Laravel runtime target: `vessel_monitoring_gateway_test` on `127.0.0.1:3307`
- Telemetry feature tests: **14/14 PASS**
- Assertions: **39**
- Application DB: `vessel_monitoring_gateway`
- Application telemetry/data rows after tests: **0**
- Dedicated test DB telemetry/data rows after tests: **0**
- Application schema remains 4 tables / 3 migration records
- Dedicated test schema remains 4 tables / 3 migration records

## Boundary

Phase 9 remains IN_PROGRESS.
Total system status remains PARTIAL.
Physical bench remains NOT_RUN.
Production readiness is NOT_CLAIMED.
No push is performed by this gate.
