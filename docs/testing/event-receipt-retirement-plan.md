# Authenticated receipt and retirement - implemented local design

ADR0010; baseline developbb4f462. Seven related scopes implemented. Final
regression/security/manual/exact staging gates remain mandatory; see current
`evidence/test-results/event-receipt-summary-20261026.md`. No document or bare
HTTP status grants deletion authority.

## Wire and backend admission

Authenticated event requests can opt in with X-VG-Event-Receipt:1. No header
retains original JSON. Invalid/multiple versions fail400 before event writes.
Caller-owned outer transactions fail503 before writes: savepoint release is
not committed persistence. Successful event_persisted201 or identical duplicate200
may sign only after transaction level returns0. Conflict/auth/schema/IO failures
do not issue a confirmation. No migration or token storage change is introduced.

Content-Type application/vnd.vgw.event-receipt-v1; no-store; exact134ASCII bytes:
`VGR1:<64lowercase hex bodySHA256>:<64lowercase hex HMACSHA256>`.
MAC key is the actual authenticated raw bearer32..256bytes, never stored digest.
Message is ASCII `VG_EVENT_COMMIT_V1` + LF + status200or201 + LF + lowercase
SHA256 of complete exact request bytes,1..4096bytes. Identity/source/schema/
metadata are therefore bound. Wrong key/body/status/encoding/version/case/length
fails closed. SDK additionally requires one exact media header (case-insensitive
media spelling, no parameters/duplicate type); structural checks are not crypto.
No credential/MAC goes into durable snapshots, evidence or argv.

PHP uses native hash/hash_hmac. Actual ESP-IDF network module uses PSA
hash_compute, volatile imported HMAC key/mac_compute, checked destroy, cleared
transient digest/material. Native B40 reference math is test-only and is compared
with independent Python stdlib HMAC over short/long keys and boundary bodies.
SDK compilation proves API compatibility, not physical PSA execution.

## Versioned bounded state

VGS1 and VGS2 stay byte-identical when confirmed_event_id0. VGS3magic0x33534756,
version3, encodes a nonzero uint64 latest_boot-scoped floor immediately after
generation, before latest sequence. Per-event VGS2 metadata flags remain, even
for empty/all-unknown event sets. VGS3 max5150bytes within existing5184 buffer;
floor0 or UINT64_MAX in VGS3 is invalid. Retained current-boot event IDs must be
above floor. Different-boot normal merge resets floor0. Latest wire max4096 and
critical journal cap8 are unchanged. Independent Python struct/CRC oracle tests
bytes/truncation/rechecksummed invalid floors; old golden bytes still pass.

Ordinary publish retains prefix/no-deletion guards and cannot advance a current
floor. Normal merge filters confirmed current facts from cumulative queued jobs.
Fresh SDK startup refuses a boot matching latest or any retained event namespace;
running owner may explicitly recover. Random fresh128-bit boot IDs remain the
runtime strategy, not an absolute global uniqueness or anti-rollback proof.

## Authenticated exact retirement and IO

`offline_retirement.h` requires an exact immutable supported record, successful
status, exact receipt and verifier bound to real SDK crypto. Current target must
be oldest outstanding among stored and accepted current-prefix facts with full
metadata equality. Full persistent capacity can refuse a current event while
accepted immutable RAM journal still knows it: actual committed current latest
state and genuine receipt are required before floor publication. Missing/downgraded
metadata or skipping earlier facts rejects. A restored already-RAM-released
current predecessor can be authenticated again from its exact stored fact.

Only after verification may candidate generation advance1, exact stored target
be removed and current floor advance. All other records/latest bytes/boot/sequence/
counters remain. Old-boot retirement does not change current floor; genuine
already-absent or covered targets are idempotent but still verify the receipt.
Low-level unselected-slot write/commit/readback is shared with ordinary publish;
ordinary admission policy is not bypassed. Any write/commit/readback uncertainty
halts IO until explicit recovery. CRC is not snapshot authentication or physical
power-loss/rollback/wear proof.

## Storage worker and owner

Dedicated worker receipt queue1/completion1 uses zero-wait submission/copies. No
bearer is copied into new jobs/snapshots. Worker waits for committed current latest,
clones accepted prefix under mutex, releases lock before crypto/IO, updates
monotonic volatile floor/normalized prefix only after durable success, then emits
typed completion. Receipt and normal state jobs alternate to avoid starvation.
Cumulative queued jobs cannot resurrect confirmed facts; within-run older valid
recovery can restore facts requiring reconfirmation without rewinding volatile IDs.

`event_delivery.h` is the actual SDK single-inflight owner. Monotonic opaque tag
is shared across event/telemetry kinds, never eventID alone; no wrap. Exact target,
source cursor and recovery epoch are captured on network queue acceptance. HTTP
success/structural receipt moves to pending worker admission; never directly frees
RAM. Only matching typed COMMITTED/ALREADY plus nonzero generation/current floor
and exact RAM-first identity/full metadata can release a prefix. NextID/clock/
refusal counters and mutable active alarm/ACK/CLEAR remain unchanged. Telemetry
completion never releases facts. Local sampling/alarm evaluation continue.

Recovered same-current-boot lower IDs override bounded alternation until earlier
facts are visited. Recovery resets current/recovered traversal and increments
epoch. Pending newer receipt is rescheduled behind predecessors without deleting
anything; old-view cursor cannot rewind a newer epoch. Storage rejection with
known predecessor reschedules, unexplained rejection halts events/retains facts.
IO failure or unavailable storage retains all facts and permits bounded unretired
publication; no capacity is falsely freed. Network exhaustion retains facts and
requires explicit reset/recovery; no unattended guaranteed delivery is claimed.
Unsupported historical RECOVERY remains reported/retained, never fabricated.

Full receipt adapter is VG_CONTINUOUS_SIMULATION-only. Retained SDK selftest
keeps VGS3 decoder but new receipt API returnsfalse. Existing partition, TLS,
assertion and stack gates are unchanged; retained app has3168byte final margin.

## Actual verification and limits

Final current PHP373cases0fail0skip; actual localTLS187checks, including thirteen
new retirement assertions: real C99 continuous facts, PHP/MariaDB committed
receipt, Python+native crypto checks, file IO commit/readback, shared owner RAM
release, old/current exact facts, valid-hex MAC forgery no writes, stale cumulative
anti-resurrection, reopen and new fact/duplicate. Host file driver compiles before
DB fixture mutation, paths are restricted to fresh owned private temp, no overwrite
of existing binaries/initial slots and no secrets printed/persisted. Driver does
not replace SDK IO/PSA evidence. Every partial-write/uncertain fault is native
logical IO evidence. Runner faults and source-stability guards remain mandatory.

Candidate985920bytes/RAM57532/frame1056 and retained1045408/RAM66436/frame1616
built source506b4e74e05cfedfa29d29fd633af80fe99f3d778f36ebd37f605cfbe34930d3.
See latest summary for all evidence, initial failures and final pending gates.
Physical ESP32/NVS/PSA/RTOS/heap/stack/clock/WiFi/TLS/power-loss, currentWokwi,
hostedCI, directMySQL8/POSIX, graphical/deployedTLS and new formal SIM/SUP remain
NOT_RUN. LOCKED38 requirements/formal registries unchanged; system PARTIAL.
