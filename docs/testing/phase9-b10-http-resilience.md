# Phase 9 B10 — HTTP framing and failure classification (scoped)

Baseline: B9 local commit `eb18432f04b479a16e142f386c0eea14994c0c3f`.

Six scoped contexts, **not** requirement-wide VERIFIED: API-001 stricter media type acceptance; SEC-002 short bearer fails without lookup; UI-002 malformed and valid cursor isolation; SYS-003 persistence/backend exception is not misclassified as cursor validation error; TST-001 actual Laravel route dispatch with service mocks; TST-002 added to DB-free CI job.

The existing B9 history mock test used the invalid literal `fixture-cursor`; B10 replaces only that placeholder with a valid `Cursor::encode()` fixture.

Production changes: `EnsureTelemetryPayloadSize` accepts only `application/json` or an `application/*+json` structured MIME subtype, optionally parameterized; rejects `application/jsonp` regardless of Laravel `isJson()` substring matching. `DeviceHistoryController` decodes/validates a supplied cursor *before* calling `DeviceReadService`; only invalid cursor receives 422, while downstream errors flow through Laravel's normal server-error handler.

All B10 HTTP tests use in-memory mocked `DeviceTokenAuthenticator` and `DeviceReadService`. `DB_PORT=1` is a fail-closed sentinel; it is not proof DB was never contacted unless test logs and mocks confirm. HTTP tests here are Laravel application-dispatch tests, **not** real network HTTPS/ESP32/MySQL/persistent telemetry evidence.

No DB access intended, no migrations/real device/hardware, no production credentials, no push. The original CI MySQL job remains unchanged; B10 is inside the no-DB job only. SIM/SUP/production readiness remain FORMAL_OPEN and `PARTIAL_NOT_PRODUCTION_READY`.
