# Firmware Core Quality - Wokwi Functional Self-Test Evidence

## 1. Identification

- Date: 2026-10-10
- Project: Integrated Vessel Monitoring & Diagnostic Gateway
- Result: CORE_QUALITY_SELFTEST_PASSED
- Environment: Wokwi ESP32 Simulator
- Framework: ESP-IDF 6.1.0
- Source branch: develop
- Build-reported version: 550ba05-dirty
- Physical hardware testing: NOT_RUN

## 2. Test Objective

Verify the behavior of `vg_measurement_is_current_valid()` using seven development-only test cases.

The function accepts a measurement as current and valid only when its quality is `VG_QUALITY_VALID` and its value is present.

## 3. Test Results

| Test Case | Expected | Observed |
|---|---|---|
| VALID_WITH_VALUE | true | PASS |
| VALID_NO_VALUE | false | PASS |
| INVALID_WITH_VALUE | false | PASS |
| MISSING_NO_VALUE | false | PASS |
| STALE_WITH_VALUE | false | PASS |
| UNKNOWN_NO_VALUE | false | PASS |
| UNKNOWN_WITH_VALUE | false | PASS |

Total: **7/7 PASSED**

## 4. Observed Wokwi Terminal Output

The operator supplied the following runtime observations:

    I (167) app_init: App version: 550ba05-dirty
    I (176) app_init: ELF file SHA256: dd1a6264d...
    I (237) main_task: Calling app_main()
    QUALITY_TEST VALID_WITH_VALUE: PASS
    QUALITY_TEST VALID_NO_VALUE: PASS
    QUALITY_TEST INVALID_WITH_VALUE: PASS
    QUALITY_TEST MISSING_NO_VALUE: PASS
    QUALITY_TEST STALE_WITH_VALUE: PASS
    QUALITY_TEST UNKNOWN_NO_VALUE: PASS
    QUALITY_TEST UNKNOWN_WITH_VALUE: PASS
    CORE_QUALITY_SELFTEST: PASS (7/7)
    I (267) main_task: Returned from app_main()

## 5. Artifact Identification

- ELF SHA-256: dd1a6264dbc72e0bdb2af5c4c39d1f6fced70586b66dd87c6554ed6c40f6ebd4
- BIN SHA-256: 80db5439aeb11f337c2a0fdfb70f6e1eda0f47fecd86edbb8ab6bfde2c9081f6
- Merged Image SHA-256: d1cbf960a575a8ba3933bf49c24db10ad6a07137f8caa084175053f08d9a856e

The firmware was built from local uncommitted changes based on commit `550ba05`.

## 6. Verification Scope and Limitations

Verified:
- Firmware compilation completed successfully.
- ESP32 virtual boot completed.
- The seven defined quality-check scenarios passed.

Not verified:
- Numeric sensor-value validation.
- Telemetry null/absent serialization.
- Sensor acquisition or freshness transitions.
- Alarm and safety-policy evaluation.
- Complete SYS-002 or TEL-002 compliance.
- Physical ESP32 or vessel integration.

## 7. Engineering Status

- Core quality self-test: PASSED
- Complete telemetry quality contract: NOT_IMPLEMENTED
- Sensor integration: NOT_IMPLEMENTED
- Physical integration: NOT_AUTHORIZED
- Safety certification: NOT_CLAIMED

This document records operator-provided simulation results. It is not an independently reproduced test report or physical safety certification.
