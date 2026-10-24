# Phase 9 B35 — Canonical host checkpoint metadata receipt

Scope: NET-002, TEL-003, SYS-003, SEC-001, TST-001, TST-002.

The B34 guarded publication envelope is **not** a portable wire blob: it
contains native struct padding and an embedded host journal. B35 adds a
**72-byte fixed-length little-endian metadata receipt**, with `VG35` magic,
version/declared size, device tag, two independent witness domain identifiers,
checkpoint generation, accepted sequence, checkpoint CRC32, externally confirmed
revision, accepted round, two observation epochs, and a final receipt CRC32.

`vg_b35_encode` requires an internally coherent B34 envelope and exact
readback snapshot CRC; `vg_b35_verify` additionally requires an independently
validated B34 envelope and snapshot bytes, rejecting any field discrepancy,
truncation, trailing byte, altered receipt CRC, missing pointer, or buffer
alias. Both APIs preserve output and length on every denial. C99 host-only
cross-process fixture exercises 41 cases (1 accept, 40 reject). Binary format
is explicit; no structure memory copy or host-endian dependence.

**Security boundary:** CRC is NOT a MAC or signature. Someone controlling
both the untrusted receipt and the purported trusted envelope can forge the
values; independent verified state is an external requirement. This metadata
record is NOT the full checkpoint and does not implement actual storage,
authenticated CAS, thread synchronization, transport encryption, ESP32/NVS,
power-loss durability, or production readiness. Formal verification OPEN.
