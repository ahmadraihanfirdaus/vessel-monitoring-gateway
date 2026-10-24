# B45 — Authenticated two-slot nonce snapshot selection (HOST ONLY)

B44 defined an authenticated 192-byte checkpoint representing B43's bounded nonce
ledger. B45 adds a deterministic readback selector for two externally supplied
slot images. It first validates buffer independence, exact encoded lengths,
trusted caller-provided minimum generation, source identity and 32-byte key;
then invokes **B44 C99 HMAC verification independently on each slot**.

- Valid slot with greatest generation is selected and copied to output; one
  corrupt/tampered slot cannot displace a valid alternate.
- Equal-generation authenticated slots containing different bytes are DENIED
  as split-brain. Exact duplicates select slot zero.
- Neither slot valid, truncated present slot, missing both, overlapping input,
  output or key buffer, wrong key/source/floor: DENY, outputs immutable.
- Cross-process C99 fixture and Python independent struct/HMAC oracle test
  failure modes and source boundaries.

## Important exclusions

No filesystem/NVS read or write is performed by the library, and its caller's
minimum generation is not authenticated by the library. Host tests do **not**
prove atomic storage, fsync, power-cut durability, trusted key provisioning,
thread safety, multi-process CAS, ESP32 integration or production readiness.
The project remains PARTIAL_NOT_PRODUCTION_READY; formal verification OPEN.
