# Phase 9 Batch 20 — Host dual-slot candidate update / readback

## Development-only objective

Validate bounded *host-memory* preparation of a successor dual-slot checkpoint, preventing the newest confirmed slot from being chosen for overwriting. The save operation remains the fixture's ordinary host file IO; this batch does **not** establish atomic disk writes, fsync-based durability, power-loss tolerance, authenticated storage, ESP32 NVS integration, or marine safety certification.

- `NET-002`: `vg_b20_prepare` selects the older/invalid slot and computes the next generation without writing caller-owned buffers on failure.
- `TEL-003`: reject confirmed-ACK high-water rollback; pending ACK is not serialized and is reset by B18/B19 restore.
- `SYS-003`, `ALM-002`: preserve local critical event journal while a new checkpoint is incomplete, selecting the last validated slot on process restart.
- `SEC-001`: reject ambiguous same-generation divergent slots, malformed snapshot/identity, and readback mismatch. CRC32 is **not** cryptographic authenticity.
- `TST-001`, `TST-002`: three two-process scenarios (torn, bitflip, fully written), strict GCC and CI regression plus evidence manifest.

## Evidence boundary

The test writes two host files (`generation=10`, `generation=11`) and starts new processes for update and restore. Update never targets the newest slot; failure injection into the target must fall back to `generation=11` with ACK high-water 8. A full verified write must restore `generation=12` with ACK high-water 9. Both restart cases must have no pending ACK. B19 guards must remain unchanged.

This is deterministic test fixture evidence, not authenticated live transport or the actual ESP32 persistence driver. No database access or schema update is performed by this batch's runner. Formal readiness remains OPEN and system status `PARTIAL_NOT_PRODUCTION_READY`.
