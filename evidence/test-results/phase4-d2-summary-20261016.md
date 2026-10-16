# Phase 4 Batch D2 — Development / Simulator Evidence

Date: 2026-10-16

Baseline:
- Branch: develop
- Pre-D2 HEAD: bab5564d69e8a8ef166e01fbe74a7d2c966cda25
- D2 scope: IF-02 Fuel Vapor surrogate provider

## Results

- Legacy host regression: PASS 226/226
- D1 Door/Hatch regression: PASS 38/38
- D2 Fuel Vapor host self-test: PASS 53/53
- D2 Wokwi parser self-test: PASS 7/7
- ESP-IDF target build: PASS
- Wokwi merged artifact: PASS
- Actual Wokwi execution: PASS
- Wokwi legacy self-tests: PASS 226/226
- Wokwi D1 provider self-test: PASS 38/38
- Wokwi D2 provider self-test: PASS 53/53
- Existing timed runtime demo: PASS 6/6
- Main-task stack watermark: 1952 before / 1952 after
- app_main(): returned normally
- LOCKED requirements: unchanged

## Target-build SHA-256

- firmware.elf: 1ab2018857339a679c46a7372d98eb88a7233bfb47b6515b052da99327371d41
- firmware.bin: ae00e888289c13622b320c824e43fc7d00528bff641ca49f790e539018403bb2
- bootloader.bin: a2b12cc6b4f84d4f22a0db21cb31ced0af1615a9c42a5577a96d7f1bff495496
- partitions.bin: 7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820
- firmware.merged.bin: 8469f1a643f791b9ea796300c56367475661c71bd95777fc310a6bcdab2b802f
- firmware.merged.bin bytes: 240656

## Safety / scope limitation

This batch implements only the development/simulator contract for IF-02 Fuel Vapor.

The value field is a surrogate engineering value and is not claimed as calibrated ppm,
%LEL, or any other physical gas concentration.

Missing or invalid provider data is represented as FAULT and is never treated as NORMAL.

The following remain NOT_RUN / pending:
- MQ-2 or other physical gas sensor bench execution
- sensor heater/wiring validation
- ADC and GPIO integration
- calibration
- physical-vessel integration
- formal SIM/SUP verification
- IF-03 through IF-07
- production readiness

Phase 4 remains PARTIAL.

No physical gas-detection, marine-safety, or production-readiness claim is made.

## Evidence preservation note

The retained Wokwi UART evidence was normalized from CRLF to LF only.
Device-emitted trailing whitespace is intentionally preserved.
