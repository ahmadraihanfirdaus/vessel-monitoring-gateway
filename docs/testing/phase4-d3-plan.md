# Phase 4 Batch D3 — IF-03 Bilge / High-Water Provider

**Status:** BATCH COMPLETE — development/simulator gate PASS; bench hardware NOT_RUN
**Baseline required:** `develop@cd7ee6f`
**Phase:** 4 — Bench/Simulator Drivers
**Batch:** D3
**Physical integration:** NOT_AUTHORIZED

## 1. Scope

D3 adds the IF-03 Bilge / High-Water development provider on top of the existing
Phase 4 provider contract.

The interface follows SAF-005 and the architecture register:

- state: `NORMAL / HIGH / FAULT / UNKNOWN`
- explicit quality
- monotonic sample timestamp
- non-zero per-provider sequence
- source provenance: `simulation` or `bench_test`

No water depth or calibrated level value is introduced.

## 2. Development behavior

For this provider contract:

- `VALID` and `STALE` carry operational state `NORMAL` or `HIGH`;
- `MISSING` and `INVALID` map to `FAULT`;
- `UNKNOWN` quality maps to `UNKNOWN`;
- `PHYSICAL` source mode is rejected during Phase 4.

This is a channel/provider contract only. It does not implement Phase 5 safety
action policy or formal SIM-005 verification.

## 3. Bench boundary

The selected Adafruit Water Detection 4965 reference remains a **bench-only
wet/dry surrogate**. D3 does not provide or authorize:

- GPIO pin mapping
- sensor supply or electrical protection design
- debounce/filter timing
- raw digital acquisition
- calibrated water depth
- marine-rated bilge sensor claim
- physical vessel connection

The bench constructor accepts an already interpreted state from a future
reviewed bench driver. Bench hardware execution remains `NOT_RUN`.

## 4. Deterministic simulation

The software provider exercises a fixed sequence:

1. `NORMAL / VALID`
2. `HIGH / VALID`
3. retained `HIGH / STALE`
4. `FAULT / MISSING`
5. `FAULT / INVALID`
6. `UNKNOWN / UNKNOWN`
7. recovery to `NORMAL / VALID`

The sequence is development test data only.

## 5. Acceptance gate

Before D3 may be called development/simulator complete:

- legacy host core remains `226/226 PASS`;
- D1 Door/Hatch remains `38/38 PASS`;
- D2 Fuel Vapor remains `53/53 PASS`;
- D3 Bilge provider is `47/47 PASS` on native host test;
- D3 Wokwi parser self-test is `8/8 PASS`;
- PlatformIO ESP-IDF target build succeeds;
- Wokwi merged image is generated;
- actual Wokwi latest boot contains legacy `226/226`, D1 `38/38`, D2 `53/53`,
  D3 `47/47`, timed runtime `6/6`, and normal `app_main()` return;
- selected fatal UART markers are absent;
- automated security screen passes;
- both LOCKED requirement files retain baseline SHA-256 values.

Bench hardware, calibration, physical integration and formal SIM/SUP remain
`NOT_RUN`.

## 6. Requirement / phase disposition

D3 may provide development evidence toward SAF-005, but does not edit LOCKED
requirements or promote SAF-005 to formal `VERIFIED`.

After D3, Phase 4 remains `PARTIAL` because IF-04 through IF-07 and physical
bench execution remain pending.
