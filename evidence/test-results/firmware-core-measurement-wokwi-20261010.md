# Firmware Core Measurement — Wokwi Test Evidence

## 1. Test Identification

- Date: 2026-10-10
- Project: Integrated Vessel Monitoring & Diagnostic Gateway
- Test environment: Wokwi ESP32 Simulator
- Framework: ESP-IDF 6.1.0
- Development branch: develop
- Build-reported application version: 7fef26c-dirty
- Test result: PASSED
- Physical hardware testing: NOT_RUN

## 2. Test Objective

Verify the development-only numeric measurement model in `firmware/src/core_measurement.h`.

The model carries:

- `source_mode`
- `quality`
- `has_value`
- `value`

The function `vg_measurement_try_get_current_value()` must reject measurements with unrecognized source modes, invalid quality, absent values, or null pointers.

Failed reads must not modify the provided output variable.

## 3. Core Quality Test Results

| Test Case | Result |
|---|---|
| VALID_WITH_VALUE | PASS |
| VALID_NO_VALUE | PASS |
| INVALID_WITH_VALUE | PASS |
| MISSING_NO_VALUE | PASS |
| STALE_WITH_VALUE | PASS |
| UNKNOWN_NO_VALUE | PASS |
| UNKNOWN_WITH_VALUE | PASS |

**CORE_QUALITY_SELFTEST: PASS (7/7)**

## 4. Source Mode Test Results

| Test Case | Result |
|---|---|
| SIMULATION | PASS |
| BENCH_TEST | PASS |
| PHYSICAL_LABEL | PASS |
| UNKNOWN_ZERO | PASS |
| UNKNOWN_99 | PASS |

**SOURCE_MODE_SELFTEST: PASS (5/5)**

The PHYSICAL_LABEL test verifies an enumeration label only. It does not represent physical sensor acquisition.

## 5. Core Measurement Test Results

| Test Case | Result |
|---|---|
| SIMULATION_VALID | PASS |
| BENCH_TEST_VALID | PASS |
| VALID_ZERO | PASS |
| ZERO_INITIALIZED | PASS |
| UNKNOWN_SOURCE_VALID | PASS |
| UNKNOWN_99_VALID | PASS |
| INVALID_WITH_VALUE | PASS |
| MISSING_NO_VALUE | PASS |
| STALE_WITH_VALUE | PASS |
| UNKNOWN_QUALITY | PASS |
| VALID_NO_VALUE | PASS |
| NULL_MEASUREMENT | PASS |
| NULL_OUTPUT | PASS |

**CORE_MEASUREMENT_SELFTEST: PASS (13/13)**

## 6. Overall Test Result

- Core Quality: 7/7 PASSED
- Source Mode: 5/5 PASSED
- Core Measurement: 13/13 PASSED

**TOTAL: 25/25 PASSED**

All results were observed in the operator-provided Wokwi terminal output.

The application returned from `app_main()` without a visible panic.

## 7. Firmware Artifact Identification

- PlatformIO build result: SUCCESS
- Build duration: 87.51 seconds
- ELF SHA-256: 9133c98ac550fe188a705e861091d6027840940543e131f781403d1231df0d68
- BIN SHA-256: e9faaf250a298809cfd1ca2e01f8b988ad6baa8b66d2f8eaa4bbfebc820a7183
- Merged image SHA-256: bc082bfbf062ce293446aabb9387002883d44e1e851f83270dae5d806eaab103
- Merged image size: 209680 bytes
- Simulation flash configuration: 2 MiB
- Wokwi-reported ELF SHA-256 prefix: 9133c98ac

## 8. Requirement Coverage and Limitations

Verified development behavior:

- The measurement structure carries explicit source and quality metadata.
- Zero-initialized measurements are not returned as valid.
- A numerical zero can be retrieved when its metadata indicates a valid measurement.
- Unrecognized source modes are rejected.
- Invalid, missing, stale, and unknown-quality measurements are rejected.
- Null pointer cases are rejected.
- Failed reads leave the output variable unchanged.

Not yet verified:

- Complete SYS-002 source provenance across all system data.
- Complete TEL-001 telemetry payload structure.
- Complete TEL-002 null/absent-value serialization.
- NaN/Infinity handling and measurement range validation.
- Authenticity of a claimed source mode.
- Physical acquisition, sensors, or vessel integration.
- Backend, network, and dashboard functionality.

## 9. Engineering Status

- Core Quality Self-Test: PASSED
- Source Mode Self-Test: PASSED
- Core Measurement Self-Test: PASSED
- Complete SYS-002 verification: NOT_RUN
- Complete TEL-001 verification: NOT_RUN
- Complete TEL-002 verification: NOT_RUN
- Physical integration: NOT_AUTHORIZED
- Safety certification: NOT_CLAIMED

This document records development-only simulation evidence. It is not evidence of operational vessel readiness or physical safety certification.
