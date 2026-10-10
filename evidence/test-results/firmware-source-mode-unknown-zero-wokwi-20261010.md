# Firmware Source Mode UNKNOWN_ZERO - Wokwi Test Evidence

## 1. Identification

- Date: 2026-10-10
- Project: Integrated Vessel Monitoring & Diagnostic Gateway
- Result: SOURCE_MODE_UNKNOWN_ZERO_SELFTEST_PASSED
- Environment: Wokwi ESP32 Simulator
- Framework: ESP-IDF 6.1.0
- Source branch: develop
- Local development commit before new changes: d4c46ac
- Build-reported application version: 97c3dc7-dirty
- Physical hardware testing: NOT_RUN

## 2. Test Objective

Verify that the default source mode is UNKNOWN and cannot be silently identified as simulation data.

The firmware uses these internal enumeration values:

| Value | Mode |
|---|---|
| 0 | VG_SOURCE_UNKNOWN |
| 1 | VG_SOURCE_SIMULATION |
| 2 | VG_SOURCE_BENCH_TEST |
| 3 | VG_SOURCE_PHYSICAL |

The enumeration values do not define an approved telemetry wire format.

## 3. Test Results

Core Quality Self-Test:

- VALID_WITH_VALUE: PASS
- VALID_NO_VALUE: PASS
- INVALID_WITH_VALUE: PASS
- MISSING_NO_VALUE: PASS
- STALE_WITH_VALUE: PASS
- UNKNOWN_NO_VALUE: PASS
- UNKNOWN_WITH_VALUE: PASS

Result: 7/7 PASSED

Source Mode Self-Test:

- SIMULATION: PASS
- BENCH_TEST: PASS
- PHYSICAL_LABEL: PASS
- UNKNOWN_ZERO: PASS
- UNKNOWN_99: PASS

Result: 5/5 PASSED

**Overall result: 12/12 PASSED**

## 4. Observed Wokwi Output

The operator supplied the following terminal observations:

    I (167) app_init: App version: 97c3dc7-dirty
    I (177) app_init: ELF file SHA256: 391bbbae6...
    I (238) main_task: Calling app_main()
    CORE_QUALITY_SELFTEST: PASS (7/7)
    SOURCE_MODE_TEST SIMULATION: PASS
    SOURCE_MODE_TEST BENCH_TEST: PASS
    SOURCE_MODE_TEST PHYSICAL_LABEL: PASS
    SOURCE_MODE_TEST UNKNOWN_ZERO: PASS
    SOURCE_MODE_TEST UNKNOWN_99: PASS
    SOURCE_MODE_SELFTEST: PASS (5/5)
    I (288) main_task: Returned from app_main()

## 5. Firmware Artifact Identification

- Build result: PASSED
- Build duration: 6.21 seconds
- ELF SHA-256: 391bbbae6cc7e6a9de665519d5f39d654f9a1ac3ea5e6d077fb8d38609102f23
- BIN SHA-256: 0e6a768454f0fbe10fc3e77035f1ee3950ae86c0bc8b761e5564be66911531cd
- Merged image SHA-256: 7982e2e5192f09adb6cd6c6e4c1264c80b32f333d7047dc659dbb4f7d3d715fe
- Merged image size: 208816 bytes
- Simulated flash configuration: 2 MiB

The build-reported Git version does not match the latest local development commit. The reason for this metadata discrepancy has not yet been established.

## 6. Verification Limitations

Verified:

- Firmware compiled successfully.
- ESP32 virtual boot completed.
- Core Quality tests passed 7/7.
- Source Mode tests passed 5/5.
- UNKNOWN_ZERO and UNKNOWN_99 were rejected as recognized source-mode labels.

Not verified:

- Complete source provenance across telemetry payloads.
- Complete SYS-002 and SUP-002 verification.
- Telemetry serialization and backend integration.
- Sensor acquisition and alarm behavior.
- Physical ESP32 or vessel integration.

## 7. Engineering Status

- Core Quality Self-Test: PASSED
- Source Mode Self-Test: PASSED
- Complete SYS-002 verification: NOT_RUN
- Complete SUP-002 verification: NOT_RUN
- Telemetry integration: NOT_IMPLEMENTED
- Physical integration: NOT_AUTHORIZED
- Safety certification: NOT_CLAIMED

This document records operator-provided simulation results and does not constitute independent physical or safety certification.
