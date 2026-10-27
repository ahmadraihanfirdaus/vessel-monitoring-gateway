# Dedicated SIM-010 / SIM-012 / SIM-013 case review

Parent develop4892054dc4aed578702e102f17f31dc459668a63; resilience batch
UNCOMMITTED when reviewed. Fixed15case definitions and LOCKED38mapping unchanged.
Prepared execution class is SIMULATOR_HOST_PROTOCOL / NO_DB_WRITE for these3cases.
The dated pre-execution protocol is
docs/testing/formal-resilience-cases-20261027.md; its NOT_RUN_AT_PROTOCOL_CREATION
marker describes creation time, not the actual current execution result.

## Actual source and execution

HTTP execution source81fa45d15a8f800e85cbf82048df8086640f26dc88a63275746424282ceab49f
is bound to fresh readonly, normal integration and approved Chrome logs. Independent
read-only review_formal_resilience.py accepted the current readonly log and wrote
formal-resilience-current-case-review-20261027.json. The same reviewer rejected
older-source evidence for current acceptance, as required.

| Existing case | Observed expected behavior | Scoped outcome |
|---|---|---|
| SIM-010 | Actual private TLS API unavailable60047ms;3real503 replies exhaust explicit3attempt policy. Native shared scheduler/provider/policy/local alarm cycles continue561times, maximum observed gap110ms,538exhausted cycles without further attempts. OFFLINE is explicit in host network diagnostic state; no full SDK/RTOS scheduling claim. | PASS, actual simulator-host protocol |
| SIM-012 | During outage exactly one temperature channel invalid/null plus engine3 RPM1500 deviation; other43domain channels stay current. Local logical alarm true, immutable raise facts IDs1/2 source4/7 and reason4003/5001; native loop continues, no deadlock or event overwrite. | PASS, actual simulator-host protocol |
| SIM-013 | Restoring path plus ONE explicit exhausted-cycle reset gives real read-only Laravel /up200 while invalid sensor/local alarm remain. STALE65 retains condition; only VALID30 and normal engine3 RPM2010 create original alarm_cleared facts IDs3/4 after61000ms. Original raise prefix/metadata retained; no ACK, receipt, deletion or implicit reset. | PASS, actual simulator-host protocol |

Numbers are explicit fixture policy (100ms sample,2000ms connect timeout,250ms
backoff,3attempts); maximum observed gap is a host observation, not a vessel or
hard-real-time limit. Native actor composes existing C99 functions under controlled
provider stimulus, not the ESP32 SDK main/task/worker executable. Its host driver
observes API-path availability; it does not emulate or verify physical WiFi.
The existing alarm_cleared lifecycle facts are recovery events; no new wire type.

## Database, dashboard and hardware boundaries

The dedicated host execution creates NO database fixture rows, never ingests
data or runs migrations. Its supervisor performs only existing guarded effective
configuration/catalog checks and actual Laravel /up. The admitted approved test
profile is127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex. Exact empty approved
catalog postflight PASS. Native actor itself never accesses PHP/database.

Separate development integration DOES write owned disposable approved DB fixtures:
formal-resilience-normal-restored-run1-20261027.txt records248real TLS checks,
including4native fast frames/4events with explicit device/lease-boot rebinding,
all44channel API readback, exact valid/invalid-null/STALE/recovery UI cells,
original event metadata rows, direct scoped DB checks and exact zero-row cleanup.
These fast frames are not the formal60s execution, physical acquisition or SDK
worker attempt-budget proof. Fresh PHP8.2.35/Laravel12.70.0/MariaDB10.4.32 suite
has388cases/0failed/0skipped and final10tables/6migrations/0application rows PASS.

Dashboard visibility supporting UI-001 is separately observed in actual owned
Chrome155: LIVE -> STALE -> OFFLINE, simulation provenance, no polling, neutral
SNAPSHOT without script/asset and UNKNOWN without valid timing, four labels agree.
This uses explicit2s/4s browser-fixture age thresholds, not a60s browser outage
or physical measurement freshness. Secure/HttpOnly/Lax cookie, real CSRF/session,
strict CA/hostname/date upstream TLS and exact row/profile cleanup PASS. The local
browser edge is HTTP localhost to verified HTTPS upstream, not deployed browser TLS.

In-sandbox Chrome crashed at Page.enable (CDP_CLOSED, exit2147483651); isolated
new-target and existing-owned-target probes reproduce it before PHP/UI. The same
unmodified browser source and flags PASS via approved outside-sandbox execution
in formal-resilience-browser-approved-runtime-20261027.txt. No certificate bypass,
security-flag/deadline/expectation weakening, personal profile or kill-by-name.
Evidence supports a runtime-isolation failure; exact Chrome internal cause is not
claimed. Earlier failures, interrupted run2 and resolved DB outage remain archived.

## Acceptance and remaining work

Only the existing3SIMrows are eligible for PASS based on this actual prescribed
host protocol and independent review. All15SIMcases then have scoped PASS records;
SUP018 remains PLANNED, other18SUP PASS. Derived requirement mapping becomes
37PASS/1NOT_RUN; implementation stays22IMPLEMENTED_UNVERIFIED/16PARTIAL, no VERIFIED.
PASS of mapped cases does not establish full requirement or system approval.

Required batch regression/security/docs/scope/index/final gates still govern local
commit. Actual248command existing/new regression, native/adversarial12 and HTTP26
have PASS evidence for unchanged code; final documentation/reference/staged checks
must pass before commit. Production firmware/SDK source is unchangedf693b0cb and
bound to both committed real build proofs, NOT_REBUILT in this batch. No migration
change; no new roundtrip required beyond prior committed actual SUP014 evidence.

ESP32/RTOS/PSA/NVS/WiFi/TLS/powerloss/wear/fullstack/heap/timing/currentWokwi,
hostedCI/SUP018, deployedTLS/directMySQL8/POSIX/graphical operator acceptance remain
NOT_RUN. No physical control, main DB, main dotenv, LOCKED/protected-file change,
repository deletion or push. System PARTIAL, final NOT_APPROVED.
