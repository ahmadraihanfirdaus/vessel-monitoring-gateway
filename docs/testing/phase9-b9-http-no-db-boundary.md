# Phase 9 Batch 9 — Real Laravel HTTP boundaries, no DB

- Six contexts: API-001 framing, SEC-002 auth denial, TEL-001 quality/uint64, TEL-003 + NET-002 response/replay mapping, UI-002 read-path bounds, TST-001 HTTP-dispatch assurance.
- Only production behavior change: existing ingest size middleware rejects non-JSON Content-Type with HTTP 415 **after** preserving 413 precedence. JSON with charset / +json accepted. Does not enable TLS, trust proxies, rate limiting, or hardware attestation.
- PHPUnit B9 routes run in Laravel request kernel using fake DeviceTokenAuthenticator, TelemetryIngestService, EventIngestService and DeviceReadService instances; no RefreshDatabase/factory/migration/DB call. Test demonstrates controller/wire/status mapping, **not** a real network socket or authenticated MySQL persistence.
- The direct PHP probe loads the production middleware with minimal framework stand-ins. Probe PASS is not Laravel feature PASS; both gates required.
- External .env is unchanged. Runner sets ephemeral test environment DB_CONNECTION=mysql with DB_PORT=1 and no DB fixtures. Existing main CI MySQL job remains separate and unchanged.
- Required tests: Python B9 probe + static TST, PHP syntax lint, Laravel HTTP PHPUnit, existing B1–B8 host Python tests, B4 PHP CLI, firmware host core 226, locked/tree scope/security audits, exact Git commit and postcommit audit.
- Formal SIM/SUP, TLS deployment, firmware transport, DB persistence, dashboard data E2E, Wokwi/ESP32/bench are **NOT_RUN** by this batch. System status remains PARTIAL_NOT_PRODUCTION_READY.
