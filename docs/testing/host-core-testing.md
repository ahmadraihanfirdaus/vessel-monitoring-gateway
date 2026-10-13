# Firmware Core Native Host Regression (Development Only)

**Status:** Test harness introduced in Batch A2; not a certification or system test.

Run from repository root with Python 3 and a native GCC or Clang compiler on PATH:

```bash
python scripts/test_firmware_core_host.py
```

The runner compiles the actual `firmware/src/main.c` and a temporary entry point with strict C11 compiler warnings and executes five current low-level self-test suites. It checks **each individual test line**, rejects malformed or duplicate results, checks five distinct summary counts, and fails with nonzero exit status on bad output. It uses a temporary directory outside the repository and does not change firmware source.

Expected suite counts at the `cad6505` foundation: quality 7; source mode 5; measurement 16; range 21; total 49. Batch B1 adds 30 alarm lifecycle cases, for a current total of 79. These are version-specific expected counts and must be reviewed when the tests intentionally change.

When there is no native compiler, the runner returns code `3` with `BLOCKED/NOT_RUN`; it must not be called PASS. The independent log-parser regressions can still be run with `--parser-only`.

This host runner verifies the current software predicates only. It does **not** test ESP32 hardware, FreeRTOS scheduling, real sensor measurements, calibration, FMEA effectiveness, safety-policy behavior, SIM-001..SIM-015, SUP-001..SUP-019, or backend integration. PlatformIO ESP-IDF build and Wokwi checks remain separate required gates. All test execution evidence must reference the actual source commit and environment.
