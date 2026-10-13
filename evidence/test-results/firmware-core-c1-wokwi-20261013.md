# Firmware Core C1 — Scheduler, Diagnostics & Volatile Event Journal (Wokwi, 2026-10-13)

## Source identity and execution context

- Project: Integrated Vessel Monitoring & Diagnostic Gateway engineering prototype.
- Build source: `develop@ff13760` plus uncommitted Batch C1 edits, corresponding to Wokwi `App version: ff13760-dirty`.
- Build: PlatformIO Espressif32 7.1.3 / ESP-IDF 6.1.0, target `esp32dev`, Wokwi simulator only.
- Test stimulus: 133 deterministic development-only self-test cases in `firmware/src/main.c`; **not continuous operational sampling**.
- Source-mode labels in negative tests are synthetic inputs; no bench or physical data were acquired.
- Operator's build log: `vessel_gateway_C1_esp32_build_20261013_145919.log` in local HOME, not committed.
- UART transcript: `evidence/logs/firmware-core-c1-wokwi-serial-20261013.txt`. This is the **second/latest boot** pasted by the operator in chat (terminal trailing whitespace normalized); the first/older B1 boot was excluded. The assistant did not independently operate the simulator.

## Artifact identity from operator's build report

| Artifact | SHA-256 |
|---|---|
| ELF | `3fddb0e2716fe1716dd59a086679e4e355adda2ffa5791c076e8d0398375d5f0` |
| Firmware BIN | `b12078b6d2403f50226cf333f43c895c22d0352ea285ac60c4b368d974e116c2` |
| Wokwi 2MB merged BIN | `87cf72d876b2c355fd3b08759ab8391a41f5b69ee8cb584fc1fa8f4054eb0119` |

- Merged BIN size: 220592 bytes. Physical ESP32 hardware flash capacity remains **TBD**.
- UART transcript SHA-256: `20f1d293b322a9590552a390f9d5599ebf8e8da3e96ecbe584f1062dbb1f1a32`.
- Wokwi reported `ELF file SHA256: 3fddb0e27...` matching the ELF prefix, and returned from `app_main()` without a visible panic or crash.

## Expected vs observed (operator-provided Wokwi UART)

| Test group | Expected | Observed | Result |
|---|---:|---:|---|
| Core Quality | 7/7 | 7/7 | PASS |
| Source Mode | 5/5 | 5/5 | PASS |
| Core Measurement | 16/16 | 16/16 | PASS |
| Core Range | 21/21 | 21/21 | PASS |
| Core Alarm | 30/30 | 30/30 | PASS |
| Core Scheduler | 16/16 | 16/16 | PASS |
| Core Diagnostics | 19/19 | 19/19 | PASS |
| Core Event Journal | 19/19 | 19/19 | PASS |
| **Overall** | **133/133** | **133/133** | **PASS** |

The UART transcript contains individual PASS case lines for each group. Native MSYS2 UCRT64 GCC host tests were reported **133/133 PASS** separately and were rerun by the C1 closure gate.

## Verification boundary and remaining work

- **Development self-test PASS only.** Formal SIM/SUP test cases, including offline and event-retention tests, remain **NOT_RUN**. This does not close SYS-003, NET-002, TST-001, or other system requirements.
- Scheduler implements due-time calculations, not an operational periodic sampling task; `app_main()` exits after the self-tests.
- Diagnostics are simulated single-channel transitions; actual acquisition, freshness timeouts and alarm integration are not implemented.
- Journal is a bounded 8-entry **RAM-only** buffer; it refuses writes when full and does **not survive reboot/power loss**. No NVS persistence, offline transport, replay, or guaranteed critical-event retention exists.
- Alarm/global event identities across reboots, hardware clock/timebase provenance, full safety-policy integration, physical sensor calibration, real LEDs/buzzer, and marine certification are **not verified**.
- Test evidence is operator-reported, not an independent simulator recording; no physical vessel integration or publication approval is implied.
