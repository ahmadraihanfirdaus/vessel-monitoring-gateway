# Failed event publication: retry the unconfirmed original prefix

Parent developbf29a8bbc28a757cdd932f66287b4984530c1ad3. Five related scopes:
actual parent/native reproduction; context-aware failed-cursor repair; SDK/host
call sites with identity/tag/epoch/alias guards; real commit/reply-loss/duplicate/
host-file retirement; full integration/regression/security/continuity review.
UNCOMMITTED precommit checkpoint: functional gates PASS, exact final index and
security review still required. No push/schema/migration/mainDB/physical control.

Actual defect: queue acceptance advanced replay cursor0->1; failed HTTP closed
the owner without rewinding. The retained head was event1 but the next selector
chose event2. Later receipts cannot retire across the unconfirmed predecessor.
Facts/metadata remained retained and the alarm active; this is a publication/
ordering liveness defect, not evidence of data deletion or a physical incident.
Strict C99 source and pinned parent-header SHA are in reproduction-20261026.json.
Current equivalent composition selects original event1 after the same failure.

The internal receive_http API now requires explicit delivery context. Matching
failed EVENT completion rewinds only the immutable matching source/index/boot/
metadata and compatible recovery epoch. Stale tags cannot touch progress; newer
views and already-reset cursors never advance. Invalid/overlapping context fails
closed. Receipt crypto/floor/generation, storage IO halt, bounded unretired
publication and explicit exhausted transport reset semantics are preserved. No
new automatic retry, hidden engineering policy or physical action is introduced.

Actual TLS fault control is a private server object, not an HTTP control header
or route: one exact owned POST/bodySHA/agent, only after real backend200/201 reply
is drained. The client observes EOF, guarded direct MariaDB audit confirms one
original event/full metadata. Native retry emits byte-identical original body,
changes no slots/floor and releases no fact. Actual backend200duplicate produces
an authenticated status/body-bound receipt. retry-current reconstructs the
observed failure and processes retrytag2 on the SAME owner instance, then genuine
host-file transaction/readback releases only prefix1; nexttag3 and all alarm
records stay intact. The multi-command host continuation is not a physical reboot
or actual SDK network-worker/attempt-budget execution. Its hardware runtime
remains NOT_RUN. No raw token/key/receipt MAC/body/cookie/profile is public output.

| Gate | Actual result | Evidence in this directory |
|---|---|---|
| Native parent/current composition and private fault admission | PASS4methods; original parent yields desired-oracle FAIL (cursor1/head1/next2), current context version cursor0/next1; one-shot exact body/status/method/agent bounds | event-delivery-retry-focused-run3-20261027.txt; reproduction JSON; current247command log |
| Shared owner regression | PASS13methods (8existing+5new), genuine signed transaction/reopen after retry; immutable identity/metadata/source/index/epoch/tag/alias negatives; no false ACK or alarm clear | event-delivery-retry-native-owner-run1-20261026.txt; current247command log |
| Actual host-file/receipt bridge | PASS6methods, old/current/forgery/reopen plus same-owner failuretag1->retrytag2/duplicate200 durable prefix/nexttag3; negative phase status0 requires original body/no receipt | event-delivery-retry-file-owner-run4-20261027.txt; current247command log |
| PHP8.2.35/Laravel12.70.0/MariaDB10.4.32 | PASS388/0FAIL/0SKIP, native receipt crosscheck, exact10table/6migration/0app-row independent postflight; approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex, process-only cipher-compatible key | event-delivery-retry-mysql-run1-20261027.txt |
| Strict real TLS/API/session/read/UI/receipt | PASS225checks including real one-shot committed-response loss, directDB count1/fullmetadata before/after and native byte-identical retry; exact owned cleanup | event-delivery-retry-normal-final-run2-20261027.txt |
| Actual Chrome155 component regression | PASS expiry LIVE->STALE->OFFLINE/no polling; script-disabled/blocked-asset SNAPSHOT; missing timing all4UNKNOWN; Secure/HttpOnly/Lax, strict upstream CA/hostname/date and owned profile/row cleanup | event-delivery-retry-browser-final-run2-20261027.txt |
| Both actual SDK builds | PASS current sourcef693b0cb..., candidate image986544/RAM57532/ownframe1040; retained1045472/RAM66436/ownframe1616 (3104image bytes margin); TLS/assertions/root bundle/1MiB partition/2048ownframe kept | esp32-transport-sdk-build-event-retry-candidate-20261027.txt; retained-20261027.txt |
| Broad integrated regression | PASS247/247commands; existing246 plus new retry proof/admission unit. Core226/226 repeated2, HTTP24lifecycle, MySQL32guards, Node13groups and existing/new native suites PASS | event-delivery-retry-integrated-regression-run1-20261027.txt |
| Security | Initial5findings/0privacy were byte-equal parent CI/runtime nonsecret expressions with stale whole-file pins. Appended5exact current-file/line reviews, detector unchanged; framework/current scanner inside247command run PASS0/0 | event-delivery-retry-security-initial-20261027.txt; security-triage CSV; broad log; final staged scan follows |
| Final source/scope/traceability/index | Current HTTP/MySQL/SDK bindings actual PASS; final docs/reference/protected/diff/working/staged/index gates required before local commit | event-delivery-retry-source-proof-20261027.json; final checkpoint follows |

Current source hashes:
HTTPf1396e27191edd9f080bb70851ab4255773226cf9b00765f942ef7d2ddc0de08;
MySQL516446eb3db89042116ca6ab4a216a06f018e4511af6ebb8a72dbd2b49e08037;
SDKf693b0cb1a77d73b8c8cc97eb65da23703a6da9c1bd7e767dfcc1f6a259631e6.
Earlier actual225source837536ad initial run is retained, not substituted for final
source proof. Current CPP/file metadata/unique phase labels/input binding changes
are covered by final run2. Two SDK builds used the identical current firmware
input hash. Retained binary is byte-identical prior retained image because this
coordinator is opt-in continuous; no hardware equivalence is inferred.

All6used migrations unchanged; this batch uses existing schema and does not
rerun migration rollback/reapply. Prior actual guarded roundtrip is separately
committed under SUP014. No manual DDL, main database, normal dotenv, global PATH/
XAMPP PHP, private configuration or protected AGENTS/two firmware file changes.
No repository deletion; welcome remains DEFERRED. Host Git-pinned baseline test
requires full history; CI source uses checkout fetch-depth0, no local fetch/skip.
Hosted CI has not run here. Both handoffs saved/updated automatically; full38
matrix synchronized without a requirement change or formal case promotion.

Formal stays32PASS/2PARTIAL/4NOT_RUN, implementation22UNVERIFIED/16PARTIAL; SIM12PASS/
3NOT_RUN, SUP18PASS/1PLANNED, no VERIFIED. SIM010/012/013 and SUP018, physical ESP32/
RTOS/PSA/NVS/powerloss/wear/fullstack/heap/timing/currentWokwi/hostedCI/deployedTLS,
directMySQL8/POSIX/graphical operator acceptance NOT_RUN/PLANNED. Browser HTTP
localhost to verified HTTPS upstream is not deployed browser TLS proof. Initial
bug's desired-gate FAIL is retained historical reproduction, not current green
functional result. SystemPARTIAL/finalNOT_APPROVED. NO PUSH. Continue local Goal.
