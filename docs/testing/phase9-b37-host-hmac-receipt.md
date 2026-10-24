# Phase 9 B37 — Host authenticated metadata receipt (HMAC-SHA256)

Contexts: SEC-001, NET-002, TEL-003, SYS-003, TST-001, TST-002.

Threat addressed: B35/B36 CRC32 protects against incidental corruption but
not malicious rewriting of the checkpoint receipt with an updated CRC.
B37 exercises a **host-only** authenticated wrapper: 4-byte `VG37` magic,
LE u32 version, LE u64 nonzero key ID, LE u64 monotonic epoch, complete
72-byte VG35 canonical wire receipt, and 32-byte HMAC-SHA256 tag. HMAC
covers a fixed protocol-domain label and exactly the first 96 bytes.

Python test-only verifier validates the full HMAC in constant-time using
`hmac.compare_digest`, checks exact 128-byte length, active key ID, supplied
exclusive minimum epoch, and byte-exact VG35 expected receipt. Keys are
freshly generated with `secrets.token_bytes(32)` and never saved to repo or
logs. The separate C99 structural check **DOES NOT** authenticate; the
suite explicitly proves that a structurally valid receipt can fail HMAC.

36 synthetic cases include genuine acceptance and rejection of forged CRC,
recomputed-but-unsigned journal/ACK changes, wrong keys and identities,
replayed epochs, truncations and malformed tags. B37 is not wired into
ESP32/firmware runtime or Laravel server, and does not provide trusted key
management, device key storage, secure counter persistence, transport
identity or replay resistance if the trusted external floor is compromised.
No database access, schema migration, push, hardware testing, or formal
closure is implied; total system remains PARTIAL_NOT_PRODUCTION_READY.
