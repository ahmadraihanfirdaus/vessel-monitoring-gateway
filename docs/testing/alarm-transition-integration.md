# Complete alarm transition integration

Continuation baseline: local `develop`
`5048525e1ff4cfad367dc31bfc42c7aa79fb393e`. See ADR-0008 and the scoped evidence
summary for actual gate results. This is a prototype monitoring/simulation path,
not physical control, a certified alert taxonomy or production approval.

## Immutable facts and identities

An alarm has identity `(device_id, boot_id, alarm_id)` and an event has identity
`(device_id, boot_id, event_id)`. The native shared allocator supplies per-boot
alarm IDs; startup boot identity remains externally identified/fresh entropy.
Priority/reason codes are opaque nonzero development codes. Every retained
transition captures its complete alarm snapshot when the transition occurs;
it is never reconstructed later from a mutable current alarm.

Event schema 1.1 keeps the original nine identity/source/event fields and adds
one required `alarm` object: `priority_code`, `reason_code`, `state`,
`raised_at_ms`, `acknowledged_at_ms`, `cleared_at_ms`. IDs and timestamps remain
uint64, source/priority/reason codes uint32. The new version requires nonzero
alarm/event IDs. Times are boot-relative milliseconds, not UTC. Null means no
ACK/CLEAR; a genuine time zero remains numeric zero on ingress and decimal
string `"0"` on reads. Metadata reads use decimal strings for every uint64 time.

Raised facts require active_unack with no ACK/CLEAR. ACK facts require active_ack
with ACK time and no CLEAR. Clear facts require cleared with a clear time and
optional previous ACK. Action time must equal root `occurred_at_ms`; all present
times must follow raised/ACK chronology using exact unsigned decimal comparison.
Only alarm_raised/alarm_ack/alarm_cleared are defined in 1.1. Existing 1.0 facts,
including its fault type and historical zero-ID acceptance, remain compatible.

Unknown/missing/extra fields, lists in place of objects, nested escaped duplicate
keys, quoted/floating/exponent/negative/overflow numeric forms, invalid states,
zero codes and contradictory lifecycle facts reject before persistence. The
shared raw-object inspector is extracted from the existing telemetry request;
both request types use the same already-valid-JSON structural primitives.
Range/type/whole-body validation remains separate and mandatory. The body cap
stays 4,096 bytes, authentication and device ownership are unchanged.

The original event 1.0 native bytes and telemetry 1.0/1.1 fixtures are retained.
For 1.0, API event reads keep their previous exact property shape. For 1.1 the
additional `alarm` value contains canonical metadata, or null if stored data is
incomplete/invalid. No missing field becomes zero, unacknowledged or cleared by
assumption. Different valid metadata at an existing event identity conflicts;
reordered identical metadata remains idempotent.

## Bounded journal and storage

`alarm_transition.h` pairs retained journal entries with immutable snapshots.
The capacity is still eight. Prefix equality includes the full snapshot, so
latest-state queue coalescing cannot drop/mutate metadata. Full refusal retains
old entries and increments existing saturated diagnostics; observation and
logical local alarm indication continue. Explicit local ACK retains its own
event or is refused; it never clears the underlying condition.

VGS1 encoding remains byte compatible with maximum 4,862 bytes. VGS2 uses an
explicit new magic/version, a per-record presence flag, fixed bounded metadata,
canonical unused-time zeros and the existing CRC. Its worst-case encoded length
is **5,142 bytes**, with a **5,184-byte** working allocation. The application
body cap and flash partition are unchanged. CRC is accidental-corruption
detection, not authentication or power-loss proof.

VGS1 recovered records are explicitly metadata-unavailable. They cannot be
retroactively filled from a current alarm. Mixed cross-boot known/unknown records
are retained in VGS2 without inventing old fields. Merge and transaction publish
both reject changing/dropping any retained known snapshot. The legacy submission
interface preserves already retained metadata; a current-boot worker queue that
has admitted full metadata cannot switch back to the unavailable interface.

The actual NVS worker still writes only its unselected slot, commits and compares
exact readback before memory publication. No erase or provisioning occurs.
Native tests inject every partial VGS2 write and every truncated/corrupted byte;
they do not prove physical NVS, flash-cache timing, wear or power-cut durability.

## SDK publication and UI

The continuous SDK candidate submits complete snapshots to the same bounded
storage worker. Current-boot retained events are queued to the existing HTTPS
worker at most once each, alternating with pending latest telemetry to avoid
starvation. Queue refusal leaves the cursor pending. The worker owns its existing
bounded transport retries. Encoding failure halts event publication explicitly
without skipping a retained fact or stopping local evaluation.

`events_queued_not_acked` is deliberately a queue counter. It is not delivery,
authenticated application ACK or durability. HTTP completion never removes a
journal entry. Recovered-old-boot replay and authenticated receipt/deletion remain
a separate incomplete contract. No recovered critical fact is silently evicted.

Read APIs and granted HTML show event-time state, opaque priority/reason and
boot-relative lifecycle times. Historical 1.0 facts show metadata unavailable.
Receipt order and a snapshot state do not establish current/global active alarm
state. The existing ACK-not-CLEAR warning remains, and there is no new dashboard
command to change the local alarm or physical equipment.

## Isolated migration and local gates

The sixth Laravel migration adds nullable JSON `alarm_metadata`; legacy rows stay
null. Tables remain ten. The current test/HTTP guard requires all six exact
migration records and the reviewed event-column inventory. It never silently
accepts the previous profile. The previous mode admits only the exact empty
ten-table/five-migration schema with no new metadata column, after the unchanged
target/account/grant/engine/environment checks.

The explicit local upgrade command is:

```powershell
python -B scripts/run_mysql_integration.py --php-binary C:/tools/php-8.2.35/php.exe --testing-env --execute --existing-schema --upgrade-previous --migration-roundtrip
```

It builds all five native fixture sets before any mutation, applies the new
migration, rolls all six back only in the verified empty isolated test catalog,
reapplies them and runs actual Laravel/MySQL tests. It must not be repeated with
`--upgrade-previous` after the catalog reaches six migrations. Subsequent gates
use `--execute --existing-schema`. No manual DDL, ordinary dotenv or primary
database is used. Mutation modes also require PHP 8.2.35 and a cipher-compatible
testing APP_KEY; the runner generates a process-only key without printing it.

Actual C99 fixture evidence contains three zero-time lifecycle facts and eight
continuous-coordinator retained events, all serialized from VGS2-recovered data.
The two native fixture stores are independent test objects, not a reset/erase of
real NVS. Default identity is `alarm:demo`; the loopback gate's fixed approved
synthetic override reuses its existing owned `runtime:demo` lease, without adding
an ownership exception. The real TCP/TLS pipeline checks these eleven events,
exact replay/conflict, raw duplicate/state negatives, API metadata and granted UI.

Both SDK images, existing plus new native/backend/security/source regressions,
scoped evidence and protected/LOCKED review remain mandatory before commit.
Hardware/Wi-Fi/TLS/trusted clock/NVS/power loss, graphical browser, hosted CI,
direct MySQL 8 and new formal SIM/SUP execution remain separate NOT_RUN gates.

## Real transaction-race correction

A two-process kernel/database barrier reproduced a pre-existing duplicate-handling
defect under actual MariaDB REPEATABLE-READ: both reads saw no row, first insert
committed, and identical replay returned 500. Event dedup now rolls back the
failed transaction before classifying the committed winner; a shared current read
also handles caller-owned outer transactions without an exclusive-lock upgrade.
The unique database key remains the independent backstop; metadata equality is
exact and no conflict tolerance is added.

The CLI-only race fixture requires explicit execution, the same approved lease,
target/token ownership proof, exact current schema and a verified owned temporary
root. It dispatches real Laravel HTTP kernels in two PHP 8.2.35 processes. A
query listener pauses each process only after its first real event read; the
first process commits before releasing the second. Session isolation is inspected
through fixed SHOW variable names and is never changed. Four cohorts check
legacy/new identical inputs, valid differing metadata and an outer transaction.
Expected results are 201/200, 201/200, 201/409 and 201/200; each identity persists
once. This is real concurrent kernel/database evidence, not concurrent TCP
serving by the single local PHP development server. Separate TLS requests verify
the final stored facts. All workers terminate before ownership-guarded cleanup;
spawn/barrier failure paths have explicit no-leak tests.
