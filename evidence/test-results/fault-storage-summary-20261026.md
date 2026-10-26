# Single-channel isolation, bounded storage and verified gate integrity

Parent develop777d762be36f9e778b9dd259476a28d42393e39f. Seven related scopes:
dedicated SIM011; SUP013 actual host-file integration; independent fault/binary
oracles; five actual raw-C99/backend/read/UI tests; SUP014 approved-target migration
roundtrip; source/postflight/CI/security/regression/evidence/continuity; separate
SUP017 public-reference acceptance audit. This adds real integration and fixes
gate-integrity defects, without new migration, physical control or cleanup.

| Gate | Actual result | Evidence prefix fault-storage- in this directory |
|---|---|---|
| Native single-channel case | PASS4actual C99 frames,44domain channels/43unaffected current, two invalid/null temperature frames and explicit valid restoration, advancing engine1RPM | focused-run1-20261026.txt; case-review; fixture/bridge |
| Bounded actual host-file case | PASS72generations/two-slot reopen,8original bootA facts/metadata, latest bootB sequence8, floor0, RAM166/disk51refusal attempts, slots3332/3344bytes; independent VGS2/CRC and older-file corruption/recovery check | same; source-proof JSON |
| Native fault/file adversarial | PASS11methods including every slot truncation/distributed corruption, wrong fault/zero/current channel, altered identity/counter/floor/metadata, foreign-root refusal and source drift | focused-run1; current241command regression |
| Guarded schema rollback/apply/reapply | PASS actual PHP8.2.35/Laravel12.70.0/mysql driver/MariaDB10.4.32 on approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex; exact6migrations,10tables,0app rows after suite | mysql-final-roundtrip-run3-20261026.txt |
| Real PHP/MariaDB regression | PASS382, FAIL0, SKIP0 including5new actual raw-native fault/API/persistence/UI/negative methods; native receipt crosscheck and independent final read-only catalog postflight PASS | same; post-registry rerun separately recorded |
| MySQL public-source stability | PASS37beceaec5b9089e36945e863901583fc10099996fe26f11817586becdb9aabe, no dotenv/credential hashing; missing input/drift/final catalog failure cannot PASS | same; mysql-final-guard-tests-20261026.txt (32methods) |
| Actual TLS/API/session/UI/receipt regression | PASS215checks after shared callback extraction; source d0f38223407a2701fcdc96a810912d3e0b91b101dd271fc58fed0f7d174846f4, exact owned cleanup to0rows | live-http-run1-20261026.txt |
| Dedicated public-reference case | PASS38requirements/34cases,147initial then157postpromotion references; original LOCKED mappings, real plans/types/lead IDs, safe stable public paths/hashes; one .env.example metadata-only sha:null/no content read | reference-audit-run1-20261026.json; reference-audit-final-20261026.json; final postdocs inventory follows |
| Reference audit/security negatives | PASS12methods, including duplicate case/header/cardinality, missing definition/wrong mapping, traversal/sensitive/linked/missing/unstable input, fabricated VERIFIED and no-clobber output | current241command regression; final-registry-delta |
| Broad integrated regression | PASS241/241commands with current source/postflight/reference hardening; earlier240/240PASS retained; counts are separate runs, not additive | integrated-regression-final-run2-20261026.txt |
| Focus/regression deltas | PASS7initial groups,7source-guard/G1/G2/security groups,5final registry/guard/source/reference groups; guard32, reference12, G1 64/64,G2 2/2, receipt file4/owner8 | focused-run1; source-guard-delta-regression; final-registry-delta |
| Core / SDK | Core226/226 repeated2PASS; firmware source a0a0eac... unchanged and identical to both committed actual SDK proofs, no rebuild/upload needed | broad log; source-proof JSON; prior SDK logs |
| Security | Initial5known existing byte-equal CI/runtime expressions/0privacy reviewed; final CI registration renewed2same CI file pins, no new literal or detector change. Current broad embedded security/framework review PASS0unresolved/0privacy; final working/staged/manual gates mandatory | security-initial; security-triage; broad log; final scan at checkpoint |
| Scope/protected/commit | Requirements LOCKED, used migrations, contracts, three protected untracked files and old evidence preserved. No repository deletion. Exact staged/manual/security/manifest gates required before local commit | final audit and scoped manifest recorded at checkpoint |

Gate bugs fixed with retained negative reproductions: accepting a successful test
report after public-source drift; missing independent final empty-catalog admission;
duplicate canonical case rows silently shadowed by dictionaries. No real production
incident or prior real DB leak is asserted by those negative orchestration tests.
Shared host file callbacks were extracted BYTE-EQUAL777 into one header used by
both fixtures; strict C99/warnings remain unchanged. Development oracle/macro/test-
stimulus failures are preserved and distinguished from firmware defects.

Source proofs: native9c3a6f4b767fc6a557ddbdbb3d1be7d6626cce5455d0ae5317dba4b073834397,
HTTPd0f38223407a2701fcdc96a810912d3e0b91b101dd271fc58fed0f7d174846f4,
MySQL37beceaec5b9089e36945e863901583fc10099996fe26f11817586becdb9aabe,
SDK a0a0eac0809da2b9be93c67a8347c3f50766b3bed163ec7d42a1e4b86fb8bf95.
Only four eligible case status/evidence rows changed: SIM011/SUP013/SUP014/SUP017.
Derived formal32PASS/2PARTIAL/4NOT_RUN; implementation stays22UNVERIFIED/16PARTIAL.
SIM12PASS/3NOT_RUN, SUP18PASS/1PLANNED. No requirement VERIFIED. Original per-case
definitions and old pinned SUP014 target remain unchanged; dated execution protocol
explicitly applies the user's approved current test target instead.

Both handoffs saved with actual HEAD/WIP, full38matrix and tested evidence. Current
captures of dynamic public evidence-table statuses are point-in-time test data;
final inventories record subsequent canonical promotions. No self-commit hash is
invented. After local commit update both actual HEAD/checkpoint documents again.

Remaining formal SIM010/012/013 require their prescribed outage/multifault/recovery
runtime; SUP018 hostedCI remains PLANNED. ESP32/RTOS/PSA/NVS/powerloss/wear/rollback/
fullheap/callstack/timing/clock/WiFi/TLS/OEM/currentWokwi/directMySQL8/POSIX/graphical/
deployedTLS NOT_RUN. Host commit/readback does not prove physical durability or
guaranteed complete retention. SystemPARTIAL/finalNOT_APPROVED. NO PUSH.

Post-registry PHP382/0fail/0skip, stable source37becea... and independent exact empty catalog PASS in mysql-after-registry-20261026.txt. New owned log line endings are stored UTF8/LF with raw-to-LF SHA audit in log-normalization-20261026.csv; no assertion/text or historical committed evidence removed. Final postdocs public-reference report is the current inventory over earlier point-in-time snapshots.
