# CODEX_RESUME - checkpoint operasional

## Native PHP SIGSEGV causality checkpoint (2026-10-27)

This section supersedes earlier publication/CI status below. GitHub main verified
read-only at1cdf4c38358656f2d88150b57330b0f7c7ab0087,145sanitized commits.
Run40511912041:393PHP/MySQL8 and231no-DB PASS;fourjobs PASS,backend HTTP/UI FAIL;
archive NOT_RUN. Relative to full PHP startup:348ms readiness PASS;4946ms disconnect
UPSTREAM_DISCONNECTED/UPSTREAM_HEADERS (request1176ms),poll ALIVE;4947ms before
cleanup ALIVE and no terminate requested;4971ms terminate requested;5003ms wait
returns-11/SIGSEGV. Earlier readonly server cleanup returns-15/SIGTERM. Last captured
stage ROWS_ADMITTED,no fatal category;markers cumulative/asynchronous.

Proved:disconnect precedes cleanup,PHP eventually exits via SIGSEGV. NOT proved:
SIGSEGV caused disconnect,exact signal initiation time,native frame/library,
extension,request-versus-shutdown trigger,or a MySQL/Blade/application cause.
ALIVE means no exit status yet;NO_FATAL_REPORTED may be from a previous request.
No production repair is justified. No backtrace/core/memory obtained or published.

Current isolated checkout:private/portfolio-php-native-causality-20261027,branch
portfolio,no remotes,parent145ancestors unchanged. Resolve this additive local
commit with `git log -1 -- evidence/test-results/php-native-causality-20261027.json`;
private final receipt records exact SHA. Original develop82ae9f87ee1162bd4b33e101286d0be48418184e,
project refs,index,WIP,protected firmware and LOCKED bytes preserved.

Three new diagnostic files are live_http_runtime.php,php_native_causality.py and
test_php_native_causality.py under scripts. Private runner/router/log collector
and existing CI test entrypoint integrate them without workflow changes.
Only failed request disconnects get a passive observation window of at most5s
INSIDE the existing total10s PHP cleanup budget. Remaining wait uses deadline-now;
existing kill5s fallback and success path unchanged. No request retry or arbitrary
timeout increase. Natural signal exit BEFORE any terminate call is distinct from
SIGSEGV observed only AFTER terminate (explicit CAUSE_UNRESOLVED). Even a pre-signal
exit does not by itself identify the native frame or prove disconnect causation.

Bounded Linux child-status probe reports only fixed kernel-state/CoreDumping and
boolean SIGSEGV/SIGTERM pending/caught/ignored categories. No PID,UID,raw masks,
status text,environment,memory,core or paths. Private runtime fingerprint reports
scrubbed PHP/SAPI/ZTS/debug,known extension numeric versions,OPcache/JIT/memory-limit
and handler categories. Unknown values suppressed. Existing bounded pipe drain,
redaction,event caps and critical checkpoint reservation retained.

Local regression:135unique Python PASS,including65HTTP/proxy/lifecycle/causality
cases;11native-contract methods and one main failure-route/cleanup regression.
Actual Windows/PHP8.2.35/MariaDB10.4.32 HTTP/TLS248PASS,all5dashboard predicates PASS,
owned fixture cleanup0application rows. Native Linux probes are injected contracts;
NOT actual Linux execution. PHP393/0FAIL/0SKIP parent regression reused only after
all276public inputs/dependencies match exactly (source fingerprint44c42da4...);
no repeated unchanged PHPUnit suite. Existing suite and5predicates byte-identical.
A negative test found metadata overhead in new passive wait could overrun its
shared budget; deadline-aware passive timeout fixes it with boundary regression.

Linux/MySQL8 reproduction NOT_RUN:Docker/Podman unavailable,WSL not installed.
GDB unavailable,debug symbols not verified,native backtrace NOT_OBTAINED. Existing
local fingerprint CLI_SERVER/PHP8.2.35,ZTS=true,debug=false,memory128M,OPcache not
loaded is not proof of hosted configuration. Hosted fingerprint still missing.
No test skip or invented native/hardware verification.

Scoped security0findings/0warnings;3unchanged runtime-input line pins renewed,
old reviews/scanner preserved. Traceability38requirements/185references PASS;
formal status unchanged,system PARTIAL/NOT_APPROVED. Before owner commit require
full security,index,manifest,scope and Git integrity PASS. Evidence:
evidence/test-results/php-native-causality-20261027.json and its file manifest;
private gate folder private/portfolio-php-native-causality-gates-20261027.

Decision:HOSTED_DIAGNOSTIC_REQUIRED. Stop after local gated candidate. NO PUSH,
NO WORKFLOW DISPATCH. New approval required for this one candidate's publication
and controlled hosted observation. Native fix awaits causal/native-frame evidence;
no automatic further iteration. PhysicalESP32,NVS/RTOS,deployedTLS,vessel NOT_RUN.

## PHP upstream lifecycle diagnostic checkpoint (2026-10-27)

This section supersedes earlier publication/CI status below. Read-only GitHub main
is194ecf07250fd194f550203492eb3d64e2a751b7,144sanitized commits. Hosted run40507282917:
393PHP/MySQL8 PASS,231no-DB PASS,firmware host/SDK/dashboard units PASS. Backend
HTTP/TLS failed earlier at CONNECTED_BROWSER_DATA_AND_SIMULATION with proxy reason
UPSTREAM_DISCONNECTED,UPSTREAM_HEADERS,961ms,unknown upstream status/no bytes.
The continuous five label checks were NOT_RUN. Archive NOT_RUN. Official job logs
were re-read without retaining raw content; PHP exit/fatal/stage flags unavailable.
PHP state at disconnect and internal cause remain UNKNOWN. Readiness passed;
source cleanup follows gate failure,which does not prove PHP was alive at failure.

Current isolated checkout:private/portfolio-php-lifecycle-diagnostics-20261027,
branch portfolio,no remotes,parent144commits unchanged. Resolve the additive local
commit with `git log -1 -- evidence/test-results/php-lifecycle-diagnostics-20261027.json`;
private final receipt records exact SHA. Original develop82ae9f87ee1162bd4b33e101286d0be48418184e,
project refs,index,WIP and protected firmware/LOCKED bytes are preserved.

New private runner diagnostics capture process poll at proxy/gate failure and
BEFORE_CLEANUP,startup/readiness/request/cleanup phases,ordered events,bounded time,
actual available exit code,static shutdown/error categories and connection reason.
A private CLI-server shutdown hook before autoload emits only fixed error types
and memory classification; existing error logging/display flags remain disabled.
No raw error message,trace,path,URL,headers,HTML,body,SQL,environment or credential
is emitted. Merged server pipe is continuously drained; no raw disk log/unbounded
queue,max4096-byte pending line/chunk,overlong line discard,16MiB numeric count cap,
128event cap with32reserved lifecycle slots (proxy failures cap96). A negative
140-error flood regression preserves failure/cleanup checkpoints. Markers explicitly PROCESS_CUMULATIVE_ASYNCHRONOUS_BEST_EFFORT;
absence is not proof of no error. Pre-cleanup exit and cleanup termination remain
separate. Undrained/failed capture blocks PASS while owned DB cleanup still runs.

Deterministic tests use actual local PHP/TCP:exit37 before headers,fatal during
request with nonzero exit,exit7 before readiness,connection closed while PHP remains
alive via stdin barrier,and normal requested cleanup termination. A2MiB stderr
fixture drains without deadlock;12lifecycle methods are included in existing CI
HTTP-gate command without workflow changes. A new collector read+close failure
was negatively reproduced and fixed to prevent raw thread exception output; it
is not a proven historical hosted defect. No production-root-cause repair made.

Local gates:393PHP/0FAIL/0SKIP,248real TLS/HTTP checks,123unique Python cases PASS
(53HTTP gate including12lifecycle and10proxy,32MySQL gate,9data/UI,6formal UI,
23scanner). Actual successful local lifecycle:STARTING,STARTED,READINESS_PASSED,
REQUESTS_BEGIN,BEFORE_CLEANUP ALIVE,requested TERMINATE,cleanup EXITED/code1 on
Windows,drain EOF. Thus code1 here is cleanup requested,not a spontaneous crash.
Local dashboard5/5PASS. Approved isolated MariaDB10.4.32 postflight10tables,
6migrations,0application rows. Linux/MySQL8 NOT_RUN:Docker unavailable,WSL not
installed. No migrations/schema change;existing-schema regression only.

Scoped security0findings/0warnings,38requirement/185reference traceability PASS.
Exactly3unchanged runtime-input line pins renewed;all old reviews retained and
scanner unchanged. Full final security/index/manifest/integrity gates are required
before local owner commit. Original suite and five dashboard predicates are byte
identical;TLS/auth/freshness/quality,request/response caps and all original deadlines
remain unchanged. Production application,firmware,workflow,dependencies and
requirements are byte-identical to parent.

Evidence:evidence/test-results/php-lifecycle-diagnostics-20261027.json and
php-lifecycle-diagnostics-files-20261027.csv;private gate directory
private/portfolio-php-lifecycle-diagnostics-gates-20261027. After local gated commit,
STOP:READY_FOR_PHP_LIFECYCLE_CI_APPROVAL. NO PUSH/NO WORKFLOW DISPATCH this task.
A newly approved hosted run is needed to obtain internal lifecycle evidence.
System PARTIAL/formal NOT_APPROVED;physicalESP32,NVS/RTOS,deployedTLS,vessel NOT_RUN.
Do not resume development or publish without new user instruction.

## Private proxy HTTP502 diagnostic checkpoint (2026-10-27)

This section supersedes older publication/CI status below. Read-only GitHub main
is `2999e6699219392eb6dd28fe5859f6ed0e09e86b`,143 sanitized commits.
Run40502887757:393PHP/MySQL8.0.46 PASS,231no-DB PASS; firmware host,SDK and
dashboard units PASS. HTTP/UI received502 from the standard Python proxy error
page. All5individual predicates FAIL because the dashboard was not received;
source/profile/schema/presentation/freshness categories UNKNOWN. Archive NOT_RUN.
The internal hosted502 cause remains UNKNOWN; do not infer a MySQL or UI bug.

Current isolated checkout:`private/portfolio-proxy-502-diagnostics-20261027`,
branch portfolio,no remotes. Parent143commits stay identical. Resolve this
additive local commit with `git log -1 -- evidence/test-results/proxy-502-diagnostics-20261027.json`;
exact final SHA and final full-scan result live in the private gate receipt.
Original develop82ae9f87ee1162bd4b33e101286d0be48418184e,index,refs,user work,
LOCKED requirements and protected untracked firmware files are preserved.

The private HTTP runner emits `LIVE_HTTP_PROXY_DIAGNOSTIC=` followed by static
reason/phase/status categories, bounded elapsed milliseconds/byte counts and the
unchanged cap. Reasons distinguish connection,timeout,disconnect,protocol,
incomplete body,other upstream I/O,oversize,upstream502 passthrough,private policy
I/O and downstream write errors. No body,URL,header,exception text,credential,
private address or profile path is emitted. Limits stay10s downstream,15s upstream,
1MiB response and8192-byte proxy request. TLS verification/auth/ownership/quality/
freshness and the original five dashboard assertions are unchanged.

Two PRIVATE TEST HARNESS defects have pre-fix negative evidence and repairs:
(1) real TCP declared30-byte body ending at5 bytes previously returned200 after
rewriting length; positive remaining declared length now fails closed502;
(2) downstream BrokenPipe previously attempted a second HTTP502 after beginning
response emission; now it records a safe reason and closes without another status.
Neither defect is proven to explain the historical hosted502. No production
application,firmware,migration,workflow or dependency was changed.

Actual local gates:393PHP cases/0FAIL/0SKIP,55focused UI,248real loopback TLS/HTTP
checks,110unique Python cases PASS (40HTTP gate including10proxy methods,32MySQL
gate,9data/UI,6formal UI review,23scanner). Real TCP refusal/malformed status/
disconnect/incomplete chunk/Content-Length truncation/oversize/upstream502 and
injected timeout/I/O/downstream/policy paths PASS. Timeout injection is deterministic;
no real15-second timeout-duration proof is claimed. Resource close and no leaked
arbitrary diagnostic values are asserted. Local dashboard5/5PASS,HTTP200,SIMULATION,
V1_1,continuous profile,ENABLED,LIVE. Approved isolated MariaDB10.4.32 only;
postflight10tables/6migrations/0application rows. No local MySQL8 runtime.

Scoped security0findings/0warnings,23scanner units PASS. Exactly3unchanged
runtime-generated input lines have renewed whole-file hash pins with byte proof;
all earlier reviews and scanner rules retained. Traceability38requirements and185
references PASS; formal statuses remain unchanged. Owner commit is allowed only
after final full index/worktree scan,manifest,scope and Git integrity PASS.
Evidence:`evidence/test-results/proxy-502-diagnostics-20261027.json` and
`evidence/test-results/proxy-502-diagnostics-files-20261027.csv`; private gate
receipts in `private/portfolio-proxy-502-diagnostics-gates-20261027`.

NO PUSH/NO WORKFLOW DISPATCH authorized for this task. After the local gated
commit,STOP for publication approval and one controlled hosted diagnostic run.
New hosted execution NOT_RUN; parent hosted CI FAILED. Do not claim hardware,
physicalNVS/RTOS,deployedTLS,real-vessel or production verification. System PARTIAL,
formal NOT_APPROVED. Preserve all older handoff history below as historical context.

## Targeted hosted HTTP/UI diagnostic checkpoint (2026-10-27)

This checkpoint supersedes earlier publication/CI status below. GitHub main was
verified read-only at `cb12113c9d07670ce33a94bf14f2bb43f8d7542d`,142 sanitized
commits. Actual run40497516366 had4jobs PASS and backend-mysql-isolated FAIL at
CONTINUOUS_BROWSER_DOMAIN_LABELS. Its PHP8.2.35/MySQL8.0.46 suite391PASS/0FAIL/0SKIP
and no-DB229PASS are actual hosted evidence; archive workflow NOT_RUN.

The current isolated diagnostic checkout is
`private/portfolio-http-ui-diagnostics-20261027`,branch portfolio,no remotes.
Resolve the additive diagnostic commit with `git log -1 -- evidence/test-results/http-ui-diagnostics-20261027.json`;
its exact final HEAD is recorded in the private gate receipt. Parent142commits,
original develop82ae9f87ee1162bd4b33e101286d0be48418184e,LOCKED requirements,
protected untracked firmware files and pre-existing user work are preserved.

Root cause remains UNCONFIRMED:the hosted composite gate did not identify which
of HTTP200,engine_4_rpm,RUNNING,vapor unit disclaimer,low-power label failed.
Actual local MariaDB10.4.32/PHP8.2.35 HTTP/TLS:all5conditions PASS,status200,
SIMULATION,V1_1,continuous profile,ENABLED,LIVE. No dashboard/application repair
has been made. Production controller,queries,views,presenter,freshness,auth,
source/quality/data contracts,migrations,firmware and workflows are unchanged.

Diagnostic changes report all5original predicates before retaining their exact
aggregate gate. Only fixed categories,condition PASS/FAIL,HTTP status and response
SHA256 are emitted. Private CLI-server/lease/owned-row guarded view instrumentation
reports the actual authorized dashboard context without changing values. Unknown
category values are suppressed. No raw HTML,cookies,CSRF,keys or credentials.

Local gates:393PHP cases/0failed/0skipped,no-DB231,focused UI55,actual private
loopback TLS/HTTP248 and100Python cases PASS. Security0findings/0warnings;
3old runtime-input lines were re-reviewed with exact unchanged line hashes after
source hash changed; old reviews remain.38requirement traceability/baselines PASS.
Evidence: `evidence/test-results/http-ui-diagnostics-20261027.json` and its file
manifest; private details in `private/portfolio-http-ui-diagnostics-gates-20261027`.

Current task authorizes NO PUSH and NO WORKFLOW DISPATCH. After local gated commit,
stop for explicit publication approval to collect hosted individual conditions.
Do not guess a MySQL,PHP,collation,profile or timing root cause; change production
behavior only after proof. Hosted CI remains FAILED on parent; diagnostic candidate
hosted execution NOT_RUN. System PARTIAL/formal NOT_APPROVED; no ESP32,NVS/RTOS,
deployedTLS or real-vessel verification. No automatic further development.

## Hosted backend repair checkpoint (2026-10-27)

This checkpoint supersedes the older 139/140-commit publication notes below.
GitHub main was verified read-only at `4e094c1dcb46d8e60a29d451359157cf5b6252be`
(141 sanitized commits). Run 40491474585 has three successful jobs and two failed
backend jobs; the independent archive workflow 40492565049 supplies the fourth
successful job across both workflows. The isolated repair checkout is
`private/portfolio-backend-ci-repair-20261027`, branch `portfolio`, no remotes.
Resolve this repair's exact owner with `git log -1 -- evidence/test-results/hosted-backend-repair-20261027.json`;
the additive private receipt records its final HEAD after the gated local commit.
Original develop remains `82ae9f87ee1162bd4b33e101286d0be48418184e` with its
pre-existing tracked stat differences and protected untracked files preserved.

The six named failures and individual diagnoses are recorded in
`evidence/test-results/hosted-backend-repair-20261027.json`. One stale unit assertion
expected SIM-010 NOT_RUN despite verified source-bound simulator-host PASS evidence.
The other five replay cases reproduce HTTP409 instead of HTTP200 when persisted
JSON keys are reordered. MySQL binary JSON may reorder keys; MariaDB LONGTEXT
retains order. The fix sorts copies of the stored/expected metadata before strict
comparison. Field set, types, exact uint64 decimals, null versus zero, legacy null
metadata, conflict rejection and immutable facts remain enforced.

Local PHP8.2.35/MariaDB10.4.32 regression:391 cases/0 failures/0 skips;
focused34, no-DB229, five-case reordered-readback probe5, actual private-loopback
TLS/HTTP248 checks and113 Python unittest cases PASS. New coverage checks all720
JSON field orders, malformed/missing/extra/type-changed stored metadata and persisted
reorder/conflict immutability. Traceability38/38 and security scanner PASS.
Private raw diagnostic artifacts remain outside the publication tree; the public
summary pins their SHA256 values and the changed source hashes.

Direct local MySQL8 execution is NOT_RUN (no available MySQL8/Docker/WSL runtime).
The five-case probe is controlled storage-order reproduction, not a MySQL8 run.
Hosted CI for the repair is NOT_RUN and requires new publication/dispatch approval.
No push or Actions dispatch is authorized in this task. Preserve all141 published
commits and wait after the local repair checkpoint. Current38 requirements,
15 scoped SIM PASS,18 SUP PASS/1 PLANNED, system PARTIAL and formal NOT_APPROVED
remain unchanged. No physical ESP32, deployed TLS or ship-trial verification.

## SANITIZED CANDIDATE CI REFERENCE FIX (2026-10-27)

This additive checkpoint supersedes the earlier 139-commit publication candidate
b14be1c4adc6c41e70cce7ba2cc66db130cc92f7. The selected isolated checkout is
private/portfolio-ci-fix-20261027, branch portfolio, with no remote configured.
The fix is one new genuine commit; resolve its exact owner with git log -1.
The original 139 commits and their author/date/message/topology are retained
byte-for-byte. Original develop remains 82ae9f87ee1162bd4b33e101286d0be48418184e.
The superseding exact candidate HEAD, 140-commit count, unique author dates,
full extended mapping, manifest, security and Git integrity are recorded in the
additive private/portfolio-ci-fix-receipt-20261027.json; do not select the old
139-commit receipt or audit ZIP as the latest publication candidate.

The pinned negative oracle in scripts/test_event_delivery_retry.py referred to
original commit bf29a8bbc28a757cdd932f66287b4984530c1ad3, absent from the
sanitized object database. Only this revision is changed to its approved map
69c33710a0cf1aa1cd3ecfec4773b06a66bc0029. The parent header SHA256 assertion
is unchanged and its bytes match exactly. The original failing test is retained
as a reproduced pre-fix observation. Seven other 40-hex source literals are
historical blob exclusion pins, not commit revision arguments, and stay intact.

Focused retry/C99 negative-and-current oracles, delivery/retirement regression,
history/security units, workflow source policy and the 38-requirement reference
checks PASS locally; see evidence/test-results/portfolio-ci-fix-20261027.json
and portfolio-ci-fix-files-20261027.csv. No runtime, dependency, LOCKED
requirement, workflow permissions/events or formal verification status changes.
The workflow events remain pull_request and workflow_dispatch; publishing main
alone does not run these jobs. Hosted CI is NOT_RUN; Actions administrative
permissions are not verified through the public API. All hardware/production
limitations and earlier failed evidence remain.

Publication remains unauthorized. A new independent audit package must include
the appended commit. Recheck remote main immediately before any future approved
single-ref fast-forward push from this sanitized repository; never publish
original develop, force/mirror-push, rewrite history or change the default branch.
Stop after final local gates and wait for explicit user publication approval.

## PUBLICATION HARNESS PORTABILITY FIX (2026-10-27)

Current follow-up is a real test-harness fix after preparation commit
`a0a92b0b0b46e64062969c7ae2b8acf3631d7b4a`; source owner hash is obtained from Git.
The138commit candidate at9888c6b9d4deb410f976b761cb3299c13d4c75e5 passed full
history/integrity and traceability but its12reference suite failed because the
metadata-only test depended on the omitted real template. The test now uses an
owned empty synthetic template/temporary ROOT, retains the no-open guard and all
negative cases, and checks bytes0. Production validator/LOCKED/statuses unchanged.
Source and isolated checkout corrections are in portfolio-portable-harness-fix-20261027.json;
current185reference inventory and exact scope are portfolio-harness-reference-20261027.json
and portfolio-harness-files-20261027.csv. Earlier failed attempts remain intact.

The original tested Windows worktree and a standard private checkout differed
only by line endings in5runtime input files. Git blobs/normalized contents are
identical; original tested raw EOL bytes are reproduced only in the private
verification checkout, restoring exact3runtime source hashes without a checksum
waiver. Original source and candidate Git objects remain untouched. This is
explicitly recorded in the final receipt, not described as a new runtime test.

Only the actual latest final receipt private/portfolio-history-final-receipt-20261027.json
selects the current candidate_repository and source/tip. Earlier bare candidates
and private verification attempts are retained; never overwrite/delete them.
It must include both genuine portfolio/fix commits after the137original commits,
all original identity/date/message/topology mappings, clean history/fsck, actual
reference/security PASS, exact binding reproduction and source Git/index checks.
Absent/failing receipt means PUBLICATION_BLOCKED. No public upload/push/default
branch change, artificial activity, original history rewrite or database access.
Stop for independent publication approval after the final receipt PASS.

## PORTFOLIO HISTORY PREPARATION (2026-10-27)

A new explicit user task authorizes local GitHub portfolio preparation, not
reopening completed software development or publishing. Source baseline is
`cf2044a69a9f7a71410f91236758de19c78c1537` on develop: 137 commits on 14 original
author dates. This preparation section belongs to the later genuine preparation
commit; obtain its actual hash using Git rather than a self-referential literal.
The implementation/audit closure below remains the runtime source baseline.

Read [the independent publication review](../portfolio/publication-review-20261027.md),
[hardware-free demo](../portfolio/local-demo.md), and current English README.
Original history is NOT directly publishable: 26 historical blob versions have
profile paths; 82 exact historical CI assignment matches are reviewed synthetic
fixtures, not operational credentials. All original identities/dates/messages/
parent topology are preserved in an isolated sanitized candidate, with a complete
old/new map. Initial137 candidate retains43 original hashes and rewrites94; all
137 commits remain. No fake/backdated activity or author replacement is allowed.

The initial candidate and full scan are in portfolio-sanitized-baseline-20261027.json;
its native core226repeat2 and24x48 wire demo PASS. An initial traceability FAIL due
to omitted dotenv template is retained, then corrected in a real isolated clone
projection. Only editable SEC002 implementation_path changes from the excluded
template to actual external key-loading source backend/laravel/config/app.php;
both full38tables below align. LOCKED texts/mappings, all assessments/formal
statuses and validator rules are unchanged. Current tooling and reference gates
are recorded in portfolio-tooling-gates-20261027.json, portfolio-tooling-correction-20261027.json and portfolio-reference-final-20261027.json. A stale one-template test oracle initially failed; it now requires all current references hashed plus the actual SEC002 key-loader path. Dedicated metadata-only template and negative cases remain;12reference tests PASS.

The FINAL actual committed source candidate is selected only by the
candidate_repository field of private/portfolio-history-final-receipt-20261027.json.
Earlier candidates, initially under private/portfolio-history-final-20261027/,
are preserved attempts and do not select the final publication artifact. These are ignored local
review artifacts, not public source or a publication authorization. Their receipt
must show actual final source/tip, every commit mapping, complete clean candidate
history, exact identity/date/message/topology preservation, strict fsck with no
unexpected unreachable objects, and final traceability/demo compatibility. If
missing or failed, status is PUBLICATION_BLOCKED despite the report's conditional
recommendation. The initial137 candidate alone does not close this new task.

Source preparation files are enumerated by portfolio-preparation-files-20261027.csv;
query Git to distinguish WIP from committed ownership. After successful closure,
expect empty index/no owned byte WIP, protected AGENTS.md and two firmware files
still untracked; old2 alarm metadata stat-cache entries remain byte-equal HEAD.
No original history/evidence/localZIP is deleted or rewritten. Private candidate
and demo workspaces (including failed attempts) are retained outside staging.
PHP/MariaDB/TLS/browser/SDK tests are not rerun for this metadata/reference/tooling
scope; prior source-bound software proofs remain qualified. No normal DB, global
PATH, XAMPP, requirements LOCKED, hardware, original remotes or default branch is
changed. No push/force push/remote merge or public upload is performed.

Recommendation after final receipt PASS: SANITIZED_HISTORY_READY_FOR_APPROVAL;
STOP before publication for independent ChatGPT/owner review. Public GitHub root page displays Public/main/2commits; profile graph failed to load. Existing contribution cells/account email association and administrative branch/fork settings are NOT_VERIFIED;
137 baseline commits over14dates are conditional potential, not guaranteed green
cells. Overall system PARTIAL/NOT_APPROVED and external NOT_RUN/BLOCKED remain.

## FINAL LOCAL SOFTWARE CLOSURE (2026-10-27)

Decision: LOCAL_SOFTWARE_SCOPE_COMPLETE_WITH_EXTERNAL_BLOCKERS.
The latest user requested this bounded final decision and cessation of automatic
local iteration when no safe independent implementation gap remains. Actual38row
source/test/evidence review classifies32LOCAL_IMPLEMENTATION_COMPLETE_BUT_NOT_
FORMALLY_VERIFIED and6EXTERNAL_PREREQUISITE (SYS003,ALM003,NET001,NET002,SEC002,TST002).
No known reproducible independent local implementation defect remains after the
archive repair. This is not exhaustive absence of bugs or system/formal approval.

Implementation/audit commit:be6bad74e0efacebfd81fa8084c5fd2e53af53f1 on develop;
parent81e9bfbb36d357a55476bb44d985cd8fa095e4c5. Its53exact files and every committed
blob/manifest/worktree were verified postcommit PASS;all mandatory scoped gates
and final current-scope readonly security exit0/0findings/0privacy PASS. Actual
Git HEAD at resume is obtained with `git rev-parse HEAD`;this checkpoint belongs
to the subsequent metadata-only closure commit (2handoffs+postcommit proof+
closure checks/manifest/security). Its own self-hash is intentionally not embedded
inside these files. The audit/source commit above identifies the tested code;
the metadata owner commit is identified by Git,not a stale previous HEAD literal.

Both handoffs were automatically updated AFTER the successful substantive audit
commit. Final metadata closure is reviewed/staged/committed under the same
fail-closed security/exact-index policy;query Git and the closure manifest for
actual completion,not a proposed plan. Expected after closure:index EMPTY,no owned
audit WIP;protected `AGENTS.md`, `firmware/.gitignore`, and
`firmware/.vscode/extensions.json` remain untracked;old2metadata stat-cache entries can showM but are byte-equal HEAD.
Do not modify/stage/remove them. Earlier9blocked/static/postcommit records are now
preserved in the audit commit. One old log extra EOF LF was normalized only after
a cached whitespace failure;rawSHA/size and append-one-LF byte-exact reconstruction
proof are preserved. No diagnostic/result was lost and other prior bytes unchanged.

Current38formal/implementation registries stay22IMPLEMENTED_UNVERIFIED/16PARTIAL,
37formalPASS/1NOT_RUN,15SIM scopedPASS/18SUP PASS/SUP018 PLANNED. Original38LOCKED
texts/mappings unchanged;no requirement VERIFIED. SYSTEM_PARTIAL/NOT_RUN/
NOT_APPROVED unchanged;no physical/system/deployment/production approval.

Current actual new local gates:18new+6retained GitZIP safety methods and Bash
syntax PASS,19relevant integrated commands0fail plus final required code delta,
core226repeat2/provider/alarm/guard/receipt/Node groups PASS,38/34/185currentref
and both38tables PASS,independent current-source host-case review PASS. PHP8.2.35
checked explicitly. Prior matching HTTP81fa45d1/MySQL516446eb/SDKf693b0cb proofs
retain actual388PHP/248TLS/Chrome155/bothSDK/60047msHOST/broad248commands;those
DB/runtime/SDK suites are NOT_RERUN in this archive-only repair. No mainDB,manual
DDL,remote,hardwareupload,physicalcontrol or globalPATH/XAMPP change.

Safe-source archive defects fixed in existing verifier/Bash plus shared Python
helper/tests/PR source:metadata-before-content exclusions,new exclusive output,
SDK defaults retained,exact filtered blob checks,ZIP bounds/links/duplicates/
metadata channels and no binary/large skip. Initial real parent payload privacy
failure7blobs is preserved;exact historical path/blob omissions disclose filtered
versions while preserving local originals. Active handoffs redact profile prefixes
to <LOCAL_HOME>;unknown/changed versions still undergo ordinary content checks.
No dotenv/password/token/APP_KEY/private coordinates copied or printed.

Actual postcommit sourceZIP PASS:1589files,6exclusions,3152907bytes;
SHA25648bb8bc88e3d04334bcd18bb1666cdcb09cb398800848c74380e0d54ec4015d2.
Retained outside repo at <SYSTEM_TEMP>/vg-final-source-snapshot-byudpxgp/
vessel-monitoring-gateway-source.zip (resolve system temp locally;no profile path
stored). Commit source is be6bad7;the later closure metadata is not in this ZIP.
No .env/.env.testing/.git/vendor/.pio or protected untracked copied. Filtered
review snapshot only,not a full clone,workspace backup,deployment or publication
permission. New archives default to metadata-only plan;--execute needs reviewed
clean source/index and fresh unlinked output outside the repo. No overwrite,
source-cache creation,renaming or deletion;partial own output is retained.

Evidence:docs/testing/final-local-software-audit-20261027.md;38row decision CSV;
final-local-audit-gate-matrix/files/manual-review/summary/source-and-baseline-proof/
reference-postformat/final-code-delta/packaging-current-proof and
final-local-audit-postcommit-be6bad7-20261027.json. Closure evidence is
final-local-audit-closure-checks/files/security-20261027.*. Earlier initial failed
privacy/payload/cached-format evidence remains,with explicit corrections.

Cleanup11tracked candidates=5DEFERRED/6PROTECTED/0SAFE_TO_DELETE,0deletions.
Welcome remains DEFERRED under unchanged security-scanner dependency;Vite inputs/
bootstrap remain configured. Used migrations,history,golden fixtures,evidence,
secrets,preexisting untracked and user work preserved. Selective safe-cleanup
policy supersedes only the old read-only rule;never delete to meet a file count.

Additional7composition GCC analysis remains BLOCKED_TOOL_COVERAGE,ASan/UBSan
NOT_RUN matching runtimes unavailable;2bounded modular object analyses PASS only
for scalar measurement validation/network-init admission. No diagnostic suppressed
or hardware proof inferred;these optional methods are separate from baseline
mandatory scoped gates and do not justify endless retries.

Remaining EXTERNAL NOT_RUN:actual authorized ESP32/RTOS/WiFi/trusted-clock/PSA/NVS,
powerloss/wear/fullstack/heap/timing,currentWokwi,hostedCI/SUP018,deployedTLS/direct
MySQL8/POSIX and graphical/operator/field acceptance. Phase14 checklist PREPARED;
survey NOT_RUN/physical integration NOT_AUTHORIZED,no FMEA residual risk accepted.
Future execution needs separately authorized real prerequisites;no control/OEM
protocol/pin/threshold/TBD answer is invented. NO PUSH or remote trigger.

STOP automatic local implementation/audit iteration after this final metadata
closure,as explicitly requested by the latest user. Goal local-software completion
is reconciled only after clean final Git/security checks;read actual Goal service
state on resume. Reopen only for a newly reproduced local defect,approved scope
change or available external verification evidence. Do not restart a baseline
audit,add a mock/admin batch,or infer remaining local defects solely from the
conservative PARTIAL/UNVERIFIED registry or optional analyzer limit. Future PHP
work uses explicit8.2.35 and fail-closed approved isolated MariaDB only;never main
DB or dotenv/credential values in output. Every future authorized change still
requires relevant tests/security/evidence/exact local commit only mandatoryPASS.

## Historical final local software audit PRECOMMIT checkpoint (2026-10-27)

Audited source HEAD81e9bfbb36d357a55476bb44d985cd8fa095e4c5 on develop; index
53EXACT files STAGED at this saved precommit checkpoint. Latest user requested a bounded final
local software decision and an end to automatic iteration if no safe local gap
remains. Decision LOCAL_SOFTWARE_SCOPE_COMPLETE_WITH_EXTERNAL_BLOCKERS is effective
after final mandatory scoped gates/local commit,not system/production approval.

38row final-local-audit-requirements-20261027.csv classifies32LOCAL_IMPLEMENTATION_
COMPLETE_BUT_NOT_FORMALLY_VERIFIED and6EXTERNAL_PREREQUISITE (SYS003,ALM003,NET001,
NET002,SEC002,TST002). Actual implementation/test/evidence/roadmap reviewed with
per-row observations. Original38LOCKED and mappings remain;living22IMPLEMENTED_
UNVERIFIED/16PARTIAL,formal37PASS/1NOT_RUN,15SIM scopedPASS/18SUP PASS/SUP018 PLANNED.
No requirement VERIFIED;SYSTEM_PARTIAL/finalNOT_APPROVED remain. Source audit
found only reproducible archive-tool defects;these are fixed and tested.

Archive fixes:metadata-first dotenv/private/cache filtering,SDK defaults retained,
exclusive new output outside repo,no rm/mv/overwrite,exact filtered commit blobs,
strict ZIP metadata/count/size/link/duplicate/encryption/NUL and directory-payload
admission. Process-only no-bytecode and Bash compatibility delegate;no global
PATH change. Initial real parent-HEAD privacy review found7historical private
profile blobs;exact path/blob pins omit and disclose only those versions from a
public snapshot. Local originals unchanged;active handoff profile prefixes now
<LOCAL_HOME>. Unknown/changed versions receive ordinary scanning. No dotenv/key/
credential values read/copied;no ZIP or publication was created by this audit.

Current18new+6retained archive methods/shell syntax PASS;19relevant integrated
commands PASS plus necessary frozen-code delta18+6. Fresh core226repeat2 and
provider/alarm/guard/receipt/Node groups included. Independent current-source
SIM010/012/013 evidence review PASS. Parent admitted-public payload1542files/
8exclusions/0findings PASS;actual CLI default plan and WIP execute refusal PASS.
38/34/current185reference guard PASS;source HTTP81fa45d1/MySQL516446eb/SDKf693b0cb
match retained actual PHP388/TLS248/Chrome155/60047msHOST/bothSDK/broad248command
proofs. Those runtime/DB/SDK suites are NOT_RERUN in this archive-only repair.
Actual current PHP8.2.35 checked explicitly. All6migrations unchanged;no DB action.

Full-composition7case GCC coverage remains BLOCKED,ASan/UBSan NOT_RUN;2limited
modular object analyses PASS without diagnostics suppression. These are optional
additional coverage,not mandatory baseline gates. HostedSUP018/ESP32/RTOS/WiFi/
clock/PSA/NVS/powerloss/wear/stack/heap/timing/deployedTLS/MySQL8/POSIX/operator
verification stays NOT_RUN. Cleanup11tracked candidates:5DEFERRED/6PROTECTED/
0SAFE_TO_DELETE,0deletions;welcome remainsDEFERRED. Historical evidence preserved.

All earlier9untracked audit/static/postcommit evidence plus approved current
archive/source/docs/tests/workflow/evidence are included by final exact manifest.
Initial cached whitespace gate failed on one extra final LF in the earlier native
analysis log. Only that LF was removed;original SHA/size and byte-exact append-LF
reconstruction are recorded in final-local-audit-evidence-format-normalization-
20261027.json. No diagnostic/result lost;all other prior WIP bytes unchanged.
ProtectedAGENTS/two firmware untracked and old2byte-equal metadata stat-cache
entries stay excluded. Both full38tables below are current. Functional/reference/
source/manual gates PASS;fresh complete working security0findings0privacy PASS.
Initial52index/blob/manifest/worktree/cached diff and staged security0/0 PASS;
fresh postformat reference report is the53rd exact file. Last metadata-stage equality and final read-only scan REQUIRED before
actual commit. Final staging authority:final-local-audit-files-20261027.csv. See final-local-audit gate
matrix/manual-review/summary/files for actual gate states. No stage/commit until
mandatory gates PASS. After the substantive audit commit update BOTH handoffs with
its actual hash/postcommit proof and finish a reviewed metadata-only closure;
retain historical WIP evidence but leave no new uncommitted audit implementation.

Then stop automatic local iteration per latest user instruction. Resume only for
a new reproducible defect,approved scope change or available external prerequisites.
No phantom features,mocks,reset-policy changes or administrative batch numbering.
NO PUSH/remote merge/mainDB/manualDDL/destructiveGit/hardwareupload. Do not label
source/archive/test success as system VERIFIED,hardware verified or production ready.

## Historical operational BLOCKED prerequisites checkpoint (2026-10-27)

Actual develop HEAD81e9bfbb36d357a55476bb44d985cd8fa095e4c5; index EMPTY.
Goal completion remains UNPROVEN. The same external prerequisites remained
unavailable across3consecutive Goal turns: committed resilience/readiness review,
additional actual native-analysis continuation, and current revalidation. Current
SUP018 is PLANNED with no execution evidence; current serial-port enumeration
returns none (not a full hardware inventory); platformio.ini explicitly prohibits
hardware upload/integration. HTTP/MySQL/SDK public snapshots, LOCKED2/protected3
and old2metadata bytes are unchanged. Current source review identified no new
independent local implementation scope. No project completion or VERIFIED claim.

Operational checkpoint is BLOCKED_EXTERNAL_VERIFICATION_PREREQUISITES. Formal
Goal-service transition to blocked is requested AFTER this checkpoint validation;
use get_goal on resume for actual service status, not a historical status line.
Do not spin more administrative batches, mocks or repeated passing tests to
replace missing prerequisites. Additional analyzer-complexity/sanitizer limitations
are separate incomplete optional coverage, not confirmed source vulnerabilities
or the sole reason for the external prerequisite block.

Saved audit:evidence/test-results/goal-prerequisites-blocked-checkpoint-20261027.json.
Final checkpoint security:evidence/test-results/goal-prerequisites-checkpoint-
security-20261027.txt (read its actual result; no PASS inferred before execution).
Prior unchanged runtime388PHP/TLS248/Chrome155/60sHOST/broad248command evidence
remains scoped/source-bound. Latest extra static analysis is BLOCKED, not PASS;
no diagnostic suppressed, no source workaround, no stage/commit/push. Both complete
38row handoff tables remain22IMPLEMENTED_UNVERIFIED/16PARTIAL and formal37PASS/
1NOT_RUN;15SIM scopedPASS/18SUP PASS/SUP018 PLANNED. SystemPARTIAL/finalNOT_APPROVED.

Preserve all current WIP: both handoffs, survey-readiness postcommit81e9bfb JSON,
six native-static-analysis run/probe/review/security artifacts, this blocked
checkpoint JSON and its security log. No production source/tests/CI/schema/
LOCKED/status changes. Preserve3protected untracked and old2byte-equal metadata
stat-cache entries; cleanup0/welcomeDEFERRED. This WIP is deliberately UNCOMMITTED
because no new complete batch gate exists. Last valid local commits98455c3 and
81e9bfb are preserved; no main DB/secret output/remote/destructive Git/physical
control/globalPATH/XAMPP changes.

Resume only when actual prerequisites change or a new independent local defect/
implementation gap is identified. Useful prerequisites: an explicitly authorized
protected ESP32 bench with external provisioning/trusted-clock plan; actual
existing hostedCI/SUP018 evidence or separately authorized execution; separately
authorized isolated deployedTLS verification environment/evidence. Never treat a
serial port, build, source registration or host-file result as that evidence or
as hardware/remote authority. NO PUSH remains. Do not send credentials or copy
.env/APP_KEY/token/private coordinates into artifacts. Future PHP work uses
explicit8.2.35 and fail-closed approved isolated MariaDB; never main DB. All future
substantive batches still require scoped tests/integration/regression/security/
evidence/exact-scope local commit only every mandatory gate PASS, followed by
BOTH-handoff update. See actual Git/index/WIP before resuming; preserve this context.

## Historical additional native static-analysis checkpoint (2026-10-27, UNCOMMITTED evidence retained)

Actual develop HEAD81e9bfbb36d357a55476bb44d985cd8fa095e4c5; index EMPTY.
Prior turn made substantive progress: resilience70-file commit98455c3 and
Phase14/readiness20-file commit81e9bfb, both exact postcommit proofs PASS.
This continuation checked current Git/WIP and current event metadata/read and
continuous coordinator contracts, finding no new reproducible implementation
bug. Additional independent GCC16.2 host static analysis was attempted on7actual
existing C99 compositions:provider/navigation,telemetry/quality,continuous alarm/
storage,single-channel isolation,event retry,authenticated retirement,resilience
parser. Historical retry fixture was copied/adapted ONLY in fresh owned temp as
the existing current-version test does; repository fixture unchanged.

New compiler gate NOT_PASS/BLOCKED_INCOMPLETE_STATIC_ANALYSIS:7object compiles
exit1,759diagnostics all analyzer-too-complex. No memory-vulnerability diagnostic
class appeared, but incomplete analysis is not proof of absence. One smallest
wire-composition probe with Os and increased per-point32/explosion16 budgets
retained49complexity diagnostics/exit1. No diagnostic disabled,source workaround,
skip,object execution,DB/network/hardware action or fake PASS. All raw sanitized
logs,commands,source hashes,exits and triage are in native-static-analysis-run1,
-budget-probe and -review dated20261027. No stage/commit/push for this incomplete
new gate. Existing scoped committed runtime PASS records remain unchanged.

Current WIP: both handoffs, survey-readiness-postcommit-81e9bfb-20261027.json,
native-static-analysis-run1-20261027.json/.txt,native-static-analysis-budget-probe-
20261027.json/.txt,native-static-analysis-review-20261027.json,native-static-analysis-security-
20261027.txt. Fresh security scanner PASS exit0/0findings/0privacy. Compiler
ASan/UBSan static/import-library resolution found0regular files; sanitizer
execution NOT_RUN_DEPENDENCY_UNAVAILABLE, not a global installation inventory.
Protected3untracked and old2metadata byte-equal stat-cache entries remain
preserved/excluded. No
LOCKED/production source/test/schema/CI/status change; cleanup0/welcomeDEFERRED.
Both38matrices remain current22IMPLEMENTED_UNVERIFIED/16PARTIAL,37formalPASS/
1NOT_RUN;15SIM scopedPASS,18SUP PASS/SUP018 PLANNED. SystemPARTIAL/finalNOT_APPROVED.

Next: no new independent local implementation scope was identified; do not make
another mock/admin batch or suppress compiler complexity just to get green.
The additional compiler proof is incomplete; modular analysis may be revisited
only with a concrete coverage objective, not claimed as full-program/hardware
verification. Remaining actual ESP32/RTOS/WiFi/clock/PSA/NVS/powerloss/wear/stack/
heap/timing and hostedCI/SUP018/deployedTLS/directMySQL8/POSIX/operator gates need
external prerequisites and retain NOT_RUN. Serial-port metadata probe returned
none; this is not a full hardware inventory or permission to connect equipment.
Goal ACTIVE; completion unproven. Preserve WIP, enforce fail-closed isolated test
DB and explicit PHP8.2.35 for future PHP execution; NO PUSH. Only real scoped gate
PASS and security/diff/exact-index review permit any next local commit.

## Historical survey-readiness postcommit checkpoint (2026-10-27)

Actual develop HEAD `81e9bfbb36d357a55476bb44d985cd8fa095e4c5`, parent `98455c392562d582d34051b2dfd2171f80a27df2`.
Six-area Phase14 checklist and38-requirement software review COMMITTED:20exact
files; postcommit20/20 paths/blobs/worktree/manifest verified BEFORE this update.
Index EMPTY; all scoped mandatory gates PASS, staged and final read-only security
0findings/0privacy; no mutation between final scan and commit. NO PUSH.

Checklist PREPARED for propulsion,navigation,radar/echo/radio,electrical/low-power,
compartment sensors/local alarms/virtual start,data/uplink/disclosure. Existing
IF01..11,TBD01..08 and LOCKED selections unchanged. Survey NOT_RUN/physical
integration NOT_AUTHORIZED; no invented OEM/model/pins/thresholds/electrical
limits or resolved TBD answers. Phase12/13 exit gates remain open.

Actual new documentary gates:9commands0fail/45unit methods plus audits; current
38requirements/34cases/176references, both38row handoff matrices, full HTTP/MySQL/
SDK public source equality, LOCKED2/protected3/all6migrations/manual scope/diff/
security PASS. Source runtime/tests/CI/contracts/schema UNCHANGED. Prior matching
actual executions PHP388/TLS248/Chrome155/60047ms host outage/561cycles/broad248
commands and both prior SDK proofs are retained, NOT_RERUN by this documentary
batch. The first document-generation field-count failure was corrected/preserved.

Evidence: survey-readiness-summary/gate-matrix/files/manual-review/regression/
source-review/reference-audit/security-*-20261027.* and
`evidence/test-results/survey-readiness-postcommit-81e9bfb-20261027.json`.
Project review: docs/testing/local-software-review-20261027.md plus38row CSV;
checklist: docs/testing/vessel-survey-readiness.md. The preceding substantive
resilience70-file batch is COMMITTED98455c3 with postcommit70/70 proof.

Both handoffs automatically updated AFTER successful commit; these two edits and
new postcommit JSON are explicitly next-checkpoint UNCOMMITTED context WIP. The
committed20-file manifest refers to committed versions, not these later edits.
Preserve protected3untracked and old2metadata stat-cache entries byte-equal HEAD.
Cleanup0/welcomeDEFERRED; positive root-route replacement does not remove the
existing missing-tracked-file security-scanner dependency. Latest user selective
safe-cleanup policy overrides only old Goal rule11; PROTECTED/DEFERRED remain.

Current38:22IMPLEMENTED_UNVERIFIED/16PARTIAL, formal37PASS/1NOT_RUN;15SIM scopedPASS,
18SUP PASS/SUP018 PLANNED. No VERIFIED, no FMEA closure, systemPARTIAL/final
NOT_APPROVED. HardwareESP32/RTOS/WiFi/TLS/clock/PSA/NVS/powerloss/wear/fullstack/
heap/hardwaretiming/currentWokwi/hostedCI/SUP018/deployedTLS/directMySQL8/POSIX/
graphical operator acceptance NOT_RUN. No main DB/dotenv disclosure/globalPATH/
XAMPP/physical control/remote/destructive Git operation.

NEXT: the targeted38-requirement/roadmap review identifies no new independent
local implementation gap; this is not an exhaustive defect-free or project-
complete claim. Do not manufacture a mock, cleanup or administrative batch to
replace missing external prerequisites. Prioritize any newly reproduced safe
local defect; otherwise obtain actual independently authorized hardware/hosted/
deployment evidence before claiming those gates. Goal remains ACTIVE, not VERIFIED
or complete. No additional physical/remote/database authority is implied.
Any future substantive batch still needs scoped tests/integration/regression/
security/evidence/exact-scope local commit only all mandatory gates PASS, then
immediate BOTH-handoff update. Use actual Git HEAD at resume, not historical
checkpoint prose; NO PUSH.

## Historical survey-readiness precommit checkpoint (superseded by actual commit above)

Actual develop HEAD98455c392562d582d34051b2dfd2171f80a27df2; index20EXACT
files STAGED at this checkpoint. Prior resilience70files COMMITTED and postcommit70/70 proof PASS.
Current owned WIP: both handoff postcommit/context updates, resilience postcommit
JSON, six-area Phase14 survey checklist,38-requirement local review/CSV, README/
roadmap links and DOC001 living references. Readiness evidence/manifest will list
all final exact files. No production source/test/schema/CI/contract changes.

Six scopes: propulsion; navigation; radar/echo/radio; electrical/low-power bench;
compartment sensors/local alarms/virtual start; data/uplink/disclosure. Checklist
PREPARED, survey NOT_RUN/physical integration NOT_AUTHORIZED; no numeric limits,
OEM protocol, physical model, pins or TBD answers invented. Open Phase12/13 gates
are not advanced. The local review found no new independent implementation gap
in its targeted38requirement scope; not an exhaustive defect-free/system-complete
claim. Current matrices22IMPLEMENTED_UNVERIFIED/16PARTIAL and formal37PASS/1NOT_RUN
remain unchanged. Full38table below includes current DOC001 references.

Pre-stage mandatory documentary gates PASS:9commands0fail/45unit methods,
current38requirements/34cases/176refs, full HTTP/MySQL/SDK snapshot equality,
LOCKED2/protected3/all6migrations, manual semantic/security/scope/diff and fresh
working scanner0findings0privacy. Prior actual runtime results are source-bound,
NOT_RERUN here. Final exact20file manifest is survey-readiness-files-20261027.csv;
initial exact index20 paths/blobs/manifest/worktree and staged scanner0/0 PASS.
Final metadata-stage equality recheck and last read-only scan are still REQUIRED
before local commit. No commit may be claimed until Git records it. After successful commit update BOTH
handoffs immediately with actual HEAD/postcommit evidence and explicit context WIP. Preserve protected3untracked/LOCKED2/all6migrations/old2statcache entries;
cleanup0/welcomeDEFERRED, NO PUSH. External ESP32/RTOS/WiFi/NVS/powerloss/wear/
fullstack/heap/physical timing/hostedCI/SUP018/deployedTLS/directMySQL8/POSIX/
graphical operator acceptance remain NOT_RUN; finalNOT_APPROVED/systemPARTIAL.

## Historical resilience postcommit checkpoint (2026-10-27)

Actual develop HEAD `98455c392562d582d34051b2dfd2171f80a27df2`, parent `4892054dc4aed578702e102f17f31dc459668a63`.
Six related resilience scopes COMMITTED:70 exact files; postcommit70/70 committed
paths/blob bytes/manifest/worktree verified BEFORE this handoff update. Index
EMPTY; final staged and read-only security0findings/0privacy; all scoped mandatory
gates PASS. No source mutation between final scan and commit; NO PUSH.

Actual PHP8.2.35/Laravel12.70.0/MariaDB10.4.32 approved isolated testing target:
388tests/0FAIL/0SKIP; effective configuration/key/overrides/catalog isolation PASS.
Actual readonly host outage60047ms/561nativecycles/538exhausted/maxgap110ms,
3real503 then explicit reset/up200, invalid->STALE->VALID ordered original alarm
facts PASS. Separate actual TLS/native/API/UI/directDB248checks, actual approved
Chrome155 component, independent current-source case review, broad248/248command
regression/core226repeat2, security0/0 PASS. See formal-resilience-summary,
gate-matrix,current-case-review,files and postcommit-98455c3-20261027 evidence.
Production firmware/6migrations unchanged; SDK retained source proof f693 unchanged,
NOT_REBUILT this batch. No hardware/RTOS/WiFi/NVS/power-loss proof is implied.

Current formal portfolio15SIM scopedPASS/18SUP PASS/SUP018 PLANNED; living38:
37formalPASS/1NOT_RUN, implementation22IMPLEMENTED_UNVERIFIED/16PARTIAL; no VERIFIED.
System PARTIAL/final NOT_APPROVED. Physical ESP32/RTOS/PSA/NVS/powerloss/wear/
fullstack/heap/timing/currentWokwi/hostedCI/deployedTLS/directMySQL8/POSIX/graphical
operator acceptance NOT_RUN. Both full38matrices below reflect current living CSV.

Both handoffs automatically updated AFTER successful commit; these two edits and
new postcommit JSON are explicitly next-checkpoint UNCOMMITTED context WIP.
The committed70-file manifest describes committed blobs, including the previous
handoff versions, not these subsequent context edits. Preserve this WIP.
Protected AGENTS.md/two firmware untracked and LOCKED2 unchanged; old two metadata
stat-cache entries byte-equal HEAD/excluded. Cleanup0/welcomeDEFERRED. No main DB,
secret output, PATH/XAMPP change, physical control, remote or destructive Git.

NEXT: targeted requirement/roadmap completion audit for remaining safe local
software gaps; do not repeat existing implementation or baseline audit. Distinguish
hardware-dependent unknowns from actionable software defects. Phase14 survey
readiness preparation appears absent and needs dependency/scope assessment;
no physical integration or guessed OEM/pin/power/threshold facts authorized.
All future batches need scoped tests/integration/regression/security/evidence,
exact-scope commit only if mandatory gates PASS, then update BOTH handoffs.
Continue Goal; NO PUSH.

## Historical resilience precommit checkpoint (superseded by actual commit above)

Actual develop HEAD4892054dc4aed578702e102f17f31dc459668a63; index70EXACT files STAGED
at this checkpoint (formal-resilience-files-20261027.csv). Goal ACTIVE after user restored approved testing DB.
Six related scopes implemented; current FUNCTIONAL/BUILD-SOURCE-BINDING/REGRESSION/
independent case review gates PASS. Latest docs/living38_34_173/manual scope/current248regression and working
security0_0,initial exact-index70 and staged-scanner0_0 PASS; final metadata-
stage equality and last read-only scan still REQUIRED before local commit; do not claim a commit until Git records
it. All previous blocked/crashed/interrupted evidence preserved, now superseded
by current actual runs; no baseline re-audit or repeated implementation.

ACTUAL current PHP8.2.35/Laravel12.70.0/MariaDB10.4.32 approved target
127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex388/0FAIL/0SKIP,all effective
overrides/cipher-compatible ephemeral process key/exact10tables6migrations0appRows
PASS. Dedicated NO_DB_WRITE readonly host TLS60047ms PASS,561subsequent shared
C99 cycles/538exhausted/maxgap110ms,3real503 then1explicit-reset Laravel/up200.
Native one temperature invalid/null plus engine3 RPM1500;other43current. Network
restores while sensor invalid,STALE65 still alarms;only VALID30/normal2010 gives
original ordered2raise/2clear metadata facts,no ACK or HTTP-driven retirement.

Separate normal actual TLS/native/API/UI/directDB gate248checks PASS,4fast native
frames/4events,all44channels/original metadata/null/source/test identity mapping
and exact cleanup0rows. Host actor uses existing C99 provider/policy/scheduler/
alarm/journal and bounded net001_host_step,not ESP32 main/SDK workers/RTOS/WiFi.
Fast DB integration and2s/4s Chrome fixture do not replace the actual60s host case.
Independent current-source reviewer PASS in formal-resilience-current-case-review-
20261027.json;3existing SIM010/012/013 accepted HOST_ONLY/NO_DB_WRITE. All15SIM
scoped PASS,18SUP PASS/SUP018 PLANNED;derived37PASS/1NOT_RUN. Implementation stays
22IMPLEMENTED_UNVERIFIED/16PARTIAL,no VERIFIED. Both full38matrices below synced.

Chrome155 component PASS via approved outside-sandbox execution on SAME source/
flags:LIVE_STALE_OFFLINE,SecureHttpOnlyLax/CSRF/session,noPolling,SNAPSHOT without
script/asset and UNKNOWN invalid timing,all4labels/exact profile+row cleanup.
Inside sandbox Page.enable crashes before UI,CDP_CLOSED/exit2147483651 reproduced
on new/existing owned targets;raw stderr not copied. Exact Chrome internal cause
unproven;approved outside execution resolves gate without security/deadline/
expectation weakening,personal profile or kill-by-name. Local HTTP localhost
browser edge to strict HTTPS upstream is not deployed browser TLS.

Current HTTPsource81fa45d15a8f800e85cbf82048df8086640f26dc88a63275746424282ceab49f;
MySQL516446eb3db89042116ca6ab4a216a06f018e4511af6ebb8a72dbd2b49e08037;
SDKf693b0cb1a77d73b8c8cc97eb65da23703a6da9c1bd7e767dfcc1f6a259631e6 unchanged
and bound to both committed actual candidate/retained SDK proofs,NOT_REBUILT here.
Broad248/248commands/core226repeat2/native12/HTTP26/previousretry4/Node13 PASS;
working scanner0findings0privacy. Initial5INFO byte-equal parent CI2/runtime3
nonsecret expressions have append-only exact pins,detector unchanged. Native
parser bounded against overflow;first2010RPM oracle correction/failures retained.

Current source/proof/summary/gate matrix/case review are in formal-resilience-*
family dated20261027. Both handoffs and previous retry postcommit JSON are owned
WIP included in the eventual reviewed manifest. Production firmware and6migrations
unchanged;no new roundtrip,prior SUP014 retained. LOCKED2/15scenario definitions/
AGENTS/two firmware untracked unchanged;old2metadata entries byte-equal HEAD and
excluded. Cleanup0/welcomeDEFERRED;no main DB/dotenv/globalPATH/XAMPP/physical
control/remote/history action. Hardware/RTOS/PSA/NVS/powerloss/wear/fullstack/heap/
timing/currentWokwi/hostedCI/deployedTLS/directMySQL8/POSIX/graphical operator
acceptance NOT_RUN;systemPARTIAL/finalNOT_APPROVED.

NEXT: pre-stage metadata/reference/doc/guard/format/manual/working-security
gates PASS. Final current staging authority is formal-resilience-files-20261027.csv;
older wip-files CSV is the immutable historical44file blocked snapshot. Verify
final exact manifest,
stage exact files only after all pre-stage gates PASS,verify every index blob/
manifest/branch/parent/protected/diff gate,staged and final read-only scanner,then
local commit. Update BOTH handoffs immediately after successful commit and
continue targeted remaining safe software Goal assessment;NO PUSH.

## Historical retry-ordering postcommit checkpoint (2026-10-27)

Actual develop HEAD `4892054dc4aed578702e102f17f31dc459668a63`, parent `bf29a8bbc28a757cdd932f66287b4984530c1ad3`.
Five related failed-event retry scopes COMMITTED:48 exact files; postcommit
48/48 committed paths/blobs/manifest/worktree verified before this handoff update.
Index EMPTY; final read-only security0findings/0privacy; all scoped mandatory
gates PASS; no source mutation after final scan and before commit; NO PUSH.

Actual current evidence: PHP8.2.35/Laravel12.70.0/MariaDB10.4.32 approved isolated
target388/0FAIL/0SKIP, strict real TLS225 checks including committed-response loss,
duplicate200/fullmetadata/count1 and SAME-owner retrytag2/durable host retirement;
Chrome155 component expiry/fallback/noPolling/ownedcleanup; broad247/247 commands,
core226repeat2/owner13/newretry4/file6/HTTP24/MySQL32/Node13; BOTH actual SDK builds
PASS. See event-delivery-retry-summary/gate-matrix/source-proof-20261027.* and
`evidence/test-results/event-delivery-retry-postcommit-4892054-20261027.json`. The initial parent oracle failure is a preserved
bug reproduction, not a failure of current mandatory gates. No actual SDK worker
retry/RTOS/NVS/PSA/power-loss/hardware proof from the host fixture.

Both handoffs automatically updated AFTER commit; these two edits and the new
postcommit JSON are explicitly next-checkpoint UNCOMMITTED context WIP. All retry
feature code and its48-file manifest/evidence are committed. Preserve this WIP.
Protected AGENTS.md/two firmware untracked unchanged; old two metadata stat-cache
entries byte-equal HEAD/excluded. No deletion, main DB/dotenv, LOCKED/migration,
global PATH/XAMPP, physical-control or remote operation. Cleanup welcome DEFERRED.

38 requirement implementation22IMPLEMENTED_UNVERIFIED/16PARTIAL; formal32PASS/
2PARTIAL/4NOT_RUN unchanged, no VERIFIED. SIM010/012/013/SUP018/physicalESP32/
RTOS/PSA/NVS/powerloss/wear/fullstack/heap/timing/currentWokwi/hostedCI/deployedTLS/
directMySQL8/POSIX/graphical operator acceptance remain NOT_RUN/PLANNED.

NEXT: continue substantive local software/formal-simulation gaps after reading
existing outage coordinator/transport reset contract and fixed scenario stimuli.
Investigate SIM010 actual60s API outage, SIM012 concurrent sensor/network/engine
faults and SIM013 valid-data recovery without inventing automatic exhausted
transport resets or treating host proof as hardware. No new implementation of
these three cases yet. Keep Goal ACTIVE, no repeated baseline audit; tests and
security/traceability/exact-index gates before any next local commit.

## Historical retry-ordering precommit checkpoint (superseded by actual commit above)

Actual develop HEADbf29a8bbc28a757cdd932f66287b4984530c1ad3; index48EXACT
files STAGED at this checkpoint (manifest event-delivery-retry-files-20261027.csv).
Previous receipt-display76file commit/postcommit audit is complete. New coherent
5scope failed-event ordering batch is implemented; FUNCTIONAL/BUILD/REGRESSION/
docs38/34/167/manual/working-and-staged-security0/0/exact-index48 gates PASS.
Final metadata-stage byte recheck and read-only security scan still REQUIRED
before local commit. Do not claim the batch committed until Git actually records it. Do not stage/commit until applicable pre-stage gates PASS; never push.

Actual bug reproduced against pinned parentbf header:2retained facts/head1, cursor
advanced onqueue to1, failed completion closed owner and next selection picked2.
Current receive_http(owner,completion,context) validates immutable source/index/
boot/fullmetadata/epoch and rewinds only failed EVENT cursor, no forward new-view
movement, stale-tag mutation, false ACK/deletion or alarm clear. Alias/invalid
context fails closed. SDK caller and actual host fixture use3args. The baseline
Cfixture remains unchanged/old2args, compiled only against copied pinned parent
header in fresh owned temp root. Current equivalent addscontext and pickshead1.
CI source fetch-depth0 provides pinned history; no local fetch/test skip. Explicit
exhausted transport reset, bounded retry, crypto/IO and bounded-unretired publication
contracts retained. No new external API/schema/policy defaults/physical control.

Real private TLS proxy one-shot fault is server-object-only, exact owned POST/
UA/bodySHA/committed200or201 then drops peer before reply. Guarded READ_ONLY
--retry-audit confirms exact owned boot/event1/full metadata/count1 before/after.
Native retry status0/body/no receipt emits identical original, changes no slots/
floor/release. Actual200duplicate receipt then retry-current reproduces failedtag1
and submits retrytag2 on SAME owner; genuine host-file commit/readback releases
only prefix1, nexttag3 and all alarm records unchanged. This multi-command host
logical continuation does NOT execute SDK network-worker attempt budget/RTOS or
physical reboot. Existing state/quality/source/null/zero/alarms/UI remain tested.

ACTUAL current gates: PHP8.2.35/Laravel12.70.0/MariaDB10.4.32 approved
127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex388/0FAIL/0SKIP +receipt crosscheck
and final10table/6migration/0appRow postflight PASS; TLS225 with real loss/count/
retry/durable host retirement/exact cleanup PASS; Chrome155 expiry/fallback/
noPolling/SecureHttpOnlyLax/profile/rowCleanup PASS; broad247/247commands/core226
repeat2/owner13/newretry4/file6/HTTP24/MySQL32/Node13 PASS. All existing plus new
tests retained. Initial5scanner findings/0privacy were stale whole-file pins on
5byte-equal parent CI/runtime nonsecret expressions; append-only exact file/line
reviews added, detector unchanged. Current framework scanner inside247run PASS0/0;
fresh final working/staged/manual scope gates still required. No actual credential
or raw MAC/body/cookie/profile/environment copy in evidence.

CURRENT source proofs, actual source-bound logs in event-delivery-retry-* family:
HTTPf1396e27191edd9f080bb70851ab4255773226cf9b00765f942ef7d2ddc0de08;
MySQL516446eb3db89042116ca6ab4a216a06f018e4511af6ebb8a72dbd2b49e08037;
SDKf693b0cb1a77d73b8c8cc97eb65da23703a6da9c1bd7e767dfcc1f6a259631e6.
Actual2SDK logs esp32-transport-sdk-build-event-retry-{candidate,retained}-20261027.txt:
 candidate image986544/RAM57532/ownframe1040/merged2741d4d9498cde22be2bc80d97190849b0ab39c48d5985b441acf73efd028d86;
 retained1045472/RAM66436/ownframe1616/mergedc3fe8b253a60165e5df455b7b1d718577bbc4129b7d882b9595586918a510070.
TLS/root bundle/assertions/1MiB partition/2048ownframe checks PASS, source stable;
retained has3104image bytes margin. No upload/erase/hardware/fullstack/heap proof.
Three protected untracked hashes unchanged after both actual builds. Current
source-proof JSON binds all actual logs/counts/binaries. Earlier837536ad first225
prototype run retained as historical; final run2 f1396e27 is authoritative.

Evidence summary/gate matrix/source-proof/security-triage/current247log are dated
20261027; protocol/reproduction/firstowner13log are20261026 (work spans midnight).
All6migrations unchanged, roundtrip NOT_RERUN this batch; prior actual SUP014 remains
committed, current exact catalog verified. Four related living38 rows and BOTH
complete38matrices updated; README/roadmap/architecture/FMEA have dated software
observations without LOCKED/IF/hardware/TBD/formal changes or hazard closure.

Actual WIP:2firmware files, receipt bridge/file fixture, private PHP/HTTP runner,
owner/native retry/file/lifecycle tests, CI registration/history, living/status/
architecture/FMEA/README docs, both handoffs, prior postcommit JSON and new dated
code/repro/tests/SDK evidence. Inspect actual Git list. Old metadata statcache
entries remain byte-equal/excluded. Preserve AGENTS.md and two firmware untracked,
all source/history/evidence/private config; removed0/welcomeDEFERRED. No main dotenv/
DB/globalPATH/XAMPP/physical-control action. Formal32PASS/2PARTIAL/4NOT_RUN and
22UNVERIFIED/16PARTIAL unchanged. SIM010/012/013/SUP018/ESP32physical/RTOS/PSA/NVS/
powerloss/wear/fullstack/heap/timing/currentWokwi/hostedCI/deployedTLS/directMySQL8/
POSIX/graphical operator acceptance NOT_RUN/PLANNED; no VERIFIED, systemPARTIAL.

NEXT: final read-only living38/reference/doc/guard checks, encode/whitespace audit
ONLY new owned logs (preserve raw/stored hashes and every assertion/failure),
manual security/scope and fresh scanner; exact manifest incl2SDK logs and prior
postcommit JSON. Stage exact files only pre-stage PASS, verify every index blob/
manifest/protected/parent/branch/diff gate, final scanner0/0 then local commit.
Update BOTH handoffs immediately after successful commit, continue main software
Goal/remaining independent gaps. Do not treat one commit or status counts as
completion. NO PUSH/history rewrite/remote action. No repeated baseline audit.


## Current receipt-expiry postcommit checkpointbf29a8b (2026-10-26)

Actual branch develop, HEAD `bf29a8bbc28a757cdd932f66287b4984530c1ad3`, parent `2b00013b6936083be18bda72d1d0e563d6482f25`.
Six related UI receipt-display/browser scopes COMMITTED76exact files after ALL
mandatory local gates PASS. Postcommit actual76/76committed paths/blobs/manifest/
worktree equality PASS; index EMPTY, NO PUSH. Final read-only scanner0findings/
0privacy, no source/file mutation after final scan before local commit. One blank
wrapper-line trailing space caught by cached diff gate was corrected with raw/
stored SHA audit, then exact index/diff gate reran PASS. All failures preserved.

Actual current PHP388/0FAIL/0SKIP, strict localTLS215, real Chrome155 expiry/fallback/
Secure/HttpOnly/Lax/no polling and exact profile/row cleanup PASS. Broad246/246
commands/core226repeat2, Node13groups, bridge8guards, HTTP24lifecycle, MySQL32guards,
and late delta4 PASS. Current HTTPsourcefd71a424a51b5999385504e4b1dc2af1016d1b477cab3357a1432285f6180ee7;
MySQL445025acd4df90ada8af97ebfc3ef3a8e4da02287cb10df89f1d5df1f1a6cc12.
SDKsourcea0a0eac0809da2b9be93c67a8347c3f50766b3bed163ec7d42a1e4b86fb8bf95
unchanged/matches two committed actual SDK proofs. No new firmware/migration/
LOCKED/secret/mainDB change, physical-control feature or repository deletion.

Both handoffs automatically updated/saved AFTER commit; these two context edits
and `evidence/test-results/receipt-expiry-postcommit-bf29a8b-20261026.json` are explicit next-checkpoint UNCOMMITTED WIP, not unfinished
receipt feature code. Preserve them. The committed76path manifest and gate matrix,
source proof/triage/summary/actual logs remain immutable evidence of this batch.
Full38matrix below/livingCSV synced. Reference38/34/163PASS, formal unchanged
32PASS/2PARTIAL/4NOT_RUN and implementation22UNVERIFIED/16PARTIAL. SIM12PASS/
3NOT_RUN; SUP18PASS/1PLANNED. SystemPARTIAL/finalNOT_APPROVED; no VERIFIED claim.

Remaining SIM010/012/013, SUP018, actualESP32/RTOS/NVS/powerloss/wear/fullheap/
callstack/timing/currentWokwi/hostedCI/deployedTLS/directMySQL8/POSIX/graphical
operator acceptance NOT_RUN/PLANNED. Actual browser component used HTTP localhost
edge to strict verified HTTPS upstream, not deployed browser HTTPS proof. Browser
expiry is display-only and not physical sensor freshness or real-time guarantee.
Pre-fixture relay timeout root cause was not inferred; bounded startup admission
still requires healthy200, per-request/race15sec bounds intact, current gates PASS.

Continue Goal immediately with a targeted remaining-software assessment against
actual38requirements/roadmap/dependencies; no repeated baseline, no invented new
requirement, redundant implementation or administrative-only batch. Find actual
safe local gaps and coherent5-7related scopes; if none can be proven closed, keep
Goal active and gather stronger evidence. Do not declare completion from green
checks or status counts. Verified Safe Cleanup policy still applies, removed0/
welcomeDEFERRED/protected AGENTS+two firmware untracked unchanged. Exact-scope local
commit only all mandatory gatesPASS, no push/remote/history rewrite/mainDB/secret
exposure. Both handoffs update again at every safe major checkpoint.


## Historical receipt-expiry precommit checkpointbf29a8b (2026-10-26)

Actual develop HEAD `2b00013b6936083be18bda72d1d0e563d6482f25`; index EMPTY at
this safe checkpoint. Previous fault/storage/reference batch60files COMMITTED.
New coherent six-scope UI001 batch UNCOMMITTED; all functional/regression gates
PASS, working scanner0findings/0privacy. Exact final docs/scope/stage/index/security
review still required before LOCAL commit. NO PUSH; do not duplicate implementation.

Implemented and tested real open-page receipt expiry LIVE->STALE->OFFLINE without
polling or value/source/quality/alarm mutation; server conservative millisecond
budgets; four consistent labels; neutral SNAPSHOT fallback if no script/asset,
UNKNOWN for invalid/unsafe policy/timing, cache/hide/freeze/rewind; optional asset
absent on server keeps authenticated snapshot200. External first-party JS with
narrow CSP; login/list/denials/errors still no script; CSRF/grants/cookies retained.
Browser timing is not hard real-time or physical measurement freshness; replay
receipt provenance explicit. Chrome155 fresh owned profile, actual session/CSRF/
Secure/HttpOnly/Lax, fixed UI-only HTTP localhost to verified HTTPS upstream;
not deployed browser TLS, graphical operator acceptance or hardware evidence.

Actual PHP8.2.35/Laravel12.70.0/approved MariaDB10.4.32 target
127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex:388PASS/0FAIL/0SKIP, receipt
crosscheck and independent10tables/6migrations/0app-row final postflight PASS.
No migration/schema/main dotenv/DB or firmware changes. Actual current TLS215,
Chrome expiry/fallback,246/246regression commands/core226repeat2, Node13unit groups,
bridge8guards, HTTP24lifecycle and MySQL32guards PASS. Earlier failures retained:
form Origin:null admission/selector/module/old CSS/source-guard expectations and
scanner encoding/pins. Intermittent pre-fixture relay TimeoutError root cause not
inferred; bounded read-only startup admission60sec still requires healthy200,
per-request/race15sec bounds retained; exact-context patch mistakes corrected.

Current source proofs: HTTPfd71a424a51b5999385504e4b1dc2af1016d1b477cab3357a1432285f6180ee7;
MySQL445025acd4df90ada8af97ebfc3ef3a8e4da02287cb10df89f1d5df1f1a6cc12;
firmware/SDK a0a0eac0809da2b9be93c67a8347c3f50766b3bed163ec7d42a1e4b86fb8bf95
unchanged/matches two committed actual SDK builds, no hardware or rebuild claim.
Evidence: evidence/test-results/receipt-expiry-summary-20261026.md,
normal-exact-scope-final/browser-exact-scope-final/mysql-final/integrated-regression-final,
source-proof/security-triage/security-working-final/encoding-review/reference-audit
(all receipt-expiry-20261026family). Detailed complete38matrix below and living CSV.
Current reference checkpoint38requirements/34cases/163refs PASS; latest inventory
at final docs checkpoint can differ. Both handoffs physically saved in repository.

All current diff is owned UI/test/tool/CI/evidence/docs WIP; exact inventory will
be evidence/test-results/receipt-expiry-files-20261026.csv. Preserve protected
AGENTS.md and two firmware untracked byte-for-byte, old metadata stat-cache evidence
byte-equal/excluded. Requirements LOCKED/migrations unchanged. Removed0/welcome
DEFERRED. Latest Verified Safe Cleanup policy supersedes Goal rule11 only; no
cleanup scope here. Preserve original38 and full previous commits/evidence.

Formal32PASS/2PARTIAL/4NOT_RUN; implementation22UNVERIFIED/16PARTIAL. SIM12PASS/
3NOT_RUN, SUP18PASS/1PLANNED. SIM010/012/013 and SUP018, physical ESP32/RTOS/NVS/
powerloss/wear/fullheap/callstack/timing/currentWokwi/hostedCI/deployedTLS,
directMySQL8/POSIX/graphical operator acceptance NOT_RUN/PLANNED. SystemPARTIAL/
finalNOT_APPROVED. No requirement VERIFIED. Continue remaining local software Goal:
final exact local commit only all gates PASS, immediately update BOTH handoffs
with actual resulting HEAD and uncommitted context, then targeted remaining-scope
assessment against roadmap/dependencies. Do not stop at this document or one commit.


## Historical fault/storage/reference postcommit checkpoint2b00013 (2026-10-26)

Actual branch develop, HEAD `2b00013b6936083be18bda72d1d0e563d6482f25` (2b00013). Seven-scope batch committed60
exact files after ALL mandatory local gates PASS. Final read-only staged scanner
0findings/0privacy; exact60blobs/index/worktree/manifest equality PASS. Postcommit
60/60committed paths/blobs/manifest/worktree equality PASS, index EMPTY. NO PUSH.
Both handoffs are saved and automatically updated AFTER commit; these context
edits are explicit next-batch WIP, never unfinished fault/storage implementation.
Requirements LOCKED, all6used migrations and three protected untracked files
unchanged; old metadata stat-cache entries byte-identical/excluded. Removed0,
welcome DEFERRED/present/unchanged. All source and test/evidence files below are
COMMITTED; earlier pending precommit descriptions are historical.

Actual current382PHP/0fail/0skip,215realTLSchecks,241broad commands,32MySQL guards,
12reference guards/38requirement34case157reference audit,11native fault/file tests,
G1 64/G2 2/core226repeat2 and scoped receipt/owner regressions PASS. Exact empty
approved catalog after suite verified, public source stable. Four case admissions
SIM011/SUP013/SUP014/SUP017; formal32PASS/2PARTIAL/4NOT_RUN, implementation unchanged
22UNVERIFIED/16PARTIAL. Hardware/runtime/hostedCI/deployedTLS and SIM010/012/013/
SUP018 remain unperformed; systemPARTIAL/finalNOT_APPROVED, no VERIFIED claim.

Next targeted residual UI001 audit is authorized and has only read source/tool
availability so far, NO new runtime edit or browser launch. Current controller
classifies receipt at authenticated GET; Blade has no script/timer, age/status
remain static in an already-open document. Primary dashboard contract specifies
manual authenticated refresh, no fabricated live feed. Assess display expiry/
clear snapshot provenance while respecting that contract; do not invent physical
measurement time, automatic data updates or a new locked requirement.
Node22.20.0 is installed, native WebSocket exists; local Chrome and Edge binaries
present, Playwright/Puppeteer/jsdom not found. Availability is not browser PASS.
Actual browser/component verification should use a fresh owned test profile,
approved isolated backend fixtures and strict upstream TLS; no certificate bypass,
personal browser profile, main dotenv/DB, global PATH or production change. Review
new coherent scope/protocol before execution. Continue Goal beyond this checkpoint.


## Historical precommit fault/storage/reference checkpoint (now committed2b00013)

Actual/current parent develop777d762be36f9e778b9dd259476a28d42393e39f, index
60exact files STAGED for final commit checkpoint. Previous data/UI54file batch is COMMITTED/verified.
This UNCOMMITTED batch has7related scopes: SIM011 actual C99 single-channel
isolation; SUP013 bounded72generation two-slot host-file integration; independent
native/CRC/state oracles;5actual raw-C99/backend/read/UI methods; SUP014 guarded
schema rollback/reapply; source/postflight/CI/security/evidence/continuity;
separate SUP017 public-reference audit. No new migration or repository deletion.

Actual mandatory functional gates PASS: PHP8.2.35/Laravel12.70.0/approved MariaDB
382/0fail/0skip after Laravel6migration rollback/apply/reapply, receipt crosscheck,
independent final10table/6record/0app-row catalog postflight and public-source
stability; current post-registry existing-schema rerun382/0fail/0skip also PASS.
Actual private TLS215checks/exact owned cleanup PASS after shared callback header
extraction; native4frames/44domain channels/43unaffected current channels, two
invalid/null temperature observations and advancing engine values PASS; actual
host-file72generations, original8bootA critical facts/metadata, latest bootBseq8,
floor0, RAM166/disk51refusal attempts, slots3332/3344bytes, older-slot corruption
preserves latest then healthy reopen after restoring only owned test byte PASS.
Host commit/reopen NEVER physical ESP32/NVS/power-loss durability.

Current broad241/241commands PASS; earlier240/240 retained separately, not added.
Native11methods, MySQL32guard methods, public-reference12methods, existing receipt
file4/owner8/HTTP22, G1 64/64/G2 2/2 and necessary delta7/5groups PASS. Source and
post-suite catalog gate bugs reproduced/fixed; duplicate canonical case shadowing
reproduced against777read-only code and fixed, plus strict definitions/headers/
public path/report guards. No previous real DB leak or production incident is
asserted by those negative orchestration reproductions. All failures retained.

Dedicated SUP017 audit/report before and after promotion PASS38requirements/
34cases,147initial/157postpromotion file refs. Original LOCKED mappings, actual
plan definitions/types/lead IDs, regular safe in-repo paths/hashes and evidence
links checked. Exact existing .env.example link is METADATA ONLY, sha:null; no
content open/hash/credential assumption. NOT_RUN/PLANNED never inferred PASS.
Final postdocs157reference inventory/source/protected/LOCKED/manual scope review PASS; working and staged security0findings/0privacy PASS. Exact final60blob/manifest and read-only staged scanner recheck remain mandatory before local commit. Initial scanner5known existing byte-equal
CI/runtime expressions/0privacy reviewed; final CI registration renewed2same CI
pins, no new literal or detector change. Broad embedded current scanner0/0PASS.

Pre-execution protocols: docs/testing/formal-fault-storage-cases-20261026.md and
formal-public-reference-audit-20261026.md. SUP014 explicitly revises only historical
operational target to user-approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex,
MariaDB10.4.32 driverMySQL, PHP8.2.35 explicit. Old pinned matrix/preparation SHA
and all6migration sources unchanged. Main dotenv/DB never booted; test key is
process-generated ephemeral/cipher-compatible, never printed/copied.

Current source proofs: native9c3a6f4b767fc6a557ddbdbb3d1be7d6626cce5455d0ae5317dba4b073834397;
HTTPd0f38223407a2701fcdc96a810912d3e0b91b101dd271fc58fed0f7d174846f4;
MySQL37beceaec5b9089e36945e863901583fc10099996fe26f11817586becdb9aabe;
firmwareSDK a0a0eac0809da2b9be93c67a8347c3f50766b3bed163ec7d42a1e4b86fb8bf95
unchanged, identical committed candidate/retained actual SDK proof reused. Shared
file callbacks were extracted BYTE-EQUAL777 into scripts/host_offline_file_io.h;
strict C99 flags preserved. Tool/reference protocol and registry hashes are in
the actual audit JSON. Public-log LF normalization preserves raw-to-LF SHA mapping.

Four cases now have their dedicated local evidence: SIM011/SUP013/SUP014/SUP017.
Derived38formal32PASS/2PARTIAL/4NOT_RUN; implementation unchanged22UNVERIFIED/
16PARTIAL, no VERIFIED. SIM12PASS/3NOT_RUN, SUP18PASS/1PLANNED. See full38matrix
below and evidence/test-results/fault-storage-summary-20261026.md, case-review,
source-proof and actual logs. Dynamic UI evidence-table captures are point-in-time
before promotions; they are not code or hardware approval. SystemPARTIAL/final
NOT_APPROVED. SIM010/012/013 and SUP018 remain unperformed. No push.

Actual uncommitted paths include both handoffs/current status docs and CSVs, CI,
scripts/event_retirement_file_fixture.c (helper extraction), run_live_http_integration.py
(dependency snapshot), run_mysql_integration.py (seventh native fixture, source
freeze and final catalog admission), guard tests/review pins and existing living
checker hardening. New source: fault_isolation_fixture.c, fault_isolation_wire_bridge.py,
formal_offline_file.py, host_offline_file_io.h, offline_bounded_file_fixture.c,
run_formal_fault_storage.py, test_formal_fault_storage.py, test_public_reference_audit.py,
backend/laravel/tests/Feature/SingleChannelFaultIntegrationTest.php;2protocols,
evidence prefix fault-storage-. Preserve ALL preexisting user/protected/untracked
files and historical evidence. Removed0; welcome still DEFERRED/present/unchanged.

Next safe checkpoint: final source/hash/LOCKED/protected/scope/working/staged
security/manifest exact review and local develop commit only allmandatoryPASS;
update BOTH actual HEAD/WIP immediately afterward. Continue targeted residual
software assessment, including UI001 freshness semantics for an already-open
page/replayed samples and available local browser/runtime tools, before declaring
all safe local work complete. This is a candidate audit, not an assumed bug or
new requirement. Remaining unavailable hardware/currentWokwi/hostedCI/deployedTLS/
directMySQL8/POSIX/graphical stay NOT_RUN. No Goal-complete claim.

## Historical data/UI postcommit checkpoint777d762 (2026-10-26)

Actual branch develop, HEAD `777d762be36f9e778b9dd259476a28d42393e39f` (777d762). Data/UI batch committed54exact
files after ALL mandatory local gates PASS; final read-only staged scan0findings/
0privacy, exact54blob/index/worktree/manifest proof PASS. Postcommit54/54committed
paths/blobs/worktree and manifest equality PASS; index EMPTY. NO PUSH. Requirements
LOCKED and three protected untracked files unchanged. Metadata stat-cache entries
remain byte-identical/excluded; welcome template unchanged/present, DEFERRED.

Both handoffs are saved and automatically updated AFTER this commit. These
postcommit context edits are explicit next-batch WIP; runtime/native/PHP/data-UI
implementation and its54file inventory below are COMMITTED, not unfinished.
Current six-case/38matrix/source proof and counts below remain valid:377PHP,
215actualTLS,30native frames/1158channels; formal28PASS/3PARTIAL/7NOT_RUN and
22IMPLEMENTED_UNVERIFIED/16PARTIAL, no VERIFIED/system-complete claim.

Next related safe software batch: dedicated SIM011 single-channel isolation;
SUP013 bounded offline latest/journal host-file integration; SUP014 explicit
approved-target protocol revision plus guarded existing-schema rollback/reapply;
negative/boundary/security/evidence/regression/CI/traceability updates. Review
case classes before execution. Preserve old pinned protocol whose SUP014 target
name is historical; user-approved target remains vessel_gateway_codex_test/
vgw_codex at127.0.0.1:3307, PHP8.2.35 explicit. Do not claim hardware/SDK worker
execution from host fixtures. No deletion or cleanup-only administrative batch.


## Historical precommit data/UI checkpoint (now committed777d762) (2026-10-26)

Parent/current develop0507fc90b63aea8aec3ee32a722a38e25c5d3147;54exact files
staged for final commit checkpoint. At this historical precommit checkpoint, seven related scopes were UNCOMMITTED (now committed777d762):
secure fixed root redirect with GET/HEAD/query/security/error coverage; retained
ExampleTest expanded to5methods; actual native identity/null/zero contract oracles
and runner; source variants/direct scoped DB audits; real TLS/session/grant/eight-
section semantic capture; separate read-only evidence reviewer/adversarial tests;
CI/status/evidence/cleanup policy and BOTH saved handoffs. No existing work removed.

Actual gates PASS: PHP8.2.35/Laravel12.70.0/approved MariaDB377,0fail,0skip;
actual private TLS215checks/exact owned0row cleanup; native30frames/1158channels,
166valid zeros/175unavailable/69stale, noDB unit; six-case read-only review; inherited
237successful commands plus initially failing security command now rerunPASS
(238unique resolved gates); final7changed/security/G1/G2 groups PASS. Initial
failures retained. Security five existing source candidates reviewed byte-equal
parent and exact file/line pins renewed; working0findings/0privacy, detector intact.
Staged security0findings/0privacy and manual scope/logic/evidence review PASS. Final exact54blob/manifest and read-only staged scanner recheck remain mandatory before local commit.

Current six local case promotions: SUP002/011/012/015 and SIM014/015; SUP15PASS/
4PLANNED, SIM11PASS/4NOT_RUN; derived38formal28PASS/3PARTIAL/7NOT_RUN. Implementation
unchanged22IMPLEMENTED_UNVERIFIED/16PARTIAL; no VERIFIED/system completion. See
full synchronized38matrix below, canonical CSVs, pre-execution protocol
 docs/testing/formal-data-ui-cases-20261026.md and evidence/test-results/data-ui-
summary-20261026.md plus case-review/case-results/final logs. SUP015 reviewer is
NO_DB_WRITE; separate actual integration producer writes approved owned DB/session
fixtures. SUP012 actual native unit is NO_DB_WRITE. Physical-labelled JSON synthetic.

Public logs are UTF8/LF with raw-to-LF SHA mapping in data-ui-log-normalization-20261026.csv. Final LF reviewer rechecks stored hashes; previous raw hashes remain historical. Post-registry PHP377/0fail/0skip and exact0row cleanup PASS.

Current HTTP source f997ab6835af1731ee4a2d71a0b1950ee5b9569d5c219bbb02b05e462669d1ba;
native7c5394350e439111aac440f60668df6b68e53abfb1f8939084bdfaf3449b7767.
Unchanged firmware a0a0eac0809da2b9be93c67a8347c3f50766b3bed163ec7d42a1e4b86fb8bf95
matches both committed actual SDK proofs (see data-ui-firmware-proof JSON).
Captured public evidence-table statuses are point-in-time test data from before
these six promotions; this is not a new hardware proof or source change.

Cleanup policy adopted: docs/testing/verified-safe-cleanup.md. Removed0. Exactly
one tracked template welcome.blade.php DEFERRED: project entry role positively
replaced/tested with template PRESENT, but current scanner rejects missing tracked
prestaging files. See data-ui-cleanup-review-20261026.md; no scanner weakening or
premature staging. All protected/untracked/WIP/cache/vendor/evidence retained.

Next safe checkpoint: exact working/index/manual/security/manifest and local
commit only allmandatoryPASS; update BOTH actual HEAD/WIP immediately afterward.
Then continue dedicated SIM011 channel isolation, SUP013 bounded offline host
integration and SUP014 approved-target schema roundtrip/protocol; actual bugs
first. SUP017 independent coverage review/SUP018 hostedCI and hardware-dependent
SIM010/012/013 remain separate. NO PUSH; no repeated full baseline audit.

## Historical cleanup-policy checkpoint0507fc9 (2026-10-26)

Actual branch develop, HEAD `0507fc90b63aea8aec3ee32a722a38e25c5d3147`; index EMPTY.
Provider/navigation batch committed44exact files. Postcommit44/44 committed blob/
manifest/worktree equality PASS; all mandatory local gates/final read-only staged
screen0findings/0privacy PASS. Receipt batch5727969 already committed77files.
NO PUSH. Source/test/evidence are not unfinished implementation. Both handoffs
are updated automatically AFTER commit; these updates are explicit next-batch
WIP, not an administrative microcommit. Verify actual Git when resuming.

Latest user policy VERIFIED SAFE CLEANUP replaces old rule11 (read-only-only). Repository policy: docs/testing/verified-safe-cleanup.md; decisions/evidence: evidence/test-results/verified-cleanup-adoption-20261026.csv. Actual removals0.
Selective cleanup policy:
selective deletion is allowed ONLY for tracked files positively proven obsolete/
replaced/unnecessary, with direct/indirect/dynamic/autoload/runtime/firmware/
ESP-IDF/PlatformIO/linker/Laravel/DB/routes/DI/CI/scanner/evidence/old-contract/
traceability dependencies reviewed and relevant tests fully proving safe removal.
Decisions: SAFE_TO_DELETE / DEFERRED / PROTECTED; only SAFE_TO_DELETE may be
removed. No forced deletion or cleanup-only numbering batch. If uncertain KEEP.
Do not alter AGENTS.md: the latest explicit user policy governs cleanup scope.

Protected from deletion: LOCKED requirements/baseline contracts, Git history,
historical evidence/audit trail, formal/traceability/verification documents,
used migrations, needed regression/golden/reference fixtures, legacy contracts,
AGENTS/instructions, all secrets/local sensitive config, two protected firmware
untracked, ALL preexisting untracked files, ALL active uncommitted changes,
and BOTH handoffs. No mainDB/app-data cleanup, gitclean/hardreset/destructive
checkout/forcepush/mass deletion. Only at a safe checkpoint or explicit related
scope, one dependency group at a time, path/reason/positive replacement proof/
compatibility/tests/security/exact staged evidence; on failure retain evidence,
no commit and restore only owned cleanup edits without overwriting other work.
Local develop commit only allmandatoryPASS. Cleanup supports the main Goal.

Actual deletion count so far:0. Current candidate DEFERRED by scanner admission; see active batch above. Earlier7-category read-only inventories are
historical evidence and are not removal permissions. A potential starter welcome
view was checked read-only: tracked but still used by routes/web.php root
view('welcome') at that historical adoption checkpoint. Current root has been replaced; candidate remains DEFERRED for the gate reason above.
Next related UI/contract batch may assess an explicit replacement plus full
runtime/reference/compatibility/gate proof before considering its removal.

Current canonical SUP15PASS/4PLANNED; per-requirement formal28PASS/3PARTIAL/7NOT_RUN;
implementation22IMPLEMENTED_UNVERIFIED/16PARTIAL, finalNOT_APPROVED, systemPARTIAL.
Current source proof hashes and exact evidence in formal-provider-summary-20261026.md.
Hardware/currentWokwi/hostedCI/deployedTLS/remaining unavailable formal NOT_RUN.
Next safe software dependency review remains active: project entry/dashboard
usability and dedicated source/schema/null/dedup/auth/required-view verification,
then remaining offline/migration/fault protocols. No Goal completion claim.


Dokumen operasional Codex lama/baru: actual source/Git and current gate evidence govern resume.

## Completed provider/navigation batch (2026-10-26)

Provider batch baseline was develop5727969e1f04f49cd26def184e0ab594a6acba6e. Receipt
batch committed77files, all scoped gatesPASS, NO PUSH. That seven-scope provider batch completed all local prerequisites and final exact staged gate; committed0507fc9.

Real navigation bug reproduced: older ingest/age calls could revive OFFLINE.
Guard fixed in navigation_nmea.h using overflow-safe now-last_valid<data_age
check before mutation; equal-time valid data allowed. Failure run1 retained.
Dedicated final actual6casesPASS,121 native assertions/303 independent comparisons,
source7c75cb16e5e5728c6f9f3011826607a3510352ad01f5f122e1afe680cbfcdd16.
Runner/oracle/property12methods, existing G1 64/G2 2/continuous13/owner8/file4 PASS.
Broad230/230 commands PASS; PHP373cases0fail0skip; actualTLS187checks/cleanup0PASS.
Both SDK sourcea0a0eac0809da2b9be93c67a8347c3f50766b3bed163ec7d42a1e4b86fb8bf95:
candidate986048/RAM57532/frame1056, retained1045472/RAM66436/frame1616,
margin3104. HTTPsource26a94bfa1c529fb339c7c72702f1cb1d50327eafeb8d6d37b97b4fcbef6fd4c2.
Working security corrected0findings/0privacy;2INFO unchangedCI lines reviewed with
exact renewed pins. Case review/summary/results under evidence/test-results/formal-provider-*.

Six SUP canonical rows now PASS after prescribed host protocol/execution/review
and complete local prerequisites. SUP total11PASS/8PLANNED, per-requirement formal
21PASS/3PARTIAL/14NOT_RUN. All implementation assessments stay22IMPLEMENTED_UNVERIFIED/
16PARTIAL; no requirementVERIFIED. SIM001-009 remain recordedPASS,010-015NOT_RUN.
SUP host execution is explicitly permitted by its existing protocol matrix; no
hardware/freshWokwi or independent final system acceptance is claimed. All unrelated
formal definitions/LOCKED mappings unchanged. Current WIP includes nav fix, dedicated
fixture/runner/tests/protocol/case evidence/CI/security pins, six reviewed SUP rows,
living docs/38matrices and both handoffs. All final scope/manual/protected/current-proof/exact staged-byte gates PASS before local commit0507fc9; NO PUSH.

## Historical receipt postcommit checkpoint 5727969 (2026-10-26)

Actual branch develop, HEAD `5727969e1f04f49cd26def184e0ab594a6acba6e`; index EMPTY.
Receipt/retirement ADR0010 seven-scope batch committed locally with77exact files.
Postcommit audit verified all77 changed paths and every committed blob against
manifest/worktree: PASS. Final staged security repeated read-only after restaging
only its log/manifest:0findings/0privacy, exact branch/parent/index verified.
NO PUSH. Protected AGENTS.md and two firmware files remain untracked/unchanged.

Both handoffs are automatically updated AFTER that commit. These two current
document updates are explicit WIP for the next substantive batch; no source,
receipt tests/evidence/CI need reimplementation. A commit cannot embed its own
hash; verify actual Git on resume. Previous pending-stage statements below are
historical batch prerequisites now satisfied by actual commit5727969.

Next work is a dependency review of still-open local software/formal protocols,
not Goal completion. Dedicated host-executable SUP004/005/007/008/009/010 have
actual implemented modules but remain PLANNED without dedicated accepted case
evidence. Review their protocol/evidence requirements before selecting the next
coherent verification slice; no automatic formal promotion from old unit tests.
Hardware/hostedCI/deployedTLS and unavailable formal runtime remain NOT_RUN.

## Historical checkpoint before provider/data-UI continuation (2026-10-26)

Receipt batch baseline was developbb4f462; the following verified gate matrix is committed in 5727969e1f04f49cd26def184e0ab594a6acba6e.
Both handoffs exist/tracked since70963d4. Latest receipt batch is COMMITTED:77exact files,76hashes+SELF.
All mandatory scoped gates and final read-only staged scan PASS0findings/0privacy. Existing continuous, metadata
and recovered replay commits remain intact; do not reimplement or reset them.
Protected AGENTS.md and two firmware files remain untracked/unchanged. Two old
metadata evidence files can show stat-cache M while bytes equal committed blobs;
exclude them from stage. Actual content scope is `git diff --name-only` plus new
receipt files; committed exact manifest is event-receipt-files-20261026.csv.

Seven related ADR0010 scopes implemented: postcommit opt-in backend receipt;
strict raw-body/status SHA256/HMAC with actual SDK PSA; VGS3 confirmed floor and
separately authorized exact retirement; bounded storage worker and normalized
accepted prefix; shared single-inflight delivery owner/recovery ordering/RAM
release; actual signed TLS/MariaDB -> native host-file retirement/reopen/new
facts; final regression/security/evidence/CI/living/handoff checkpoint work.
All mandatory local functional/build/regression/security/manual/exact staged gates PASS. Postcommit committed-blob/manifest equality77/77 verified.

| Current gate | Actual result/evidence under evidence/test-results/ |
|---|---|
| PHP8.2.35/MariaDB | PASS373 cases0failed0skipped;event-receipt-mysql-final-20261026.txt;10tables/6migrations/0app rows |
| Actual loopback TLS/kernel/MariaDB/native retirement/read/UI | PASS187checks;event-receipt-http-retirement-final-run2-20261026.txt;exact owned cleanup0rows |
| Shared owner/file fixture | PASS8+4methods;event-receipt-owner-file-native-run3-20261026.txt;positive auth uses real C crypto and independent Python HMAC |
| Primitives/protocol | PASS retirement17/floor7/state9/transaction7/metadata9/replay13/continuous13/protocol8,core226 per boot repeat2; worker-primitives regression |
| SDK candidate | PASS985920bytes/RAM57532/frame1056;esp32-transport-sdk-build-event-receipt-owner-final-20261026.txt |
| SDK retained | PASS1045408bytes/RAM66436/frame1616;3168byte margin;esp32-transport-sdk-build-event-receipt-owner-legacy-final-20261026.txt |
| Both SDK source | 506b4e74e05cfedfa29d29fd633af80fe99f3d778f36ebd37f605cfbe34930d3 |
| HTTP source | 6695a197ad6b03efbbd5d3911027877df9e3676e37f02e5e6291ddd36ab35a85 |
| Broad regression | PASS229/229commands;event-receipt-integrated-regression-20261026.txt |
| Initial security | FAIL5INFO unchanged source false positives,0privacy;exact five renewed pins/triage CSV;corrected final working scan PASS0findings/0privacy |
| Cleanup | Read-only7categories,event-receipt-cleanup-audit-20261026.csv;no deletion |

Full current contract/failures/limits: docs/testing/event-receipt-retirement-plan.md,
docs/adr/0010-authenticated-event-retirement.md and event-receipt-summary-20261026.md.
No new migration. Ordinary JSON/event1.0/1.1 remain compatible; VGS1/VGS2 unchanged
when floor0, new VGS3 max5150 within5184. HTTP receipt alone never frees a fact.
Only actual worker verification + commit/readback authorizes exact RAM-prefix
release; operator alarm ACK and underlying condition remain independent.
Older recovered current-boot predecessors are reconfirmed before newer facts.
Finite cap8/refusal, unsupported RECOVERY retention and explicit reset/recovery
remain; no unlimited/automatic guaranteed delivery or physical durability claim.

## Arsitektur dan status fase

Firmware: seven simulator/bench-interface providers feed pure quality/source,
measurement, safety, four-engine/N model and navigation modules. Continuous
coordinator emits48 typed channels, schema1.1 cap72/body4096; schema1.0 cap16
preserved. Local alarms have immutable transition metadata and bounded raw/full
journals. Network and two-slot NVS workers use zero-wait admission independent
of local observation. External vgw_demo/vgw_net policy/profile provisioning,
trusted time and physical providers remain dependencies; firmware never erases
or provisions them.

Backend: bearer-authenticated Laravel12 ingest validates raw JSON duplicates,
identity/schema/null/uint/source/action-time and sizes. Transactional MySQL
services deduplicate stable identities and reject conflicts, including real
REPEATABLE-READ race cohorts. Receipt is a negotiated representation after
committed create or exact duplicate. Database uses six Laravel migrations only;
canonical alarm JSON preserves unknown/null and genuine timestamp0.

Frontend: eight Blade dashboard views read per-device grants through sessions,
CSRF/throttle/revoke/disable guards. Views distinguish source simulation and
live/stale/offline freshness, show exact immutable event facts without assuming
receipt order is current alarm state. No remote physical or operator alarm
control is invented. Real graphical/deployed browser remains unverified.

Communication: HTTPS/auth, external bearer and CA/hostname/date verification,
body4096 and bounded retries/exhaustion/reset. Exact134 ASCII receipt VGR1 binds
SHA256(raw bytes) and successful status with domain-separated HMAC. Standard
PSA is the SDK provider; host B40 math is test-only. CRC snapshots are not
cryptographic storage authentication. Full receipt adapter is continuous-only;
retained selftest decodes VGS3 but new receipt API returnsfalse.

Phases3-8 scoped software development closed;9 backend/transport/storage and10
dashboard have substantial local implementation, system/formal verification
remains OPEN. No phase status implies hardware, production or full38 VERIFIED.

## Identitas, otoritas dan batas proyek

Integrated Vessel Monitoring & Diagnostic Gateway adalah prototipe monitoring/diagnostik. Tujuan Goal: menyelesaikan software lokal yang aman sesuai Engineering Blueprint v1.0 LOCKED, dengan evidence nyata dan tanpa mengurangi pengujian. Sistem masih **PARTIAL**, final approval **NOT_APPROVED**. Tidak ada klaim produksi, sertifikasi, pemasangan kapal atau hardware verified.

Otoritas: `AGENTS.md`, `requirements/system-requirements.md`, `requirements/traceability-matrix.csv`, `docs/architecture/architecture-and-icd.md`, `docs/github-repository-plan.md`, ADR dan evidence aktual. Requirements LOCKED dan mapping baseline tidak boleh diubah. Living assessment berada di `docs/testing/living-requirement-status.csv`; status implementasi tidak sama dengan status formal atau VERIFIED.

Arsitektur: provider simulator/bench-interface -> pure C99 quality/measurement/alarm/safety/N-engine/navigation -> continuous snapshot/journal lokal -> worker jaringan ESP-IDF HTTPS dan worker NVS terpisah -> Laravel 12 API autentikasi/device/schema -> MariaDB/MySQL via migrations -> read API dan dashboard Blade berbasis session/grant. Sampling, indikasi lokal dan evaluasi safety tidak menunggu dashboard/cloud. Tidak ada starter, ignition, steering, radar, radio, atau kontrol fisik/mission-system.

## Riwayat implementasi yang sah

| Commit lokal | Hasil dan evidence utama |
|---|---|
| `231cc2b2022223b47790347a5fecf71eb0ee2c44` | Referensi ZIP B46; bukan HEAD yang harus dipulihkan. Host B44/B45/B46 dan core tidak membuktikan ESP32/NVS. |
| `b999492c7f12d4e19cc6270983e4390122455e81` | Security/runtime PHP 8.2.35, 215 kasus PHP; `evidence/test-results/security-php8235-summary-20261025.md`. |
| `ccf57405634c8752b11fb3e34ac72281cee386ac` | Read API device/event/channel, 251 kasus; `evidence/test-results/device-read-summary-20261025.md`. |
| `bd34639940fff98461cf0e12cbf7e2e76c6664ce` | Dashboard terhubung, grant/session/CSRF/throttle, 325 kasus; `evidence/test-results/dashboard-summary-20261025.md`. |
| `9406777159af26db0a61b4bac84daa5b316892cd` | Transport ESP-IDF aktual dibangun SDK, 326 kasus; `evidence/test-results/esp32-transport-summary-20261025.md`. |
| `895e031ed205b6888c46a423cd1c9ee39c8f6e61` | Worker persistent bounded NVS, host fault checks; `evidence/test-results/offline-nvs-summary-20261025.md`. |
| `054cfa5f7f00362e3246d46e9bf5dce9309f9059` | Loopback TCP/TLS/session nyata, 335 kasus PHP + 65 pemeriksaan integrasi; `evidence/test-results/live-http-summary-20261025.md`. |
| `5048525e1ff4cfad367dc31bfc42c7aa79fb393e` | Continuous simulation committed;348PHP/94local;continuous-simulation-summary-20261025.md. |
| `70963d463fa5cd2d43914950ef7a9ece5b3185d7` | Immutable alarm metadata end to end;362PHP/122integration;both handoffs first committed,81 exact files. |
| `bb4f462db3d0692a7c6ae9a8f96c704b3aea43f5` | Recovered cross-boot replay;366PHP/142integration,both SDK/security;43 exact files. |

Fase 3-8 menutup scope development: core C99, tujuh provider simulator/bench-interface, quality/null semantics, virtual safety, empat engine/N configurable, parser/generator NMEA-style development dan telemetry contract. Fase 9 memiliki implementasi backend/dashboard/transport/storage serta evidence lokal; tidak lagi NOT_STARTED, tetapi formal/system verification belum selesai. Historical closure bukan persetujuan sistem.

Continuous simulation committed: `firmware/src/domain_snapshot.h`, `telemetry_snapshot_v11.h`, `continuous_simulation.h`, `esp32_continuous_main.h`; 4 engine menghasilkan 48 channel termasuk diagnostik, kapasitas schema 1.1 sampai 72 channel dengan batas body tetap 4096 byte. Schema 1.0 tetap 16 channel. Semua source SIMULATION, policy demo eksplisit, tanpa default batas engineering kapal. Native 2000-cycle progression tetap berjalan saat jurnal penuh. Dashboard menampilkan quality, source dan freshness terpisah; valid zero berbeda dari null. Perbaikan binary64 persistence menggunakan 17-digit locale-independent representation, exact duplicate vs one-ULP conflict diuji. Jangan mengimplementasikan ulang.

## Batch metadata yang sudah committed pada70963d4

Commit hasil `70963d463fa5cd2d43914950ef7a9ece5b3185d7` (81exact files). Baseline batch `5048525`; keputusan `docs/adr/0008-alarm-transition-integration.md`, desain `docs/testing/alarm-transition-integration.md`, kontrak `docs/contracts/alarm-event-schema-v1.1.json`.

1. `firmware/src/alarm_transition.h`: immutable event-time alarm snapshot dengan identity/source/priority/reason/state/raised/ACK/CLEAR, validasi shared alarm model dan bounded ledger delapan.
2. `continuous_simulation.h`: metadata saat transisi, ACK tidak CLEAR; jurnal penuh menolak event eksplisit tanpa menghentikan observasi/indikasi.
3. `offline_state.h`, `offline_transaction.h`, `esp32_offline_store.c/.h`: VGS2 metadata-preserving, VGS1 tetap kompatibel dan historical metadata tidak direkonstruksi. Maksimum VGS2 5142 byte, buffer 5184; VGS1 4862. Zero-wait submission, IO worker, dua slot/readback. Known metadata tidak boleh diturunkan/mutasi/drop. CRC bukan autentikasi/power-loss proof.
4. Request event 1.1 dan shared `InspectsRawJsonObjects` dari parser telemetry yang sudah ada; exact raw/nested/escaped duplicate keys, uint32/uint64 lexical, lifecycle/action-time, null versus zero. Legacy event 1.0 tidak berubah.
5. Migration `2026_10_25_100006_add_alarm_metadata_to_monitoring_events.php`, canonical JSON di model/service/read API/escaped UI. Legacy metadata tetap unavailable. Receipt order tidak membuktikan global active alarm. Tidak ada remote operator control.
6. Native wire fixtures -> Laravel/PHP 8.2.35 -> MariaDB -> TLS/read/UI; previous-schema guard, migration roundtrip, fault/race regression. Real REPEATABLE-READ race diperbaiki pada `EventIngestService.php`: duplicate 1062 ditangani di luar failed transaction, shared current read juga aman bagi caller-owned outer transaction. Empat cohort aktual: 201/200, 201/200, 201/409, 201/200; masing-masing satu row, metadata pemenang tidak berubah. CLI workers memanggil kernel Laravel aktual; ini bukan pengujian concurrency server TCP deployment.
7. SDK dua target/CI source/security/living traceability/evidence/cleanup read-only. Perubahan firmware terakhir menambah laporan FULL/REJECTED/degraded storage yang sebelumnya tidak terlihat; log dibatasi first/every256. Final source-stability HTTP/SDK telah diulang dan PASS sebelum70963d4; lihat summary metadata. Source replay setelahnya memerlukan proof-nya sendiri.

Event identity device/boot/event-ID; alarm identity device/boot/alarm-ID. Waktu uint64 boot-relative milliseconds, bukan UTC. Priority/reason opaque development codes, bukan marine taxonomy yang disetujui. Absent ACK/CLEAR null, genuine timestamp zero dipertahankan. Immutable event facts tidak boleh dibentuk ulang dari current mutable alarm.

## Runtime dan database yang diizinkan

- Semua PHP wajib `C:/tools/php-8.2.35/php.exe`: CLI 8.2.35, int64; Laravel lock v12.70.0. Jangan ubah PATH global atau PHP XAMPP.
- Python 3.12.10; native GCC `gcc.exe (Rev5, Built by MSYS2 project) 16.2.0`, child PATH dapat menambahkan `C:/msys64/ucrt64/bin`.
- PlatformIO `<LOCAL_HOME>/.platformio/penv/Scripts/platformio.exe` 6.2.0; espressif32@7.1.3, ESP-IDF 6.1.0; `firmware/platformio.ini`, CMake dan sdkconfig. Target `esp32dev_continuous` kandidat runtime dan `esp32dev_espidf` retained selftest. Tidak ada upload/erase. Batas app 1048576 byte; stack frame <=2048. Flash konfigurasi SDK bukan pengukuran hardware.
- Target testing yang disetujui **127.0.0.1:3307 / vessel_gateway_codex_test / vgw_codex**, MariaDB 10.4.32, driver mysql. Nama ini nonrahasia. Target lama `vessel_monitoring_gateway_test`/`vg_gateway_test` tidak disetujui.
- Kredensial hanya file lokal ignored `backend/laravel/.env.testing`, dipakai internal harness; jangan mencetak/mengopi isi, password, APP_KEY, environment dump atau SQL bindings. File testing APP_KEY kosong; runner membuat ephemeral cipher-compatible process key, tidak mengubah file.
- Effective override audit mencakup PHPUnit/env/cache/session/queue/URLs/socket/auth. `tests/Support/TestEnvironment.php`, `TestSchema.php`, `LiveHttpSafety.php` dan `scripts/mysql_test_gate.php` fail-closed sebelum mutation. Current schema **10 tabel / 6 migration records / 0 application rows** setelah gate terakhir. Jangan gunakan previous-upgrade lagi pada schema enam. Manual DDL, main .env/DB, SQLite substitute dilarang.
- Ten tables: cache, cache_locks, devices, migrations, monitoring_device_access, monitoring_events, sessions, telemetry_channels, telemetry_samples, users. Grant memakai string device_id; grant table tidak memiliki timestamps. Nullable alarm_metadata hanya lewat migration keenam.
- NVS external read-only `vgw_net` dan `vgw_demo`: tidak ada default kredensial/engineering policy. Dua-slot storage `vgw_state`; trusted clock adalah dependency TLS, unset clock gagal aman. Provisioning, recovery fisik dan key confidentiality belum verified.

## Evidence metadata committed dan kontinuitas

Batch70963d4 menutup seluruh local scope gates:362PHP cases0failure0skip,
122actual local integration checks, native/host regresi dan kedua SDK targets,
final content+staged scan0unresolved/0privacy. Source proofs dan seluruh failure
historis/correction: `evidence/test-results/alarm-metadata-summary-20261025.md`,
`alarm-metadata-checkpoint-audit-20261025.txt`, review dan81-file manifest.
Pada commit itu candidate974032/frame880 dan retained1044112/frame1616;
angka tersebut historis, gunakan matrix replay terbaru untuk current source.
Dua handoff pertama masuk commit ini. Setelahnya kedua dokumen di-update pada
checkpoint batch replay; updates WIP akan ikut commit substantif berikutnya.

## Bug, security dan risiko tersisa

Audit scanner awal36 sudah ditriase di `docs/testing/security-scanner-review.md` dan security evidence: 32 INFO false positives, dua LOW synthetic CI, dua MEDIUM CI issue diperbaiki sebelum commit b999492. Exact reviewed non-secret lines/file SHA di `scripts/security-reviewed-findings.json`, bukan global detector waiver. Metadata batch meninjau ulang lima INFO source occurrences dan tiga source-version re-review, bukan delapan kerentanan unik. Temuan nyata baru: RR dedup race menghasilkan500, kini fixed dan reproduced/verified; diagnostic storage failures sebelumnya tidak dikonsumsi caller, source fixed, hardware observability belum diuji. Lihat `alarm-metadata-development-observations-20261025.txt` dan triage CSV. Tidak ada rahasia disalin ke dokumen.

Batch replay bb4f462 menghubungkan nondestructive recovered publication. Receipt ADR0010 kini implemented WIP: genuine authenticated durable retirement dan RAM capacity release sudah diuji lokal; seluruh gate final tetap wajib sebelum commit. HTTP status sendiri tetap bukan otorisasi penghapusan. Jurnal delapan tetap bounded/refuse; jangan mengklaim unlimited offline delivery. Delivery ACK berbeda dari operator alarm ACK dan tidak boleh clear kondisi. Cross-boot ordering/current-state tidak boleh disimpulkan dari receipt sequence. Durability, wear, NVS confidentiality, real sensor/OEM providers, trust clock/provisioning, resource watermark/timing/outage memerlukan physical evidence. Jangan mengarang protokol OEM atau mengubah threshold demo menjadi aturan kapal nyata.

Formal actual: SIM001-009 recordedPASS and010-015NOT_RUN. Canonical SUP now11PASS/8PLANNED: six newly dedicated prescribed host cases004/005/007/008/009/010 plus earlier001/003/006/016/019. Living formal21PASS/3PARTIAL/14NOT_RUN; no requirementVERIFIED. See current case review and summary for exact host scope; old historical14PLANNED counts describe prior checkpoints. SUP014 historical prepared DB target remains superseded by user-approved current isolated catalog for development; any future formal protocol revision must explicitly record that correction without editing pinned history.

## Aturan fail-closed dan kesinambungan

1. Jaga LOCKED baseline, user changes, `AGENTS.md`, `firmware/.gitignore`, `firmware/.vscode/extensions.json` dan ignored secret files. Jangan stage/overwrite/delete dua firmware untracked.
2. Tidak push, remote, pull/rebase/merge/reset/clean/history rewrite. Jangan delete evidence/build/vendor sebagai collateral. Audit kandidat cleanup read-only.
3. Sebelum DB mutation verifikasi effective exact target/account/schema/isolation dan ephemeral key. Laravel migrations saja untuk DDL. Test rows hanya owned isolated fixtures dengan verified cleanup; tidak menyentuh real/main data.
4. Batch terkait 5-7 scope; jangan mengulang implementasi atau membuat micro-batch nomor. Specific positive/negative/boundary/security/logical tests + existing/new integrated regression + security/manual scope/diff wajib. Missing mandatory gate => NO staging/commit; external exclusions tetap NOT_RUN, bukan PASS.
5. Sesudah mandatory local gates PASS, expected develop/HEAD/index, stage **exact approved files**, scan staged bytes, local commit otomatis sesuai izin. Git metadata sandbox dapat perlu approved narrow escalation; patuhi penolakan, jangan bypass.
6. Jangan edit firmware/backend di tengah SDK/HTTP source-stability gate. Log public disanitasi UTF-8, secret/SQL output tidak dicetak. Jika whitespace log dinormalisasi catat before/after SHA, jangan rewrite failure evidence.
7. Perbarui **kedua** handoff setelah batch besar committed. Self hash commit tidak dapat ditulis ke commit itu sendiri: sebut hash checkpoint yang diverifikasi dan periksa actual Git lagi saat resume. Jika WIP/limit/blocker muncul, checkpoint dulu dan tulis pending scope/gates eksplisit.
8. Satu commit/handoff bukan akhir Goal. Lanjut scope software independen yang aman; jangan tandai proyek VERIFIED/Goal complete sebelum audit aktual semua38 requirements dan seluruh kriteria Goal. Jangan mengarang status aktif/complete dari tool atau menganggap status UI sebagai evidence teknis.


## Seluruh 38 requirement LOCKED: status dan evidence

Authoritative LOCKED baseline stays unchanged. Formal status follows actual canonical cases; no requirement VERIFIED.

| ID / requirement | Implementation | Formal / planned cases | Source and evidence | Qualification |
|---|---|---|---|---|
| SYS-001: System shall operate as a monitoring and diagnostic prototype, not as certified ship safety equipment. | PARTIAL | PASS / SUP-001 | README.md;docs/architecture/architecture-and-icd.md / evidence/test-results/phase9-wave1-sup001-documentation-review-20261020.txt | Prototype and non-certification boundaries reviewed under SUP-001 PASS; no certification or production readiness claimed. |
| SYS-002: System shall separate source_mode = simulation, bench_test, physical for all data. | PARTIAL | PASS / SUP-002 | firmware/src/core_types.h;firmware/src/core_source_mode.h;firmware/src/telemetry_contract.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;scripts/data_ui_contracts.py;scripts/run_formal_data_native.py;scripts/review_formal_data_ui.py / evidence/test-results/phase8-h1-summary-20261017.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/data-ui-case-review-20261026.md | SUP-002 dedicated synthetic telemetry source-mode contract/API/directDB review PASS for simulation, bench_test and physical-labelled fixtures. Native acquisition remains simulation, event1.1 physical mode remains unsupported, and physical-labelled JSON is explicitly synthetic. This does not complete all physical-data integration; implementation remains PARTIAL. |
| SYS-003: Backend/cloud failure shall not stop local sampling, local alarms, or safety-policy evaluation. | PARTIAL | PASS / SIM-010;SIM-012 | firmware/src/network_outage_local_guard.h;firmware/src/phase9_sys003_outage_cycle_host.h;firmware/src/esp32_network_client.c;firmware/src/main.c;firmware/src/esp32_offline_store.c;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/esp32_continuous_main.h;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/resilience_host_fixture.c;scripts/resilience_native_bridge.py;scripts/formal_resilience.py;scripts/review_formal_resilience.py;scripts/test_formal_resilience.py / evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/esp32-transport-summary-20261025.md;evidence/test-results/offline-nvs-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/formal-resilience-case-review-20261027.md | PARTIAL: shared actual C99 scheduler/providers/policy/local alarm/journal continue561cycles through actual60047ms private TLS API outage. Dedicated SIM010/SIM012 host protocols and current-source independent review PASS; no DB writes in host case. Separate actual native/PHP/MariaDB/TLS/UI integration and approved Chrome component support software composition. Does not execute ESP32 main/RTOS workers or establish physical sampling/timing/NVS guarantees; implementation remains PARTIAL. |
| SYS-004: No physical engine starter, ignition, steering, radar, radio, or third-party operational or mission system shall be controlled by V1. | PARTIAL | PASS / SUP-003 | docs/architecture/architecture-and-icd.md;firmware/src/safety_policy.h;firmware/src/engine_model.h / evidence/test-results/phase5-closure-summary-20261016.md;evidence/test-results/phase9-wave1-sup003-static-review-20261021.txt | Monitoring-only and prohibited-control interface static review SUP-003 PASS; no physical control or operational installation claimed. |
| SAF-001: Ventilation hatch/door state shall be modeled as OPEN/CLOSED/UNKNOWN with quality. | IMPLEMENTED_UNVERIFIED | PASS / SIM-001;SIM-002 | firmware/src/provider_door.h;firmware/src/safety_policy.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Door OPEN/CLOSED/UNKNOWN quality model is implemented; both mapped formal software-simulation scenarios PASS, but requirement-level VERIFIED is not claimed. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| SAF-002: A virtual start request shall be rejected when configured blocking conditions are not satisfied. | IMPLEMENTED_UNVERIFIED | PASS / SIM-001;SIM-002;SIM-003;SIM-004 | firmware/src/safety_policy.h;firmware/src/safety_policy_runtime.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Virtual start decision/rejection path is implemented; all four mapped formal software-simulation scenarios PASS. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| SAF-003: Blocking/alert-only behavior shall be configuration-driven; only field-verified rules may be labeled real-vessel rules. | PARTIAL | PASS / SIM-002;SIM-005 | firmware/src/safety_policy.h;firmware/src/safety_monitor_policy.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Configuration-driven BLOCK/ALERT_ONLY behavior is demonstrated; no field-verified real-vessel rule labeling is claimed. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| SAF-004: Fuel-vapor channel shall support NORMAL/WARNING/ALARM/FAULT/UNKNOWN and shall never map missing data to safe. | IMPLEMENTED_UNVERIFIED | PASS / SIM-003;SIM-004 | firmware/src/provider_fuel_vapor.h;firmware/src/safety_policy.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Fuel-vapor states and fail-safe missing-data behavior are implemented; mapped formal scenarios PASS. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| SAF-005: Bilge/high-water channel shall support NORMAL/HIGH/FAULT/UNKNOWN. | IMPLEMENTED_UNVERIFIED | PASS / SIM-005 | firmware/src/provider_bilge.h;firmware/src/safety_monitor_policy.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Bilge NORMAL/HIGH/FAULT/UNKNOWN development model is implemented; SIM-005 PASS. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| SAF-006: Compartment temperature shall support valid/invalid/missing/stale quality and configurable demo thresholds. | IMPLEMENTED_UNVERIFIED | PASS / SIM-006;SIM-011 | firmware/src/provider_temperature.h;firmware/src/safety_monitor_policy.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;scripts/fault_isolation_fixture.c;scripts/fault_isolation_wire_bridge.py;backend/laravel/tests/Feature/SingleChannelFaultIntegrationTest.php / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/fault-storage-case-review-20261026.md | SIM-006 historical scoped temperature policy and dedicated SIM-011 host single-channel isolation PASS. Actual provider/domain wire has valid25, invalid/null on2frames and valid30 only after valid sample;43other domain channels stay current and engine values advance. Actual C99/PHP/MariaDB/read/UI integration supports this software case. No physical DS18B20/shared-bus/network recovery proof or operational threshold claimed. |
| ALM-001: Alerts shall have unique ID, source, priority, state, reason, raised_at, acknowledged_at and cleared_at. | IMPLEMENTED_UNVERIFIED | PASS / SIM-003;SIM-005;SIM-006 | firmware/src/core_alarm.h;firmware/src/core_event_journal.h;firmware/src/safety_local_alarm.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/test_event_delivery_retry.py;scripts/test_event_delivery.py;scripts/event_retirement_file_fixture.c / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/event-delivery-retry-summary-20261027.md | Local software: complete immutable alarm transition snapshots now carry device/boot/alarm identity, source, opaque nonzero priority/reason, state and exact boot-relative raised/ACK/CLEAR times through native journal, VGS2/NVS worker, event 1.1, MariaDB and read/UI. Legacy facts remain explicitly metadata-unavailable; physical/global-clock/taxonomy approval is not inferred. Recovered replay continuation preserves original cross-boot identities and known/unknown metadata through a zero-wait recovered NVS-worker view and fair event queueing. Local native/PHP/MariaDB/TLS evidence does not authorize deletion/application ACK or establish physical recovery, delivery guarantees or new formal PASS; see latest replay summary. Authenticated receipt continuation adds exact-body/status HMAC, VGS3 confirmed floor, worker durable retirement and shared single-inflight RAM release. Actual host-file/MariaDB/loopback and both SDK results are in the latest receipt summary; all local functional/build/regression/working-security/manual gates passed; final staged-byte review is required before commit. No alarm condition is cleared; host readback is not physical NVS durability or formal verification. Failed-publication continuation20261027: actual parent C99 skipped an unconfirmed prefix after failed HTTP. Context-bound immutable fact/source/index/epoch rewind now retries the original without ACK/deletion/alarm clear; same-owner retrytag2, real committed-reply loss/MariaDB count1/duplicate200/genuine host-file retirement and both current SDK builds have scoped local evidence. Explicit exhausted transport reset and IO/crypto halt contracts retained; no physical durability/runtime or formal promotion. See event-delivery-retry-summary-20261027.md. |
| ALM-002: Acknowledgement shall not clear the underlying alarm condition. | IMPLEMENTED_UNVERIFIED | PASS / SUP-004 | firmware/src/core_alarm.h;firmware/src/main.c;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/formal_provider_fixture.c;scripts/run_formal_provider_verification.py;scripts/test_formal_provider_verification.py / evidence/test-results/firmware-core-alarm-wokwi-20261013.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/formal-provider-summary-20261026.md;evidence/test-results/formal-provider-case-review-20261026.md | Local ACK preserves the active condition and immutable event-time fact; full journal refusal cannot silently consume operator ACK. Delivery receipt retirement remains separate and cannot ACK/CLEAR a live alarm. Dedicated prescribed host SUP-004 PASS, actual core lifecycle and zero-vs-absent times observed. Current provider summary records actual module/oracle/regression/SDK/backend gates; physical indication/NVS/durability and final requirement approval remain unverified. No remote physical control or requirement VERIFIED. |
| ALM-003: Local buzzer/LED behavior shall be independent from dashboard availability. | PARTIAL | PASS / SIM-003;SIM-010;SIM-012 | firmware/src/safety_local_alarm.h;firmware/src/safety_policy_runtime.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;scripts/resilience_host_fixture.c;scripts/resilience_native_bridge.py;scripts/formal_resilience.py;scripts/review_formal_resilience.py;scripts/test_formal_resilience.py / evidence/test-results/phase5-e4-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/formal-resilience-case-review-20261027.md | PARTIAL: dedicated actual SIM010/SIM012 host execution keeps logical local indication active while dashboard/backend path is unavailable; only valid provider recovery clears the condition. Ordered immutable event-time metadata retained. Logical buzzer/LED request is not actual GPIO/buzzer/LED hardware execution or physical approval; existing independent local policy code unchanged. |
| ENG-001: Engine model shall support N engines; demo profile shall configure four engines. | IMPLEMENTED_UNVERIFIED | PASS / SIM-007 | firmware/src/engine_model.h;firmware/src/phase6_f2_formal_scenarios.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase6-f2-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Configurable N-engine model and four-engine demonstration exist; SIM-007 PASS. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| ENG-002: Each engine shall expose state, rpm, temperature, runtime, alarm and communication quality in simulation. | IMPLEMENTED_UNVERIFIED | PASS / SUP-005 | firmware/src/engine_model.h;firmware/src/phase6_f1_selftest.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;scripts/formal_provider_fixture.c;scripts/run_formal_provider_verification.py;scripts/test_formal_provider_verification.py / evidence/test-results/phase6-f1-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/formal-provider-summary-20261026.md;evidence/test-results/formal-provider-case-review-20261026.md | N-engine development model and four-engine SIMULATION profile expose state/RPM/temperature/runtime/alarm/communication quality with identity/source guards. Dedicated prescribed host SUP-005 PASS for all four field sets and count/invalid/lost-comm boundaries. Continuous C99/backend/TLS evidence remains development integration. No physical engine/OEM provider or production verification; requirement IMPLEMENTED_UNVERIFIED. |
| ENG-003: System shall detect configurable cross-engine RPM deviation in simulation. | IMPLEMENTED_UNVERIFIED | PASS / SIM-007;SIM-012 | firmware/src/engine_model.h;firmware/src/phase6_f2_formal_scenarios.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;scripts/resilience_host_fixture.c;scripts/resilience_native_bridge.py;scripts/formal_resilience.py;scripts/review_formal_resilience.py;scripts/test_formal_resilience.py / evidence/test-results/phase6-f2-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/formal-resilience-case-review-20261027.md | Cross-engine configurable RPM deviation implemented; SIM007 and dedicated actual concurrent-fault SIM012 host case PASS. Engine3 synthetic RPM1500 with other engines current is detected through shared existing engine policy while network unavailable and temperature invalid; recovery to normal2010 only after valid stimulus. No OEM/physical engine diagnostics or requirement VERIFIED. |
| ENG-004: Yamaha physical provider shall remain an interface placeholder until exact model/protocol is verified. | PARTIAL | PASS / SUP-006 | docs/architecture/architecture-and-icd.md;docs/bom-and-tbd.md / evidence/test-results/phase9-wave1-sup006-static-review-20261021.txt | Yamaha physical provider remains a placeholder/TBD; SUP-006 static review PASS, not physical integration verification. |
| NAV-001: Navigation module shall parse/generate NMEA 0183-style development data using Furuno GP-39 as reference, without claiming GP-39 is installed onboard. | IMPLEMENTED_UNVERIFIED | PASS / SIM-008 | firmware/src/navigation_nmea.h;firmware/src/phase7_g2_formal_scenarios.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase7-g2-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Development NMEA-style parser/generator with reference disclaimer exists; SIM-008 PASS; no full NMEA conformance or installed GP-39 claim. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| NAV-002: Navigation state shall expose latitude, longitude, SOG, COG, fix, data age and quality. | IMPLEMENTED_UNVERIFIED | PASS / SUP-007 | firmware/src/navigation_nmea.h;firmware/src/phase7_g1_selftest.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;scripts/formal_provider_fixture.c;scripts/run_formal_provider_verification.py;scripts/test_formal_provider_verification.py / evidence/test-results/phase7-g1-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/formal-provider-summary-20261026.md;evidence/test-results/formal-provider-case-review-20261026.md | Development navigation state exposes position/SOG/COG/fix/age/quality. Dedicated prescribed host SUP-007 PASS using independently checksummed synthetic input, malformed/no-fix/domain checks and age boundaries. Actual execution reproduced/fixed arrival/age timestamp rewind; overflow-safe monotonic guards and uint64 property regression PASS. Historical SIM-008/009 evidence retained; no fresh physical GNSS/NMEA/GP39/standards or requirement VERIFIED claim. |
| NAV-003: Invalid checksum/malformed input shall not replace last valid navigation state as current live data. | IMPLEMENTED_UNVERIFIED | PASS / SIM-008 | firmware/src/navigation_nmea.h;firmware/src/phase7_g2_formal_scenarios.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase7-g2-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Invalid checksum input rejection and last-valid preservation are implemented; SIM-008 PASS. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| NAV-004: Navigation shall transition VALID -> STALE -> OFFLINE according to configurable data-age thresholds. | IMPLEMENTED_UNVERIFIED | PASS / SIM-009 | firmware/src/navigation_nmea.h;firmware/src/phase7_g2_formal_scenarios.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h / evidence/test-results/phase7-g2-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md | Configurable VALID/STALE/OFFLINE development transitions are implemented; SIM-009 PASS. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. |
| MOT-001: Motion channel shall expose roll/pitch prototype values and clearly label them as attitude/motion, not vessel stability certification. | IMPLEMENTED_UNVERIFIED | PASS / SUP-008 | firmware/src/provider_attitude.h;firmware/src/phase4_d5_selftest.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;scripts/formal_provider_fixture.c;scripts/run_formal_provider_verification.py;scripts/test_formal_provider_verification.py / evidence/test-results/phase4-d5-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/formal-provider-summary-20261026.md;evidence/test-results/formal-provider-case-review-20261026.md | Attitude/motion prototype roll/pitch, provenance/quality and non-certification labels implemented. Dedicated prescribed host SUP-008 PASS for actual simulator and decoded-input constructor; valid zero/signed angles/stale/missing/invalid/unknown/refusal behavior observed. MPU6050 acquisition/calibration/physical stability are not verified; requirement IMPLEMENTED_UNVERIFIED. |
| VIB-001: Vibration channel shall provide a demo indicator and fault state without claiming machinery diagnosis. | IMPLEMENTED_UNVERIFIED | PASS / SUP-009 | firmware/src/provider_vibration.h;firmware/src/phase4_d6_selftest.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;scripts/formal_provider_fixture.c;scripts/run_formal_provider_verification.py;scripts/test_formal_provider_verification.py / evidence/test-results/phase4-d6-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/formal-provider-summary-20261026.md;evidence/test-results/formal-provider-case-review-20261026.md | Prototype vibration/acceleration indicator and explicit quality/fault handling implemented. Dedicated prescribed host SUP-009 PASS for actual simulator/constructor, indicator/nonfinite/negative/refusal/absence and non-certification labels. No ADXL345 physical acquisition, machinery diagnosis or condition certification; requirement IMPLEMENTED_UNVERIFIED. |
| PWR-001: Bench power channel shall monitor a safe low-power circuit using INA219 or simulator; real propulsion-current measurement is out of scope. | IMPLEMENTED_UNVERIFIED | PASS / SUP-010 | firmware/src/provider_power.h;firmware/src/phase4_d7_selftest.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;scripts/formal_provider_fixture.c;scripts/run_formal_provider_verification.py;scripts/test_formal_provider_verification.py / evidence/test-results/phase4-d7-summary-20261016.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/formal-provider-summary-20261026.md;evidence/test-results/formal-provider-case-review-20261026.md | Safe low-power simulation/decoded-bench interface preserves voltage/current/power and quality, including signed current/power and valid zero distinct from unavailable. Dedicated prescribed host SUP-010 PASS for actual simulator/constructor/labels and negative-voltage/nonfinite/refusal cases. No physical INA219 circuit, wiring/electrical safety or real propulsion-current measurement verified; requirement IMPLEMENTED_UNVERIFIED. |
| TEL-001: Telemetry payload shall carry schema_version, device_id, firmware_version, boot_id, sequence, uptime_ms, source_mode and per-channel quality. | IMPLEMENTED_UNVERIFIED | PASS / SUP-011 | firmware/src/telemetry_contract.h;docs/contracts/telemetry-schema-v1.json;firmware/src/runtime_uplink_frame.h;backend/laravel/tests/Feature/RuntimeUplinkIntegrationTest.php;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;backend/laravel/tests/Feature/ContinuousSimulationIntegrationTest.php;scripts/data_ui_contracts.py;scripts/run_formal_data_native.py;scripts/review_formal_data_ui.py / evidence/test-results/phase8-h1-summary-20261017.md;evidence/test-results/esp32-transport-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/data-ui-case-review-20261026.md | SUP-011 dedicated actual C99 identity/source/schema/quality contract PASS before DB fixture mutation; real PHP/MariaDB/read crosschecks retain six complete native packets and all48 latest1.1 channels. Required uint64/scalar/channel bounds and negative cases executed. Host/native proof does not establish hardware acquisition. |
| TEL-002: Invalid/missing channel values shall be null/absent with quality metadata, never silently converted to zero. | IMPLEMENTED_UNVERIFIED | PASS / SUP-012 | firmware/src/telemetry_contract.h;docs/contracts/telemetry-schema-v1.json;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;backend/laravel/tests/Feature/ContinuousSimulationIntegrationTest.php;scripts/data_ui_contracts.py;scripts/run_formal_data_native.py;scripts/review_formal_data_ui.py / evidence/test-results/phase8-h1-summary-20261017.md;evidence/test-results/device-read-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/data-ui-case-review-20261026.md | SUP-012 dedicated actual native UNIT_TEST/NO_DB_WRITE PASS:175unavailable/null,166genuine valid zero,69stale observations. Invalid/missing/unknown cannot become safe zero; stale may retain finite value without being current. Actual PHP/DB/UI development integration is separate supporting proof. |
| TEL-003: Backend shall deduplicate samples by stable identity key and reject conflicting duplicates. | PARTIAL | PASS / SIM-014 | firmware/src/telemetry_contract.h;docs/contracts/telemetry-contract-v1.md;backend/laravel/tests/Feature/FirmwareMySqlIntegrationTest.php;scripts/run_live_http_integration.py;backend/laravel/tests/Support/LiveHttpSafety.php;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;backend/laravel/tests/Feature/ContinuousSimulationIntegrationTest.php;scripts/data_ui_contracts.py;scripts/run_formal_data_native.py;scripts/review_formal_data_ui.py / evidence/test-results/phase8-h1-summary-20261017.md;evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/mariadb-integration-summary-20261025.md;evidence/test-results/security-php8235-summary-20261025.md;evidence/test-results/live-http-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/data-ui-case-review-20261026.md | SIM-014 dedicated actual isolated backend case PASS: fresh201, identical200, conflicting409; direct scoped MariaDB one row with original valid42value, no duplicate/overwrite. Existing unique device/boot/sequence schema unchanged; exact owned cleanup returns zero rows. |
| NET-001: Network client shall implement timeout, reconnect and bounded retry/backoff without blocking sampling. | PARTIAL | PASS / SIM-010;SIM-012;SIM-013 | firmware/src/network_transport_host_adapter.h;firmware/src/phase9_net001_uplink_host_bridge.h;firmware/src/esp32_network_client.c;firmware/src/esp32_network_profile.h;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/esp32_continuous_main.h;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/test_event_delivery_retry.py;scripts/test_event_delivery.py;scripts/event_retirement_file_fixture.c;scripts/resilience_host_fixture.c;scripts/resilience_native_bridge.py;scripts/formal_resilience.py;scripts/review_formal_resilience.py;scripts/test_formal_resilience.py / evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/esp32-transport-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/event-delivery-retry-summary-20261027.md;evidence/test-results/formal-resilience-case-review-20261027.md | PARTIAL: current shared bounded net001_host_step host actor executes actual TLS503 outage60047ms while sampling continues;3attempts stop until1explicit reset then actual read-only Laravel/up200. Dedicated SIM010/012/013 and independent review PASS with invalid/STALE/valid recovery and original facts. Host API-path driver is not physical WiFi or ESP32 SDK HTTP worker budget/RTOS execution. Real ESP-IDF worker/TLS/NVS production source unchanged, compiled evidence retained; hardware runtime/trusted clock/durability remain NOT_RUN. No automatic exhausted reset or new operational defaults. |
| NET-002: Offline mode shall preserve latest state and critical event journal within bounded storage. | PARTIAL | PASS / SUP-013 | firmware/src/core_event_journal.h;firmware/src/core_runtime_guard.h;firmware/src/main.c;firmware/src/offline_state.h;firmware/src/offline_transaction.h;firmware/src/esp32_offline_store.c;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/esp32_continuous_main.h;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;backend/laravel/database/migrations/2026_10_25_100006_add_alarm_metadata_to_monitoring_events.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/offline_bounded_file_fixture.c;scripts/formal_offline_file.py;scripts/host_offline_file_io.h;scripts/test_event_delivery_retry.py;scripts/test_event_delivery.py;scripts/event_retirement_file_fixture.c / evidence/test-results/firmware-core-c4-wokwi-20261013.md;evidence/test-results/esp32-transport-summary-20261025.md;evidence/test-results/offline-nvs-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/fault-storage-case-review-20261026.md;evidence/test-results/event-delivery-retry-summary-20261027.md | SUP-013 dedicated actual native/host-file integration PASS:72generations, two bounded slots3332/3344bytes, original8critical bootA facts/metadata retained while latest bootB sequence8 advances. Full refusal diagnostics RAM166/disk51 recorded, no guaranteed total retention. Older-file corruption preserves latest, healthy reopen after restoring only owned test byte. Host commit/reopen is not physical ESP32/NVS/power-loss durability; implementation remains PARTIAL. Failed-publication continuation20261027: actual parent C99 skipped an unconfirmed prefix after failed HTTP. Context-bound immutable fact/source/index/epoch rewind now retries the original without ACK/deletion/alarm clear; same-owner retrytag2, real committed-reply loss/MariaDB count1/duplicate200/genuine host-file retirement and both current SDK builds have scoped local evidence. Explicit exhausted transport reset and IO/crypto halt contracts retained; no physical durability/runtime or formal promotion. See event-delivery-retry-summary-20261027.md. |
| API-001: Laravel API shall validate authentication, schema, payload size, device identity and value contracts. | PARTIAL | PASS / SIM-015 | backend/laravel/routes/api.php;backend/laravel/app/Http/Controllers/Api/TelemetryIngestController.php;backend/laravel/app/Http/Middleware/AuthenticateDeviceToken.php;backend/laravel/app/Http/Middleware/EnsureTelemetryPayloadSize.php;backend/laravel/app/Http/Requests/TelemetryIngestRequest.php;backend/laravel/app/Http/Requests/EventIngestRequest.php;backend/laravel/tests/Feature/FirmwareMySqlIntegrationTest.php;scripts/run_live_http_integration.py;backend/laravel/tests/Support/LiveHttpSafety.php;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;backend/laravel/tests/Feature/ContinuousSimulationIntegrationTest.php;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/data_ui_contracts.py;scripts/run_formal_data_native.py;scripts/review_formal_data_ui.py / evidence/test-results/phase9-p3-runtime-http-evidence-audit-summary-20261018.md;evidence/test-results/phase9-p3-securityfix-feature-tests-audit-summary-20261018.md;evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/mariadb-integration-summary-20261025.md;evidence/test-results/security-php8235-summary-20261025.md;evidence/test-results/live-http-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/data-ui-case-review-20261026.md | SIM-015 actual local backend HTTP case PASS with fresh otherwise-valid401/401 and directDB0before/after; existing schema/size/device/value and negative security regression gates PASS. PHP8.2.35 and approved MariaDB only. No production/main DB or deployed TLS claim. |
| DB-001: All schema changes shall use Laravel migrations; no manual database shortcut is accepted. | PARTIAL | PASS / SUP-014 | backend/laravel/database/migrations/2026_10_17_100001_create_devices_table.php;backend/laravel/database/migrations/2026_10_17_100002_create_telemetry_samples_table.php;backend/laravel/database/migrations/2026_10_17_100003_create_telemetry_channels_table.php;backend/laravel/database/migrations/2026_10_18_100004_create_monitoring_events_table.php;scripts/run_mysql_integration.py;backend/laravel/tests/Support/TestEnvironment.php;backend/laravel/database/migrations/2026_10_25_100005_create_monitoring_access_tables.php;backend/laravel/tests/Support/TestSchema.php;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;backend/laravel/database/migrations/2026_10_25_100006_add_alarm_metadata_to_monitoring_events.php;firmware/src/offline_state.h;scripts/run_mysql_integration.py;scripts/test_mysql_integration_gate.py / evidence/test-results/phase9-p3-migration-rollback-support-summary-20261018.md;evidence/test-results/phase9-p3-migration-rollback-support-evidence-audit-summary-20261018.md;evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/mariadb-integration-summary-20261025.md;evidence/test-results/security-php8235-summary-20261025.md;evidence/test-results/dashboard-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/fault-storage-case-review-20261026.md | SUP-014 dedicated actual guarded Laravel6migration rollback/apply/reapply PASS on approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex/MariaDB10.4.32 with explicit PHP8.2.35 and ephemeral valid process key. Current382tests/0fail/0skip and independent final catalog10tables/6records/0app rows PASS; public source stable. Historical protocol target explicitly revised by dated execution protocol without editing old pinned matrix. No manual DDL/mainDB/directMySQL8 approval. |
| UI-001: Dashboard shall distinguish live, stale, offline and simulation states visibly. | IMPLEMENTED_UNVERIFIED | PASS / SIM-010 | backend/laravel/app/Support/DashboardSignalLabel.php;backend/laravel/resources/views/monitoring/index.blade.php;backend/laravel/routes/web.php;backend/laravel/app/Support/MonitoringFreshness.php;backend/laravel/app/Http/Controllers/MonitoringController.php;scripts/run_live_http_integration.py;backend/laravel/tests/Support/LiveHttpSafety.php;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;backend/laravel/tests/Feature/ContinuousSimulationIntegrationTest.php;backend/laravel/public/assets/monitoring-freshness.js;backend/laravel/resources/views/monitoring/freshness.blade.php;backend/laravel/tests/Feature/MonitoringExpiryTest.php;scripts/browser_monitoring_probe.js;scripts/test_monitoring_freshness.js;scripts/resilience_host_fixture.c;scripts/resilience_native_bridge.py;scripts/formal_resilience.py;scripts/review_formal_resilience.py;scripts/test_formal_resilience.py / evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/dashboard-summary-20261025.md;evidence/test-results/live-http-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/receipt-expiry-summary-20261026.md;evidence/test-results/formal-resilience-case-review-20261027.md | Local software visibly distinguishes receipt-policy LIVE/STALE/OFFLINE and simulation. Current actual owned Chrome155 component PASS with2s/4s fixture thresholds, Secure/HttpOnly/Lax session, no polling, neutral SNAPSHOT without script/asset and UNKNOWN with missing timing; four labels agree. Dedicated actual60s host SIM010 PASS includes explicit offline network diagnostics; Chrome component is separate supporting integration, not a60s browser outage or physical freshness proof. Approved outside-sandbox run passes unchanged browser source after in-sandbox Page.enable crash; failures retained. Local HTTP localhost browser edge to strict HTTPS upstream is not deployed TLS; implementation remains UNVERIFIED. |
| UI-002: Dashboard shall provide overview, safety, propulsion, navigation, power, alarms/events, device health and test evidence views. | IMPLEMENTED_UNVERIFIED | PASS / SUP-015 | backend/laravel/resources/views/monitoring/index.blade.php;backend/laravel/resources/views/monitoring/sections/overview.blade.php;backend/laravel/app/Services/DeviceEventReadService.php;backend/laravel/app/Services/MonitoringAccess.php;backend/laravel/app/Support/MonitoringEvidence.php;scripts/run_live_http_integration.py;backend/laravel/tests/Support/LiveHttpSafety.php;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;backend/laravel/tests/Feature/ContinuousSimulationIntegrationTest.php;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;scripts/data_ui_contracts.py;scripts/run_formal_data_native.py;scripts/review_formal_data_ui.py / evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/device-read-summary-20261025.md;evidence/test-results/dashboard-summary-20261025.md;evidence/test-results/live-http-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/data-ui-case-review-20261026.md | SUP-015 read-only FUNCTIONAL_REVIEW/NO_DB_WRITE PASS for actual authenticated/granted eight-section semantic/hash evidence with connected data, quality, provenance and freshness. Producer separately writes approved owned test DB/session fixtures; reviewer performs no DB access. Secure project root entry and5retained regressions PASS. Graphical/deployed browser verification remains NOT_RUN. |
| SEC-001: No production secret, real operational route or coordinate, radio frequency, credential, or confidential vessel detail shall be committed to public GitHub. | PARTIAL | PASS / SUP-016 | scripts/audit_precommit_security.py;docs/github-repository-plan.md;scripts/security-reviewed-findings.json;scripts/create_public_archive.py;scripts/test_public_archive.py;scripts/test_public_archive_safety.py;docs/public-release-archive.md / evidence/test-results/phase4-closure-summary-20261016.md;evidence/test-results/phase9-wave1-sup016-security-review-20261020.txt;evidence/test-results/security-php8235-summary-20261025.md;evidence/test-results/final-local-audit-requirements-20261027.csv;evidence/test-results/final-local-audit-final-code-delta-20261027.txt;evidence/test-results/final-local-audit-packaging-current-proof-20261027.json | Public-repository security review SUP-016 PASS within reviewed scope; no production security or deployment approval claimed. PHP 8.2.35 continuation: 215 tests and verified migration roundtrip PASS; content security scan has zero unresolved findings/privacy warnings with exact reviewed non-secret/author metadata pins. No hosted CI, direct MySQL 8, TLS or new formal verification claimed. Final local software audit20261027: archive exact-set/defaults/overwrite/admission defects repaired;dotenv/cache/private historic blob metadata excluded before content;new exclusive output and exact filtered commit validation. Full38decision32local_complete6external is separate from unchanged formal/implementation status. Historical private-profile evidence stays local and unchanged;public omission is exact path/blob pinned,not a scanner waiver. |
| SEC-002: Demo API shall use HTTPS/authentication and secrets shall be external to source code. | PARTIAL | PASS / SIM-015 | backend/laravel/routes/api.php;backend/laravel/app/Http/Middleware/AuthenticateDeviceToken.php;backend/laravel/app/Services/DeviceTokenAuthenticator.php;backend/laravel/config/app.php;backend/laravel/app/Services/MonitoringAccess.php;backend/laravel/app/Http/Controllers/MonitoringSessionController.php;firmware/src/esp32_network_client.c;firmware/sdkconfig.defaults;firmware/src/esp32_offline_store.c;scripts/run_live_http_integration.py;backend/laravel/tests/Support/LiveHttpSafety.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/data_ui_contracts.py;scripts/run_formal_data_native.py;scripts/review_formal_data_ui.py / evidence/test-results/phase9-p3-security-review-20261018.txt;evidence/test-results/phase9-p3-securityfix-feature-tests-audit-summary-20261018.md;evidence/test-results/security-php8235-summary-20261025.md;evidence/test-results/dashboard-summary-20261025.md;evidence/test-results/esp32-transport-summary-20261025.md;evidence/test-results/offline-nvs-summary-20261025.md;evidence/test-results/live-http-summary-20261025.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/data-ui-case-review-20261026.md | SIM-015 actual private loopback TLS/authentication case PASS, including CA/hostname/no-downgrade, fresh unauthorized no-acceptance and no secret echo. Secrets remain external/process-generated, scanner/manual gates required. Physical/deployed TLS, hardware key/storage and production readiness remain NOT_RUN. |
| TST-001: Every requirement shall map to code module, automated/manual test and evidence. | PARTIAL | PASS / SUP-017 | requirements/traceability-matrix.csv;docs/testing/living-requirement-status.csv;docs/testing/firmware-evidence-index.md;scripts/run_mysql_integration.py;scripts/run_live_http_integration.py;backend/laravel/tests/Support/LiveHttpSafety.php;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;scripts/test_public_reference_audit.py;scripts/test_event_delivery_retry.py;scripts/test_event_delivery.py;scripts/event_retirement_file_fixture.c;docs/testing/final-local-software-audit-20261027.md / evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/mariadb-integration-summary-20261025.md;evidence/test-results/security-php8235-summary-20261025.md;evidence/test-results/dashboard-summary-20261025.md;evidence/test-results/live-http-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/fault-storage-case-review-20261026.md;evidence/test-results/fault-storage-reference-audit-run1-20261026.json;evidence/test-results/event-delivery-retry-summary-20261027.md;evidence/test-results/final-local-audit-requirements-20261027.csv;evidence/test-results/final-local-audit-source-and-baseline-proof-20261027.json | SUP-017 dedicated read-only public-reference audit PASS for38original LOCKED requirement mappings and34case definitions/records, real implementation/evidence paths and plan links. Duplicate header/row shadowing, wrong definition/mapping, private/foreign/linked paths and unstable reads rejected. Exact .env.example reference metadata-only/no content hash. Public inventory is point-in-time; NOT_RUN/PLANNED not inferred PASS, no full semantic/hardware or requirement VERIFIED approval. Failed-publication continuation20261027: actual parent C99 skipped an unconfirmed prefix after failed HTTP. Context-bound immutable fact/source/index/epoch rewind now retries the original without ACK/deletion/alarm clear; same-owner retrytag2, real committed-reply loss/MariaDB count1/duplicate200/genuine host-file retirement and both current SDK builds have scoped local evidence. Explicit exhausted transport reset and IO/crypto halt contracts retained; no physical durability/runtime or formal promotion. See event-delivery-retry-summary-20261027.md. Final local audit20261027 classifies32local implementation complete but unverified and6external prerequisites without changing LOCKED or formal registry statuses. Additional compiler/sanitizer coverage limitations are distinct from mandatory baseline gates;no new simulation/admin iteration after bounded final closure. |
| TST-002: CI shall build firmware and backend tests on each pull request; Wokwi CI shall be added if available for the project plan. | PARTIAL | NOT_RUN / SUP-018 | .github/workflows/phase9-multi-context-ci.yml;scripts/run_mysql_integration.py;scripts/build_esp32_port.py;scripts/test_esp32_build_gate.py;scripts/test_offline_state.py;scripts/test_offline_transaction.py;scripts/run_live_http_integration.py;backend/laravel/tests/Support/LiveHttpSafety.php;firmware/src/domain_snapshot.h;firmware/src/continuous_simulation.h;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;backend/laravel/database/migrations/2026_10_25_100006_add_alarm_metadata_to_monitoring_events.php;firmware/src/offline_state.h;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php / evidence/test-results/mysql-integration-gate-20261025.md;evidence/test-results/mariadb-integration-summary-20261025.md;evidence/test-results/security-php8235-summary-20261025.md;evidence/test-results/esp32-transport-summary-20261025.md;evidence/test-results/offline-nvs-summary-20261025.md;evidence/test-results/live-http-summary-20261025.md;evidence/test-results/continuous-simulation-summary-20261025.md;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md | PARTIAL: PR source includes native offline codec/transaction tests and pinned SDK build checks. Actual local source, native and PHP 8.2.35/MariaDB gates have dated evidence. Hosted CI, direct MySQL 8 and SUP-018 remain NOT_RUN. CI source now includes the guarded loopback TLS pipeline after full isolated backend migration/tests. Hosted CI, direct MySQL 8 and SUP-018 remain NOT_RUN. Continuous simulation continuation adds typed full-domain 1.1 snapshots and local/native/isolated backend evidence; v1.0 compatibility and formal statuses remain unchanged. See latest summary for scoped gates and hardware limits. CI source includes complete-metadata native codec/transition gates and real schema-six backend/loopback integration. Both SDK targets retain partition/TLS/assertion/stack checks; hosted CI and direct MySQL 8 remain NOT_RUN. Recovered replay continuation preserves original cross-boot identities and known/unknown metadata through a zero-wait recovered NVS-worker view and fair event queueing. Local native/PHP/MariaDB/TLS evidence does not authorize deletion/application ACK or establish physical recovery, delivery guarantees or new formal PASS; see latest replay summary. Authenticated receipt continuation adds exact-body/status HMAC, VGS3 confirmed floor, worker durable retirement and shared single-inflight RAM release. Actual host-file/MariaDB/loopback and both SDK results are in the latest receipt summary; all local functional/build/regression/working-security/manual gates passed; final staged-byte review is required before commit. No alarm condition is cleared; host readback is not physical NVS durability or formal verification. |
| DOC-001: Repository shall contain architecture, ICD, standards matrix, FMEA, ADRs, traceability matrix, test evidence and limitations. | IMPLEMENTED_UNVERIFIED | PASS / SUP-019 | docs/architecture/architecture-and-icd.md;docs/standards/standards-applicability-matrix.md;docs/fmea/fmea-prototype.md;docs/adr/0001-repository-naming.md;docs/testing/firmware-evidence-index.md;firmware/src/alarm_transition.h;backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php;firmware/src/offline_replay.h;backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php;firmware/src/event_delivery.h;firmware/src/offline_retirement.h;backend/laravel/app/Support/EventCommitReceipt.php;docs/testing/vessel-survey-readiness.md;docs/testing/local-software-review-20261027.md;docs/testing/final-local-software-audit-20261027.md / evidence/test-results/phase9-wave1-sup019-documentation-review-20261021.txt;evidence/test-results/alarm-metadata-summary-20261025.md;evidence/test-results/recovered-replay-summary-20261026.md;evidence/test-results/event-receipt-summary-20261026.md;evidence/test-results/local-software-review-20261027.csv;evidence/test-results/final-local-audit-requirements-20261027.csv;evidence/test-results/final-local-audit-source-and-baseline-proof-20261027.json | Engineering documentation inventory reviewed under SUP-019 PASS; document presence does not establish system approval. ADR-0008 and the complete event 1.1 schema/design/evidence describe compatibility, exact metadata, migration profiles, capacity and remaining replay/hardware/formal gaps. Recovered replay continuation preserves original cross-boot identities and known/unknown metadata through a zero-wait recovered NVS-worker view and fair event queueing. Local native/PHP/MariaDB/TLS evidence does not authorize deletion/application ACK or establish physical recovery, delivery guarantees or new formal PASS; see latest replay summary. Authenticated receipt continuation adds exact-body/status HMAC, VGS3 confirmed floor, worker durable retirement and shared single-inflight RAM release. Actual host-file/MariaDB/loopback and both SDK results are in the latest receipt summary; all local functional/build/regression/working-security/manual gates passed; final staged-byte review is required before commit. No alarm condition is cleared; host readback is not physical NVS durability or formal verification. Dated roadmap continuation20261027: Phase14 six-area technical survey checklist PREPARED, all38 local software dispositions reviewed; no new requirement approval, physical survey or hardware/deployment evidence. Checklist preparation does not advance past open Phase12/13 gates. Final local audit20261027 classifies32local implementation complete but unverified and6external prerequisites without changing LOCKED or formal registry statuses. Additional compiler/sanitizer coverage limitations are distinct from mandatory baseline gates;no new simulation/admin iteration after bounded final closure. |

## Resume dan roadmap berdasarkan dependensi

1. Verify actual develop HEAD/index/worktree against top checkpoint and actual source proofs. Baseline audit done; do not repeat implemented code or overwrite protected/unrelated WIP. Current major batch is resilience6scope, all functional gates PASS, final staged/commit guards still required until actual commit is recorded.
2. Read formal-resilience-summary/gate-matrix/source-proof/case-review-20261027.*. Current source81fa45d1 HTTP has fresh PHP388, readonly actual60047ms, normalTLS248checks and approved Chrome155 PASS. Broad248commands/native12/HTTP26/Node13/core226repeat2 PASS. Retain old failed/interrupted/blocked evidence; do not substitute it for current-source proof.
3. Finish latest docs/living38/reference/manual/security guards,owned-log encoding audit and exact manifest; then stage exact files,verify every staged blob/hash/path/branch/parent/protected/diff gate,staged scanner and final read-only scan before local commit. No push. A known failed/missing mandatory gate forbids commit.
4. Immediately update BOTH handoffs after a major successful local commit with actual new HEAD,tests/evidence/traceability/blockers and explicit postcommit context WIP. A commit cannot embed its own hash. Continue targeted remaining software assessment against the original38/roadmap,not administrative numbering or duplicate mocks; do not stop because one commit succeeded.
5. All15SIM now have accepted scoped execution records;18SUP PASS and hostedSUP018 PLANNED. Derived37mappedPASS/1NOT_RUN is not requirementVERIFIED; implementation22UNVERIFIED/16PARTIAL. Actual ESP32/RTOS/WiFi/TLS/NVS/PSA/powerloss,hostedCI,deployedTLS/directMySQL8/POSIX/graphical operator acceptance remain NOT_RUN. Host actor is controlled shared-C99 composition,not SDK runtime; browser component2s/4s is not a60s browser outage.
6. PHP C:/tools/php-8.2.35/php.exe explicit and child VG_PHP_CLI; approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex/MariaDB10.4.32 only. DB was restored by user; require effective config/key/catalog admission and exact empty postflight. Run DB gates sequentially. Chrome Page.enable crashes in sandbox; approved outside-sandbox SAME source/flags PASS. Respect approval,no bypass/security-flag or deadline weakening.
7. Preserve LOCKED/AGENTS/two firmware untracked,old metadata stat-cache bytes,all history/evidence/migrations/secrets/WIP. No main dotenv/DB,manualDDL,globalPATH/XAMPP,physical control,remote/reset/clean/history rewrite. Verified Safe Cleanup only positively proven tracked SAFE_TO_DELETE after full gates; current welcomeDEFERRED/present,removed0.

```powershell
$env:VG_PHP_CLI = 'C:/tools/php-8.2.35/php.exe'
python -B scripts/check_living_traceability.py
python -B scripts/test_formal_resilience.py
python -B scripts/test_live_http_integration_gate.py
# Read-only admission after runtime/service changes; stop if it fails.
python -B scripts/run_live_http_integration.py --testing-env --php-binary C:/tools/php-8.2.35/php.exe
python -B scripts/audit_precommit_security.py
```

Use current source-bound actual evidence to avoid unnecessary reruns; a relevant code change invalidates affected proofs. New CLI reports/logs must use NEW filenames. The independent reviewer takes --log and --report and never boots PHP/network/DB. Actual runtime commands are recorded in formal-resilience-execution-commands-20261027.json; browser requires approved execution when sandbox prevents Chrome renderer. Use existing child GCC PATH only when needed,never global PATH. Public-reference audit reads no dotenv content; exact tracked .env.example metadata-only. All text reads/writes UTF8.

## Blocker dan risiko terbuka

Current local DB/TLS/native/browser environment blocker is RESOLVED: user
restored approved testing instance, fresh effective preflight/PHP388/actual60047ms/
normalTLS248/approved Chrome155 and exact cleanup PASS on current source81fa45d1.
The sandbox-only Chrome Page.enable crash remains a documented execution
limitation,not an app-code fix; use approved outside-sandbox GUI execution.

Physical ESP32/RTOS/WiFi/NVS/PSA execution,wear/powerloss/rollback,full heap/
callstack,timing,physical flash capacity,trusted-clock provisioning NOT_RUN.
CurrentWokwi,hostedCI,directMySQL8/POSIX,graphical operator acceptance/deployedTLS
NOT_RUN. All15SIM and18SUP scoped PASS;hostedSUP018 PLANNED. Derived mapped
formal37PASS/1NOT_RUN,implementation22IMPLEMENTED_UNVERIFIED/16PARTIAL,no VERIFIED.
No test/SDK compilation establishes physical acceptance,standards conformity,
residual-risk approval,production readiness or completed system verification.

Original36 scanner occurrences were32INFO false positives,2LOW synthetic CI,
2MEDIUM CI issues fixed beforeb999492; current five INFO occurrences are exact
unchanged CI/runtime source lines with renewed whole-file+line pins. Actual
initial scanner FAIL is retained and a final zero-unresolved screen is mandatory.
See security-scanner-review and current triage/summary. Genuine historical RR
race500 and metadata diagnostics were corrected and remain in regression.
New fixture/oracle failures are recorded honestly; final passing gates supersede
failures only for the corrected exact source, never erase their history.

## Prompt pembuka siap pakai

Lanjutkan Integrated Vessel Monitoring & Diagnostic Gateway dari HEAD develop dan worktree AKTUAL; checkpoint paling atas/Git/source/evidence mengalahkan sejarah. Baca AGENTS.md dan kedua handoff. Baseline audit sudah selesai; jangan mengulang implementasi, menimpa WIP/protected, membaca main .env/DB, mengubah LOCKED38/AGENTS/dua firmware untracked atau push. Batch resilience6scope sudah memiliki source-bound PHP388/actual60047ms readonly host/normalTLS248checks/approvedChrome155/broad248commands PASS; source81fa45d1 HTTP,516446eb MySQL,f693b0cb SDK unchanged. All15SIM/18SUP scoped PASS,hostedSUP018 PLANNED,37mappedPASS1NOT_RUN,22UNVERIFIED16PARTIAL,no VERIFIED. Old DB3307 blocker resolved by user; Chrome fails Page.enable inside sandbox but SAME source/flags PASS approved outside sandbox, no weakened security. Finish only pending latest docs/reference/manual/security/manifest/exact-index/staged/final guards before local commit if not yet recorded; do not claim commit until actual Git result. Update BOTH handoffs after major commit and continue substantive remaining safe local software per original38/roadmap and dependencies. Exact-scope commit only all mandatory gates PASS; no globalPATH/XAMPP/manualDDL/mainDB/physical control/history rewrite. Verified Safe Cleanup only positive SAFE_TO_DELETE;welcomeDEFERRED/removed0. Keep hardware/RTOS/NVS/PSA/powerloss/hostedCI/deployedTLS/directMySQL8/POSIX/graphical operator acceptance NOT_RUN;systemPARTIAL/finalNOT_APPROVED.

## Hash penjaga checkpoint

| File | SHA256 |
|---|---|
| `requirements/system-requirements.md` | `a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b` |
| `requirements/traceability-matrix.csv` | `bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3` |
| `AGENTS.md` | `421e2b5d5748cf5e4bdac3c189223915850c8894688a7e3ffd090975aa87864b` |
| `firmware/.gitignore` | `d952abf002d5e1ec80c8ab1bfc9f38eb5b62fc310667d501cb2ce9f21c3effb2` |
| `firmware/.vscode/extensions.json` | `31cc8f05084d96b65be8f147533017c7a1b89b055d85886a2e4ab3ce532f34fb` |
| `docs/testing/formal-scenario-status.csv` | `391048d94f1c792a193480ed439d6bb2b346ef182cf9be7a8d11d412c993ceb7` |
| `docs/testing/supplemental-verification-plan.csv` | `97a89bfa2643305f734e662c7cb0e0f5daccf49742c8a2683223510e083a51ff` |


## Receipt scope committed5727969 (historical exact path inventory)

The following receipt paths were committed5727969; they are not unfinished implementation:

- `.github/workflows/phase9-multi-context-ci.yml`
- `backend/laravel/app/Http/Controllers/Api/EventIngestController.php`
- `backend/laravel/app/Support/EventCommitReceipt.php`
- `backend/laravel/tests/Feature/EventCommitReceiptIntegrationTest.php`
- `backend/laravel/tests/Unit/EventCommitReceiptTest.php`
- `docs/adr/0010-authenticated-event-retirement.md`
- `docs/handoff/CHATGPT_CONTEXT.md`
- `docs/handoff/CODEX_RESUME.md`
- `docs/testing/event-receipt-retirement-plan.md`
- `docs/testing/living-requirement-status.csv`
- `firmware/src/esp32_continuous_main.h`
- `firmware/src/esp32_network_client.c`
- `firmware/src/esp32_network_client.h`
- `firmware/src/esp32_offline_store.c`
- `firmware/src/esp32_offline_store.h`
- `firmware/src/event_commit_receipt.h`
- `firmware/src/event_delivery.h`
- `firmware/src/offline_replay.h`
- `firmware/src/offline_retirement.h`
- `firmware/src/offline_state.h`
- `firmware/src/offline_transaction.h`
- `scripts/event_receipt_native_bridge.py`
- `scripts/event_receipt_native_crypto.h`
- `scripts/event_receipt_verify_fixture.c`
- `scripts/event_retirement_file_fixture.c`
- `scripts/run_live_http_integration.py`
- `scripts/security-reviewed-findings.json`
- `scripts/test_alarm_offline_metadata.py`
- `scripts/test_event_commit_receipt.py`
- `scripts/test_event_delivery.py`
- `scripts/test_event_retirement_file.py`
- `scripts/test_live_http_integration_gate.py`
- `scripts/test_offline_authenticated_retirement.py`
- `scripts/test_offline_confirmed_floor.py`
- `scripts/test_offline_replay.py`

New receipt logs/triage/cleanup evidence are under evidence/test-results/event-receipt-* and esp32-transport-sdk-build-event-receipt-*. Final exact manifest records every approved file; untracked protected files and byte-identical old metadata logs are excluded. Index empty at this saved checkpoint. Receipt batch fully committed5727969; only these two automatically updated handoffs are current WIP before next substantive scope.

## Historical provider batch path inventory (now committed0507fc9)

These source/docs/tests/evidence paths are now committed0507fc9; they are not unfinished implementation.

- `.github/workflows/phase9-multi-context-ci.yml`
- `README.md`
- `docs/fmea/fmea-prototype.md`
- `docs/github-repository-plan.md`
- `docs/handoff/CHATGPT_CONTEXT.md`
- `docs/handoff/CODEX_RESUME.md`
- `docs/testing/firmware-evidence-index.md`
- `docs/testing/formal-provider-cases-20261026.md`
- `docs/testing/living-requirement-status.csv`
- `docs/testing/security-scanner-review.md`
- `docs/testing/supplemental-verification-plan.csv`
- `docs/testing/traceability-status.md`
- `evidence/test-results/esp32-transport-sdk-build-formal-provider-candidate-20261026.txt`
- `evidence/test-results/esp32-transport-sdk-build-formal-provider-retained-20261026.txt`
- `evidence/test-results/formal-provider-case-results-20261026.csv`
- `evidence/test-results/formal-provider-case-review-20261026.md`
- `evidence/test-results/formal-provider-checkpoint-audit-20261026.txt`
- `evidence/test-results/formal-provider-cleanup-audit-20261026.csv`
- `evidence/test-results/formal-provider-development-observations-20261026.txt`
- `evidence/test-results/formal-provider-encoding-review-20261026.csv`
- `evidence/test-results/formal-provider-execution-final-20261026.txt`
- `evidence/test-results/formal-provider-execution-run1-20261026.txt`
- `evidence/test-results/formal-provider-execution-run2-20261026.txt`
- `evidence/test-results/formal-provider-execution-utf8-final-20261026.txt`
- `evidence/test-results/formal-provider-final-delta-regression-20261026.txt`
- `evidence/test-results/formal-provider-focused-regression-run1-20261026.txt`
- `evidence/test-results/formal-provider-http-20261026.txt`
- `evidence/test-results/formal-provider-integrated-regression-20261026.txt`
- `evidence/test-results/formal-provider-mysql-20261026.txt`
- `evidence/test-results/formal-provider-security-initial-20261026.txt`
- `evidence/test-results/formal-provider-security-triage-20261026.csv`
- `evidence/test-results/formal-provider-security-working-20261026.txt`
- `evidence/test-results/formal-provider-summary-20261026.md`
- `firmware/src/navigation_nmea.h`
- `scripts/formal_provider_fixture.c`
- `scripts/run_formal_provider_verification.py`
- `scripts/security-reviewed-findings.json`
- `scripts/test_formal_provider_verification.py`

Protected three untracked files and byte-identical old metadata stat-cache entries remain excluded. Current nav source has fresh matching SDK/HTTP proofs. Encoding restoration has exact before/after SHA inventory; no LOCKED/user file changed.

Late exact-scope review removed only an unused diagnostic local from the unchanged
race helper after the246command PASS. Current TLS215 and Chrome reran PASS on
sourcefd71a424..., plus4targeted HTTP24/UI002/evidence/reference guard groups PASS
in receipt-expiry-final-scope-docs-delta-20261026.txt. No production behavior change.

Historical retry-ordering precommit checkpoint:48exact paths/blobs/manifest/
index/diff/parent/branch and scanners PASS, completed by commit4892054. The later
resilience batch is committed98455c3 with all scoped gates PASS. This historical
paragraph is not a current WIP/gate instruction; use the latest top checkpoint.
