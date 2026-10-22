# Phase 9 Batch 4 – Cross-Language Host Contract Boundaries

Five contexts: TEL-001, TEL-002, API-001, SEC-002, TST-001. Development-only.

- TEL-001: reused Phase 8 serializer with schema, identity, uptime, source_mode, and quality; synthetic/bench data only. No real gateway output.
- TEL-002: invalid/missing/unknown never become numeric zero. A real zero marked valid stays zero. Stale handling follows Phase 8 telemetry contract.
- API-001: new standalone PHP host-fixture check of selected synthetic payloads, **not** connected to Laravel routes, device.auth, FormRequest, duplicate detection, or MySQL. Do not rely on it instead of existing API validation. Raw duplicate JSON keys are **not checked here**.
- SEC-002: a fail-closed boolean decision for mocked preverified TLS/auth claims; claims are fixture-controlled, NOT actual TLS, authenticated endpoint or deployed credentials.
- TST-001: five source/test pairs checked; formal SUP017 and TST-001 remain OPEN. CI does not demonstrate Wokwi or bench hardware results.
- Integration: C99 serializer output parsed with the PHP CLI, and null-vs-zero negative checks. Production network settings including endpoint, certificates, timeout/retry/backoff remain TBD.
- No modifications to firmware main.c, locked requirements or database. No live network calls, Laravel migration, DB write or actuator control.
- Existing core 226/226 and B1/B2/B3 regressions are re-executed in scope.
- Passing Batch 4 host gate never closes formal SIM/SUP cases and does not imply production readiness.
