# B42 — Host-only session-challenge binding over authenticated receipts

## Problem and scope

B40 validates HMAC-SHA256 in C99, and B41 rejects key policy/revision drift between two caller-provided authority observations. Neither check alone binds an otherwise valid receipt to a **specific verifier-issued session challenge**. B42 adds a narrow C99 host-only verification adapter, without changing locked firmware, database migrations, backend endpoint, or production authorization.

## Wire/proof contract

Keep the original sealed receipt (128 bytes) and B35 metadata wire receipt (72 bytes) unchanged. Supply independent 16-byte `issued_nonce`, 16-byte `received_nonce`, and 32-byte `received_proof` buffers. Nonces must match byte-for-byte and be nonzero. After B41 verification succeeds, the C99 adapter computes

`HMAC_SHA256(master32, "VG_PHASE9_B42_CHALLENGE_AUTH_V1\\0" || issued_nonce16 || sealed128 || wire72 || revision_le64 || source_le64 || purpose_le32 || device_le32 || verified_epoch_le64)`.

The literal domain is NUL-terminated (C `sizeof`), and all numeric fields are encoded explicitly little-endian. The independent Python oracle uses standard `hmac` and `struct` rather than reusing the C99 implementation. On denial, the verified-epoch destination remains byte-unchanged. Pairwise nonaliasing applies to all nine input/output regions; secret and message temporaries are cleared best-effort. No allocation, I/O, network, database, or hardware access in the C99 helper.

## Host tests and trust boundary

68 cross-process scenarios: 3 accepted (pre-rotation, post-rotation, distinct publish domain) and 65 denied (wrong/zero/changed nonce, flipped proof, tampered receipt, changed authority revision/source/rotated key/purpose/device, and output alias). Separate contract, negative, and CI policy gates register in the existing host-only job.

**NOT VERIFIED:** The verifier-issued challenge is supplied by a caller in this host prototype; a trusted random issuer, freshness/expiry, consumed-nonce storage, single-use enforcement, persistent monotonic policy, atomic CAS, ESP32 hardware crypto, NVS/powerloss and production key management are not implemented or proven. An already accepted pair can still be replayed **if the verifier reuses the challenge**. Never use this helper alone as a production ACK authorization gate. All tests remain in development scope, formal status open and production not ready.
