# Bounded NVS continuation, 2026-10-25

Baseline: local `develop` HEAD `9406777159af26db0a61b4bac84daa5b316892cd`.
The preceding ESP32 transport batch is committed separately. This slice adds
actual NVS APIs and full-packet transaction code rather than extending the old
256-byte/32-bit host fixture. LOCKED requirements, migrations, formal registries,
protected files, primary database and remotes are unchanged.

## Seven related implementation scopes

1. Canonical complete telemetry-byte snapshot, full-width identities and CRC.
2. Cross-boot critical journal, identity conflict rejection, bounded retention,
   explicit FULL reporting and saturated rejection-attempt accounting.
3. Two-slot recovery, selected-slot protection, commit/readback publication and
   fail-closed uncertain-write handling.
4. Real NVS worker, zero-wait foreground API and prefix-preserving latest queue.
5. Finite runtime composition independent of Wi-Fi startup/transport success,
   startup entropy sequencing, observable storage outcomes and explicit recovery.
6. Actual recovered C99 bytes through Laravel/MariaDB/browser and fault regression.
7. SDK/CI/security/resource gates, living traceability and metadata-only cleanup.

## Executed gate matrix

| Gate | Actual result | Evidence in this directory |
|---|---|---|
| Final canonical codec/merge | PASS: nine methods; strict C99, every truncation/byte corruption of reference snapshot, maximum names/body/events, full/alias/conflict/overflow/source negatives | `offline-nvs-final-integration-20261025.txt`; boundary-run2 log |
| Independent binary oracle | PASS: Python struct parsing and zlib CRC, explicit full-width fields; maximal valid encoding 4,862 bytes | same codec logs |
| Transaction/failure behavior | PASS: seven methods including six actual C99 binaries; every partial cut of a 4 KiB-body checkpoint, commit uncertainty, readback/IO/corruption/identity/ambiguous-generation rejection | host-final, final-integration and retention-boundary logs |
| Native core/reentry | PASS: same 226/226 cases per entry, two boot entries; no emitted phase failures | `offline-nvs-host-final-20261025.txt` |
| Existing transport/build/isolation checks | PASS: port five, build adversarial three, runner 21 methods | same host-final log |
| Actual final PHP/Laravel/MariaDB suite | PASS: 326 cases, zero failed/skipped, explicit PHP 8.2.35 | final-integration log |
| Effective isolation/key/fixtures | PASS: approved MariaDB 10.4.32/catalog/account; override audit; process-only valid APP_KEY; original 2/4 and recovered 6 C99 packets; HTTP receipt crosscheck | same final-integration log |
| Source/CI/security and legacy checkpoint regression | PASS: 67 commands, including unchanged B18–B21 contracts/native fault oracles and scanner adversarial methods | `offline-nvs-scoped-regression-20261025.txt` |
| Final database postcheck | Required PASS: exact ten tables/five migrations and zero application rows | final-security log |
| Final content/security/scope/diff | Required PASS, repeated on exact staged index before commit | final-security/integrity logs and exact manifest |
| Actual final SDK compile/link | PASS: app 1,041,904 bytes below existing 1,048,576-byte factory partition; 66,436 bytes static RAM | `esp32-transport-sdk-build-storage-run3-20261025.txt` |
| SDK compiler frame bound | PASS: largest own compiler frame 1,616 bytes; this is not complete stack/heap verification | same final SDK log |
| Offline simulator merge and source stability | PASS: actual app slice verified, NVS blank, 2 MiB SDK-configured simulator layout only; no hardware upload | same final SDK log |
| Cleanup candidate inventory | Metadata only; six dependency/generated categories retained | cleanup-inventory CSV |
| Actual ESP32 NVS API execution, power cuts, wear, capacity and confidentiality, full heap/stack/cache timing | NOT_RUN; no substitution with synthetic byte IO | No hardware execution |
| Current Wokwi image, hosted CI, direct MySQL 8, physical Wi-Fi/TLS/clock and remaining formal SIM/SUP | NOT_RUN | No formal promotion |

Final merged image SHA-256:
`457fbd631d21c6ee618810c6c2dd752144800e0cb5d3b8314f1aea06d70a873b`.
Final source-stability digest:
`e79474b93d71d1cb00c0c8dde90c6ec5a9c70b1d29accbfd9950d9aad45a0acb`.
Application headroom is 6,672 bytes; physical flash capacity remains TBD.
No partition enlargement, assertion removal or TLS relaxation was used.

The fixture now merges, serializes and recovers each real core frame before
Laravel ingestion. Its six JSON packets retain SHA-256
`21930ab910d66844d7903d2e726c3c5a8db9809018deacb0e26d93d61f88ee4a`.
Stored invalid/missing/null/source behavior therefore reaches the actual database
and granted view without a schema or API contract change. No migration ran in
this existing-schema suite. The previous migration roundtrip remains separate. The testing file APP_KEY is
still empty; only the actual test process receives an ephemeral valid key. The
read-only postcheck intentionally does not configure or print a key.

## Retained failures and review corrections

The first transaction fixture failed strict compilation because one injected-IO
test line had misleading indentation. Braces fixed the fixture; no compiler flag
was relaxed. The first maximum-size oracle had a hand-calculated length typo;
the corrected 4,862-byte bound and independent Python field/CRC oracle pass.
Both failed logs remain. The first diagnostic's local home path was redacted,
with before/after hashes retained and diagnostic content preserved.

Diff review additionally tightened direct merge admission: a later cumulative
journal cannot omit any retained event from the same boot, including after
recovery. This case has a negative regression, final integration rerun and final
SDK source-stability proof. The intermediate first SDK image is retained but
does not certify the final tightened header. A further transaction-boundary
review ensures a caller bypassing merge cannot publish critical deletion, changed
critical metadata, sequence regression or a reduced rejection counter. The
additional negative method passes; final SDK run3 includes these guards.

Two unchanged CI environment-label lines received new exact whole-file/line
hash review records after the additional test steps. No secret-pattern exemption,
credential literal, source token or provisioning image was added. Snapshot CRC
provides no authenticity, and no recovered data is applied to physical outputs.

## Remaining work and limits

Accepted submission means queued, not durable. FULL means new critical records
were refused while previous records/latest state remain bounded; it never means
lossless retention. No receipt deletes data. There is no automatic latest/event
network replay or durable ACK reconciliation. The runtime remains a six-step
simulation, not a continuous all-domain monitor. Physical NVS execution and
power-loss behavior must still be tested, including flash/cache effects on
sampling and resource watermarks. Trusted clock, confidential credential
provisioning, deployed TLS and hosted CI remain external gates.

Formal SIM-001..009 PASS, SIM-010..015 NOT_RUN, five SUP PASS/fourteen PLANNED,
overall PARTIAL and final NOT_APPROVED are unchanged. The full design and API
limitations are in `docs/testing/esp32-offline-storage.md`; exact changed files
and byte hashes are listed in the batch manifest.
