# Phase 4 Batch D5 — Development / Simulator Evidence

Date: 2026-10-16

Baseline:
- Branch: develop
- Pre-D5 HEAD: 0df81fd
- Scope: IF-05 Attitude / MPU-6050 provider

Results:
- Legacy host: PASS 226/226
- D1 regression: PASS 38/38
- D2 regression: PASS 53/53
- D3 regression: PASS 47/47
- D4 regression: PASS 67/67
- D5 host: PASS 54/54
- ESP-IDF build: PASS
- Wokwi: PASS
- Timed demo: PASS 6/6
- Stack watermark: 1952 -> 1952
- LOCKED requirements: unchanged

Build SHA-256:
- firmware.elf: 120d1d638c0aed803ac11fda01474b036a8564bb82cafb90b645d713b5c10a01
- firmware.bin: cef4a15aaf5352604e889dd1250ab70c1e58f957563db6eee9fdb5cd2f6cf0d7
- bootloader.bin: e060059816301e22279f0a366ac169453c8aab19c456a3f680fdcfe91f1085a5
- partitions.bin: 7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820
- firmware.merged.bin: df947d9769339adda70705a3f6ae4c56aceaae10ffb4be4e83e6734bdf3415c7

Bench hardware, calibration, stability assessment, physical integration and formal SIM/SUP: NOT_RUN.
Phase 4 remains PARTIAL.
