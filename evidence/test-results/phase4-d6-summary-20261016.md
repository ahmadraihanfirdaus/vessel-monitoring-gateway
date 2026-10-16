# Phase 4 Batch D6 — Development / Simulator Evidence

Date: 2026-10-16

Baseline:
- Branch: develop
- Pre-D6 HEAD: a45f37b
- Scope: IF-06 Vibration / ADXL345 provider

Results:
- Legacy host: PASS 226/226
- D1 regression: PASS 38/38
- D2 regression: PASS 53/53
- D3 regression: PASS 47/47
- D4 regression: PASS 67/67
- D5 regression: PASS 54/54
- D6 host: PASS 61/61
- ESP-IDF build: PASS
- Wokwi: PASS
- Timed demo: PASS 6/6
- Stack watermark: 1952 -> 1952
- LOCKED requirements: unchanged

Build SHA-256:
- firmware.elf: 0bf920200b2446b75c7e03c90e9b18c65a03dc739310fa9225c794d51444670c
- firmware.bin: dd36274bbd8f5a6fc9245881f42881b2beef3ee6cff25c3b78eb67105796ddb9
- bootloader.bin: da41c5e975d5d9fc0470c0a6e2095844ac4d577db487ee21b649206a7da23aaf
- partitions.bin: 7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820
- firmware.merged.bin: adf891927c1e0c841c83c5864df3588ee5a8502daf1e95979b019e7f10815850

Bench hardware, calibration, frequency analysis, physical integration and formal SIM/SUP: NOT_RUN.
Phase 4 remains PARTIAL.
