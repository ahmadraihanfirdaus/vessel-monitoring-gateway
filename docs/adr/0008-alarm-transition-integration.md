# ADR-0008 — Complete alarm transition metadata

Status: accepted for scoped local software implementation; mandatory local gates and exact staged review documented in the alarm metadata evidence summary. External/formal approval remains open.
Continuation baseline: `5048525e1ff4cfad367dc31bfc42c7aa79fb393e` on `develop`.

ALM-001 requires identity, source, priority, state, reason and lifecycle times.
These exist in the native alarm model, while the active event wire/storage path
retains only a link to an alarm. Complete the actual path without reconstructing
historical metadata from a later mutable alarm record.

## Seven related scopes

1. Capture immutable full alarm snapshots at retained journal transitions;
   validate event/alarm identity, source, state and action-time correspondence.
2. Integrate that bounded metadata ledger into the continuous coordinator,
   preserving observation progress, full-journal refusal and ACK-not-CLEAR.
3. Add a versioned persistent representation and worker submission that retain
   complete metadata, read existing snapshots explicitly as metadata unavailable,
   and never silently downgrade or invent missing historical fields.
4. Add event schema 1.1 with strict raw-object/uint64/lifecycle checks and reuse
   existing JSON inspection primitives. Keep 1.0 and its wire fixtures unchanged.
5. Store metadata through a Laravel migration, exact dedup/conflict comparison,
   device read API and escaped event-fact presentation. Legacy rows remain
   explicitly incomplete; receipt order does not infer global active state.
6. Verify an exact empty prior test schema before an explicit migration upgrade,
   then apply/rollback/reapply and full real PHP 8.2.35/MariaDB/HTTP integration.
7. Preserve native/SDK/CI/security gates, fault injection, traceability/evidence,
   LOCKED/protected files and metadata-only cleanup audit.

## Compatibility and safety

Alarm identity is the device/boot/alarm-ID tuple; event identity remains the
device/boot/event-ID tuple. Codes remain opaque development values, not an
approved marine taxonomy. Times are uint64 boot-relative milliseconds, not UTC.
Unacknowledged/uncleared times are null, including when a genuine timestamp zero
is present. ACK does not clear a live condition. Changed reasons can produce a
new alarm identity; an old retained transition must stay immutable.

The journal capacity remains eight with explicit rejection. Metadata does not
authorize eviction, automatic ACK, durable replay/deletion or physical control.
Legacy snapshots must remain readable with an explicit unavailable-metadata
state, and new metadata must not disappear through an old submission interface.
No NVS erase, physical provisioning, deployed TLS or hardware verification is
granted. Formal SIM/SUP results remain unchanged; system stays PARTIAL.

## Persistent byte budget

Unchanged VGS1 records remain at most 4,862 bytes and use the existing exact
encoding when metadata is absent. VGS2 adds a one-byte presence flag and at
most 34 metadata bytes per event: maximum 5,142 bytes for eight events and a
4,096-byte latest packet with maximum identity lengths. Its bounded working
buffer is 5,184 bytes (64 bytes above the former 5,120 allocation). This changes
no application wire-body or flash-partition size. Legacy records remain explicitly
metadata-unavailable; retained known metadata cannot be downgraded or mutated.
An independent Python struct/CRC oracle verifies the new byte layout, and
actual 5,142/4,862 boundary tests pass. Physical NVS space/wear/power loss remain
unverified; software allocation is not a physical-capacity guarantee.
