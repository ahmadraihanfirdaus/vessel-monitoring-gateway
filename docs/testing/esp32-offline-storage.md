# Bounded ESP32 offline storage

Continuation baseline: local `develop` commit
`9406777159af26db0a61b4bac84daa5b316892cd`. The earlier 256-byte/32-bit host store
and its checkpoint tests remain unchanged. They cannot hold a complete telemetry
v1 packet or the actual core journal's full-width identities.

The seven related areas are full-packet canonical encoding, cross-boot critical
journal retention, two-slot transaction/recovery, actual asynchronous NVS binding,
finite runtime composition, recovered-wire backend integration, and regression/
security/resource evidence. This is software implementation evidence; physical
NVS durability and formal NET-002 verification remain open.

## Stored data and capacity

`offline_state.h` stores the latest opaque telemetry bytes up to 4,096 bytes,
device/boot identity, full-width sequence/generation, a saturated rejection-attempt
counter, and eight critical journal records. Each event retains its own boot ID,
64-bit event/alarm/time fields, source ID, source mode and event type. Source
modes are development SIMULATION/BENCH_TEST only; physical acquisition is not
enabled. These are prototype resource bounds, not approved vessel capacities.

Canonical little-endian snapshots have a version, bounded string lengths and a
CRC using existing tested byte/CRC primitives. No raw C struct or pointer is
stored. The envelope is at most 5,120 bytes. CRC is accidental-corruption
detection, not authentication, encryption or a durability guarantee. Opaque wire
bytes must still pass normal API identity/schema validation before admission;
storage does not reinterpret numeric values, source labels or nulls.

Critical identity is `(boot_id, event_id)`. Identical records deduplicate;
conflicting records fail without changing published state. A new boot preserves
older pending critical records. When full, existing records are never evicted:
latest state can advance, but new critical records receive an explicit partial
FULL result and increment a saturated rejection-attempt counter. This counts
attempts, not distinct dropped events. There is no unbounded/lossless claim.
Generation/sequence wrap is not guessed. No HTTP completion or receipt removes
records in this slice; replay/ACK reconciliation remains separate work.

## Transaction and recovery

`offline_transaction.h` implements the actual storage transaction independently
of SDK IO. It reads both slots, validates complete bytes/identity, selects the
highest valid generation and rejects conflicting equal-generation snapshots.
One surviving valid slot may be recovered as degraded, with possible conservative
older data. Two positively absent keys permit empty initialization. Corrupt,
unreadable or ambiguous storage does not silently become an empty store.

Only the unselected slot is written. A commit and exact readback must succeed
before in-memory publication advances. Any uncertain write/commit/readback halts
further IO until explicit recovery. A failed commit may already have written
bytes; the software does not claim rollback. Readback success does not prove
survival of sudden power loss or SDK storage durability.

`esp32_offline_store.c` binds this engine to `nvs_get_blob`, `nvs_set_blob` and
`nvs_commit` in namespace `vgw_state`, keys `state0`/`state1`. It never erases NVS
or touches the network profile namespace. Storage exhaustion/error is reported
and latched. There is no formatting/provisioning shortcut.

## Acquisition and integration

A dedicated worker owns NVS calls. Foreground submission uses a zero-wait mutex
and one-item latest queue; only increasing sequences from the startup-bound boot
are accepted. A queued packet may be replaced only when its cumulative journal
contains the entire previously accepted critical prefix, with identical metadata.
This preserves critical records while coalescing latest-state backlog. Acceptance
means queued, not committed. The caller retains its own latest RAM bytes.

Serial completion status codes are 1 RECOVERED, 2 COMMITTED, 3 CRITICAL_FULL,
4 UNCHANGED, 5 REJECTED and 6 IO_HALTED. The generation/event count and degraded
flag accompany the status. CRITICAL_FULL explicitly refuses new critical records;
it is not a success claim for those records.

Startup recovery can run while the queue retains the newest snapshot. On IO
failure the worker retains the uncertain active job and queued cumulative state;
explicit recovery retries conservatively. Only the worker may wait for a result
consumer. Physical flash/cache stalls and full heap/stack watermarks still need
device measurement; a nonblocking API is not a hard sampling-latency proof.

The finite simulation generates a boot ID using the SDK entropy source before
starting Wi-Fi, and disables that source again before radio initialization. This
startup composition owns the device and has no physical ADC provider. Storage
startup depends on a valid external identity/profile, and can proceed when Wi-Fi
startup or backend connectivity fails. Local core sampling never depends on
storage success. No physical engine/mission output is introduced.

The actual C99 runtime fixture now stores and recovers every packet before it
crosses the real Laravel kernel, approved MariaDB and granted browser rendering.
The six existing wire packets remain byte-identical. Native transaction fault
injection tests exercise real codec/selection/publication code with a synthetic
byte backend; they are not real NVS or power-cut tests.

## Verification boundary

Run `scripts/test_offline_state.py` and `scripts/test_offline_transaction.py`
with the existing strict C99 compiler harness. Run the guarded real backend
suite with explicit PHP 8.2.35 and approved testing configuration. The SDK build
helper enforces the existing 1 MiB application partition, TLS checks, source
stability, compiler frame bounds and offline blank-NVS image assembly.

The physical NVS layout/capacity, wear, confidentiality/key provisioning,
power-loss retention, flash/cache interference, trustworthy TLS clock, Wi-Fi/TLS
handshake, hosted CI and remaining formal SIM/SUP execution remain NOT_RUN.
The candidate has no enabled flash encryption; no provisioned secret is included
in the simulator image. Latest-state replay, event wire composition and receipt
driven durable deletion are not implemented by this storage slice. Overall status
remains PARTIAL and final approval NOT_APPROVED.
