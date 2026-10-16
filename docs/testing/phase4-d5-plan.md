# Phase 4 Batch D5 — IF-05 Attitude / Motion Provider

**Status:** BATCH COMPLETE — development/simulator gate PASS; bench hardware NOT_RUN
**Baseline required:** `develop@0df81fd`
**Phase:** 4 — Bench/Simulator Drivers
**Batch:** D5
**Physical integration:** NOT_AUTHORIZED

## 1. Scope

D5 adds the IF-05 Attitude / Motion development provider on top of the existing
Phase 4 provider contract.

The interface follows MOT-001 and the architecture register:

- values: `roll_deg` and `pitch_deg`
- quality: `VALID / INVALID / MISSING / STALE / UNKNOWN`
- monotonic sample timestamp
- non-zero per-provider sequence
- source provenance: `simulation` or `bench_test`
- explicit prototype attitude/motion labeling
- explicit statement that values are not vessel stability certification

## 2. Development behavior

For this provider contract:

- `VALID` carries finite roll and pitch values and is current;
- `STALE` retains finite roll and pitch values but is not current;
- `MISSING`, `INVALID`, and `UNKNOWN` carry no numeric values;
- `PHYSICAL` source mode is rejected during Phase 4.

D5 does not classify stability, safe heel, capsize risk, or operating limits.
No roll/pitch threshold is introduced.

## 3. Bench boundary

The selected MPU-6050 breakout remains a **simulation/bench reference**. D5
does not provide or authorize:

- I2C bus/GPIO mapping
- bus address or clock policy
- raw register driver
- axis frame / sign convention for a real vessel
- mounting alignment
- accelerometer/gyro calibration
- filtering or sensor fusion
- rate/latency acceptance limits
- marine installation
- certified vessel stability assessment

The bench constructor accepts already decoded roll/pitch values from a future
reviewed bench driver. Bench hardware execution remains `NOT_RUN`.

## 4. Deterministic simulation

The software provider exercises a fixed eight-step sequence:

1. `0 / 0 deg / VALID`
2. `+12.5 / -4 deg / VALID`
3. `-8 / +6 deg / VALID`
4. retained `-8 / +6 deg / STALE`
5. `MISSING`
6. `INVALID`
7. `UNKNOWN`
8. recovery to `+1 / -1 deg / VALID`

The values are development test data only and have no vessel stability meaning.

## 5. Acceptance gate

Before D5 may be called development/simulator complete:

- legacy host core remains `226/226 PASS`;
- D1 Door/Hatch remains `38/38 PASS`;
- D2 Fuel Vapor remains `53/53 PASS`;
- D3 Bilge remains `47/47 PASS`;
- D4 Temperature remains `67/67 PASS`;
- D5 Attitude provider is `54/54 PASS` on native host test;
- D5 Wokwi parser self-test is `10/10 PASS`;
- PlatformIO ESP-IDF target build succeeds;
- Wokwi merged image is generated;
- actual Wokwi latest boot contains legacy `226/226`, D1 `38/38`, D2 `53/53`,
  D3 `47/47`, D4 `67/67`, D5 `54/54`, timed runtime `6/6`, and normal
  `app_main()` return;
- selected fatal UART markers are absent;
- automated security screen passes;
- both LOCKED requirement files retain baseline SHA-256 values.

Bench hardware, calibration, physical integration and formal SIM/SUP remain
`NOT_RUN`.

## 6. Requirement / phase disposition

D5 may provide development evidence toward MOT-001, but does not edit LOCKED
requirements or promote MOT-001 to formal `VERIFIED`.

After D5, Phase 4 remains `PARTIAL` because IF-06 through IF-07 and physical
bench execution remain pending.
