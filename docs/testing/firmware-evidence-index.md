# Firmware Development Evidence Index

**Basis:** Existing source snapshot `develop@cad6505` and evidence artifacts committed on 2026-10-10. This file catalogs evidence, not formal SIM/SUP completion.

| Source suite | Latest tests | Evidence | Formal requirement verified? |
|---|---:|---|---|
| Core Quality | 7/7 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |
| Source Mode | 5/5 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |
| Core Measurement | 16/16 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |
| Core Range | 21/21 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |

The latest recorded **49/49 PASS** is one self-test run containing these four suites. Older evidence files are historical revisions; **do not add their counts** to the latest 49. Current firmware entrypoint `firmware/src/main.c` is a development-only test runner, not a continuously operating monitoring loop.

**Locked traceability snapshot:** `requirements/traceability-matrix.csv` intentionally remains unchanged and has `NOT_IMPLEMENTED/NOT_RUN` placeholders for 38 requirement rows. No requirement is declared verified by this index.

**Remaining:** Formal SIM-001..SIM-015 and SUP-001..SUP-019 not executed to completion, along with independent calibration and physical integration testing (not authorized).
