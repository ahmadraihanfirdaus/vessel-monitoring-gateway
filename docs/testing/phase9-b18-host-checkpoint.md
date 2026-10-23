# Phase 9 B18: bounded HOST restart checkpoint (development only)

### Purpose

Close part of the NET-002 host evidence gap by serializing a bounded **simulated** latest telemetry sample, circular critical-event backlog and **last confirmed** ACK into a versioned binary format. A second process reconstructs the snapshot and proves a pending ACK is not restored as accepted. Identity tag is a non-secret synthetic 32-bit fixture discriminator, not authentication. CRC32 detects accidental corruption, not malicious modifications. This is not a ship safety mechanism, permanent event journal or cryptographic transport receipt.

### Seven linked contexts

- NET-002: bounded queue/cursor checkpoint and separate-process simulated reboot.
- TEL-003: replay identity must not mutate on corrupt record; only confirmed cursor persists.
- ALM-002: critical event order and explicit eviction count retained, local alarm logic unchanged.
- SYS-003: recovery does not invoke network or suppress local alarm processing.
- SEC-001: malformed, foreign identity, partial/trailing and corrupted records rejected atomically; no secrets written into evidence.
- TST-001: deterministic CLI output + SHA-256 raw fixture evidence + negative tests.
- TST-002: host-only CI registration, no database action.

### Explicit limitations

- C99 stdio write/flush is **not** atomic filesystem replacement or guaranteed after sudden power loss. `fsync`/wear-leveling/ESP-IDF NVS implementation NOT_RUN/NOT_IMPLEMENTED. CRC32 alone does not protect malicious tampering or rollback. Snapshot identity tag is not an attestation primitive. Paths are fixed by the local test harness; no public file IO surface or network listener.
- Event store currently overwrites oldest at bounded capacity, recording `evicted_count`; retention policy is NOT verified for vessel safety. Local alarm should never be driven by backend success/failure.
- B18 host test uses two separate invocations for save/restore; real ESP32 reset and storage corruption behavior remain UNTESTED.
- Receipt authentication, transport TLS, MySQL end-to-end and hardware acceptance remain FORMAL_OPEN.

### Acceptance for this scoped batch

1. C99 GCC `-std=c99 -Wall -Wextra -Werror -pedantic` test compiles and runs on Windows GCC.
2. Snapshot round-trip independently restores eight events (two evicted), telemetry with `0`/`null` literal bytes and ACK high-water mark, no pending ACK.
3. Wrong device tag, truncated, trailing and tampered bytes do not change destination state or ACK.
4. Existing 49 legacy host scripts including core 226/226, B9–B17 Laravel 82 cases and B14–B17 cross-language gates all PASS (Windows runner).
5. Exact path stage and local commit only on ALL PASS; no DB access/write, no push, no hardware flash.

Result is **scoped host evidence**, not formal closure. Total system `PARTIAL_NOT_PRODUCTION_READY`.
