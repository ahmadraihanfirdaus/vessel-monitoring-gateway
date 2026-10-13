# Changelog

This log distinguishes planning/documentation work from verified software behavior. Dates are local engineering record dates, not deployment dates.

## Unreleased — Batch A1 (pre-commit review)

- Correct documentation that previously described all firmware as unimplemented.
- Permit `.c` and `.h` text source review in the repository security screen.
- Add isolated security-screen regression tests and a current firmware evidence index.
- Preserve the locked system requirements and traceability matrix without edits.

## 2026-10-10 — Firmware Core foundation (`develop@cad6505`)

- Added low-level source-mode, quality, finite-measurement and configurable-range validation.
- Recorded Wokwi firmware self-tests: 49/49 PASS (four suites).
- No operational monitoring loop, formal SIM/SUP verification, sensor calibration or physical integration claimed.
