# Phase 4 Batch D1 — Development / Simulator Evidence

Date: 2026-10-16

Baseline:
- Branch: develop
- Pre-D1 HEAD: 6069f894ef95
- D1 scope: common provider contract + IF-01 Door/Hatch

## Results

- Legacy host regression: PASS 226/226
- D1 Door/Hatch host self-test: PASS 38/38
- D1 Wokwi parser self-test: PASS 6/6
- ESP-IDF target build: PASS
- Actual Wokwi execution: PASS
- Wokwi legacy self-tests: PASS 226/226
- Wokwi D1 provider self-test: PASS 38/38
- Existing timed runtime demo: PASS 6/6
- Main-task stack watermark: 1952 before / 1952 after
- app_main(): returned normally
- LOCKED requirements: unchanged
- Automated security scan: PASS, 0 findings

## Target-build SHA-256

- firmware.elf: bb09072172649a406415e656ae8703097ac1cfb0cf5de2cb07177b2f6ad5023f
- firmware.bin: 78a19e4e2d4cd24dafae3e6862d0bde951e2eba008574cd5dbe39b760360de57
- bootloader.bin: 9d5bd503e4560c05fbeb65975bce06f6fe43fa3639a0a8cf9f3904545eb2990a
- partitions.bin: 7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820

## Evidence files

- `evidence/logs/phase4-d1-wokwi-serial-20261016.txt`
- `evidence/test-results/phase4-d1-host-regression-20261016.txt`
- `evidence/test-results/phase4-d1-host-20261016.txt`
- `evidence/test-results/phase4-d1-wokwi-verifier-20261016.txt`
- `evidence/test-results/phase4-d1-sha256-20261016.txt`

## Scope limitation

This evidence closes only the Phase 4 Batch D1 development/simulator checkpoint.

The following remain NOT_RUN / pending:
- bench hardware execution
- physical sensor integration
- wiring and GPIO authorization
- calibration
- formal SIM/SUP verification
- IF-02 through IF-07
- production readiness

Phase 4 therefore remains PARTIAL.

No production-readiness, physical-vessel, or formal verification claim is made.

## Evidence preservation note

The retained Wokwi UART evidence was normalized from CRLF to LF only.
Device-emitted trailing whitespace is intentionally preserved. Generic staged
whitespace validation therefore excludes only the raw UART evidence file.
