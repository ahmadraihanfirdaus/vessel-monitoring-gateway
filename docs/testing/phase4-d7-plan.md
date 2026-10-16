# Phase 4 Batch D7 — IF-07 Power Bench Provider

**Status:** BATCH COMPLETE — development/simulator gate PASS; bench hardware NOT_RUN
**Baseline required:** `develop@96e2165`
**Phase:** 4 — Bench/Simulator Drivers
**Batch:** D7
**Physical integration:** NOT_AUTHORIZED

## 1. Scope

D7 adds the IF-07 low-power electrical development provider on top of the
existing Phase 4 provider contract.

The interface follows the architecture register:

- values: `voltage_v`, `current_a`, and `power_w`
- quality: `VALID / INVALID / MISSING / STALE / UNKNOWN`
- monotonic sample timestamp
- non-zero per-provider sequence
- source provenance: `simulation` or `bench_test`
- explicit low-power bench labeling
- explicit statement that this is not vessel electrical safety certification

INA219 remains a simulation/controlled-bench reference only.

## 2. Development behavior

For this provider contract:

- `VALID` carries finite voltage/current/power and is current;
- `STALE` retains finite values but is not current;
- voltage must not be negative;
- signed current and signed power are allowed as development direction values;
- `MISSING`, `INVALID`, and `UNKNOWN` carry no numeric values;
- `PHYSICAL` source mode is rejected during Phase 4.

D7 defines no vessel operating voltage, current limit, fuse rating, conductor
size, shunt rating, isolation requirement, trip threshold, or safety limit.

## 3. Bench boundary

The selected INA219 module remains a **safe low-power simulation/bench
reference**. D7 does not provide or authorize:

- I2C address, GPIO, bus speed, or wiring policy
- raw INA219 register driver
- shunt resistor selection or calibration
- high-voltage or high-current operation
- galvanic isolation or protective-device design
- battery, alternator, starter, shore-power, or propulsion-bus integration
- energy/coulomb accounting
- electrical safety certification
- physical vessel integration

The bench constructor accepts already decoded voltage/current/power from a
future reviewed bench driver. Bench hardware execution remains `NOT_RUN`.

## 4. Deterministic simulation

The software provider exercises a fixed eight-step sequence:

1. `5.0 V / +0.10 A / +0.50 W`, `VALID`
2. `12.0 V / +0.25 A / +3.00 W`, `VALID`
3. `12.0 V / -0.05 A / -0.60 W`, `VALID`
4. retained step 3 values, `STALE`
5. `MISSING`
6. `INVALID`
7. `UNKNOWN`
8. recovery `5.0 V / +0.05 A / +0.25 W`, `VALID`

These are deterministic low-power development test values only.

## 5. Acceptance gate

Before D7 may be called development/simulator complete:

- legacy host core remains `226/226 PASS`;
- D1 Door/Hatch remains `38/38 PASS`;
- D2 Fuel Vapor remains `53/53 PASS`;
- D3 Bilge remains `47/47 PASS`;
- D4 Temperature remains `67/67 PASS`;
- D5 Attitude remains `54/54 PASS`;
- D6 Vibration remains `61/61 PASS`;
- D7 Power provider is `61/61 PASS` on native host test;
- D7 Wokwi parser self-test is `12/12 PASS`;
- PlatformIO ESP-IDF target build succeeds;
- Wokwi merged image is generated;
- actual Wokwi latest boot contains legacy `226/226`, D1 `38/38`, D2 `53/53`,
  D3 `47/47`, D4 `67/67`, D5 `54/54`, D6 `61/61`, D7 `61/61`, timed
  runtime `6/6`, and normal `app_main()` return;
- selected fatal UART markers are absent;
- automated security screen passes;
- both LOCKED requirement files retain baseline SHA-256.

Passing this gate does **not** imply INA219 hardware verification, calibration,
electrical safety approval, formal SIM/SUP verification, physical integration,
or production readiness.
