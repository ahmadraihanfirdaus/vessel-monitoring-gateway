# Phase 9 P3 Runtime HTTP Summary — 2026-10-18

- Source commit: `2a1596ae47ec8a4572affe1cd457b27579234cf2`.
- Attempt 1 stopped at server bootstrap because the Laravel built-in router was
  launched from the backend root rather than `backend/laravel/public`.
- Attempt 2 corrected the server launcher and passed scenarios 01-09, then
  scenario 10 received HTTP 422 because the runtime-only telemetry fixture used
  a list instead of the telemetry-v1 channel object keyed by channel name.
- Recovery v3 itself did not start a new runtime attempt; it stopped in a
  whitespace-sensitive verification check against a pretty-printed committed
  JSON fixture.
- Recovery v4 changed that check to semantic JSON parsing and reused the
  corrected object-shaped runtime telemetry fixture. No application source or
  database schema was changed.
- Runtime database: `vessel_monitoring_gateway_test` on isolated MariaDB `127.0.0.1:3307`.
- Runtime HTTP endpoint: loopback `http://127.0.0.1:18083`.
- Runtime scenarios: 16/16 PASS.
- Event ingest verified: unauthenticated rejection, distinct insert, idempotent
  duplicate, conflicting duplicate rejection, physical-source rejection,
  device-identity mismatch rejection, 4096-byte payload boundary, and UInt64
  maximum event identity preservation.
- Device read verified: null pre-telemetry state, latest state, newest-first
  history, bounded history with continuation cursor, health metadata, and
  unauthenticated read rejection.
- Runtime database semantic check: PASS.
- Application database received no runtime test data.
- Runtime fixture was created and removed through Laravel model operations.
- Test database returned to zero device/telemetry/channel/event rows.
- Formal SIM010-SIM015 remain NOT_RUN.
- SUP013/SUP014 remain NOT_RUN.
- Physical bench remains NOT_RUN.
- Production readiness is not claimed.
