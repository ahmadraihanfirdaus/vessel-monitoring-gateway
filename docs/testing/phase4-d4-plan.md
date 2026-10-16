# Phase 4 Batch D4 — IF-04 Compartment Temperature Provider

**Status:** BATCH COMPLETE — development/simulator gate PASS; bench hardware NOT_RUN
**Baseline required:** `develop@70581ac`
**Phase:** 4 — Bench/Simulator Drivers
**Batch:** D4
**Physical integration:** NOT_AUTHORIZED

## 1. Scope

D4 adds the IF-04 Compartment Temperature development provider on top of the
existing Phase 4 provider contract.

The interface follows SAF-006 and the architecture register:

- value: `temperature_c`
- quality: `VALID / INVALID / MISSING / STALE / UNKNOWN`
- monotonic sample timestamp
- non-zero per-provider sequence
- source provenance: `simulation` or `bench_test`
- configurable development/demo high-temperature thresholds

## 2. Development behavior

For this provider contract:

- `VALID` carries a finite Celsius value and is current;
- `STALE` retains a finite Celsius value but is not current;
- `MISSING`, `INVALID`, and `UNKNOWN` carry no numeric value;
- `PHYSICAL` source mode is rejected during Phase 4.

The configurable thresholds produce only development/demo evaluation bands:
`BELOW_WARNING`, `WARNING`, or `ALARM`. Non-current samples are explicitly
reported as not current. These thresholds are not vessel safety limits and do
not implement Phase 5 safety actions.

## 3. Bench boundary

The selected DS18B20 remains a **bench-only reference**. D4 does not provide or
authorize:

- GPIO pin mapping
- 1-Wire bus driver
- pull-up resistor or supply design
- parasite-power design
- ROM/device discovery policy
- CRC handling
- conversion-resolution/timing policy
- probe enclosure or marine placement
- calibration or installed accuracy claim
- physical vessel connection

The bench constructor accepts an already decoded Celsius value from a future
reviewed bench driver. Bench hardware execution remains `NOT_RUN`.

## 4. Deterministic simulation

The software provider exercises a fixed sequence using demo thresholds
`warning_high_c=40` and `alarm_high_c=60`:

1. `25 C / VALID` -> below warning
2. `45 C / VALID` -> warning
3. `65 C / VALID` -> alarm
4. retained `65 C / STALE` -> not current
5. `MISSING` -> no value
6. `INVALID` -> no value
7. `UNKNOWN` -> no value
8. recovery to `30 C / VALID` -> below warning

The values and thresholds are development test data only.

## 5. Acceptance gate

Before D4 may be called development/simulator complete:

- legacy host core remains `226/226 PASS`;
- D1 Door/Hatch remains `38/38 PASS`;
- D2 Fuel Vapor remains `53/53 PASS`;
- D3 Bilge remains `47/47 PASS`;
- D4 Temperature provider is `67/67 PASS` on native host test;
- D4 Wokwi parser self-test is `9/9 PASS`;
- PlatformIO ESP-IDF target build succeeds;
- Wokwi merged image is generated;
- actual Wokwi latest boot contains legacy `226/226`, D1 `38/38`, D2 `53/53`,
  D3 `47/47`, D4 `67/67`, timed runtime `6/6`, and normal `app_main()` return;
- selected fatal UART markers are absent;
- automated security screen passes;
- both LOCKED requirement files retain baseline SHA-256 values.

Bench hardware, calibration, physical integration and formal SIM/SUP remain
`NOT_RUN`.

## 6. Requirement / phase disposition

D4 may provide development evidence toward SAF-006, but does not edit LOCKED
requirements or promote SAF-006 to formal `VERIFIED`.

After D4, Phase 4 remains `PARTIAL` because IF-05 through IF-07 and physical
bench execution remain pending.
