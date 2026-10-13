# ADR-0004 — Transactional Simulated Core Event Flow

**Status:** PROPOSED development implementation; not a vessel interface contract or deployment authorization.

## Scope and decision

Batch C2 adds `core_flow.h`, a deterministic single-channel orchestrator for **caller-injected**
`simulation` and `bench_test` measurements. It combines the existing cooperative due-time
arithmetic, diagnostic quality classification, local alarm lifecycle, and bounded RAM event
journal. All calls are synchronous, single-writer, and use caller-supplied monotonic milliseconds.
There is **no running ESP-IDF task**, sensor driver, watchdog, GPIO, buzzer, NVS, network
operation, cross-thread locking, or actual sampled input. The caller supplies opaque nonzero
**demo-only** alarm priority and reason codes; neither represents an approved marine threshold.

A due-time sample classified `FAULT_STARTED` raises an `ACTIVE_UNACK` alarm and writes
`ALARM_RAISED`. A sample classified `FAULT_CONTINUING` does not produce duplicate events.
An explicit acknowledgement creates `ALARM_ACK` but does not clear the condition. A subsequent
valid diagnostic recovery clears the condition and writes `ALARM_CLEARED`; a later fault obtains
a new boot-local alarm identifier. Each alarm transition must be journaled or it is refused.

A transition that cannot be journaled leaves scheduler, diagnostic, alarm, ID allocator,
and journal unchanged. The caller receives `VG_FLOW_JOURNAL_FULL` when relevant; retrying
will not consume an ID. A WAIT updates scheduler timing state only and does not process
measurement data. Events are **volatile** and limited to eight entries. A full journal
also blocks subsequent event-producing state transitions; the higher-level design needs
an approved backpressure/persistence policy before any operational claim.

## Remaining limitations and engineering gates

- The alarm record retains only the newest alarm, not durable alarm history.
- IDs are unique only within each local allocator/boot. No device-wide deduplication key exists.
- The time domain is simulated monotonic uptime, not authoritative wall time or UTC.
- Neither source authentication nor physical integration is implemented; `physical` is refused.
- Critical events are **not** guaranteed to survive power loss, reboot, or capacity exhaustion.
- Runtime scheduling, sampling, alarm outputs, backend-offline independence and associated
  formal `SIM`/`SUP` requirements remain `NOT_RUN`.
- This does not complete `ALM-001..003`, `SYS-003`, `NET-001..002`, or a safety-policy engine.

Quality gates: independent host C11 regression, ESP-IDF target build, and Wokwi console
checks are recorded separately. Do not modify LOCKED requirements or claim certification.
