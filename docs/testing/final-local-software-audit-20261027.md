# Final local software audit and completion decision

Audit source: develop `81e9bfbb36d357a55476bb44d985cd8fa095e4c5`,2026-10-27.
Decision: **LOCAL_SOFTWARE_SCOPE_COMPLETE_WITH_EXTERNAL_BLOCKERS**, effective
only after the final scoped mandatory gate matrix is PASS and Git records the
exact-scope local commit. Before that checkpoint it is a proposed disposition.
This is completion of the authorized local software implementation, not whole
system verification, exhaustive absence of bugs or production readiness.

## Authority and unchanged state

The original38requirements and mappings are unchanged. Implementation registry
stays22IMPLEMENTED_UNVERIFIED/16PARTIAL; formal mapping37PASS/1NOT_RUN. All15SIM have
scoped PASS,18SUP PASS/SUP018 PLANNED. SYSTEM_PARTIAL,NOT_RUN and NOT_APPROVED are
preserved;no requirement becomes VERIFIED. Field rules,physical acquisitions,
OEM protocols,pins,thresholds and TBD answers are not invented.

The source review examined actual provider/quality/policy/alarm/coordinator and
SDK queue/worker boundaries;N-engine/deviation and development navigation;
telemetry serialization/validation,transactional dedup/schema,read/grant/UI and
freshness behavior;current CI,reference/security tooling,roadmap,ICD/BOM/FMEA and
both handoffs. Existing execution evidence was inspected for scope and terminal
results,then bound to unchanged HTTP/MySQL/SDK public input snapshots. It was not
inferred from a case label or a referenced filename alone. Historical design and
checkpoint statuses remain historical;current living registries govern counts.

## Requirement decisions

L = LOCAL_IMPLEMENTATION_COMPLETE_BUT_NOT_FORMALLY_VERIFIED.
X = EXTERNAL_PREREQUISITE, with the corresponding local implementation present
and the remaining runtime/target evidence requiring that external prerequisite.
32L/6X. No remaining REPRODUCIBLE_LOCAL_DEFECT identified after the archive repair.
No requirement has a mandatory baseline gate classified TOOL_VERIFICATION_BLOCKED;
additional optional compiler/sanitizer limits are recorded separately below.

The [full38row decision CSV](../../evidence/test-results/final-local-audit-requirements-20261027.csv)
contains original requirement text,implementation/test/evidence paths,unchanged
registry statuses,semantic observations and exact remaining dependencies. L does
not close a formal/hardware/disclosure approval;X does not imply an unimplemented
local software feature. This distinction follows the final-audit instruction.

| Requirement | Decision | Existing implementation / formal | Source/test/evidence observation |
|---|---|---|---|
| SYS-001 | L | PARTIAL / PASS | Prototype boundary is explicit in UI,firmware messages,requirements/roadmap;no certification or operational equipment claim introduced. |
| SYS-002 | L | PARTIAL / PASS | Known modes and quality/provenance validation implemented;synthetic simulation/bench/physical-labelled contract cases retain identity. Physical acquisition is not inferred. |
| SYS-003 | X | PARTIAL / PASS | Actual ESP32 acquisition/RTOS and flash/cache timing under network failure require protected authorized hardware. Shared C99 host outage60047ms/561cycles and SDK queues/builds are existing scoped evidence. |
| SYS-004 | L | PARTIAL / PASS | Current SDK composition only acquires/simulates,stores and transmits monitoring data;no starter/ignition/steering/radar/radio actuation path. Virtual start stays a policy result. |
| SAF-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Door enum and consistency enforce OPEN/CLOSED/UNKNOWN plus quality;invalid/missing cannot be current OPEN. |
| SAF-002 | L | IMPLEMENTED_UNVERIFIED / PASS | Configured BLOCK conditions reject virtual start with explicit reasons;disabled/alert-only modes retain their defined contract. |
| SAF-003 | L | PARTIAL / PASS | External explicit policy config distinguishes disabled,ALERT_ONLY,BLOCK where allowed;bilge/temperature forbid invented block interlocks;no field-verified rule label. |
| SAF-004 | L | IMPLEMENTED_UNVERIFIED / PASS | NORMAL/WARNING/ALARM/FAULT/UNKNOWN modeled;invalid/missing map FAULT,no current safe NORMAL fallback. |
| SAF-005 | L | IMPLEMENTED_UNVERIFIED / PASS | NORMAL/HIGH/FAULT/UNKNOWN modeled with quality;configured high-water monitoring is alert-only and does not invent starter control. |
| SAF-006 | L | IMPLEMENTED_UNVERIFIED / PASS | Temperature quality,presence,finiteness and configured demo thresholds distinguish invalid/missing/stale;recovery requires current VALID. |
| ALM-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Monotonic unique alarm/event identity,source,priority,state,reason and nullable lifecycle times preserved through sidecar,wire1.1,DB/API/UI. Legacy unknown metadata remains explicit. |
| ALM-002 | L | IMPLEMENTED_UNVERIFIED / PASS | ACK only sets acknowledgement metadata and ACTIVE_ACK;condition clearing requires separate evaluator action. Receipt retirement never clears an alarm. |
| ALM-003 | X | PARTIAL / PASS | Logical LED/buzzer independence implemented/tested; physical GPIO indications and wiring remain unexecuted and unauthorized. |
| ENG-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Bounded configurable N-engine model and explicit four-engine profile implemented;8-engine serializer boundary tested,no truncation. |
| ENG-002 | L | IMPLEMENTED_UNVERIFIED / PASS | Simulation exposes state,rpm,temperature,runtime,alarm and communication quality;lost/unknown communication does not become a current zero measurement. |
| ENG-003 | L | IMPLEMENTED_UNVERIFIED / PASS | Configured RPM deviation compares eligible peers;normal2010 vs fault1500 engine3 and original recovery events tested. |
| ENG-004 | L | PARTIAL / PASS | Yamaha physical interface remains documented TBD/placeholder,with no physical provider implementation or guessed model/protocol. This is the required local state. |
| NAV-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Approved development RMC-style formatter/parser/checksum implementation uses GP39 reference only;Phase7 scope does not claim full NMEA conformity or installed GP39. |
| NAV-002 | L | IMPLEMENTED_UNVERIFIED / PASS | Navigation state and serialized fields expose position,SOG,COG,fix,age,quality;no-fix positions unavailable;only synthetic positions used. |
| NAV-003 | L | IMPLEMENTED_UNVERIFIED / PASS | Checksum/malformed/regressing arrivals rejected before replacing state;invalid input cannot refresh old valid data. |
| NAV-004 | L | IMPLEMENTED_UNVERIFIED / PASS | Explicit configured age limits transition VALID/STALE/OFFLINE at boundaries;monotonic age cannot rewind. |
| MOT-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Roll/pitch prototype values,quality and attitude/motion label implemented;no stability assessment claim. |
| VIB-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Demo vibration index and fault/quality implemented;no machinery-diagnosis claim. |
| PWR-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Safe low-power simulator/INA219 bench-interface contracts and quality implemented;propulsion-current acquisition is excluded. |
| TEL-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Wire1.0 and1.1 preserve version/device/firmware/boot/sequence/uptime/source and per-channel quality;exact integer boundaries tested. |
| TEL-002 | L | IMPLEMENTED_UNVERIFIED / PASS | Serializer/admission/storage/read/UI retain invalid/missing null vs valid zero and stale quality;nonfinite values refused. |
| TEL-003 | L | PARTIAL / PASS | Unique device/boot/sequence plus transaction classification return201/200/409;identical retry retains one row and conflicts do not overwrite. |
| NET-001 | X | PARTIAL / PASS | Async SDK WiFi/HTTPS worker and bounded host timeout/backoff/explicit exhausted reset implemented. Actual board WiFi/worker/clock behavior and callback timing need hardware. |
| NET-002 | X | PARTIAL / PASS | Bounded latest state/journal, explicit refusal, replay and authenticated durable host-file retirement implemented. Actual ESP32 NVS power-loss/wear/physical scheduling durability needs hardware. |
| API-001 | L | PARTIAL / PASS | Real middleware/request/service contract validates bearer,schema,4096byte bound,device identity,value/null/quality/raw integer and duplicate JSON keys. |
| DB-001 | L | PARTIAL / PASS | All6schema changes are Laravel migrations;guarded approved MariaDB rollback/apply/reapply and isolated suite evidence retained;no manual DDL. |
| UI-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Eight-view UI and actual Chrome distinguish LIVE/STALE/OFFLINE and simulation;monotonic no-poll display expiry,neutral SNAPSHOT/UNKNOWN fallback implemented. |
| UI-002 | L | IMPLEMENTED_UNVERIFIED / PASS | Overview,safety,propulsion,navigation,power,alarms/events,health,evidence are connected;authenticated grant boundary and original alarm facts preserved. |
| SEC-001 | L | PARTIAL / PASS | Source/index/WIP gates and public-path policy implemented. Reproduced archive parity/defaults/no-clobber/admission defects fixed with focused integration and security tests;manual disclosure approval still separate. |
| SEC-002 | X | PARTIAL / PASS | Strict verified loopback TLS/auth and external secrets implemented. Actual deployed/physical TLS and externally provisioned trusted clock/keys require the authorized target environment. |
| TST-001 | L | PARTIAL / PASS | Unchanged38LOCKED mappings/34cases plus current source,test,evidence references and scoped execution statuses are auditable;path presence alone is not semantic approval. |
| TST-002 | X | PARTIAL / NOT_RUN | Actual PR workflow builds firmware/backend and source registers safety checks. Hosted clean-clone SUP018 remains PLANNED;no execution or remote trigger is authorized here. |
| DOC-001 | L | IMPLEMENTED_UNVERIFIED / PASS | Architecture,ICD,standards,FMEA,ADRs,traceability,limitations,evidence,both handoffs and Phase14 six-area checklist are present;final audit reconciles their scoped statuses. |

## Reproducible local defect repaired: audit ZIP mechanism

Metadata-only reproduction found two tracked files rejected by the old exact-
tracked-set archive validator:the dotenv template and sdkconfig.defaults. No
contents of any dotenv file were inspected to establish the conflict. The shell
helper also forced temporary/output replacement. Old validation read forbidden
members before final metadata refusal,and skipped large/NUL-containing bodies.

The existing verifier/helper were repaired;the Bash entry delegates to the same
cross-platform exporter. A committed metadata allowlist excludes dotenv/private/
cache paths BEFORE blob content or size retrieval,retains sdkconfig.defaults,
uses exclusive new output outside the repo,checks exact filtered commit bytes,
rejects hostile paths/duplicates/links/modes/encryption/size violations before
payload reads,and never silently skips binary content. Directory payloads,comments,extra fields
and ambiguous/NUL-truncated names are also rejected as non-source metadata. Default is metadata-only;
execution requires clean tracked/index and reviewed untracked state. Interrupted
own output is retained and is never reported successful. No production source,
wire/schema/firmware/DB behavior changed. See [archive instructions](../public-release-archive.md).

New hostile-Git/ZIP integration and existing scanner tests pass in fresh owned
synthetic repositories. Actual HEAD metadata-only planning confirms filtered
selection and no output;dirty-WIP execution is deliberately blocked. The new
archive workflow source registers tests,but hosted execution remains NOT_RUN.
A full parent-HEAD admitted-payload audit initially found7historical blobs with
machine-profile paths. Original local evidence is preserved;exact path/blob-ID
omissions now report the restricted versions,while active handoffs redact profile
prefixes to <LOCAL_HOME>. A changed or unknown version still undergoes the full
ordinary scan. The final parent-HEAD review admits1542files/excludes8 (dotenv
metadata plus7exact versions),with0content findings. No ZIP was created by that
read-only review. New focused18+6tests cover pinned omission/nonmatching versions.
This tool creates a filtered review snapshot,not a complete clone/deployment or
publication approval. Existing raw workspace ZIPs containing local secrets/caches
must not be used as approved public snapshots;retain them privately under the
existing evidence policy. No old ZIP was opened,redistributed or deleted here.

## Mandatory baseline versus extra verification

Mandatory local gates for this repair are focused real Git/ZIP positive/negative/
boundary/security/no-clobber tests,retained scanner tests,relevant integrated
regression,source/LOCKED/protected/WIP equality,traceability/manual scope/security,
exact index/blob/manifest and final read-only scan. A metadata-only source package
repair does not require a new schema roundtrip or hardware run.

Prior actual source-matching baseline evidence remains PHP8.2.35/Laravel12.70.0/
MariaDB10.4.32,388/0FAIL/0SKIP,248TLS checks,248regression commands,actual Chrome155
component,both SDK builds and60047ms actual host outage. These runtime/DB/SDK
executions are retained,not claimed rerun by this audit. New relevant regression
is recorded separately. Approved DB remains127.0.0.1:3307/vessel_gateway_codex_test/
vgw_codex;no main DB,manual DDL,dotenv value or credential output is involved.

GCC full-composition7case analysis remains BLOCKED_TOOL_COVERAGE;759complexity
limits and the49limit probe are preserved and not rerun. Two bounded modular
object analyses of actual scalar measurement validation and network init
admission pass with all diagnostics enabled. They do not replace whole-program,
composition,RTOS or runtime proof. ASan/UBSan remain NOT_RUN:the local GCC did not
resolve matching sanitizer static/import libraries. A compatible compiler with
matching instrumented runtime and isolated fresh build is required;no global
PATH/configuration changes,downloads or fabricated PASS were used.

SUP018 requires actual hosted PR/clean-clone firmware/backend execution. Existing
workflow uses PHP8.2.35,isolated MySQL service,guarded migrations,host C99 and both
SDK targets;new source registers archive regressions. Local source inspection and
Windows component tests do not prove Ubuntu/POSIX,MySQL8 or hosted execution.
No push,remote trigger,fetch or merge was performed.

## Cleanup and remaining dependencies

[Tracked candidate inventory](../../evidence/test-results/final-local-audit-cleanup-inventory-20261027.csv):
11reviewed,5DEFERRED/6PROTECTED/0SAFE_TO_DELETE,0deletions. Welcome runtime role
has a replacement,but the unchanged prestaging scanner dependency still blocks
safe deletion. Vite CSS/JS and bootstrap imports remain configured;no absence-of-
text-hit argument is used. Used migrations,history,golden fixtures,instructions,
handoffs,evidence,all preexisting untracked and active WIP/secrets are protected.
Ignored vendor/.pio/local environments are not cleanup targets.

Remaining actual execution:authorized ESP32/RTOS/WiFi/PSA/NVS,external provisioning
and trusted-clock plan,power-loss/wear/full-stack/heap/timing,hosted CI/SUP018,
deployed TLS/direct MySQL8/POSIX and graphical/operator or field approval. The
six-area Phase14 checklist is preparation only;survey execution NOT_RUN and
physical integration NOT_AUTHORIZED. No residual FMEA risk is accepted.

## Closure and resume

Preserve the preexisting blocker/static-analysis/postcommit evidence and both
handoffs;the final exact manifest defines what is committed. All mandatory scoped
gates must PASS before any local commit;failed initial privacy review is retained
and corrected without scanner weakening. The synthetic test identity now uses a
non-address marker;it is not a person/contact/credential. No security waiver added.

After successful final gates,stop automatic local implementation iteration under
the final-audit instruction. Reopen only for a new reproducible local defect,
approved scope change or genuinely available external verification prerequisites.
Do not start another administrative/mock batch merely to keep a Goal active.
System remains PARTIAL/finalNOT_APPROVED. NO PUSH,remote merge,main DB,manual DB
changes,destructive Git or hardware upload.
