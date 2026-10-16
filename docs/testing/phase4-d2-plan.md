# Phase 4 Batch D2 — IF-02 Fuel Vapor Surrogate Provider

**Status:** BATCH COMPLETE — development/simulator gate PASS; bench hardware NOT_RUN
**Baseline required:** `develop@bab5564`
**Phase:** 4 — Bench/Simulator Drivers
**Batch:** D2
**Physical integration:** NOT_AUTHORIZED

## 1. Scope

D2 adds the IF-02 Fuel Vapor development provider on top of the D1 common
provider contract. The implementation is limited to software simulation and an
already-interpreted `bench_test` constructor.

The interface contract follows the existing architecture register:

- state: `NORMAL / WARNING / ALARM / FAULT / UNKNOWN`
- optional finite surrogate value
- explicit quality
- monotonic sample timestamp
- non-zero per-provider sequence
- source provenance: `simulation` or `bench_test`

The surrogate value is intentionally unitless and has no ppm, %LEL,
concentration, calibration, or marine-safety meaning.

## 2. SAF-004 development behavior

For this provider contract:

- `VALID` and `STALE` carry an operational state (`NORMAL`, `WARNING`, or
  `ALARM`) plus a finite surrogate value.
- `MISSING` and `INVALID` map to `FAULT` with no numeric value.
- `UNKNOWN` quality maps to `UNKNOWN` with no numeric value.
- Missing/invalid data therefore cannot be represented as a safe `NORMAL`
  sample.
- `PHYSICAL` source mode is rejected during Phase 4.

This is channel-contract behavior only. It does not implement Phase 5 virtual
start rejection, local alarm output, or formal SIM-003/SIM-004 verification.

## 3. Bench boundary

The selected MQ-2 reference remains a **bench-only surrogate**. D2 does not
provide or authorize:

- GPIO/ADC pin mapping
- 5 V heater or loop wiring
- signal conditioning or voltage protection
- raw ADC acquisition
- threshold derivation
- calibration curves
- gas-specific conversion
- ppm or %LEL claims
- certified fuel-vapor detection
- physical vessel connection

The bench constructor accepts a state/value already interpreted by a future
reviewed bench driver. Bench hardware execution remains `NOT_RUN`.

## 4. Deterministic simulation

The software provider exercises a fixed sequence containing:

1. `NORMAL / VALID`
2. `WARNING / VALID`
3. `ALARM / VALID`
4. `FAULT / MISSING`
5. `FAULT / INVALID`
6. `UNKNOWN / UNKNOWN`
7. retained `WARNING / STALE`
8. recovery to `NORMAL / VALID`

This sequence is development test data only and does not establish alarm
thresholds or safe-atmosphere criteria.

## 5. Acceptance gate

Before D2 may be called development/simulator complete:

- legacy host core remains `226/226 PASS`;
- D1 Door/Hatch remains `38/38 PASS`;
- D2 Fuel Vapor provider is `53/53 PASS` on the native host test;
- D2 Wokwi log parser self-test is `7/7 PASS`;
- PlatformIO ESP-IDF target build succeeds;
- actual Wokwi latest boot contains legacy `226/226`, D1 `38/38`, D2 `53/53`,
  timed runtime `6/6`, and normal `app_main()` return;
- selected fatal UART markers are absent;
- automated security screen passes;
- both LOCKED requirement files retain their baseline SHA-256 values.

Bench hardware, calibration, physical integration, and formal SIM/SUP remain
`NOT_RUN` and are not implied by this gate.

## 6. Requirement / phase disposition

D2 may provide development evidence toward SAF-004, but it does not edit the
LOCKED requirement or traceability files and does not promote an original
requirement to formal `VERIFIED`.

After D2, Phase 4 remains `PARTIAL` because IF-03 through IF-07 and physical
bench execution remain pending.

## Execution evidence — 2026-10-16

Batch D2 development/simulator acceptance completed successfully.

- Legacy host regression: 226/226 PASS.
- D1 Door/Hatch regression: 38/38 PASS.
- D2 Fuel Vapor host provider suite: 53/53 PASS.
- ESP-IDF target build: PASS.
- Wokwi merged artifact generated successfully.
- Actual Wokwi boot: PASS.
- Wokwi D2 provider suite: 53/53 PASS.
- Timed runtime demonstration: 6/6 PASS.
- Main-task stack watermark: 1952 before and after.
- LOCKED requirement files remained unchanged.

Evidence:
- `evidence/test-results/phase4-d2-summary-20261016.md`
- `evidence/test-results/phase4-d2-host-regression-20261016.txt`
- `evidence/test-results/phase4-d2-host-20261016.txt`
- `evidence/test-results/phase4-d2-wokwi-verifier-20261016.txt`
- `evidence/logs/phase4-d2-wokwi-serial-20261016.txt`

MQ-2 bench hardware, calibration, physical integration and formal SIM/SUP remain NOT_RUN.
Phase 4 remains PARTIAL.
