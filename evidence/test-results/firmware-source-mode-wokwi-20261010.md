# Firmware Source Mode - Wokwi Self-Test Evidence

## 1. Identification

- Date: 2026-10-10
- Project: Integrated Vessel Monitoring & Diagnostic Gateway
- Result: SOURCE_MODE_SELFTEST_PASSED
- Environment: Wokwi ESP32 Simulator
- Framework: ESP-IDF 6.1.0
- Source branch: develop
- Build-reported version: 97c3dc7-dirty
- Physical hardware testing: NOT_RUN

## 2. Test Objective

Verify source-mode identification and preservation of the existing Core Quality self-test.

Source modes:

- `simulation`
- `bench_test`
- `physical`

An unknown source-mode value must not be silently converted into a recognized mode.

Recognition of the `physical` label does not authorize or demonstrate physical integration.

## 3. Test Results

| Test Case | Expected | Result |
|---|---|---|
| VALID_WITH_VALUE | true | PASS |
| VALID_NO_VALUE | false | PASS |
| INVALID_WITH_VALUE | false | PASS |
| MISSING_NO_VALUE | false | PASS |
| STALE_WITH_VALUE | false | PASS |
| UNKNOWN_NO_VALUE | false | PASS |
| UNKNOWN_WITH_VALUE | false | PASS |
| SIMULATION | simulation / known | PASS |
| BENCH_TEST | bench_test / known | PASS |
| PHYSICAL_LABEL | physical / known | PASS |
| UNKNOWN_99 | NULL / unknown | PASS |

Core Quality: **7/7 PASSED**

Source Mode: **4/4 PASSED**

Total: **11/11 PASSED**

## 4. Observed Wokwi Terminal Output

The operator supplied the following runtime observations:

    I (167) app_init: App version: 97c3dc7-dirty
    I (176) app_init: ELF file SHA256: 1b7800f0e...
    I (237) main_task: Calling app_main()
    Development scaffold only; monitoring and alarms are not implemented.
    QUALITY_TEST VALID_WITH_VALUE: PASS
    QUALITY_TEST VALID_NO_VALUE: PASS
    QUALITY_TEST INVALID_WITH_VALUE: PASS
    QUALITY_TEST MISSING_NO_VALUE: PASS
    QUALITY_TEST STALE_WITH_VALUE: PASS
    QUALITY_TEST UNKNOWN_NO_VALUE: PASS
    QUALITY_TEST UNKNOWN_WITH_VALUE: PASS
    CORE_QUALITY_SELFTEST: PASS (7/7)
    SOURCE_MODE_TEST SIMULATION: PASS
    SOURCE_MODE_TEST BENCH_TEST: PASS
    SOURCE_MODE_TEST PHYSICAL_LABEL: PASS
    SOURCE_MODE_TEST UNKNOWN_99: PASS
    SOURCE_MODE_SELFTEST: PASS (4/4)
    I (287) main_task: Returned from app_main()

## 5. Artifact Identification

- ELF SHA-256: 1b7800f0e693a1cfceb3b96e25a89ed1706433532c98b5456c4a4ed2b1e6e21e
- BIN SHA-256: f95f7bea64d61ce1645cde35a245a28e3c6dd68f2f2d524717d1f8bd3c71ddcc
- Merged Image SHA-256: 68610d1f9372f80fa867e5fba7c5c5e04511ce7dd9be78c9363976346e13c035

The firmware image was built from local uncommitted changes based on commit `97c3dc7`.

## 6. Verification Scope

Verified:

- Successful ESP-IDF firmware build.
- Successful ESP32 virtual boot.
- Seven Core Quality test cases passed.
- Four Source Mode test cases passed.
- Unknown source-mode value rejected as unrecognized.

Not verified:

- Complete SYS-002 data provenance separation.
- SUP-002 end-to-end telemetry contract.
- Sensor acquisition and validation.
- Telemetry serialization and backend ingestion.
- Alarm and safety-policy evaluation.
- Physical ESP32 or vessel integration.

## 7. Engineering Status

- Core Quality Self-Test: PASSED
- Source Mode Self-Test: PASSED
- Complete SYS-002 verification: NOT_RUN
- Complete SUP-002 verification: NOT_RUN
- Telemetry integration: NOT_IMPLEMENTED
- Physical integration: NOT_AUTHORIZED
- Safety certification: NOT_CLAIMED

This document records operator-provided simulation results. It is not an independently reproduced test report or physical safety certification.
