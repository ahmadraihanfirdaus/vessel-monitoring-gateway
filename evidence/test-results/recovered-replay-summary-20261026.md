# Recovered cross-boot event replay, checkpoint 2026-10-26

Baseline local develop `70963d463fa5cd2d43914950ef7a9ece5b3185d7`.
The previous metadata batch and both handoffs are already committed there.
This next six-scope batch connects successful NVS-worker recovery to actual
continuous event publication while retaining all critical facts.
Design: ADR0009 and `docs/testing/recovered-event-replay.md`.
System PARTIAL; final NOT_APPROVED. NO PUSH and no hardware/production claim.

## Scope

1. Shared bounded immutable recovered view and compatibility serializer.
2. Zero-wait dedicated recovery-export queue from actual storage worker.
3. Shared native fair selection/progress, queue-refusal and unsupported-type behavior.
4. Continuous SDK recovered/current/latest publication integration and diagnostics.
5. Real native cross-boot fixture -> PHP/MariaDB/TLS/read/UI, exact identities/dedup.
6. Existing/new regression, SDK/CI/security/living/cleanup/evidence and both handoffs.

No persistence format or database migration is added. VGS1/VGS2 bytes/capacity,
event1.0/1.1 contracts, app/body limits, mandatory guards and LOCKED requirements
remain unchanged. Recovery view never contains credentials or old latest telemetry.
No runtime reads NVS on acquisition thread; all recovery IO stays in storage worker.

## Actual gates

Log filenames below are in `evidence/test-results/`. Runs started on2026-10-25
local time retained that date; continuation checkpoint/review is2026-10-26.
PHP executable remains C:/tools/php-8.2.35/php.exe; Laravel12.70.0;
MariaDB10.4.32 approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex.
Testing config/override/isolation/key guards run before fixtures, with ephemeral
process key and no secret output. Main dotenv/database never used.

| Gate | Actual result | Evidence |
|---|---|---|
| Native recovered capture/serializer/fairness/faults | PASS initial12 methods (11 real C99,1 source integration), final13 including full-eight/ninth boundary; continuous13 and existing metadata6+9 PASS | `recovered-replay-native-run2-20261025.txt`; `recovered-replay-checkpoint-audit-20261026.txt` |
| Native actual transaction two-slot cross-boot fixture | PASS6 events from3boots in one bounded store, both isolated/HTTP synthetic identities | `recovered-replay-wire-run2-20261025.txt` |
| Full real PHP8.2.35/MariaDB suite | PASS366 PHPUnit cases,0failed0skipped; six native fixture families, receipt crosscheck; ten-table/six-migration/zero-app-row postcheck | `recovered-replay-mysql-run1-20261025.txt` |
| MySQL runner fail-closed/ordering | PASS26 methods | `recovered-replay-mysql-runner-20261025.txt` |
| HTTP runner lifecycle/owned cleanup/prerequisite faults | PASS17 methods | `recovered-replay-http-runner-20261025.txt` |
| Actual local TLS/PHP/kernel/MariaDB/read/UI/security | PASS142 labeled checks, source-stable, exact owned cleanup0app rows | `recovered-replay-http-run1-20261025.txt` |
| SDK continuous | PASS image975856/1048576, RAM57004, own frame944 | `esp32-transport-sdk-build-recovered-replay-run1-20261025.txt` |
| SDK retained esp32dev_espidf | PASS image1044352/1048576, own frame1616 | `esp32-transport-sdk-build-recovered-replay-legacy-run1-20261025.txt` |
| Broad host/source/PHP-lint regression | 220 commands:219PASS,1 security-review FAIL due to five stale whole-file pins; corrected framework/content rerun PASS in checkpoint audit | `recovered-replay-regression-20261025.txt` |
| Initial content scan/triage | 5INFO false-positive source occurrences,0privacy warnings; unchanged lines byte-equal to70963d4, exact new file pins reviewed | `recovered-replay-security-run1-20261025.txt`; `recovered-replay-security-triage-20261026.csv` |
| Corrected final security/living/scanner adversarial, hashes, handoff matrix | PASS0unresolved/0privacy, scanner23 methods, all38 mapped, actual source digests and protected hashes unchanged | `recovered-replay-checkpoint-audit-20261026.txt` |
| Manual scope/diff/index/exact manifest | Final exact-scope review/manifest recorded; staged-byte security scan mandatory before commit | `recovered-replay-review-20261026.md`; `recovered-replay-files-20261026.csv`; staged security log |

No migration/rollback is run in this batch: current schema is already the exact
six-migration profile from the prior approved roundtrip. This is an explicit
existing-schema gate, not a skipped necessary migration. The latest local
suite and HTTP cleanup verify that test data leaves no application rows.

## Source and fixture hashes

- HTTP source-stability SHA256
  `3531e10519b7047b92ac8b56b464b68a5574eb68c37991fe9e4a7206c2ff8614`.
- Both SDK source SHA256
  `0602eed18cc45351f4652d970e0c75f3d725f9278ab49b54f6be35f15e6bdad1`.
- Candidate merged image
  `11008f2deac216a6949bc073845383c49e38a1d386cd6ba525aec61a90dcc2b8`.
- Retained merged image
  `f3f9139013d15b5d9ea26b157ce0f018483da8c68dc4f2424b20aa4a9f057373`.
- Six native replay events under isolated fixture identity
  `4e4934bdfd943ac6cb471dd68ff35e8462e63e9bce82289222544ce67cbb1050`;
  HTTP identity `57fc107456d67c83039cb5bb541ae2e905788d2877fad7a4304e8777f0d2f89d`.

## Failure correction and remaining limits

Initial C fixture unused variables failed Werror; corrected without compiler
relaxation. A new-boot fixture reused its cleared mutable alarm while restarting
the allocator, and shared alarm logic correctly refused; fixture now zeroes its
new-boot volatile record. Failures retained in development observations/run1.
The broad-regression security failure is not passed over: five unchanged CI or
runtime form-input source lines were compared with committed bytes, classified
INFO non-secret and given exact renewed whole-file pins. No wildcard or secret,
private-key, credential-URL, format/encoding or privacy-rule exemption is added.

No queue/HTTP completion authorizes application ACK, deletion or alarm clear.
Recovered/current facts are queued at most once per recovered-view traversal;
new explicit recovery can replay duplicates. Network worker retains bounded
retry/exhaustion/reset behavior. Guaranteed delivery, authenticated receipt binding
and crash-safe outbox retirement/freeing capacity remain subsequent software gaps.
Journal capacity8/refusal, prefix retention and local progression stay intact.
Unsupported legacy RECOVERY type is explicitly reported and remains stored.
Late events preserve original boot identities; receipt ordering is not global
alarm state. Recovered events do not replace the current telemetry sample.

Physical ESP32/NVS/wear/power-loss/flash/heap/timing/WiFi/trusted-clock TLS,
current Wokwi execution, hosted CI, direct MySQL8/POSIX, graphical browser and
deployed TLS: NOT_RUN. SIM010-015 and remaining SUP are NOT_RUN/PLANNED; no formal
registry is changed. All38 living requirements remain22 IMPLEMENTED_UNVERIFIED,
16PARTIAL. No system/production/Goal completion is inferred from this checkpoint.
