# Phase 9 Batch 3 — five-context HOST integration boundary

## Scope
NET-001 host uplink callback on READY only; NET-002 volatile ordered event replay cursor with explicit caller acknowledgement; SYS-002 synthetic source-mode consistency and physical-mode refusal; SYS-003 local sampling/safety/alarm callbacks before network progression, including offline; TEL-003 in-memory bounded duplicate/replay/conflict classification.

## Nonclaims
- Not ESP32 firmware `main.c` integration or proof of real-time/nonblocking behavior of real network drivers.
- No Wi-Fi, HTTPS, TLS, endpoint, real credentials or operational data.
- No ESP32 flash/NVS, power-loss replay durability, server acknowledgement or global ordering proof.
- No MySQL-backed deduplication, API ingestion integration, SIM-014, physical sensors, actuator control or formal requirement PASS.
- `TEL003_HOST_WINDOW_CAP`, `NET002_HOST_JOURNAL_CAP` and `NET002_HOST_LATEST_MAX` are host fixture limits only, not approved production configuration.
- Numerical NET-001 policy in test snippets is fixture data only. Production timeout/retry/backoff remain TBD.

## Audit
Run each added host test plus the combined five-context host fixture, all prior Batch 1/2 host test cases, and core regression 226/226. Evidence is written outside repository. Exact source scope: 14 ADD and 1 MODIFY (`.github/workflows/phase9-multi-context-ci.yml`). All locked anchors and B1/B2 committed files are byte-pinned. Source stays unstaged; separate approval needed for local commit. Formal requirements remain OPEN and total system PARTIAL_NOT_PRODUCTION_READY.
