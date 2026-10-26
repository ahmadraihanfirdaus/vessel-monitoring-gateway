# Dedicated alarm/provider verification and navigation clock fix

Baseline develop5727969e1f04f49cd26def184e0ab594a6acba6e. Seven related scopes:
SUP004/005/007/008/009/010 dedicated actual-module verification plus guarded
runner/oracles/CI/integration/security/traceability/evidence/handoff. This is
not another implementation of existing providers or a numbering-only batch.

Real defect discovered: navigation accepted arrival/age timestamps behind the
last observation and could revive OFFLINE. Ingest/update_age now refuse before
mutation using now<last_valid or now-last_valid<data_age; no unsigned addition
or overflow. Equal time/new valid data allowed. No schema/default threshold or
LOCKED requirement change. Files scripts/formal_provider_fixture.c,
run_formal_provider_verification.py, test_formal_provider_verification.py;
firmware/src/navigation_nmea.h; reviewed protocol/docs/CI and evidence.

| Mandatory gate | Actual result | Evidence in evidence/test-results/ |
|---|---|---|
| Dedicated six prescribed host protocols | PASS6,121native assertions/303independent comparisons, source-stable; first FAIL retained | formal-provider-execution-run1-20261026.txt; formal-provider-execution-utf8-final-20261026.txt; formal-provider-case-review-20261026.md |
| Runner/oracle/clock/property fault regression | PASS12methods; missing/duplicate/nonfinite/bool/fields/source-drift/unavailable prerequisites,900older timestamps plusUINT64 boundaries | formal-provider-focused-regression-run1-20261026.txt; formal-provider-final-delta-regression-20261026.txt |
| Existing focused regression | PASS Phase7G1 64/64,G2 2/2,continuous13,receipt owner8,file4 | same focused regression log |
| Actual PHP8.2.35/Laravel12.70.0/MariaDB10.4.32 | PASS373cases0fail0skip, six real native wire families,10tables/6migrations/0app rows; approved effective target/key guarded | formal-provider-mysql-20261026.txt |
| Actual local TLS/PHP/kernel/MariaDB/read/UI/retirement | PASS187checks, source-stable, exact owned cleanup0app rows | formal-provider-http-20261026.txt |
| Both SDK | PASS candidate986048/RAM57532/frame1056; retained1045472/RAM66436/frame1616; margin3104, no upload | esp32-transport-sdk-build-formal-provider-candidate-20261026.txt; esp32-transport-sdk-build-formal-provider-retained-20261026.txt |
| CI source | Dedicated actual host execution + adversarial group registered; hostedNOT_RUN | .github/workflows/phase9-multi-context-ci.yml |
| Broad regression | PASS230/230commands: inherited229 +1new actual provider/oracle/property group | formal-provider-integrated-regression-20261026.txt |
| Initial security | FAIL2INFO unchanged CI label expressions,0privacy; exact byte-equal5727969 reviews/pins renewed, corrected working scanPASS0unresolved/0privacy; final staged scan mandatory | formal-provider-security-initial-20261026.txt; formal-provider-security-triage-20261026.csv |
| Formal canonical rows / living38 | Six prescribed host SUP nowPASS after dedicated execution/review and complete local prerequisites; total11PASS/8PLANNED. Living formal21PASS/3PARTIAL/14NOT_RUN; no requirementVERIFIED, unrelated formal/LOCKED untouched | formal-provider-case-results-20261026.csv; case review |
| Manual/final security/exact staged manifest | Manual/current working security prerequisitesPASS; exact staged security/manifest mandatory before commit | final review/manifest to be recorded |

Dedicated native source digest7c75cb16e5e5728c6f9f3011826607a3510352ad01f5f122e1afe680cbfcdd16;
both SDK a0a0eac0809da2b9be93c67a8347c3f50766b3bed163ec7d42a1e4b86fb8bf95;
HTTP26a94bfa1c529fb339c7c72702f1cb1d50327eafeb8d6d37b97b4fcbef6fd4c2.
Candidate merged85d429b2d2f147cc079a31909ab264cc5a55a7f43456a1fb91048a774dadcf28;
retained mergedc3fe8b253a60165e5df455b7b1d718577bbc4129b7d882b9595586918a510070.
Parent commit is recorded together with exact WIP tested hashes; no self-commit
hash is fabricated. A source change invalidates affected proofs.

No DB migration is added; existing six-migration isolated schema is intentional.
Only approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex with guarded
ephemeral cipher-compatible process key; no main dotenv/DB/credential output.
All PHP uses C:/tools/php-8.2.35/php.exe without global PATH/XAMPP changes.
Both handoffs automatically track current HEAD/WIP/gates; no Goal completion.

Hardware ESP32/RTOS/NVS/PSA/powerloss/wear/rollback/fullheap/callstack/timing,
physical flash/clock/WiFi/TLS, sensor/OEM interfaces, currentWokwi, hostedCI,
directMySQL8/POSIX, graphical/deployedTLS: NOT_RUN. No NMEA/diagnostic/certification
or real-vessel rule is invented. SystemPARTIAL, finalNOT_APPROVED; all38 requirement
implementation assessments stay22IMPLEMENTED_UNVERIFIED/16PARTIAL.
