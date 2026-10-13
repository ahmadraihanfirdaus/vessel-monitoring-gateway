# ADR-0003 — Pure Firmware Core Scheduling, Diagnostics, Volatile Journal

**Status:** PROPOSED (development implementation); no physical or interface approval.

## Decision and boundaries

- The cooperative scheduler performs **due-time calculations only** with caller-supplied monotonic milliseconds. It never samples hardware, blocks, sleeps, schedules callbacks or controls a buzzer. Late intervals are coalesced; skipped periods are explicitly reported. Clock regressions are rejected; integer overflow ends the schedule in an explicit EXHAUSTED state.
- The single-channel diagnostic classifier distinguishes HEALTHY, FAULT, and RECOVERED from numeric measurement validity. Unknown, missing, stale, or non-finite readings trigger FAULT. It rejects unverified physical source mode, source-mode change in one channel, and backwards time. It does **not** implement data-age timeout, authenticated provenance, specific sensor quality models, an actual fault manager, or a policy for escalating to alarms.
- A bounded 8-entry **RAM-only** journal keeps accepted events in insertion order with nonzero per-instance IDs. It **refuses** inserts when full and counts those rejected; it never silently overwrites existing events. No event is guaranteed to survive reset/power loss and no online/offline transport/replay logic exists. Real event IDs across boots, critical-event prioritization, backpressure mitigation, and NVS wear/persistence require separate design.
- Event reason/severity mapping, global timestamps/UTC, journal-alarm integration, physical buses, and security controls remain unresolved. Existing ALM IDs are not globally unique; their mapping into journal events is only an opaque link.

## Verification gates

Native C11 self-tests are development evidence. ESP-IDF build and Wokwi execution must be recorded independently. Neither completes `SYS-003`, `NET-002`, `ALM-001`, `ALM-003`, or other formal SIM/SUP acceptance criteria. Source-mode `physical` remains future-only. Requirements and traceability baseline remain LOCKED.
