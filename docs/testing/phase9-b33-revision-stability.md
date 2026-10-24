# Phase 9 B33 — Revision stability across host checkpoint validation

The trusted revision probe is called **twice**: before B32/B30 validation and after all proposal results are staged privately. The same external revision must be returned both times and match the expected CAS revision. Four immutable input regions are snapshotted and compared after each callback. Validation operates on private snapshots and only writes caller outputs after the second probe has succeeded. All four output regions remain pairwise disjoint and independent of the four inputs.

**Fail-closed test matrix:** 30 C99 two-process cases, one accepted and 29 denied (failed/stale first or second revision, input mutation during either probe, missing external receipts, malformed/aliased controls, null probes). On denial, B33 does not modify publication output; a deliberately untrusted mutation callback may itself alter the caller-owned *input*, which is explicitly outside B33's no-write guarantee.

**Formal boundary:** a callback is not an authenticated persistent revision witness, CAS transaction, synchronization primitive, linearizable output publisher, or ESP32/NVS flash durability proof. For concurrent code, calling adapter must synchronize access. All LOCKED requirements unchanged, no DB, no hardware, formal open, total PARTIAL_NOT_PRODUCTION_READY.
