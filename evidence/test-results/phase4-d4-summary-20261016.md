# Phase 4 Batch D4 — Development / Simulator Evidence

Date: 2026-10-16

Baseline:
- Branch: develop
- Pre-D4 HEAD: 70581ac
- Scope: IF-04 Temperature / DS18B20 provider

Results:
- Legacy host: PASS 226/226
- D1 regression: PASS 38/38
- D2 regression: PASS 53/53
- D3 regression: PASS 47/47
- D4 host: PASS 67/67
- ESP-IDF build: PASS
- Wokwi: PASS
- Timed demo: PASS 6/6
- Stack watermark: 1952 -> 1952
- LOCKED requirements: unchanged

Build SHA-256:
- firmware.elf: bce2ed364e13a2d27a7ccb7a5d338eef53954c6388f4e38f587d9ba1de263286
- firmware.bin: 8c1594cd91269f31491b39ecda8dbfc8ad3ce23680ebdb9fe28cfe2b2388d1d0
- bootloader.bin: 768ec61fdca7043b9009839b665a7cccc82ddc64ad17a1a3f55e7e4369453662
- partitions.bin: 7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820
- firmware.merged.bin: 5acd4ae8fba9e081408a1f9b560de9cee56d9d0cf505a42198833b45f5473714

Bench hardware, calibration, physical integration and formal SIM/SUP: NOT_RUN.
Phase 4 remains PARTIAL.
