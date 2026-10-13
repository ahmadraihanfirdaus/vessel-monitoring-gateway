# Firmware Core C2 — Integrated Simulated Event Flow (Wokwi, 2026-10-13)

## Provenance and execution identity

- Project: Integrated Vessel Monitoring & Diagnostic Gateway engineering prototype, **simulation only**.
- Source state: local `develop@0d6c262` plus uncommitted Batch C2 changes. The Wokwi app identifies `App version: 0d6c262-dirty`.
- Target: `esp32dev`, PlatformIO Espressif32 7.1.3 / ESP-IDF 6.1.0, using 2MB Wokwi simulated flash configuration.
- Stimulus: **169 deterministic firmware self-tests** in `firmware/src/main.c`; 36 new C2 orchestrator tests, with 133 previously developed tests.
- Operator-reported build report: `vessel_gateway_C2_esp32_build_20261013_153139.log` (outside repository, in local HOME; **not** included here).
- UART captured from the **third/latest boot** in operator-provided multi-boot transcript. The first two old-image boots are excluded. The transcript was supplied in chat; assistant did not independently run the simulator.
- Archived UART: `evidence/logs/firmware-core-c2-wokwi-serial-20261013.txt`, with Windows CRLF converted to LF and trailing spaces normalized; individual test lines not synthesized.

## Firmware artifact identity from operator build output

| File | SHA-256 |
|---|---|
| ELF | `b9ae25ade5c903937ec7869d5e08e2efffd90ba1576656655430d9eb10bf4280` |
| Firmware BIN | `3567bb50de72cda4668932c7cb190d5ba4f732a0b4bf24e8f0f5b0cf25199139` |
| Wokwi merged BIN | `3f85008a51c31f5947322b9cebad93b06bc6dd92b6b9968fbced9d42b68afb32` |

- Merged BIN size: **225280 bytes**. This does not confirm physical flash capacity.
- Archived C2 UART SHA-256: `e4296bdcd5bca6838425f55e1fd73f0cf291c291fef121aaa7e35c4a4653d834`.
- C2 UART reports `ELF file SHA256: b9ae25ade...` matching the ELF prefix. ESP-IDF boot completes; no visible panic/reset in this boot, and `app_main()` returns normally.

## Expected vs observed software self-tests

| Development suite | Expected | Observed | Result |
|---|---:|---:|---|
| Core Quality | 7/7 | 7/7 | PASS |
| Source Mode | 5/5 | 5/5 | PASS |
| Core Measurement | 16/16 | 16/16 | PASS |
| Core Range | 21/21 | 21/21 | PASS |
| Core Alarm | 30/30 | 30/30 | PASS |
| Core Scheduler | 16/16 | 16/16 | PASS |
| Core Diagnostics | 19/19 | 19/19 | PASS |
| Core Event Journal | 19/19 | 19/19 | PASS |
| Core Flow | 36/36 | 36/36 | PASS |
| **Total** | **169/169** | **169/169** | **PASS** |

Each case line appears once in the operator-reported C2 boot log. The closure gate validates all case and suite counts with the source test runner, reruns native GCC and repository audits, checks the actual ELF/BIN/merged file hashes, and makes a **local** commit only when gates pass.

## Scope limitations and unverified requirements

- **Self-tests, not formal verification**. `SIM-001..SIM-015` and `SUP-001..SUP-019` remain `NOT_RUN`; requirement statuses are not automatically changed to VERIFIED by this evidence.
- The orchestrator is caller-injected (simulation or bench *labels*), synchronous, single channel, and single writer. There is **no operational ESP-IDF periodic acquisition loop**, sensor driver, timestamp provenance, or physical input.
- Alarm raise, acknowledge and clear are simulated events; priority/reason codes are placeholders, not approved vessel safety thresholds. No GPIO/buzzer/LED outputs or full safety policy are exercised.
- The journal is **RAM-only (8 events)**, refuses further event-producing state transitions when full, and does not survive reboot or power loss. No NVS, offline sync/replay, idempotent global event IDs, network link, backend, or end-to-end testing exists.
- Software atomic rollback cases and Wokwi self-test PASS do **not** demonstrate durable event retention, backend-offline independence, operator acknowledgement controls, real-time scheduling or marine certification.
- `hardware flash capacity: TBD`; no hardware testing, publication authorization or vessel integration is implied.
