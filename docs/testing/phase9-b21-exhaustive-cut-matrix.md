# Phase 9 B21: exhaustive host prefix-write and bitflip matrix

**Scope:** NET-002, TEL-003, SYS-003, ALM-002, SEC-001, TST-001, TST-002. This is bounded host C99 development evidence, not ESP32/NVS/filesystem crash durability.

- Derive candidate generation 12/ACK 9 using B20 preparation from valid slots 10/11; write only older slot 10.
- For every prefix length `[0, candidate length)`, model both truncation and prefix overwrite retaining old suffix; ensure generation 11/ACK 8 can still be selected and pending ACK stays cleared.
- For every byte and each of its eight bits, corrupt one candidate bit; fallback to generation 11 while rejecting readback.
- Confirm the full candidate restores generation 12/ACK 9, and active slot bytes remain unchanged.
- Reject malformed injection parameters without changing caller output. Capture exact cardinalities in test output; CI and local runner require the marker and prohibit `NOT_RUN` conversion to `PASS`.

This models only deterministic **in-memory** corruptions. It cannot establish torn-sector behavior, fsync/rename guarantees, power-fail durability, wear, authentication, ESP32 NVS atomicity, or a production-safe retry protocol. An older successful ACK may be conservatively replayed; backend idempotency is still necessary. No DB, device writes, real network, hardware flashing, or formal acceptance.
