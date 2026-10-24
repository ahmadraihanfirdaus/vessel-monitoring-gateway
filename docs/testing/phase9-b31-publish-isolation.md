# Phase 9 B31 — Host publication buffer isolation

The B30 finalization algorithm verifies checkpoint bytes, receipt fields,
ACK, and external revision. It assumes that caller-owned output buffers are
separate from pending evidence and from one another. In C, aliasing these
objects can overwrite evidence mid-publication or yield multiple logically
inconsistent outputs. B31 adds **host-only memory-range checks** before
calling B30. It rejects overlapping writable outputs, overlap with any
pending/readback/CAS input, and reuse of pending memory as independent
storage readback. It rejects invalid pointer spans, null parameters and
oversized readbacks.

The fixture saves a canonical B28 two-round snapshot in one process and tests
31 scenarios in separate processes (1 authorized publish, 30 denied), then
checks that denial did not change output buffers or input evidence. C99
`-Wall -Wextra -Werror -pedantic` applies. Historical B18-B30 tests and
PHPUnit B9-B17 must also PASS before exact-scope local commit.

**Trust boundary**: uintptr_t address comparisons work only within the host
address model; no MPU/isolation technology is added. Nothing authenticates
external CAS or independent readback, implements NVS storage, performs
persistent compare-and-swap, provides power-loss durability, or proves ESP32
hardware behavior. The firmware integration, bench and formal gates remain
NOT_RUN. `PARTIAL_NOT_PRODUCTION_READY` remains mandatory.
