# Phase 9 B16 — Host receipt decision contract, not a deployed authenticated transport

Scope: NET-002, TEL-003, API-001, SEC-002, SYS-003, TST-001, TST-002.

A strict C99 *host* gate admits only a verified status/result pairing:
- Telemetry `201 + created`, or `200 + identical_duplicate`.
- Event `201 + event_persisted`, or `200 + identical_event_duplicate`.
- Conflicts (409), missing/unauthorized (401), outage (503), unknown/bad pairings never advance ACK.
- Preexisting `phase9_b8_ack_window` still requires sequence/correlation equality and local safety success.

**Threat model:** `authenticated_response_verified` and the decoded semantic tag are TEST INJECTIONS. The helper is not a TLS verification routine, HTTP client, or JSON decoder. A forged tag or claim is not authenticated evidence. No firmware NVS/flash persistence, actual connectivity, MySQL HTTP E2E, closed-loop safety, certified navigation, actuator control, or formal SIM/SUP closure can be inferred.

The PHP fixture exercises the real Laravel POST routes `/api/v1/telemetry` and `/api/v1/events` using byte-preserved C99-generated JSONL B14/B15 and dependency-mocked auth and ingest service; it verifies both successful idempotent receipts and denied/conflicting results. The C99 fixture separately exercises the ACK decision gate (21 cases). Together these constitute a **contract boundary**, not execution of a real device request/response over network.

Tests require PHP with vendor dependencies, gcc, and Python. DB_CONNECTION=mysql to an intentionally unreachable port, without DB migration. All B9–B16 JUnit and 49 prior host suites must pass in Windows runner before exact-scope local auto-commit.
