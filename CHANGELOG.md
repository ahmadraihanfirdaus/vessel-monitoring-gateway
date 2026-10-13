# Changelog

This log distinguishes planning/documentation work from verified software behavior. Dates are local engineering record dates, not deployment dates.

## 2026-10-13 — Batch C4 (finite runtime guard; development Wokwi verified)

- Add a simulation-only, fail-stop supervisory guard for the existing finite six-sample runtime. Explicitly latch `JOURNAL_FULL` and unexpected runtime errors; never auto-retry, drop event evidence, acknowledge alarms or silently advance the scripted cursor.
- Add 25 pure C11 guard self-tests to the previous 201 cases (**226 expected**); integrate guard into the ESP-IDF timed demonstration and report raw main-task stack watermark before and after the demo.
- Native C11 and ESP-IDF/Wokwi developer self-tests **226/226 PASS**; finite timed demonstration **6/6 PASS** on the matching ELF. Initial main-task stack high-water mark was **256 bytes**; after moving four test-only flow workspaces to static storage, the new Wokwi build reported **1952 bytes** before/after the finite demo and returned normally. This is not an approved production stack threshold or stress test. Hardware, persistence, operational resilience, safety-control and formal SIM/SUP remain NOT_RUN.

## 2026-10-13 — Batch C3 (bounded synthetic runtime, Wokwi development verified)

- Add finite scripted SIMULATION-only source fed into C2 flow with timed due-time processing, fault/recovery journal event checks, and explicit fail/hold behavior.
- Add 32 self-tests and an ESP-IDF-only six-step demonstration driven by `esp_timer_get_time()` with cooperative FreeRTOS waiting.
- Native C11 and ESP-IDF/Wokwi development self-tests **201/201 PASS**, plus a separate six-step timed demonstration **6/6 PASS**. An initial Wokwi build reset from an ESP-IDF main-task stack overflow; relocating C3 test workspaces to static storage resolved the observed failure on the new build. This does not prove indefinite operation, thread safety, real sensors, persistent journal, auto-acknowledgement, or approved safety thresholds. Formal SIM/SUP remains NOT_RUN.

## 2026-10-13 — Batch C2 (integrated simulated core, development self-tested)

- Add transactional orchestration of caller-injected simulated/bench measurements through scheduler, diagnostics, alarm transitions, and volatile event journal.
- Add 36 deterministic C11 integrated self-tests, including backpressure and rollback checks.
- Native GCC and ESP-IDF/Wokwi firmware self-tests are **169/169 PASS** with C2 evidence; formal SIM/SUP remains NOT_RUN, and operational loop and journal persistence remain out of scope.

## 2026-10-13 — Batch C1 (pure core models, under verification)

- Add C11 cooperative due-time arithmetic, numeric-channel health transitions and a fixed-capacity **volatile** event journal with overflow reporting.
- Add native host self-tests and record separate ESP-IDF/Wokwi execution (133/133 PASS; see C1 evidence). Formal SIM/SUP requirements remain NOT_RUN.
- This does not implement running sampling, I/O, persistent offline storage, actual alarm journal integration, physical sensors, or the complete SYS-003/NET-002 requirements.

## 2026-10-13 — Batch B1 (local alarm model development)

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
