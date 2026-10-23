# Phase 9 B12 — authenticated device HTTP no-store boundary

Development-only scoped integration, not production certification.

The existing Laravel device HTTP routes are instrumented with the registered
`device.response.no-store` middleware. Middleware is deliberately first within
the five route stacks, before payload framing and bearer auth, so ordinary 413,
415, 401, 403, 422, 200, 201, 409 and typed 503 receipts on these routes use
`Cache-Control: no-store, private`, `Pragma: no-cache`, and preserve existing
Vary headers while adding Authorization. An exception-generated response
outside the route middleware's return path is NOT covered by this guarantee.

## Why

Device state, event receipts, telemetry and authentication decisions must not
be reused from stale intermediary/browser caches. This measure does not provide
TLS, cryptographic provisioning, rate limits, bearer secrecy, hardware
provenance, DB E2E or a working dashboard data adapter.

## Evidence boundaries

- Laravel feature tests exercise real route/middleware/controller dispatch with
  Mockery services (no DB, migrations, network, or hardware).
- Host contract and CI policy tests complement rather than replace feature tests.
- 49 historical suites, core 226 and B9/B10/B11 Laravel suites remain required.
- No formal SIM/SUP closure; overall PARTIAL_NOT_PRODUCTION_READY.
