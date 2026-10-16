# Phase 4 Batch D7 — Development / Simulator Evidence

Date: 2026-10-16

Baseline:
- Branch: develop
- Pre-D7 HEAD: 96e2165
- Scope: IF-07 Power Bench / INA219 provider

Results:
- Legacy host: PASS 226/226
- D1 regression: PASS 38/38
- D2 regression: PASS 53/53
- D3 regression: PASS 47/47
- D4 regression: PASS 67/67
- D5 regression: PASS 54/54
- D6 regression: PASS 61/61
- D7 host: PASS 61/61
- ESP-IDF build: PASS
- Wokwi: PASS
- Timed demo: PASS 6/6
- Stack watermark: 1952 -> 1952
- LOCKED requirements: unchanged

Build SHA-256:
- firmware.elf: 3357cba67247c0b6afd90865b264269880084a994f29bb14fbc368ebe9af5168
- firmware.bin: 716813a5c5dea3f21875dd24b80134fef1f8778342e5d3e2dd8cbf2ea1b04abc
- bootloader.bin: cc26dc8b523649656dbb794945fc40433222b90c27d7497d1880aa5cdc302e42
- partitions.bin: 7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820
- firmware.merged.bin: 3c18770e8d14c3015f5a6c0c6011ef4a9da2619085c9f593e8f7ba12127cf4ca

Bench hardware, calibration, electrical-safety approval, physical integration and formal SIM/SUP: NOT_RUN.
Phase 4 remains PARTIAL.
