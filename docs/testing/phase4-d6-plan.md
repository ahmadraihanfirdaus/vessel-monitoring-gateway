# Phase 4 Batch D6 — IF-06 Vibration / Acceleration Provider

**Status:** BATCH COMPLETE — development/simulator gate PASS; bench hardware NOT_RUN
**Baseline required:** `develop@a45f37b`
**Phase:** 4 — Bench/Simulator Drivers
**Batch:** D6
**Physical integration:** NOT_AUTHORIZED

## 1. Scope

D6 adds the IF-06 Vibration / Acceleration development provider on top of the
existing Phase 4 provider contract.

The interface follows the architecture register:

- values: `accel_x_g`, `accel_y_g`, `accel_z_g`, and `vibration_index`
- quality: `VALID / INVALID / MISSING / STALE / UNKNOWN`
- monotonic sample timestamp
- non-zero per-provider sequence
- source provenance: `simulation` or `bench_test`
- explicit prototype vibration/acceleration labeling
- explicit statement that the channel is not machinery condition certification

`vibration_index` is a unitless development surrogate. D6 does not define an
engineering vibration severity unit or acceptance threshold.

## 2. Development behavior

For this provider contract:

- `VALID` carries finite acceleration axes and a finite non-negative
  `vibration_index` and is current;
- `STALE` retains those values but is not current;
- `MISSING`, `INVALID`, and `UNKNOWN` carry no numeric values;
- `PHYSICAL` source mode is rejected during Phase 4.

D6 introduces no machinery alarm threshold, bearing/engine diagnosis, FFT
acceptance criterion, or vessel operating limit.

## 3. Bench boundary

The selected ADXL345 breakout remains a **simulation/bench reference**. D6
does not provide or authorize:

- I2C/SPI bus selection, GPIO mapping, address or clock policy
- raw register driver
- real sensor range or data-rate configuration
- axis frame / sign convention for a real vessel
- mounting alignment or structural coupling assumptions
- accelerometer calibration
- filtering, FFT, RMS, envelope or frequency-domain diagnosis
- machinery condition or marine certification
- physical vessel integration

The bench constructor accepts already decoded acceleration/index values from a
future reviewed bench driver. Bench hardware execution remains `NOT_RUN`.

## 4. Deterministic simulation

The software provider exercises a fixed eight-step sequence:

1. near-rest `0 / 0 / 1 g`, index `0.02`, `VALID`
2. signed motion `+0.12 / -0.08 / 1.03 g`, index `0.35`, `VALID`
3. stronger surrogate `-0.25 / +0.20 / 0.92 g`, index `0.80`, `VALID`
4. retained step 3 values, `STALE`
5. `MISSING`
6. `INVALID`
7. `UNKNOWN`
8. recovery `+0.01 / 0 / 1 g`, index `0.05`, `VALID`

These are deterministic development test values only.

## 5. Acceptance gate

Before D6 may be called development/simulator complete:

- legacy host core remains `226/226 PASS`;
- D1 Door/Hatch remains `38/38 PASS`;
- D2 Fuel Vapor remains `53/53 PASS`;
- D3 Bilge remains `47/47 PASS`;
- D4 Temperature remains `67/67 PASS`;
- D5 Attitude remains `54/54 PASS`;
- D6 Vibration provider is `61/61 PASS` on native host test;
- D6 Wokwi parser self-test is `11/11 PASS`;
- PlatformIO ESP-IDF target build succeeds;
- Wokwi merged image is generated;
- actual Wokwi latest boot contains legacy `226/226`, D1 `38/38`, D2 `53/53`,
  D3 `47/47`, D4 `67/67`, D5 `54/54`, D6 `61/61`, timed runtime `6/6`, and
  normal `app_main()` return;
- selected fatal UART markers are absent;
- automated security screen passes;
- both LOCKED requirement files retain baseline SHA-256 values.

Bench hardware, calibration, physical integration and formal SIM/SUP remain
`NOT_RUN`.

## 6. Requirement / phase disposition

D6 provides development evidence for the IF-06 provider boundary only. It does
not edit LOCKED requirements or promote a requirement to formal `VERIFIED`.

After D6, Phase 4 remains `PARTIAL` because IF-07 and physical bench execution
remain pending.
