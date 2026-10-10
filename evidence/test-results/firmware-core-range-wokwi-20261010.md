# Firmware Core Range — Wokwi Test Evidence

## 1. Test Identification

| Field | Value |
|---|---|
| Date | 2026-10-10 |
| Project | Integrated Vessel Monitoring & Diagnostic Gateway |
| Environment | Wokwi ESP32 Simulator |
| Framework | ESP-IDF 6.1.0 |
| Development branch | develop |
| Source HEAD before changes | 1edc41b |
| Build-reported application version | 1edc41b-dirty |
| Test result | PASSED |
| Physical hardware testing | NOT_RUN |

## 2. Test Objective

Verify the development-only configurable numeric measurement range implemented in `firmware/src/core_range.h`.

The `vg_measurement_range_t` structure contains:

- `configured`
- `minimum`
- `maximum`

The `vg_measurement_try_get_in_range()` function must:

- Reject unconfigured or invalid ranges.
- Reject non-finite boundaries.
- Reject a minimum greater than the maximum.
- Validate measurement source, quality, presence, and numeric finiteness using the existing measurement validator.
- Accept values within inclusive minimum and maximum boundaries.
- Leave the output value unchanged when validation fails.

All configured ranges in these tests are synthetic simulation examples, not verified physical sensor limits.

## 3. Core Range Test Results

| Test Case | Result |
|---|---|
| IN_RANGE | PASS |
| MIN_BOUNDARY | PASS |
| MAX_BOUNDARY | PASS |
| NEGATIVE_ALLOWED | PASS |
| BENCH_TEST_IN_RANGE | PASS |
| BELOW_MINIMUM | PASS |
| ABOVE_MAXIMUM | PASS |
| UNCONFIGURED_RANGE | PASS |
| ZERO_INITIALIZED_RANGE | PASS |
| REVERSED_RANGE | PASS |
| NAN_MINIMUM | PASS |
| NAN_MAXIMUM | PASS |
| POSITIVE_INFINITY_MINIMUM | PASS |
| NEGATIVE_INFINITY_MAXIMUM | PASS |
| UNKNOWN_SOURCE | PASS |
| INVALID_QUALITY | PASS |
| MISSING_VALUE | PASS |
| NAN_MEASUREMENT | PASS |
| NULL_MEASUREMENT | PASS |
| NULL_RANGE | PASS |
| NULL_OUTPUT | PASS |

**CORE_RANGE_SELFTEST: PASS (21/21)**

The self-test also checks that failed reads do not modify the output sentinel.

## 4. Regression Test Results

| Test Suite | Result |
|---|---|
| Core Quality Self-Test | PASS (7/7) |
| Source Mode Self-Test | PASS (5/5) |
| Core Measurement Self-Test | PASS (16/16) |
| Core Range Self-Test | PASS (21/21) |
| **Overall** | **PASS (49/49)** |

All 49 scenarios passed in the operator-provided Wokwi terminal output.

## 5. Observed Wokwi Output

    I (169) app_init: App version:      1edc41b-dirty
    I (178) app_init: ELF file SHA256:  623b1212f...
    CORE_QUALITY_SELFTEST: PASS (7/7)
    SOURCE_MODE_SELFTEST: PASS (5/5)
    CORE_MEASUREMENT_SELFTEST: PASS (16/16)
    RANGE_TEST IN_RANGE: PASS
    RANGE_TEST MIN_BOUNDARY: PASS
    RANGE_TEST MAX_BOUNDARY: PASS
    RANGE_TEST ZERO_INITIALIZED_RANGE: PASS
    RANGE_TEST REVERSED_RANGE: PASS
    RANGE_TEST NAN_MINIMUM: PASS
    RANGE_TEST NAN_MAXIMUM: PASS
    RANGE_TEST NULL_RANGE: PASS
    CORE_RANGE_SELFTEST: PASS (21/21)
    I (419) main_task: Returned from app_main()

No panic was visible in the supplied terminal output.

## 6. Firmware Artifact Identification

| Artifact | SHA-256 |
|---|---|
| firmware.elf | 623b1212f33d36aa465c67179d3563910ce0a38ed325f01dd53c227bfcb75540 |
| firmware.bin | d33f4e544864c95bb205e29657b2e0211e93cf4672a75bad9248c4d7d95db8fb |
| firmware.merged.bin | ca9898df18eeb420ed82ce12d393325590eebb678189b6a23be71217a16017e3 |

- PlatformIO clean rebuild result: SUCCESS
- Clean rebuild duration: 86.33 seconds
- Merged image size: 211504 bytes
- Simulation flash configuration: 2 MiB
- Wokwi-reported ELF SHA-256 prefix: 623b1212f

The prior CMake configuration failure was resolved for this build by isolating the previous build directory and performing a fresh build. This does not establish the underlying cause of the earlier failure.

## 7. Design and Requirement Limitations

The Core Range model verifies numeric acceptance against explicitly configured limits.

It does not define or evaluate alarm thresholds, sensor calibration, physical safety conditions, or field-verified operating limits.

| Engineering Item | Status |
|---|---|
| Core Quality Self-Test | PASSED |
| Source Mode Self-Test | PASSED |
| Core Measurement Self-Test | PASSED |
| Core Range Self-Test | PASSED |
| Complete SYS-002 verification | NOT_RUN |
| Complete TEL-001 verification | NOT_RUN |
| Complete TEL-002 verification | NOT_RUN |
| SAF-006 alarm/threshold behavior | NOT_IMPLEMENTED |
| Physical sensor range validation | NOT_RUN |
| Physical integration | NOT_AUTHORIZED |
| Safety certification | NOT_CLAIMED |

## 8. Conclusion

**Overall result: 49/49 PASSED.**

The configurable Core Range validator passed the tested cases for inclusive boundaries, invalid configuration, non-finite limits, invalid measurement metadata, and null pointers.

Existing firmware self-tests continued to pass.

This evidence is limited to development-only Wokwi simulation. It does not establish operational vessel readiness, physical sensor compatibility, or safety certification.
