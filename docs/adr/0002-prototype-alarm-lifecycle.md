# ADR-0002 — Prototype Alarm Lifecycle (Development Only)

**Status:** PROPOSED — implementation-level decision for simulation/bench development; not a marine interface approval.

## Context

`ALM-001` requires alarm identity, source, priority, state, reason and timestamps. `ALM-002` requires acknowledgement without clearing an active condition. The internal engineering blueprint illustrates `ACTIVE_UNACK`, `ACTIVE_ACK`, `CLEARED`; IEC 62923-1 / IMO BAM is a **concept reference only**, not verified compliance. Local alarm outputs, authenticated commands, event journal, and end-to-end tests are separate outstanding work.

## Decision

- Model `UNKNOWN` (zero-initialized, invalid), `ACTIVE_UNACK`, `ACTIVE_ACK`, `CLEARED`. Acknowledgement is a lifecycle state transition, while `condition_active` remains true until an explicit separate condition-clear operation. This avoids the ambiguity of the earlier unimplemented `ACTIVE` + acknowledged flag proposal.
- An allocator issues monotonically increasing nonzero `uint64_t` IDs, unique **within one allocator instance / boot** when a single allocator is shared. It rejects exhaustion. Global identity across boots requires future `boot_id` pairing and is **not yet implemented**.
- Source identifier, reason code, and priority code are opaque positive integers; definitive priority taxonomy, mappings and event serialisation remain TBD. Simulation and bench source modes are accepted. Unverified physical provenance is rejected here.
- `raised_at`, `acknowledged_at`, `cleared_at` are caller-provided monotonic values in a consistent **single-boot** time domain. Comparisons enforce nondecreasing ordering, but time source, units, event time precision and UTC mapping remain TBD. Zero is a valid timestamp at boot; explicit `has_*` flags distinguish absent timestamps.
- Acknowledge only when `ACTIVE_UNACK`; preserve `condition_active`, `raised_at`, alarm ID, priority, reason and source. Clear only when a separate evaluator has determined that the condition is resolved, and only via `vg_alarm_try_clear_condition`. A cleared instance is not reused/reopened; a newly raised condition requires a new ID.
- Reject invalid pointers, unknown source, zero IDs/codes, inconsistent state metadata, repeated ack/clear, backwards timestamps, and allocator overflow without changing a valid existing record.
- No network, GPIO, physical-vessel, equipment actuation, alarm journal persistence, alarm priority mapping or sensor integration is included in this prototype model.

## Verification boundary

Batch B1 adds host C11 and ESP32-compatible development self-test cases. Their PASS demonstrates only covered state-machine behavior; it does not complete `ALM-001`, `ALM-002` / `SUP-004`, or `ALM-003` formal verification. Formal evidence is gated until integration, timestamps, journal identity, and the actual planned test case are executed and recorded.

## Follow-up

Resolve priority vocabulary, event ID/boot ID contract, clock semantics, retained event journal and alarm output dependencies in later reviewed changes before declaring the complete requirements verified.
