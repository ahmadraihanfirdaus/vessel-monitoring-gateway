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

## Additional evidence after the original foundation

- Alarm lifecycle: [Batch B1 Wokwi 79/79](../../evidence/test-results/firmware-core-alarm-wokwi-20261013.md); includes the original four suites and 30 alarm cases.
- Pure scheduler, diagnostics, bounded RAM journal: [Batch C1 Wokwi 133/133](../../evidence/test-results/firmware-core-c1-wokwi-20261013.md), with [full latest-boot UART](../../evidence/logs/firmware-core-c1-wokwi-serial-20261013.txt). Includes earlier suites and 54 C1 cases.
- Integrated simulated scheduler/diagnostics/alarm/journal flow: [Batch C2 Wokwi 169/169](../../evidence/test-results/firmware-core-c2-wokwi-20261013.md), with [operator-reported latest-boot UART](../../evidence/logs/firmware-core-c2-wokwi-serial-20261013.txt). Includes the prior 133 suites cases and 36 orchestrator cases; formal SIM/SUP NOT_RUN.

- Finite ESP-IDF runtime with synthetic source: [Batch C3 Wokwi 201/201 and timed demonstration 6/6](../../evidence/test-results/firmware-core-c3-wokwi-20261013.md), with [successful latest-boot UART](../../evidence/logs/firmware-core-c3-wokwi-serial-20261013.txt); earlier stack overflow build is excluded from passing evidence. Runtime is bounded, journal remains volatile, and formal SIM/SUP NOT_RUN.

Recorded counts are cumulative software self-tests on a single build, **not additive across historical runs**. The index and living traceability do not approve or complete formal SIM/SUP tests, hardware calibration, persistence, or operational sampling.

## Development evidence — Batch C4

- [Batch C4 Wokwi 226/226 self-tests, timed demo 6/6, and stack watermark](../../evidence/test-results/firmware-core-c4-wokwi-20261013.md), with [archived operator UART](../../evidence/logs/firmware-core-c4-wokwi-serial-20261013.txt) (LF-normalized for Git).
- The passing hotfix build showed 1952-byte main-task stack high-water mark (pre-hotfix 256 bytes); finite test only, no approved minimum for production.
- Formal SIM/SUP, continuous monitoring, persistent journal, physical hardware and system safety approvals remain NOT_RUN/NOT_IMPLEMENTED.
