# Phase 9 B22 — externally witnessed host restart floor

**Scope:** host-only non-production C99 contract assurance, NO DB, NO hardware.

## Gap and implementation

B19 picks highest valid snapshot. An attacker or storage error can leave a checksum-valid but old pair of snapshots; CRC alone does not establish freshness. B22 adds `vg_b22_restore_guarded` and `vg_b22_prepare_guarded` to reject any selection beneath an *externally supplied trusted* generation/confirmed-ACK floor. This witness **must** be obtained via an independent trustworthy mechanism in a future scope: the header neither persists nor authenticates it. No witness means no anti-rollback claim.

## Acceptance

C99 strict compilation `-std=c99 -Wall -Wextra -Werror -pedantic`; host fixture exercises normal selection, conservative fallback permitted/denied by floor, same-generation conflict vs exact replica, bad device identity, invalid inputs, ACK high-water, update/readback, advanced witness, generation rollover denied, no output writes on failure. Retain B18–B21 regression and 82 Laravel HTTP mock cases.

**Limitations:** CRC is non-cryptographic; if both slots and witness are replaced/rolled back, this policy does not prevent replay. Does not prove flash durability, power-loss atomicity, HTTPS, real MySQL, ESP32/NVS integration, or formal SIM/SUP closure.
