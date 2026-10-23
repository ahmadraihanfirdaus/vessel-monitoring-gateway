# Phase 9 B15 — Volatile C99 journal to Laravel event HTTP, host-only

Source: `firmware/src/core_event_journal.h` produces 4 real journal entries (raise/ack/clear/fault) with source mode labels, monotonic times and bounded per-boot event identity. A host-only C99 JSON adapter (`scripts/phase9_b15_event_wire_fixture.c`) prints versioned objects. The Python bridge preserves raw bytes (LF or CRLF); Laravel B15 feature tests POST those raw objects through the real `/api/v1/events` middleware/request/controller with a strict auth + persistence service double. No SQL, DB migrations, sockets, device driver, NVS, physical source attestation or network replay are executed by this gate.

Coverage: ALM-001 event identity, provenance labels SYS-002, authenticated HTTP SEC-002/API-001, valid/invalid event schema, NET-002 receipt behavior and TEL-003 conflict receipt (service outputs deliberately mocked). Tests cannot prove actual persistence/dedup, HTTP transport, event durability, replay ACK invariants or operational alarm safety; SIM/SUP formal acceptance remains OPEN.

This adapter is *not* deployed firmware event serializer. It maps `vg_journal_event_t` fields to the existing Laravel event schema explicitly, refusing journal `recovery` and `physical` modes because current API does not admit them. Never silently revise LOCKED constraints or imply physical sensors are verified.
