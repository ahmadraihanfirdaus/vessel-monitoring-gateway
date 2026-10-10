# Firmware Numeric Finiteness — Wokwi Test Evidence

## 1. Test Identification

| Field | Value |
|---|---|
| Date | 2026-10-10 |
| Project | Integrated Vessel Monitoring & Diagnostic Gateway |
| Environment | Wokwi ESP32 Simulator |
| Framework | ESP-IDF 6.1.0 |
| Development branch | develop |
| Source HEAD before changes | 218989e |
| Build-reported application version | 7fef26c-dirty |
| Result | PASSED |
| Physical hardware testing | NOT_RUN |

## 2. Test Objective

Verify that `vg_measurement_try_get_current_value()` rejects non-finite floating-point measurements without modifying the output variable.

The validation uses `isfinite()` from `<math.h>`.

This test extends the existing Core Quality, Source Mode, and Core Measurement self-tests.

## 3. Numeric Finiteness Results

| Test Case | Result |
|---|---|
| NAN_REJECTED | PASS |
| POSITIVE_INFINITY_REJECTED | PASS |
| NEGATIVE_INFINITY_REJECTED | PASS |

All three new scenarios passed in Wokwi.

The test harness also checks that unsuccessful reads do not modify the output sentinel.

## 4. Regression Test Results

| Test Suite | Result |
|---|---|
| Core Quality Self-Test | PASS (7/7) |
| Source Mode Self-Test | PASS (5/5) |
| Core Measurement Self-Test | PASS (16/16) |
| **Overall** | **PASS (28/28)** |

Existing tests for valid numerical zero, zero-initialized measurements, unrecognized source modes, invalid quality, and null pointers also passed.

## 5. Observed Wokwi Output

    I (168) app_init: App version:      7fef26c-dirty
    I (177) app_init: ELF file SHA256:  308992dfb...
    CORE_QUALITY_SELFTEST: PASS (7/7)
    SOURCE_MODE_SELFTEST: PASS (5/5)
    MEASUREMENT_TEST NAN_REJECTED: PASS
    MEASUREMENT_TEST POSITIVE_INFINITY_REJECTED: PASS
    MEASUREMENT_TEST NEGATIVE_INFINITY_REJECTED: PASS
    CORE_MEASUREMENT_SELFTEST: PASS (16/16)
    I (348) main_task: Returned from app_main()

No panic was visible in the supplied terminal output.

## 6. Firmware Artifact Identification

| Artifact | SHA-256 |
|---|---|
| firmware.elf | 308992dfb8a4b7713857f8cdf004ec9841a1dcd6f96ce8b20707b0e5e4098819 |
| firmware.bin | 9652890e733bfbe32e634b639f2266b36cad1c94be6ecc337a08f6d51384ac79 |
| firmware.merged.bin | e7ed0532ea5bf907dce23ef053054de2b161b6a3e132118cf93399ed3459b52a |

- Build result: SUCCESS
- Build duration: 5.38 seconds
- Merged image size: 209872 bytes
- Simulated flash configuration: 2 MiB
- Wokwi-reported ELF SHA-256 prefix: 308992dfb

The build-reported application version differs from the latest local source commit. The firmware artifact identity matches the ELF SHA-256 observed in Wokwi, but the application-version metadata discrepancy remains unresolved.

## 7. Engineering Limitations

This test verifies numeric finiteness validation within the development-only firmware self-test environment.

It does not establish sensor-range validation, source authenticity, telemetry serialization, backend integration, alarm behavior, or physical vessel safety.

| Engineering Item | Status |
|---|---|
| Core Quality Self-Test | PASSED |
| Source Mode Self-Test | PASSED |
| Core Measurement Self-Test | PASSED |
| Numeric Finiteness scenarios | PASSED |
| Complete SYS-002 verification | NOT_RUN |
| Complete TEL-001 verification | NOT_RUN |
| Complete TEL-002 verification | NOT_RUN |
| Physical integration | NOT_AUTHORIZED |
| Safety certification | NOT_CLAIMED |

## 8. Conclusion

**Overall result: 28/28 PASSED.**

The updated measurement validation passed the tested rejection cases for NaN and positive/negative infinity, while existing firmware self-tests continued to pass.

This document records operator-provided Wokwi simulation evidence only. It does not constitute operational vessel readiness or safety certification.
