# Phase 9 B44 — Host-only signed nonce ledger snapshot

**Scope:** HOST-ONLY. Extends B43 bounded eight-slot in-memory nonce ledger with a
canonical 192-byte wire snapshot protected by HMAC-SHA256. Restores in a separate
host process subject to caller-supplied *trusted* minimum generation and fixed
source identity. Never evicts nonce history or accepts structurally invalid
active/trailing entries. No physical device, production key service, DB or NVS.

## Canonical format

Offsets in bytes, integer fields **little-endian**:

| Offset | Size | Contents |
|---|---:|---|
| 0 | 4 | Magic `VG44` |
| 4 | 4 | Version 1 |
| 8 | 8 | Nonzero snapshot generation |
| 16 | 8 | Nonzero source identity |
| 24 | 4 | Used nonce count 0..8 |
| 28 | 4 | Zero reserved field |
| 32 | 128 | Eight 16-byte nonce slots, zeros in unused slots |
| 160 | 32 | HMAC-SHA256 over bytes 0..159, prefixed by the domain with terminating NUL |

Domain `VG_PHASE9_B44_LEDGER_SNAPSHOT_HMAC_V1\0`; the key is 32 bytes, supplied
externally at test runtime and **never embedded in source or Git evidence**.
The C99 encode/decode implementation uses the previously host-validated B40 HMAC
primitive, and the Python oracle uses `struct` and `hmac` independently.

## Acceptance and denial

- Valid, authenticated snapshot restores into a freshly initialized ledger
  with exact slot contents, including after process restart.
- Tampering any field/MAC, using the wrong key/source, unsupported version,
  stale generation, duplicate active nonce, zero active nonce or nonzero unused
  padding returns DENY. Even when a test key can recompute a valid MAC, malformed
  nonce state is denied.
- Both encoder and decoder preserve caller output completely upon failure;
  overlapping address ranges are denied; no partial state publication.
- The caller must ensure generation is monotonic through a *trusted durable*
  authority; HMAC cannot alone prevent rollback of an older valid signed file.

## Trust boundaries / open formal gates

The fixture writes local files to demonstrate **simulated** restart only. No
crash-atomic storage guarantees, fsync/rename guarantee, rollback-protected
hardware counter, trusted key provisioning, multi-process compare-and-insert,
thread-safe serialization, real ESP32/NVS, formal acceptance or production
readiness is claimed. This snapshot is *not* integrated into the firmware
boot path; applications must not use it to authorize production ACK.

No DB access or migrations; baseline/pins exact and commit only after all gates
pass. Overall `PARTIAL_NOT_PRODUCTION_READY`.
