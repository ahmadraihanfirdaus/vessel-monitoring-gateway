# Recovered critical event replay

See ADR0009, `firmware/src/offline_replay.h` and the dated
`evidence/test-results/recovered-replay-summary-20261026.md`.
This is a monitoring prototype and a nondestructive publication path.

The actual NVS worker validates existing VGS1/VGS2 slots through the existing
transaction engine. After successful recovery it copies only critical-event
facts/device/generation/degraded status to a capacity-one recovered-view queue.
The acquisition owner takes a bounded copy with zero queue wait; it never
accesses NVS or the worker's mutable transaction. Empty view is emitted only
after successful positively-empty recovery. Failed recovery emits IO_HALTED.

The shared serializer preserves every original boot/event/alarm identity, source
and boot-relative uint64 time. Complete metadata delegates to the event1.1
serializer. Unknown historical metadata uses event1.0 without inventing fields.
Legacy RECOVERY events have no backend contract: the caller reports them as
unpublishable, leaves them retained and allows supported facts to proceed.
Invalid view/progress/encoding halts event publication explicitly; observation
and latest telemetry remain independent. Network queue rejection does not advance
the cursor. Supported queue admission and unsupported-type reports are distinct
from delivery confirmation, application ACK and alarm acknowledgement.

The continuous caller alternates recovered and current-boot facts, with latest
telemetry opportunities between successful event queue copies. A new successful
explicit recovery replaces the immutable view and restarts recovered traversal;
current-boot queue progress remains. Duplicate publication remains safe through
the backend's exact device/boot/event identity comparison. Recovered telemetry
is outside this event-only route; old receipt order does not establish live data.

The capacity-eight journals, cumulative-prefix retention and transaction publish
guards are unchanged. No event deletion, eviction, current-alarm clearing,
durable ACK/floor or automatic capacity recovery is implemented here. Network
worker owns its existing bounded retries and explicit exhausted-cycle reset.
At-most-once traversal per recovered view is not a delivery guarantee. A failed
HTTP operation can still require operator/external reset and another explicit
recovery; authenticated receipts/retirement remain the next software dependency.

The native integration fixture reuses the existing deterministic transaction IO
fixture from `scripts/test_offline_transaction.py`. It executes real merge,
publish, VGS1/VGS2 encoding, two-slot recovery, recovered capture, fair progress
and wire serialization. Six events from three boots fit one capacity-eight
store; three event-ID1 values remain distinct by boot. Original legacy metadata
absence, bench fault/alarm link0, complete ACK-time0 and CLEAR-time100 are checked
through real MariaDB, TLS read API and granted HTML. Native IO is not flash proof.

Commands use explicit PHP8.2.35 and approved isolated MariaDB via guarded runners.
No schema change is needed for replay; six migrations remain current and no
roundtrip is repeated unnecessarily. External ESP32/NVS/power loss/WiFi/clock,
hosted CI, MySQL8/POSIX/graphical/deployed TLS and new SIM/SUP remain NOT_RUN.
Both handoffs are updated at safe checkpoints; exact-scope commit requires all
mandatory local gates PASS and final security/index/diff review.
