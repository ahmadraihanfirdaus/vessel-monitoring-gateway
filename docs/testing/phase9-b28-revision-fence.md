# Phase 9 Batch 28 — host-only external revision fence

Status: scoped development. Total system: PARTIAL_NOT_PRODUCTION_READY.

## Scope and change

NET-002 / TEL-003 / SYS-003 / SEC-001 / TST-001 / TST-002.

B27 checks two sequential independent quorum observations, but its in-memory
state alone cannot detect a concurrent writer that advanced the externally
stored epoch/revision. B28 adds a **caller-supplied trusted revision** coupled
to both witness-domain guards, accepted_round and current generation/ACK. It
requires exact equality with the independently observed revision *before*
the B27 two-round policy can publish outputs. Success produces a next revision,
next guard, next witness, and restored checkpoint together. On any denial
all four caller outputs stay byte-for-byte unchanged.

Validation: compile `-std=c99 -Wall -Wextra -Werror -pedantic` and exercise
31 cross-process stage/verify modes including stale/future revision, replay,
overflow, wrong device/domain, broken candidate/ticket, split quorum, and
wrong guard source epochs. A successful run also rejects stale guard + new
fence, new guard + stale fence, and old quorum votes after promotion.

## Explicit trust boundary

This module is **NOT a database transaction or storage CAS**. The caller
must independently authenticate and durably serialize the revision/guard
read-compare-write, prevent rollback of both, and bind sources to this device.
Untrusted revision metadata does not prevent replay. No authenticated
witness backend, ESP32 NVS adapter, flash power-interruption test, network
availability test, or production safety certification is provided.

No schema/database modification, push, firmware flash, locked requirement
change, or alteration to existing API semantics.
