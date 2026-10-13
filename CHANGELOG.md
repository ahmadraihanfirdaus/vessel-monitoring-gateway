# Changelog

This log distinguishes planning/documentation work from verified software behavior. Dates are local engineering record dates, not deployment dates.

## Unreleased — Batch B1 (local alarm model development)

- Introduce an internal alarm lifecycle that keeps acknowledgement separate from condition clearing, with boot-local ID allocation.
- Add C11-compatible alarm state self-tests and a proposed ADR; traceability remains PARTIAL and formal SUP-004 remains NOT_RUN.
- No device alarm outputs, event persistence, certified alert behavior, or hardware integration.

## 2026-10-13 — Batch A2 (verification foundation)

- Add a native host C11 regression runner for the existing 49 development self-tests, with parser negative tests.
- Add a separate 38-row living traceability assessment; do not modify the two LOCKED baseline files.
- Document a preliminary simulation FMEA and a read-only ESP32/Wokwi build-configuration review.
- Formal SIM/SUP execution, calibration, and physical integration remain NOT_RUN / NOT_AUTHORIZED.

## 2026-10-13 — Batch A1 (`develop@2af05ab`)

- Correct documentation that previously described all firmware as unimplemented.
- Permit `.c` and `.h` text source review in the repository security screen.
- Add isolated security-screen regression tests and a current firmware evidence index.
- Preserve the locked system requirements and traceability matrix without edits.

## 2026-10-10 — Firmware Core foundation (`develop@cad6505`)

- Added low-level source-mode, quality, finite-measurement and configurable-range validation.
- Recorded Wokwi firmware self-tests: 49/49 PASS (four suites).
- No operational monitoring loop, formal SIM/SUP verification, sensor calibration or physical integration claimed.
