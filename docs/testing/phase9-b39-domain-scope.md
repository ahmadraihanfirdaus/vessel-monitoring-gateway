# Phase 9 Batch 39 — Host-only HMAC domain separation

## Scoped objective

SEC-001, SEC-002, NET-002, TEL-003, SYS-003, TST-001, TST-002. Protect the
B37/B38 canonical 128-byte authenticated host receipt from *cross-purpose*
replay between **RESTORE=1** and **PUBLISH=2**, including unexpected device
identity, using a purpose/device/key-ID-specific HMAC-derived signing subkey.
No original firmware, backend, database, or hardware path is modified.

## Policy and wire

B35 retains its 72-byte little-endian canonical receipt. The B37 sealed
128-byte receipt retains `VG37 | version | key_id | epoch | wire | MAC`.
B39 uses explicit domain-separated HMAC-SHA256 key derivation over
`purpose_id (u32 LE) | key_id (u64 LE) | device_tag (u32 LE)` and separately
binds that context to the authenticated transcript. The external authority
supplies the active/retired key IDs, exclusive epoch floor, activation epoch,
expected purpose and expected device; mock inputs only.

The B39 C99 helper **only structurally prechecks** key cutover, purpose,
identity, disjoint regions and canonical wire. Its `PASS_NO_AUTH` result
cannot authorize an ACK, promotion, replay suppression, or CAS. The Python
host HMAC oracle performs cryptographic verification using ephemeral randomly
generated keys. All keys remain outside repository and stored evidence.

## Test boundaries

45 deterministic policy cases, including two acceptable scopes and 43
rejections (cross-purpose replay, wrong device, retired key, wrong MAC,
recomputed CRC, replay epoch and invalid policy types), with independent C99
structural checks. Tests do not prove concurrency, trust of policy inputs,
cryptographic key lifecycle on ESP32, persistent revocation, durable CAS,
network integration, or power-loss survival.

Automatic exact-scope LOCAL Git commit only after the entire 167-execution
Windows gate passes (including 82 Laravel PHPUnit cases), with no DB
connection/migration, no push, no firmware flash, and two local firmware
untracked configuration files preserved. Formal verification remains OPEN;
system status `PARTIAL_NOT_PRODUCTION_READY`.
