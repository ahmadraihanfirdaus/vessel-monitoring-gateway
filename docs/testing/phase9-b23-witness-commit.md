# Phase 9 B23 — host exact-witness commit protocol

Scope: C99 HOST simulation, no ESP-IDF NVS, filesystem durability, real network or DB.

B22 accepted a snapshot above a trusted minimum, even when an advanced external witness had not been committed. B23 offers an *exact* external (generation, confirmed ACK) witness contract:

- `vg_b23_restore_witnessed`: select only a slot matching the externally witnessed tuple. A fully written newer slot is **not** promoted until a new external witness is supplied.
- `vg_b23_prepare_witnessed`: create a bounded candidate only if there is no unwitnessed newer slot; refuse generation rollover or ACK regression.
- `vg_b23_propose_after_readback`: verify target bytes, decoder, unchanged other slot, and candidate tuple; emit a witness proposal, **not** persist it.

This cannot guarantee that any independent witness is authenticated, durably written, rollback-resistant, monotonic, or available after reboot. Integrating an actual witness store, fsync/flash barriers, device identity attestation, TLS, and power-loss bench test remains OPEN. No witnessed tuple => fail closed, no automatic bootstrap or data acceptance.

Gate: strict C99 `-std=c99 -Wall -Wextra -Werror -pedantic`, old-witness recovery after staged candidate, new-witness promotion, interrupted witness commit, partial/bitflip/other-slot corruption, wrong target/ACK, missing witness, bad identity, same-generation conflict, and no output mutation on failure. All B1–B22 regression gates, 82 DB-isolated mock PHPUnit cases, and firmware 226 core remain mandatory prior to exact-scope local commit.
