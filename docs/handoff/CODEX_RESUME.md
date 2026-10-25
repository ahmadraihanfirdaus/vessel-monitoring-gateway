# CODEX_RESUME - checkpoint operasional

Dokumen operasional Codex lama/baru. Repository aktual dan evidence mengalahkan snapshot ini.

## Kondisi aktual checkpoint2026-10-26

Branch **develop**, HEAD **70963d463fa5cd2d43914950ef7a9ece5b3185d7**.
Index **kosong** saat checkpoint. Kedua handoff **ada, tracked, sudah committed**
pada70963d4 dan sekarang memiliki update WIP untuk replay. Reference054cfa5 dan
ZIPB46 adalah sejarah; continuous sudah5048525, metadata sudah70963d4. NO PUSH.

Batch aktif **BELUM COMMIT**: recovered critical-event replay ADR0009, enam scope.
Implemented: pure-C recovered view/serializer, actual NVS-worker zero-wait export,
fair recovered/current progress, SDK integration, native three-boot fixture,
real backend/TLS/read/UI checks, CI source/security/living/evidence/handoff.
Source utama `firmware/src/offline_replay.h`, `esp32_offline_store.c/.h`,
`esp32_continuous_main.h`, `scripts/recovered_replay_wire_fixture.c`,
`recovered_replay_wire_bridge.py`, `test_offline_replay.py`,
`backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php`.

| Gate replay terbaru | Hasil / evidence di evidence/test-results/ |
|---|---|
| Real PHP8.2.35/MariaDB full regression | PASS366cases0failure0skip, existing schema; `recovered-replay-mysql-run1-20261025.txt` |
| Actual local TLS/kernel/MariaDB/read/UI | PASS142checks, source3531e10519b7047b92ac8b56b464b68a5574eb68c37991fe9e4a7206c2ff8614; `recovered-replay-http-run1-20261025.txt` |
| Native/focused | Final13replay methods incl8/ninth capacity + existing continuous13/metadata6+9 PASS; runner26MySQL/17HTTP PASS; native/run2 and checkpoint audit |
| Broad existing regression | 220commands219PASS1stale-scanner-pinFAIL; corrected framework/content gate subsequently PASS; regression and checkpoint audit |
| Security/living/config postcheck | PASS0unresolved/0privacy, scanner23 adversarial,38mapped, correct target/key/10tables/6migrations/0app rows; `recovered-replay-checkpoint-audit-20261026.txt` |
| SDK candidate | PASS975856bytes/staticRAM57004/frame944; `esp32-transport-sdk-build-recovered-replay-run1-20261025.txt` |
| SDK retained | PASS1044352bytes/staticRAM66436/frame1616; `esp32-transport-sdk-build-recovered-replay-legacy-run1-20261025.txt` |
| Both SDK current source | PASS0602eed18cc45351f4652d970e0c75f3d725f9278ab49b54f6be35f15e6bdad1; no upload |
| Final exact-scope staged byte review/commit | Still required at this checkpoint; do not assume commit occurred |

Full gate/hash/limit matrix: `evidence/test-results/recovered-replay-summary-20261026.md`.
Runs started25 retained that filename; latest review26. Five INFO scanner source
occurrences are byte-identical to70963d4; exact renewed pins, no detector waiver.
Early unused-fixture Werror and new-boot fixture reset failures preserved/corrected.
Current replay queueing never deletes facts or clears alarms and is **not delivery
confirmation**. Authenticated application receipts/durable retirement/free capacity
remain software gaps. Unsupported historical RECOVERY types explicitly retained,
other supported facts proceed. Previous-boot telemetry is not published as latest.
Queue/context heap/full-stack/timing and physical behavior remain unverified.

Protected AGENTS/two firmware untracked remain untouched. Two older metadata
logs may appear M due Git stat cache; their bytes equal committed blobs, no content
diff and outside next scope. Actual WIP inventory at checkpoint follows; always
recheck actual Git before resuming, preserve unknown/user changes:

```text
 M .github/workflows/phase9-multi-context-ci.yml
 M README.md
 M docs/engineering/esp32-build-configuration-review.md
 M docs/fmea/fmea-prototype.md
 M docs/handoff/CHATGPT_CONTEXT.md
 M docs/handoff/CODEX_RESUME.md
 M docs/testing/living-requirement-status.csv
 M docs/testing/traceability-status.md
 M evidence/test-results/alarm-metadata-development-observations-20261025.txt
 M evidence/test-results/alarm-metadata-log-normalization-20261025.csv
 M firmware/src/esp32_continuous_main.h
 M firmware/src/esp32_offline_store.c
 M firmware/src/esp32_offline_store.h
 M scripts/run_live_http_integration.py
 M scripts/run_mysql_integration.py
 M scripts/security-reviewed-findings.json
 M scripts/test_live_http_integration_gate.py
 M scripts/test_mysql_integration_gate.py
?? AGENTS.md
?? backend/laravel/tests/Feature/RecoveredReplayIntegrationTest.php
?? docs/adr/0009-recovered-event-replay.md
?? docs/testing/recovered-event-replay.md
?? evidence/test-results/esp32-transport-sdk-build-recovered-replay-legacy-run1-20261025.txt
?? evidence/test-results/esp32-transport-sdk-build-recovered-replay-run1-20261025.txt
?? evidence/test-results/recovered-replay-checkpoint-audit-20261026.txt
?? evidence/test-results/recovered-replay-cleanup-inventory-20261026.csv
?? evidence/test-results/recovered-replay-development-observations-20261025.txt
?? evidence/test-results/recovered-replay-http-run1-20261025.txt
?? evidence/test-results/recovered-replay-http-runner-20261025.txt
?? evidence/test-results/recovered-replay-log-normalization-20261026.csv
?? evidence/test-results/recovered-replay-mysql-run1-20261025.txt
?? evidence/test-results/recovered-replay-mysql-runner-20261025.txt
?? evidence/test-results/recovered-replay-native-run1-20261025.txt
?? evidence/test-results/recovered-replay-native-run2-20261025.txt
?? evidence/test-results/recovered-replay-regression-20261025.txt
?? evidence/test-results/recovered-replay-security-run1-20261025.txt
?? evidence/test-results/recovered-replay-security-triage-20261026.csv
?? evidence/test-results/recovered-replay-summary-20261026.md
?? evidence/test-results/recovered-replay-wire-run2-20261025.txt
?? firmware/.gitignore
?? firmware/.vscode/extensions.json
?? firmware/src/offline_replay.h
?? scripts/recovered_replay_wire_bridge.py
?? scripts/recovered_replay_wire_fixture.c
?? scripts/test_offline_replay.py
```

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
| `5048525e1ff4cfad367dc31bfc42c7aa79fb393e` | Continuous simulation sudah committed, 348 kasus PHP + 94 pemeriksaan lokal; `evidence/test-results/continuous-simulation-summary-20261025.md`. |

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

Batch replay aktif sekarang menghubungkan nondestructive recovered publication; gap software berikutnya: HTTP success bukan authenticated application receipt; belum ada durable confirmed-outbox deletion/free capacity. Jurnal delapan tetap bounded/refuse; jangan mengklaim unlimited offline delivery. Delivery ACK berbeda dari operator alarm ACK dan tidak boleh clear kondisi. Cross-boot ordering/current-state tidak boleh disimpulkan dari receipt sequence. Durability, wear, NVS confidentiality, real sensor/OEM providers, trust clock/provisioning, resource watermark/timing/outage memerlukan physical evidence. Jangan mengarang protokol OEM atau mengubah threshold demo menjadi aturan kapal nyata.

Formal: `docs/testing/formal-scenario-status.csv` mencatat SIM001-009 PASS dan SIM010-015 NOT_RUN. `docs/testing/supplemental-verification-plan.csv` mencatat SUP001/003/006/016/019 PASS, 14 PLANNED. Dedicated SIM010-015/SUP remaining tidak dieksekusi hanya karena local host/TLS PASS. Older SUP014 prepared target berbeda; user-approved target di atas menang, tetapi formal protocol amendment harus eksplisit sebelum eksekusi formal, bukan diam-diam mengubah pinned record.

## Aturan fail-closed dan kesinambungan

1. Jaga LOCKED baseline, user changes, `AGENTS.md`, `firmware/.gitignore`, `firmware/.vscode/extensions.json` dan ignored secret files. Jangan stage/overwrite/delete dua firmware untracked.
2. Tidak push, remote, pull/rebase/merge/reset/clean/history rewrite. Jangan delete evidence/build/vendor sebagai collateral. Audit kandidat cleanup read-only.
3. Sebelum DB mutation verifikasi effective exact target/account/schema/isolation dan ephemeral key. Laravel migrations saja untuk DDL. Test rows hanya owned isolated fixtures dengan verified cleanup; tidak menyentuh real/main data.
4. Batch terkait 5-7 scope; jangan mengulang implementasi atau membuat micro-batch nomor. Specific positive/negative/boundary/security/logical tests + existing/new integrated regression + security/manual scope/diff wajib. Missing mandatory gate => NO staging/commit; external exclusions tetap NOT_RUN, bukan PASS.
5. Sesudah mandatory local gates PASS, expected develop/HEAD/index, stage **exact approved files**, scan staged bytes, local commit otomatis sesuai izin. Git metadata sandbox dapat perlu approved narrow escalation; patuhi penolakan, jangan bypass.
6. Jangan edit firmware/backend di tengah SDK/HTTP source-stability gate. Log public disanitasi UTF-8, secret/SQL output tidak dicetak. Jika whitespace log dinormalisasi catat before/after SHA, jangan rewrite failure evidence.
7. Perbarui **kedua** handoff setelah batch besar committed. Self hash commit tidak dapat ditulis ke commit itu sendiri: sebut hash checkpoint yang diverifikasi dan periksa actual Git lagi saat resume. Jika WIP/limit/blocker muncul, checkpoint dulu dan tulis pending scope/gates eksplisit.
8. Satu commit/handoff bukan akhir Goal. Lanjut scope software independen yang aman; jangan tandai proyek VERIFIED/Goal complete sebelum audit aktual semua38 requirements dan seluruh kriteria Goal. Jangan mengarang status aktif/complete dari tool atau menganggap status UI sebagai evidence teknis.


## Seluruh 38 requirement: assessment dan evidence

Snapshot sinkron living CSV pada checkpoint2026-10-26, bukan status formal baru.
22IMPLEMENTED_UNVERIFIED/16PARTIAL; formal requirement15PASS/3PARTIAL/20NOT_RUN.
Setiap assessment tetap qualified; lihat full implementation paths/qualification di
`docs/testing/living-requirement-status.csv`. LOCKED baseline tidak berubah.

| Requirement (level) dan teks LOCKED | Implementasi | Formal / planned tests | Source utama; evidence |
|---|---|---|---|
| **SYS-001** (Mandatory): System shall operate as a monitoring and diagnostic prototype, not as certified ship safety equipment. | PARTIAL | PASS; SUP-001 | `README.md`; `docs/architecture/architecture-and-icd.md`; full refs: living CSV; evidence: `evidence/test-results/phase9-wave1-sup001-documentation-review-20261020.txt` |
| **SYS-002** (Mandatory): System shall separate source_mode = simulation, bench_test, physical for all data. | PARTIAL | NOT_RUN; SUP-002 | `firmware/src/core_types.h`; `firmware/src/core_source_mode.h`; full refs: living CSV; evidence: `evidence/test-results/phase8-h1-summary-20261017.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **SYS-003** (Mandatory): Backend/cloud failure shall not stop local sampling, local alarms, or safety-policy evaluation. | PARTIAL | NOT_RUN; SIM-010;SIM-012 | `firmware/src/network_outage_local_guard.h`; `firmware/src/phase9_sys003_outage_cycle_host.h`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **SYS-004** (Mandatory): No physical engine starter, ignition, steering, radar, radio, or third-party operational or mission system shall be controlled by V1. | PARTIAL | PASS; SUP-003 | `docs/architecture/architecture-and-icd.md`; `firmware/src/safety_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-closure-summary-20261016.md`; `evidence/test-results/phase9-wave1-sup003-static-review-20261021.txt` |
| **SAF-001** (Mandatory): Ventilation hatch/door state shall be modeled as OPEN/CLOSED/UNKNOWN with quality. | IMPLEMENTED_UNVERIFIED | PASS; SIM-001;SIM-002 | `firmware/src/provider_door.h`; `firmware/src/safety_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-002** (Mandatory): A virtual start request shall be rejected when configured blocking conditions are not satisfied. | IMPLEMENTED_UNVERIFIED | PASS; SIM-001;SIM-002;SIM-003;SIM-004 | `firmware/src/safety_policy.h`; `firmware/src/safety_policy_runtime.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-003** (Mandatory): Blocking/alert-only behavior shall be configuration-driven; only field-verified rules may be labeled real-vessel rules. | PARTIAL | PASS; SIM-002;SIM-005 | `firmware/src/safety_policy.h`; `firmware/src/safety_monitor_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-004** (Mandatory): Fuel-vapor channel shall support NORMAL/WARNING/ALARM/FAULT/UNKNOWN and shall never map missing data to safe. | IMPLEMENTED_UNVERIFIED | PASS; SIM-003;SIM-004 | `firmware/src/provider_fuel_vapor.h`; `firmware/src/safety_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-005** (Mandatory): Bilge/high-water channel shall support NORMAL/HIGH/FAULT/UNKNOWN. | IMPLEMENTED_UNVERIFIED | PASS; SIM-005 | `firmware/src/provider_bilge.h`; `firmware/src/safety_monitor_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-006** (Mandatory): Compartment temperature shall support valid/invalid/missing/stale quality and configurable demo thresholds. | IMPLEMENTED_UNVERIFIED | PARTIAL; SIM-006;SIM-011 | `firmware/src/provider_temperature.h`; `firmware/src/safety_monitor_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **ALM-001** (Mandatory): Alerts shall have unique ID, source, priority, state, reason, raised_at, acknowledged_at and cleared_at. | IMPLEMENTED_UNVERIFIED | PASS; SIM-003;SIM-005;SIM-006 | `firmware/src/core_alarm.h`; `firmware/src/core_event_journal.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **ALM-002** (Mandatory): Acknowledgement shall not clear the underlying alarm condition. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-004 | `firmware/src/core_alarm.h`; `firmware/src/main.c`; full refs: living CSV; evidence: `evidence/test-results/firmware-core-alarm-wokwi-20261013.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **ALM-003** (Mandatory): Local buzzer/LED behavior shall be independent from dashboard availability. | PARTIAL | PARTIAL; SIM-003;SIM-010;SIM-012 | `firmware/src/safety_local_alarm.h`; `firmware/src/safety_policy_runtime.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **ENG-001** (Mandatory): Engine model shall support N engines; demo profile shall configure four engines. | IMPLEMENTED_UNVERIFIED | PASS; SIM-007 | `firmware/src/engine_model.h`; `firmware/src/phase6_f2_formal_scenarios.h`; full refs: living CSV; evidence: `evidence/test-results/phase6-f2-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **ENG-002** (Mandatory): Each engine shall expose state, rpm, temperature, runtime, alarm and communication quality in simulation. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-005 | `firmware/src/engine_model.h`; `firmware/src/phase6_f1_selftest.h`; full refs: living CSV; evidence: `evidence/test-results/phase6-f1-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **ENG-003** (Mandatory): System shall detect configurable cross-engine RPM deviation in simulation. | IMPLEMENTED_UNVERIFIED | PARTIAL; SIM-007;SIM-012 | `firmware/src/engine_model.h`; `firmware/src/phase6_f2_formal_scenarios.h`; full refs: living CSV; evidence: `evidence/test-results/phase6-f2-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **ENG-004** (Mandatory): Yamaha physical provider shall remain an interface placeholder until exact model/protocol is verified. | PARTIAL | PASS; SUP-006 | `docs/architecture/architecture-and-icd.md`; `docs/bom-and-tbd.md`; full refs: living CSV; evidence: `evidence/test-results/phase9-wave1-sup006-static-review-20261021.txt` |
| **NAV-001** (Mandatory): Navigation module shall parse/generate NMEA 0183-style development data using Furuno GP-39 as reference, without claiming GP-39 is installed onboard. | IMPLEMENTED_UNVERIFIED | PASS; SIM-008 | `firmware/src/navigation_nmea.h`; `firmware/src/phase7_g2_formal_scenarios.h`; full refs: living CSV; evidence: `evidence/test-results/phase7-g2-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **NAV-002** (Mandatory): Navigation state shall expose latitude, longitude, SOG, COG, fix, data age and quality. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-007 | `firmware/src/navigation_nmea.h`; `firmware/src/phase7_g1_selftest.h`; full refs: living CSV; evidence: `evidence/test-results/phase7-g1-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **NAV-003** (Mandatory): Invalid checksum/malformed input shall not replace last valid navigation state as current live data. | IMPLEMENTED_UNVERIFIED | PASS; SIM-008 | `firmware/src/navigation_nmea.h`; `firmware/src/phase7_g2_formal_scenarios.h`; full refs: living CSV; evidence: `evidence/test-results/phase7-g2-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **NAV-004** (Mandatory): Navigation shall transition VALID -> STALE -> OFFLINE according to configurable data-age thresholds. | IMPLEMENTED_UNVERIFIED | PASS; SIM-009 | `firmware/src/navigation_nmea.h`; `firmware/src/phase7_g2_formal_scenarios.h`; full refs: living CSV; evidence: `evidence/test-results/phase7-g2-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **MOT-001** (Mandatory): Motion channel shall expose roll/pitch prototype values and clearly label them as attitude/motion, not vessel stability certification. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-008 | `firmware/src/provider_attitude.h`; `firmware/src/phase4_d5_selftest.h`; full refs: living CSV; evidence: `evidence/test-results/phase4-d5-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **VIB-001** (Mandatory): Vibration channel shall provide a demo indicator and fault state without claiming machinery diagnosis. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-009 | `firmware/src/provider_vibration.h`; `firmware/src/phase4_d6_selftest.h`; full refs: living CSV; evidence: `evidence/test-results/phase4-d6-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **PWR-001** (Mandatory): Bench power channel shall monitor a safe low-power circuit using INA219 or simulator; real propulsion-current measurement is out of scope. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-010 | `firmware/src/provider_power.h`; `firmware/src/phase4_d7_selftest.h`; full refs: living CSV; evidence: `evidence/test-results/phase4-d7-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **TEL-001** (Mandatory): Telemetry payload shall carry schema_version, device_id, firmware_version, boot_id, sequence, uptime_ms, source_mode and per-channel quality. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-011 | `firmware/src/telemetry_contract.h`; `docs/contracts/telemetry-schema-v1.json`; full refs: living CSV; evidence: `evidence/test-results/phase8-h1-summary-20261017.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **TEL-002** (Mandatory): Invalid/missing channel values shall be null/absent with quality metadata, never silently converted to zero. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-012 | `firmware/src/telemetry_contract.h`; `docs/contracts/telemetry-schema-v1.json`; full refs: living CSV; evidence: `evidence/test-results/phase8-h1-summary-20261017.md`; `evidence/test-results/device-read-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **TEL-003** (Mandatory): Backend shall deduplicate samples by stable identity key and reject conflicting duplicates. | PARTIAL | NOT_RUN; SIM-014 | `firmware/src/telemetry_contract.h`; `docs/contracts/telemetry-contract-v1.md`; full refs: living CSV; evidence: `evidence/test-results/phase8-h1-summary-20261017.md`; `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **NET-001** (Mandatory): Network client shall implement timeout, reconnect and bounded retry/backoff without blocking sampling. | PARTIAL | NOT_RUN; SIM-010;SIM-012;SIM-013 | `firmware/src/network_transport_host_adapter.h`; `firmware/src/phase9_net001_uplink_host_bridge.h`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **NET-002** (Mandatory): Offline mode shall preserve latest state and critical event journal within bounded storage. | PARTIAL | NOT_RUN; SUP-013 | `firmware/src/core_event_journal.h`; `firmware/src/core_runtime_guard.h`; full refs: living CSV; evidence: `evidence/test-results/firmware-core-c4-wokwi-20261013.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **API-001** (Mandatory): Laravel API shall validate authentication, schema, payload size, device identity and value contracts. | PARTIAL | NOT_RUN; SIM-015 | `backend/laravel/routes/api.php`; `backend/laravel/app/Http/Controllers/Api/TelemetryIngestController.php`; full refs: living CSV; evidence: `evidence/test-results/phase9-p3-runtime-http-evidence-audit-summary-20261018.md`; `evidence/test-results/phase9-p3-securityfix-feature-tests-audit-summary-20261018.md`; `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **DB-001** (Mandatory): All schema changes shall use Laravel migrations; no manual database shortcut is accepted. | PARTIAL | NOT_RUN; SUP-014 | `backend/laravel/database/migrations/2026_10_17_100001_create_devices_table.php`; `backend/laravel/database/migrations/2026_10_17_100002_create_telemetry_samples_table.php`; full refs: living CSV; evidence: `evidence/test-results/phase9-p3-migration-rollback-support-summary-20261018.md`; `evidence/test-results/phase9-p3-migration-rollback-support-evidence-audit-summary-20261018.md`; `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **UI-001** (Mandatory): Dashboard shall distinguish live, stale, offline and simulation states visibly. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SIM-010 | `backend/laravel/app/Support/DashboardSignalLabel.php`; `backend/laravel/resources/views/monitoring/index.blade.php`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **UI-002** (Mandatory): Dashboard shall provide overview, safety, propulsion, navigation, power, alarms/events, device health and test evidence views. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-015 | `backend/laravel/resources/views/monitoring/index.blade.php`; `backend/laravel/resources/views/monitoring/sections/overview.blade.php`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/device-read-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **SEC-001** (Mandatory): No production secret, real operational route or coordinate, radio frequency, credential, or confidential vessel detail shall be committed to public GitHub. | PARTIAL | PASS; SUP-016 | `scripts/audit_precommit_security.py`; `docs/github-repository-plan.md`; full refs: living CSV; evidence: `evidence/test-results/phase4-closure-summary-20261016.md`; `evidence/test-results/phase9-wave1-sup016-security-review-20261020.txt`; `evidence/test-results/security-php8235-summary-20261025.md` |
| **SEC-002** (Mandatory): Demo API shall use HTTPS/authentication and secrets shall be external to source code. | PARTIAL | NOT_RUN; SIM-015 | `backend/laravel/routes/api.php`; `backend/laravel/app/Http/Middleware/AuthenticateDeviceToken.php`; full refs: living CSV; evidence: `evidence/test-results/phase9-p3-security-review-20261018.txt`; `evidence/test-results/phase9-p3-securityfix-feature-tests-audit-summary-20261018.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md` |
| **TST-001** (Mandatory): Every requirement shall map to code module, automated/manual test and evidence. | PARTIAL | NOT_RUN; SUP-017 | `requirements/traceability-matrix.csv`; `docs/testing/living-requirement-status.csv`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **TST-002** (Target): CI shall build firmware and backend tests on each pull request; Wokwi CI shall be added if available for the project plan. | PARTIAL | NOT_RUN; SUP-018 | `.github/workflows/phase9-multi-context-ci.yml`; `scripts/run_mysql_integration.py`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |
| **DOC-001** (Mandatory): Repository shall contain architecture, ICD, standards matrix, FMEA, ADRs, traceability matrix, test evidence and limitations. | IMPLEMENTED_UNVERIFIED | PASS; SUP-019 | `docs/architecture/architecture-and-icd.md`; `docs/standards/standards-applicability-matrix.md`; full refs: living CSV; evidence: `evidence/test-results/phase9-wave1-sup019-documentation-review-20261021.txt`; `evidence/test-results/alarm-metadata-summary-20261025.md`; `evidence/test-results/recovered-replay-summary-20261026.md` |

## Resume operasional dan roadmap berdasarkan dependency

1. Baca latest summary/ADR0009 dan targeted branch/HEAD/index/content-diff. Baseline
   audit telah dilakukan; jangan mengulang implementasi continuous/metadata/replay.
2. Untuk batch replay yang masih WIP: latest source proofs/native/PHP/TLS/SDK
   sudah PASS. Final manual scope/diff/manifest dan staged-byte security harus PASS,
   lalu exact-scope local commit otomatis di develop. Jangan stage protected/secret
   files atau melakukan remote/DB utama. Jangan mengulang migration roundtrip
   yang tidak diperlukan: schema sudah enam, tidak ada migration baru batch replay.
3. Set child VG_PHP_CLI ke C:/tools/php-8.2.35/php.exe. Native child compiler PATH
   boleh C:/msys64/ucrt64/bin tanpa PATH global/XAMPP. Guarded runners membaca
   approved testing file internal dan membuat ephemeral process key; tidak dump env.

```powershell
python -B scripts/test_offline_replay.py
python -B scripts/test_mysql_integration_gate.py
python -B scripts/test_live_http_integration_gate.py
python -B scripts/run_mysql_integration.py --testing-env --execute --existing-schema --php-binary C:/tools/php-8.2.35/php.exe
python -B scripts/run_live_http_integration.py --testing-env --execute --php-binary C:/tools/php-8.2.35/php.exe
python -B scripts/audit_precommit_security.py
python -B scripts/check_living_traceability.py
```

Gunakan evidence nama run baru jika perlu rerun; jangan overwrite failure evidence.
SDK helper environment valid esp32dev_espidf atau esp32dev_continuous, PlatformIO
CLI eksplisit di runtime section; no upload. SDK cache writes bisa perlu approved
narrow escalation; jangan bypass penolakan. Jangan edit firmware/backend selama
SDK/HTTP source-stability gate. Final scan mencakup working+index+evidence/handoff.

4. Setelah commit berhasil, perbarui **kedua handoff** dengan actual HEAD dan
   status. Self commit hash tak bisa ditulis ke commit itu sendiri; next handoff
   update boleh WIP untuk batch substantif berikut dan harus jelas didokumentasi.
5. Prioritas software berikut: aplikasi receipt terautentikasi dan bound ke exact
   payload/device/boot/event identity + bounded retry/replay correlation + crash-safe
   outbox retirement/freeing capacity + transaction/accepted-prefix invariants +
   real PHP/C99/MariaDB/TLS fault regression. Pisahkan delivery ACK dari operator
   alarm ACK; network completion tidak boleh menghapus atau clear kondisi.
   Historical B37-46 host receipts/HMAC/nonce prechecks bukan runtime trust chain.
   Gunakan desain berbasis ICD/LOCKED, jangan weaken retained-prefix guard demi lulus.
6. Dedicated SIM010-015/SUP tetap memerlukan protocol/dependencies/approved target
   eksplisit; jangan silently amend pinned historical formal records. Hardware,
   actual device clock/WiFi/NVS/power-loss, hostedCI/MySQL8/POSIX/graphical/deployed
   TLS unavailable tetap NOT_RUN. Teruskan software independen aman dan full38
   requirement audit sebelum Goal complete. Satu batch/commit/handoff bukan akhir.

## Hash penjaga checkpoint

| File | SHA256 |
|---|---|
| `requirements/system-requirements.md` | `a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b` |
| `requirements/traceability-matrix.csv` | `bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3` |
| `AGENTS.md` | `421e2b5d5748cf5e4bdac3c189223915850c8894688a7e3ffd090975aa87864b` |
| `firmware/.gitignore` | `d952abf002d5e1ec80c8ab1bfc9f38eb5b62fc310667d501cb2ce9f21c3effb2` |
| `firmware/.vscode/extensions.json` | `31cc8f05084d96b65be8f147533017c7a1b89b055d85886a2e4ab3ce532f34fb` |
| `docs/testing/formal-scenario-status.csv` | `391048d94f1c792a193480ed439d6bb2b346ef182cf9be7a8d11d412c993ceb7` |
| `docs/testing/supplemental-verification-plan.csv` | `73b78e84ba608f04767e4456fdf13c65a397de0c85dbdeab1c657542ac564f01` |

## Prompt pembuka siap pakai

> Lanjutkan Goal Integrated Vessel Monitoring & Diagnostic Gateway secara lokal pada develop dari HEAD/worktree aktual. Baca kedua docs/handoff terlebih dahulu, lalu targeted Git check. Metadata dan handoff committed70963d4; continuous5048525 sudah selesai scoped gates. Batch recovered replay ADR0009 masih WIP pada checkpoint26, implementation dan366PHP/142integration/duaSDK/current-source security sudah PASS; verifikasi latest evidence/manifest/index sebelum exact-scope local commit. Jangan ulang implementasi/migration atau menimpa WIP. PHP8.2.35 eksplisit, MariaDB127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex melalui guard; no secrets output/mainDB. LOCKED, evidence, AGENTS dan dua firmware untracked utuh. NO PUSH/remotes/destructive Git. Update kedua handoff setelah committed batch lalu lanjut receipt binding/durable outbox retirement sesuai dependency, dengan5-7related scopes dan seluruh mandatory tests/security/evidence. Jaga null/zero/source/quality/offline/alarm ACK-not-CLEAR. Jangan anggap queue/HTTP sebagai deletion permission atau host/SDK/localTLS sebagai hardware/formal/production proof. Goal tetap berlangsung sampai completion audit semua38 requirement dan semua software aman benar-benar tuntas.
