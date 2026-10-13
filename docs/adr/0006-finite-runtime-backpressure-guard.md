# ADR-0006 — Finite Runtime Failure Guard (Development-Only)

**Status:** PROPOSED / under C4 verification. No vessel system, hardware, network, or safety authorization.

## Context and bounded decision

The six-step C3 demonstration already uses transactional event processing, but its direct polling caller has no single visible terminal state for a full RAM journal or an unexpected time/mode rejection. C4 introduces `core_runtime_guard.h` as a **single-writer, volatile** status layer: RUNNING, COMPLETE, BLOCKED_JOURNAL, STOPPED_ERROR. It does not replace the `core_flow.h` atomic rollback behavior or journal.

- WAIT and PROCESSED increment saturating diagnostic counters; COMPLETE latches and refuses further polls.
- A journal-full attempt latches BLOCKED_JOURNAL. The previously committed scheduler, alarm state, journal, allocator, and script cursor remain unchanged according to C2/C3 semantics. No subsequent automatic retry is allowed by the guard.
- Unexpected runtime rejection/time regression/exhaustion latches STOPPED_ERROR. Rejecting invalid argument pointers does not change state. No automatic reset, alarm acknowledgement, data deletion, or recovery is implemented.
- ESP-IDF's six-step demonstration polls through the guard and prints raw main-task stack high-water-mark before/after for engineering diagnosis. These values are *not* a verified margin, portable unit conversion, or functional safety acceptance level.
- The guard and runtime are **simulation-only** and finite. In particular, a halt is an observable software stop, **not** a physical safe state or local buzzer/LED action.

## Explicit limitations and exit gates

The RAM journal still holds at most eight events, loses contents across restart, and provides no persistence, replay, backend outage tolerance, reboot identity, approved safety policy, or physical-device integration. No automatic clearing of a full journal is permitted by this design. A reviewed store-and-forward and storage/recovery contract is required in future work.

Native C11 226-case regression and target ESP-IDF/Wokwi validation are **separate** gates. The C4 target gate requires a new ELF hash, all 226 tests, a six-step timed run, normal `app_main` return, no panic/reboot and visible stack watermark lines. Formal SIM/SUP remain NOT_RUN; existing locked requirements and traceability mapping are unchanged.
