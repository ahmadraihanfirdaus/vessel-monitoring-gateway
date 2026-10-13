# Firmware Core Alarm Lifecycle — ESP32 Wokwi Development Self-Test (2026-10-13)

## Identification and provenance

- Project: Integrated Vessel Monitoring & Diagnostic Gateway.
- Requirement relevance: ALM-001 (PARTIAL), ALM-002 (PARTIAL), SYS-002 (partial foundation). ALM-003 NOT_IMPLEMENTED.
- Source revision at build time: `b6af121` + uncommitted Batch B1 changes; ESP-IDF logs `App version: b6af121-dirty`.
- Simulation framework: Wokwi ESP32 `esp32dev`, ESP-IDF 6.1.0 via PlatformIO / Espressif32 7.1.3.
- Test input: development-only deterministic firmware self-test cases in `firmware/src/main.c`; these are synthetic scenarios, **not sensor measurements**.
- Data source: simulation. Source-mode handling also includes synthetic BENCH_TEST and PHYSICAL labels in negative/metadata tests; **no bench or vessel hardware was connected**.
- Native host recheck: 79/79 PASS (MSYS2 UCRT64 GCC on Windows); not a substitute for Wokwi evidence.
- Build report (operator's local HOME, not committed): `vessel_gateway_B1_esp32_build_20261013_141304.log`.

## Firmware artifact fingerprint

| File | SHA-256 |
|---|---|
| ELF | `92178fcb6f0a6b78c51a18e46b1e8022a8138a8bb7cbe52a9db599488401e174` |
| Application BIN | `4a99d63f640ccf0473bdde1c4d936d161316d645a6e8cb3ad582d26a8d84deac` |
| Wokwi merged BIN | `35c68ef1b43fd1dc5134b236c642e16e7922f3eca97469ba0a05443ee9fca766` |

- Merged image size: 215168 bytes (Wokwi 2 MiB target configuration, **not** physical flash-capacity verification).
- Wokwi reported: `ELF file SHA256: 92178fcb6...`; matches local ELF SHA-256 prefix.
- Wokwi reported `App version: b6af121-dirty`; correct for code built before the Batch B1 commit.

## Actual observed simulation results

The operator pasted the Wokwi Serial Monitor output to the project conversation on 2026-10-13. Selected lines are transcribed below. This Markdown record **does not archive the full raw UART transcript**; original full output is in the conversation and should be retained/exported for independent evidence preservation.

```text
CORE_QUALITY_SELFTEST: PASS (7/7)
SOURCE_MODE_SELFTEST: PASS (5/5)
CORE_MEASUREMENT_SELFTEST: PASS (16/16)
CORE_RANGE_SELFTEST: PASS (21/21)
CORE_ALARM_SELFTEST: PASS (30/30)
I (522) main_task: Returned from app_main()
```

| Self-test group | Expected | Operator-observed | Result |
|---|---:|---:|---|
| Core Quality | 7/7 | 7/7 | PASS |
| Source Mode | 5/5 | 5/5 | PASS |
| Core Measurement | 16/16 | 16/16 | PASS |
| Core Range | 21/21 | 21/21 | PASS |
| Core Alarm | 30/30 | 30/30 | PASS |
| **Total** | **79/79** | **79/79** | **PASS** |

Alarm cases reported PASS included ACK_DOES_NOT_CLEAR, ACK_ACTIVE, CLEAR_AFTER_RECOVERY, CLEAR_UNACK, SECOND_ID_UNIQUE_IN_BOOT, REJECT_EARLY_ACK, REJECT_BACKWARDS_CLEAR_UNACK, PHYSICAL_MODE_REJECTED, ALLOCATOR_OVERFLOW_GUARD and INCONSISTENT_STATE_REJECTED. The observed log showed successful execution returning from `app_main()`, with no panic in the provided transcript.

## Verification scope and limitations

- **Development-only self-test PASS**; formal planned SIM/SUP test cases remain NOT_RUN. In particular SUP-004 is not claimed VERIFIED.
- The test scaffold exits from `app_main()`; it does not establish long-term continuous sampling, timing guarantees, or an operational alarm manager.
- Alarm ID uniqueness is only within a single initialized allocator / boot. Stable global identity and `boot_id` are not implemented.
- Caller-supplied monotonic timestamp units, clock source, priority taxonomy and event-journal linkage remain to be specified and verified.
- No local buzzer/LED GPIO path, authenticated acknowledgement, event persistence, physical calibration, marine qualification, or vessel integration was tested.
- Wokwi runtime evidence was provided by the operator; the assistant did not directly access the operator's simulator.
- Safety and publication approvals are not implied by these tests.
