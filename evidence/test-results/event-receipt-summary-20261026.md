# Authenticated receipt and bounded retirement - local checkpoint 2026-10-26

Baseline develop `bb4f462db3d0692a7c6ae9a8f96c704b3aea43f5`. ADR0010 seven related
scopes are implemented; all mandatory local functional/build/regression/working-security/manual gates PASS; final exact staged-byte security gate is required before local commit.
NO COMMIT until every mandatory local gate passes. System PARTIAL, NOT_APPROVED.

## Actual gates

All filenames below are under evidence/test-results/ unless stated otherwise.

| Gate | Actual result | Evidence |
|---|---|---|
| Protocol SHA256/HMAC/media native | PASS8 methods, independent Python oracle vs actual C verifier | event-receipt-media-native-20261026.txt; integrated regression |
| VGS3 floor/legacy/max/CRC oracle | PASS7 methods; VGS3 max5150 within5184, old VGS1/VGS2 bytes unchanged | event-receipt-floor-native-run2-20261026.txt; integrated regression |
| Authenticated transaction/prefix/recovery/faults | PASS17 methods, actual native SHA/HMAC, all partial writes/uncertain IO, floor anti-resurrection and boot ownership | event-receipt-worker-primitives-regression-20261026.txt; integrated regression |
| Shared single-inflight delivery owner | PASS8 methods; no positive mocked receipt authority | event-receipt-owner-file-native-run3-20261026.txt |
| Actual host file commit/readback/reopen/owner | PASS4 methods including root/path/overwrite negatives | event-receipt-owner-file-native-run3-20261026.txt |
| Real PHP8.2.35/MariaDB full suite | PASS373 cases,0fail0skip; six native wire families and exact ten-table/six-migration/zero-app-row postcheck | event-receipt-mysql-final-20261026.txt |
| Real local TLS/PHP/MariaDB/read/UI/receipt -> native retirement | PASS187 checks, exact owned cleanup0app rows;13 new retirement checks | event-receipt-http-retirement-final-run2-20261026.txt |
| SDK continuous candidate | PASS985920/1048576 bytes, staticRAM57532, largest own frame1056 | esp32-transport-sdk-build-event-receipt-owner-final-20261026.txt |
| SDK retained selftest | PASS1045408/1048576 bytes, staticRAM66436, largest own frame1616;3168-byte app margin | esp32-transport-sdk-build-event-receipt-owner-legacy-final-20261026.txt |
| CI source | Five new native groups included; hosted execution NOT_RUN | .github/workflows/phase9-multi-context-ci.yml |
| Broad host/source/lint regression | PASS229/229 commands: inherited220 +5 new native groups +4 changed PHP lints | event-receipt-integrated-regression-20261026.txt |
| Security initial triage | FAIL5 INFO unchanged source false positives,0privacy; exact re-review pins renewed, corrected final working scan PASS0findings/0privacy | event-receipt-security-initial-20261026.txt; event-receipt-security-triage-20261026.csv; event-receipt-security-final-working-20261026.txt |
| Cleanup candidates | READ_ONLY7 categories; nothing deleted | event-receipt-cleanup-audit-20261026.csv |
| Current source/LOCKED/protected/formal/config/handoff matrix | PASS matching SDK/HTTP digests, both saved tracked handoffs with38 rows, approved DB/key/schema0app rows | event-receipt-checkpoint-audit-20261026.txt |
| Final security/manual/exact staged bytes | Working security/manual PASS; exact staged-byte gate required before commit | event-receipt-review-20261026.md; event-receipt-files-20261026.csv (prepared at final gate) |

No migration is added: approved existing schema already has six migration records.
Migration roundtrip previously passed in metadata batch; this existing-schema mode
is explicit, not a bypass of a needed schema change. Test harness rejects wrong
effective host/port/catalog/account, URL/socket/config overrides and wrong key
before fixture writes. File testing key is not copied or changed: process key is
ephemeral and cipher-compatible. Main dotenv/DB is not booted. All PHP uses the
explicit C:/tools/php-8.2.35/php.exe; Laravel12.70.0/MariaDB10.4.32.

## Source-stable proofs

- Both final SDK source: `506b4e74e05cfedfa29d29fd633af80fe99f3d778f36ebd37f605cfbe34930d3`.
- Candidate merged image: `75e4f208060b4cdd3d4535eedb46975685e6a535edb8c26612b54f191039b988`.
- Retained merged image: `027845f2a47bb4a1230e080265ddfab75fc9b728326375a1a93e446206bcec34`.
- HTTP current source: `6695a197ad6b03efbbd5d3911027877df9e3676e37f02e5e6291ddd36ab35a85`.

## Behavior and compatibility

Opt-in event header1 returns a fixed134-byte status/body-bound SHA256/HMAC receipt
only after actual committed create201 or identical duplicate200. Raw authenticated
bearer is the MAC input key, never its stored digest; no secret or receipt enters
snapshots/evidence/argv. Ordinary JSON and event1.0/1.1 remain unchanged. Wrong
opt-in, outer transactions, conflicts/auth/schema/IO errors do not confirm facts.
SDK validates strict media and the actual worker uses PSA standard crypto.

VGS3 encodes a nonzero latest-boot-scoped uint64 confirmed floor; ordinary publish
cannot advance it or delete outstanding facts. Only exact authenticated target
retirement may remove one record/advance the oldest current prefix. All unrelated
records/latest bytes/IDs/clocks/counters remain. Current events refused by full
persistent capacity still require accepted immutable prefix and a committed current
latest state before confirmation. Queued cumulative jobs filter confirmed facts.
Older valid recovery may require re-authentication of restored predecessors.
Fresh startup rejects a boot namespace already in latest or retained events.

Shared owner correlates one transport request and one pending receipt by unique
monotonic tag. HTTP/media is structural only; RAM prefix release follows typed
authenticated durable worker completion. Recovery epoch/cursor rules reschedule
newer current facts behind recovered predecessors. Telemetry/local observation
remain independent; delivery confirmation never operator ACK or condition CLEAR.
Unavailable storage permits bounded unretired publication without freeing RAM.
Malformed/forged receipt halts events without discarding facts; timeout/exhaustion
retains facts and requires explicit transport reset/recovery. No infinite delivery
or unattended recovery guarantee is established. Retained selftest has the VGS3
reader but explicitly refuses the new continuous-only receipt adapter.

## Failures retained and limits

Earlier enum/unused fixture/compiler/alarm-reuse/source-name assumptions are in
development observations and run1/2 logs. Initial actual HTTP retirement checks
passed, but the overall race gate failed because a suffix-only fixture filter
included new receipt boots. Exact four-cohort identity selection fixed that
oracle; corrected whole187-check run passed. Nothing was bypassed or deleted.
Five scanner INFO occurrences are byte-equal to committed bb4f462 source lines;
only whole-file and line SHA pins renewed, no detector/secret/privacy exemption.

Host file fflush/commit/readback/reopen and SDK compilation do not prove ESP32
NVS power-loss/wear/rollback resistance, PSA runtime, full heap/stack/timing,
physical flash capacity, trusted clock/WiFi/TLS, current Wokwi, hosted CI,
direct MySQL8/POSIX, graphical browser or deployed TLS: NOT_RUN. CRC is not
storage authentication. Finite journal cap8/refusal and unsupported historical
RECOVERY retention remain explicit. Exact cloned valid old state may resurrect
facts; reconfirmation is idempotent and no physical anti-rollback is claimed.
Formal SIM010-015 remain NOT_RUN,14SUP PLANNED; all38 remain22 IMPLEMENTED_UNVERIFIED
and16PARTIAL, per-requirement formal15PASS/3PARTIAL/20NOT_RUN. No formal/LOCKED
registry is edited. This batch and these handoffs are not Goal completion.
