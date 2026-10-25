# CODEX_RESUME - checkpoint operasional

## Checkpoint siap exact-scope commit (2026-10-25)

Semua mandatory **local** test/SDK/integration gates pada batch metadata telah
PASS pada source terbaru. Security content scan current+index PASS dengan nol
unresolved findings/privacy warnings; scanner adversarial23 methods PASS.
Read-only postcheck exact testing target/key/schema PASS (10tables/6migrations/0app rows).
Manual final scope/diff dan exact staging review dicatat di
`evidence/test-results/alarm-metadata-review-20261025.md`; daftar/hash files ada di
`evidence/test-results/alarm-metadata-files-20261025.csv`.
Staged-byte rescan masih harus PASS sebelum local commit; tidak boleh dianggap
sudah executed hanya karena path ada di summary. Metadata/handoff masih WIP
hingga Git membuktikan commit berhasil. Ringkasan akhir dan semua batas:
`evidence/test-results/alarm-metadata-summary-20261025.md`.
Current HTTP source proof `2be135e7d73e2b12a1a0b19f45e2d16e4ce0fa3d182f09a472e77242a6333428`;
SDK proof `22a297bf2fa3cecb8806d9340dfaa6be59856099f002734ce6d6b97578a5f733`.
Bagian checkpoint pertama berikut adalah sejarah, bukan instruksi mengulang
migration/SDK/HTTP yang kini sudah PASS. Resume mulai dari actual Git dan latest
review/manifest. External gates tetap NOT_RUN, bukan syarat yang diam-diam dilewati.

## Pembaruan checkpoint sebelum review/commit

Continuous tetap committed pada5048525; metadata dan handoff masih uncommitted.
Gate terbaru setelah last firmware diagnostic change: 6 native transition +9
codec +13 continuous +25 MySQL-runner +16 HTTP-runner methods PASS;
122 actual integration checks PASS dengan source digest
`2be135e7d73e2b12a1a0b19f45e2d16e4ce0fa3d182f09a472e77242a6333428`.
Evidence: `evidence/test-results/alarm-metadata-checkpoint-regression-20261025.txt`
dan `evidence/test-results/alarm-metadata-http-checkpoint-final-20261025.txt`.
Kedua target SDK latest source22a297bf... PASS, retained image1044112 dan
candidate974032 byte, frame1616/880. Evidence retained final:
`evidence/test-results/esp32-transport-sdk-build-alarm-metadata-legacy-final-20261025.txt`.
Postcheck read-only: effective isolated target/account/key PASS,10tables/6migrations/0app rows.
Kedua matrix handoff tepat38 unique requirements, LOCKED/protected/formal hashes
utuh. Oracle audit awal keliru mengasumsikan prefix3huruf (DB/UI2huruf), diperbaiki;
semua38 sudah ada sejak awal. Rincian audit:
`evidence/test-results/alarm-metadata-checkpoint-audit-20261025.txt`.

**Langkah saat ini**: selesaikan security scan current+index, manual scope/diff,
manifest exact files dan staged-byte review; commit hanya bila semua mandatory
PASS. Jangan ulang upgrade schema/implementasi continuous. Bagian snapshot pertama
di bawah dipertahankan sebagai sejarah; daftar PENDING sebelumnya untuk SDK/HTTP
sudah diselesaikan oleh pembaruan ini. Summary kini berisi matrix lengkap,
bukan lagi placeholder. Gate keamanan/staging/commit belum boleh diasumsikan PASS.
External NOT_RUN dan seluruh software replay/receipt gaps tetap berlaku.

Tanggal checkpoint lokal: 2026-10-25 (Asia/Jakarta). Dibuat atas prioritas handoff sebelum batch besar berikutnya. Snapshot bukan final release atau bukti semua gate batch PASS.

## Git pada checkpoint pertama

- Branch: `develop`. HEAD aktual: `5048525e1ff4cfad367dc31bfc42c7aa79fb393e`.
- HEAD user sebelumnya `054cfa5` sudah maju ke `5048525` melalui continuous simulation lokal; jangan reset. Reference B46 berbeda dan tetap historis.
- Index: **EMPTY**, tidak ada staged paths. Worktree: batch metadata uncommitted, dua dokumen handoff baru disertakan checkpoint ini.
- Tiga protected pre-existing untracked: `AGENTS.md`, `firmware/.gitignore`, `firmware/.vscode/extensions.json`. Tidak menjadi scope commit.
- Snapshot di bawah dicatat sebelum dua handoff dibuat; `?? docs/handoff/CODEX_RESUME.md` dan `?? docs/handoff/CHATGPT_CONTEXT.md` adalah tambahan baru. Selalu ulang targeted Git check saat resume, jangan mengulang baseline audit seluruh repo.

```text
 M .github/workflows/phase9-multi-context-ci.yml
 M README.md
 M backend/laravel/app/Http/Requests/EventIngestRequest.php
 M backend/laravel/app/Http/Requests/TelemetryIngestRequest.php
 M backend/laravel/app/Models/MonitoringEvent.php
 M backend/laravel/app/Services/DeviceEventReadService.php
 M backend/laravel/app/Services/EventIngestService.php
 M backend/laravel/resources/views/monitoring/sections/alarms-events.blade.php
 M backend/laravel/tests/Support/TestSchema.php
 M docs/contracts/device-read-api-v1.md
 M docs/engineering/esp32-build-configuration-review.md
 M docs/fmea/fmea-prototype.md
 M docs/testing/live-loopback-integration.md
 M docs/testing/living-requirement-status.csv
 M docs/testing/traceability-status.md
 M firmware/src/continuous_simulation.h
 M firmware/src/esp32_continuous_main.h
 M firmware/src/esp32_offline_store.c
 M firmware/src/esp32_offline_store.h
 M firmware/src/offline_state.h
 M firmware/src/offline_transaction.h
 M scripts/mysql_test_gate.php
 M scripts/phase9_b4_testlib.py
 M scripts/run_live_http_integration.py
 M scripts/run_mysql_integration.py
 M scripts/security-reviewed-findings.json
 M scripts/test_continuous_simulation.py
 M scripts/test_live_http_integration_gate.py
 M scripts/test_mysql_integration_gate.py
 M scripts/test_phase9_p3_mysql_source.py
?? AGENTS.md
?? backend/laravel/app/Support/AlarmTransitionMetadata.php
?? backend/laravel/app/Support/InspectsRawJsonObjects.php
?? backend/laravel/database/migrations/2026_10_25_100006_add_alarm_metadata_to_monitoring_events.php
?? backend/laravel/tests/Feature/AlarmMetadataIntegrationTest.php
?? backend/laravel/tests/Unit/AlarmTransitionMetadataTest.php
?? docs/adr/0008-alarm-transition-integration.md
?? docs/contracts/alarm-event-schema-v1.1.json
?? docs/testing/alarm-transition-integration.md
?? evidence/test-results/alarm-metadata-cleanup-inventory-20261025.csv
?? evidence/test-results/alarm-metadata-corrected-regression-20261025.txt
?? evidence/test-results/alarm-metadata-development-observations-20261025.txt
?? evidence/test-results/alarm-metadata-early-regression-20261025.txt
?? evidence/test-results/alarm-metadata-final-regression-20261025.txt
?? evidence/test-results/alarm-metadata-final-security-20261025.txt
?? evidence/test-results/alarm-metadata-http-final-20261025.txt
?? evidence/test-results/alarm-metadata-http-nested-final-20261025.txt
?? evidence/test-results/alarm-metadata-http-proof-final-20261025.txt
?? evidence/test-results/alarm-metadata-http-run1-20261025.txt
?? evidence/test-results/alarm-metadata-log-normalization-20261025.csv
?? evidence/test-results/alarm-metadata-mysql-final-20261025.txt
?? evidence/test-results/alarm-metadata-mysql-race-final-20261025.txt
?? evidence/test-results/alarm-metadata-native-run1-20261025.txt
?? evidence/test-results/alarm-metadata-previous-preflight-20261025.txt
?? evidence/test-results/alarm-metadata-race-fixed-20261025.txt
?? evidence/test-results/alarm-metadata-race-reproduction-20261025.txt
?? evidence/test-results/alarm-metadata-race-reproduction2-20261025.txt
?? evidence/test-results/alarm-metadata-scoped-regression-20261025.txt
?? evidence/test-results/alarm-metadata-security-run1-20261025.txt
?? evidence/test-results/alarm-metadata-security-triage-20261025.csv
?? evidence/test-results/alarm-metadata-summary-20261025.md
?? evidence/test-results/alarm-metadata-toolchain-20261025.txt
?? evidence/test-results/alarm-metadata-upgrade-mysql-run1-20261025.txt
?? evidence/test-results/esp32-transport-sdk-build-alarm-metadata-final-20261025.txt
?? evidence/test-results/esp32-transport-sdk-build-alarm-metadata-legacy-run1-20261025.txt
?? evidence/test-results/esp32-transport-sdk-build-alarm-metadata-run1-20261025.txt
?? firmware/.gitignore
?? firmware/.vscode/extensions.json
?? firmware/src/alarm_transition.h
?? scripts/alarm_metadata_wire_bridge.py
?? scripts/alarm_metadata_wire_fixture.c
?? scripts/live_http_event_race.php
?? scripts/test_alarm_offline_metadata.py
?? scripts/test_alarm_transition.py
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

## Batch aktif: complete alarm transition metadata (BELUM COMMIT)

Baseline batch `5048525`; keputusan `docs/adr/0008-alarm-transition-integration.md`, desain `docs/testing/alarm-transition-integration.md`, kontrak `docs/contracts/alarm-event-schema-v1.1.json`.

1. `firmware/src/alarm_transition.h`: immutable event-time alarm snapshot dengan identity/source/priority/reason/state/raised/ACK/CLEAR, validasi shared alarm model dan bounded ledger delapan.
2. `continuous_simulation.h`: metadata saat transisi, ACK tidak CLEAR; jurnal penuh menolak event eksplisit tanpa menghentikan observasi/indikasi.
3. `offline_state.h`, `offline_transaction.h`, `esp32_offline_store.c/.h`: VGS2 metadata-preserving, VGS1 tetap kompatibel dan historical metadata tidak direkonstruksi. Maksimum VGS2 5142 byte, buffer 5184; VGS1 4862. Zero-wait submission, IO worker, dua slot/readback. Known metadata tidak boleh diturunkan/mutasi/drop. CRC bukan autentikasi/power-loss proof.
4. Request event 1.1 dan shared `InspectsRawJsonObjects` dari parser telemetry yang sudah ada; exact raw/nested/escaped duplicate keys, uint32/uint64 lexical, lifecycle/action-time, null versus zero. Legacy event 1.0 tidak berubah.
5. Migration `2026_10_25_100006_add_alarm_metadata_to_monitoring_events.php`, canonical JSON di model/service/read API/escaped UI. Legacy metadata tetap unavailable. Receipt order tidak membuktikan global active alarm. Tidak ada remote operator control.
6. Native wire fixtures -> Laravel/PHP 8.2.35 -> MariaDB -> TLS/read/UI; previous-schema guard, migration roundtrip, fault/race regression. Real REPEATABLE-READ race diperbaiki pada `EventIngestService.php`: duplicate 1062 ditangani di luar failed transaction, shared current read juga aman bagi caller-owned outer transaction. Empat cohort aktual: 201/200, 201/200, 201/409, 201/200; masing-masing satu row, metadata pemenang tidak berubah. CLI workers memanggil kernel Laravel aktual; ini bukan pengujian concurrency server TCP deployment.
7. SDK dua target/CI source/security/living traceability/evidence/cleanup read-only. Perubahan firmware terakhir menambah laporan FULL/REJECTED/degraded storage yang sebelumnya tidak terlihat; log dibatasi first/every256. **Final source-stability HTTP dan retained SDK perlu diulang setelah perubahan terakhir ini.**

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

## Matriks hasil dan evidence batch aktif

Semua path berikut di `evidence/test-results/`. Historical FAIL dipertahankan; hasil corrected tidak menghapus failure.

| Gate | Hasil aktual checkpoint | Evidence / batas |
|---|---|---|
| Previous-schema isolation dan upgrade | PASS; exact empty 10/5, apply6/rollback6/reapply6 | `alarm-metadata-previous-preflight-20261025.txt`; `alarm-metadata-upgrade-mysql-run1-20261025.txt` |
| Full PHP 8.2.35/MariaDB current suite | PASS **362 cases**, 0 failed/skipped, setelah shared-read race fix | `alarm-metadata-mysql-race-final-20261025.txt`; existing-schema mode, tidak mengulang DDL |
| Native metadata/codec | PASS 6 transition + 9 offline metadata; old codec/transaction regresi | `alarm-metadata-corrected-regression-20261025.txt`; `alarm-metadata-final-regression-20261025.txt` |
| Broad host regression | 218 commands: 217 PASS, 1 historical source-inventory FAIL; corrected source guard PASS | `alarm-metadata-scoped-regression-20261025.txt`; corrected/final regression logs; counts bukan 218 unique test cases |
| Focused final regression | 11 commands PASS sebelum storage log change terakhir | `alarm-metadata-final-regression-20261025.txt`; continuous source assertion perlu rerun |
| Actual race failure -> fix | FAIL 201/500 pada RR; kemudian empat cohort PASS | `alarm-metadata-race-reproduction2-20261025.txt`; `alarm-metadata-http-proof-final-20261025.txt`; tidak ada tolerance/skip |
| Actual loopback TLS/kernel/MariaDB | PASS **122 labeled checks** pada source digest `6cda6a5d8d47b75d561809137cb50d5ccb6867b6502fa13349187f34e52efb7a` | `alarm-metadata-http-proof-final-20261025.txt`; **source firmware berubah setelahnya, final proof PENDING** |
| Candidate ESP-IDF latest build | PASS app **974032** bytes, RAM55572, own largest frame880 | `esp32-transport-sdk-build-alarm-metadata-final-20261025.txt`; source digest `22a297bf2fa3cecb8806d9340dfaa6be59856099f002734ce6d6b97578a5f733` |
| Retained SDK | Earlier PASS app1044112, RAM66436, frame1616, source edf7... | `esp32-transport-sdk-build-alarm-metadata-legacy-run1-20261025.txt`; **latest source final build PENDING** |
| Security scanner | Earlier 0 unresolved findings/privacy warnings; current final rescan PENDING | `alarm-metadata-final-security-20261025.txt`; exact FP pins in registry, adversarial scanner tests23 PASS |
| Cleanup audit | PASS metadata inventory only; semua retained | `alarm-metadata-cleanup-inventory-20261025.csv`; tidak menghapus build/vendor/evidence/user files |
| Final summary/manifest/diff/index/manual review | **PENDING, NO COMMIT** | `alarm-metadata-summary-20261025.md` masih placeholder checkpoint ini |
| ESP32 physical/Wokwi current/NVS power loss/trusted-clock Wi-Fi | NOT_RUN / dependency unavailable | SDK/native PASS bukan hardware proof |
| Hosted CI / POSIX host / MySQL8 / graphical browser / deployed TLS | NOT_RUN | POSIX -lm branch hanya source-review; local TLS bukan deployment |
| Formal SIM/SUP baru | NOT_RUN | Registri formal tidak diubah |

Native fixtures: eleven VGS2-recovered metadata events SHA256 `b5cad847c1ac7f808587eb367d0589f05f841a4001ae5ac112eebf3b5358c677`; fixture runtime identity SHA256 `ba891a36338b0554f7964e6787bef8cdb19300cf99854f2058dd7b4419eddcba`. Eleven berasal dari dua fixture stores terpisah, bukan satu jurnal berkapasitas11. Continuous 24-frame fixture SHA256 `ceda0c0794257456cdaace3d1fb001c6ae430ead882acc693fa36069c1521920` tetap kompatibel. SDK latest merged image SHA256 `5d695240d9e2fe5007af9f29640e56e129f5b2876c93d87f957099e4fc1b940f`; binary ignored, bukan source/evidence commit.

## Bug, security dan risiko tersisa

Audit scanner awal36 sudah ditriase di `docs/testing/security-scanner-review.md` dan security evidence: 32 INFO false positives, dua LOW synthetic CI, dua MEDIUM CI issue diperbaiki sebelum commit b999492. Exact reviewed non-secret lines/file SHA di `scripts/security-reviewed-findings.json`, bukan global detector waiver. Metadata batch meninjau ulang lima INFO source occurrences dan tiga source-version re-review, bukan delapan kerentanan unik. Temuan nyata baru: RR dedup race menghasilkan500, kini fixed dan reproduced/verified; diagnostic storage failures sebelumnya tidak dikonsumsi caller, source fixed, hardware observability belum diuji. Lihat `alarm-metadata-development-observations-20261025.txt` dan triage CSV. Tidak ada rahasia disalin ke dokumen.

Gap utama software: old-boot retained events belum replay lengkap; HTTP success bukan authenticated application receipt; belum ada durable confirmed-outbox deletion/free capacity. Jurnal delapan tetap bounded/refuse; jangan mengklaim unlimited offline delivery. Delivery ACK berbeda dari operator alarm ACK dan tidak boleh clear kondisi. Cross-boot ordering/current-state tidak boleh disimpulkan dari receipt sequence. Durability, wear, NVS confidentiality, real sensor/OEM providers, trust clock/provisioning, resource watermark/timing/outage memerlukan physical evidence. Jangan mengarang protokol OEM atau mengubah threshold demo menjadi aturan kapal nyata.

Formal: `docs/testing/formal-scenario-status.csv` mencatat SIM001-009 PASS dan SIM010-015 NOT_RUN. `docs/testing/supplemental-verification-plan.csv` mencatat SUP001/003/006/016/019 PASS, 14 PLANNED. Dedicated SIM010-015/SUP remaining tidak dieksekusi hanya karena local host/TLS PASS. Older SUP014 prepared target berbeda; user-approved target di atas menang, tetapi formal protocol amendment harus eksplisit sebelum eksekusi formal, bukan diam-diam mengubah pinned record.

## Aturan fail-closed dan kesinambungan

1. Jaga LOCKED baseline, user changes, `AGENTS.md`, `firmware/.gitignore`, `firmware/.vscode/extensions.json` dan ignored secret files. Jangan stage/overwrite/delete dua firmware untracked.
2. Tidak push, remote, pull/rebase/merge/reset/clean/history rewrite. Jangan delete evidence/build/vendor sebagai collateral. Audit kandidat cleanup read-only.
3. Sebelum DB mutation verifikasi effective exact target/account/schema/isolation dan ephemeral key. Laravel migrations saja untuk DDL. Test rows hanya owned isolated fixtures dengan verified cleanup; tidak menyentuh real/main data.
4. Batch terkait 5-7 scope; jangan mengulang implementasi atau membuat micro-batch nomor. Specific positive/negative/boundary/security/logical tests + existing/new integrated regression + security/manual scope/diff wajib. Missing mandatory gate => NO staging/commit; external exclusions tetap NOT_RUN, bukan PASS.
5. Sesudah mandatory local gates PASS, expected develop/HEAD/index, stage **exact approved files**, scan staged bytes, local commit otomatis sesuai izin. Git metadata sandbox dapat perlu approved narrow escalation; patuhi penolakan, jangan bypass.
6. Jangan edit firmware/backend di tengah SDK/HTTP source-stability gate. Log public disanitasi UTF-8, secret/SQL output tidak dicetak. Jika whitespace log dinormalisasi catat before/after SHA, jangan rewrite failure evidence.
7. Perbarui **kedua** handoff setelah batch besar committed. Self hash commit tidak dapat ditulis ke commit itu sendiri: sebut hash checkpoint yang diverifikasi dan periksa actual Git lagi saat resume. Jika WIP/limit/blocker muncul, checkpoint dulu dan tulis pending scope/gates eksplisit.
8. Satu commit/handoff bukan akhir Goal. Lanjut scope software independen yang aman; jangan tandai proyek VERIFIED/Goal complete sebelum audit aktual semua38 requirements dan seluruh kriteria Goal. Authority remote Goal UI bisa stale/blocked; user meminta resume kerja, jangan mengarang tool status aktif/complete.

## Seluruh 38 requirement: assessment dan evidence

Snapshot diambil dari living CSV aktual saat checkpoint. **22 IMPLEMENTED_UNVERIFIED / 16 PARTIAL**; formal per requirement 15 PASS / 3 PARTIAL / 20 NOT_RUN. PASS formal adalah scoped mapped scenarios/review, bukan full requirement VERIFIED. Current uncommitted metadata assessment ALM001/002 masih tunduk final batch gates. Deskripsi berikut disalin dari requirement baseline tanpa mengubahnya. Semua code/test refs lengkap dan qualification berada di `docs/testing/living-requirement-status.csv`; masing-masing entry berikut menyertakan seluruh internal evidence refs.

| Requirement (level) dan teks LOCKED | Implementasi | Formal / planned tests | Source utama; evidence |
|---|---|---|---|
| **SYS-001** (Mandatory): System shall operate as a monitoring and diagnostic prototype, not as certified ship safety equipment. | PARTIAL | PASS; SUP-001 | `README.md`; `docs/architecture/architecture-and-icd.md`; full refs: living CSV; evidence: `evidence/test-results/phase9-wave1-sup001-documentation-review-20261020.txt` |
| **SYS-002** (Mandatory): System shall separate source_mode = simulation, bench_test, physical for all data. | PARTIAL | NOT_RUN; SUP-002 | `firmware/src/core_types.h`; `firmware/src/core_source_mode.h`; full refs: living CSV; evidence: `evidence/test-results/phase8-h1-summary-20261017.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **SYS-003** (Mandatory): Backend/cloud failure shall not stop local sampling, local alarms, or safety-policy evaluation. | PARTIAL | NOT_RUN; SIM-010;SIM-012 | `firmware/src/network_outage_local_guard.h`; `firmware/src/phase9_sys003_outage_cycle_host.h`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SYS-004** (Mandatory): No physical engine starter, ignition, steering, radar, radio, or third-party operational or mission system shall be controlled by V1. | PARTIAL | PASS; SUP-003 | `docs/architecture/architecture-and-icd.md`; `firmware/src/safety_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-closure-summary-20261016.md`; `evidence/test-results/phase9-wave1-sup003-static-review-20261021.txt` |
| **SAF-001** (Mandatory): Ventilation hatch/door state shall be modeled as OPEN/CLOSED/UNKNOWN with quality. | IMPLEMENTED_UNVERIFIED | PASS; SIM-001;SIM-002 | `firmware/src/provider_door.h`; `firmware/src/safety_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-002** (Mandatory): A virtual start request shall be rejected when configured blocking conditions are not satisfied. | IMPLEMENTED_UNVERIFIED | PASS; SIM-001;SIM-002;SIM-003;SIM-004 | `firmware/src/safety_policy.h`; `firmware/src/safety_policy_runtime.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-003** (Mandatory): Blocking/alert-only behavior shall be configuration-driven; only field-verified rules may be labeled real-vessel rules. | PARTIAL | PASS; SIM-002;SIM-005 | `firmware/src/safety_policy.h`; `firmware/src/safety_monitor_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-004** (Mandatory): Fuel-vapor channel shall support NORMAL/WARNING/ALARM/FAULT/UNKNOWN and shall never map missing data to safe. | IMPLEMENTED_UNVERIFIED | PASS; SIM-003;SIM-004 | `firmware/src/provider_fuel_vapor.h`; `firmware/src/safety_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-005** (Mandatory): Bilge/high-water channel shall support NORMAL/HIGH/FAULT/UNKNOWN. | IMPLEMENTED_UNVERIFIED | PASS; SIM-005 | `firmware/src/provider_bilge.h`; `firmware/src/safety_monitor_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **SAF-006** (Mandatory): Compartment temperature shall support valid/invalid/missing/stale quality and configurable demo thresholds. | IMPLEMENTED_UNVERIFIED | PARTIAL; SIM-006;SIM-011 | `firmware/src/provider_temperature.h`; `firmware/src/safety_monitor_policy.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **ALM-001** (Mandatory): Alerts shall have unique ID, source, priority, state, reason, raised_at, acknowledged_at and cleared_at. | IMPLEMENTED_UNVERIFIED | PASS; SIM-003;SIM-005;SIM-006 | `firmware/src/core_alarm.h`; `firmware/src/core_event_journal.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **ALM-002** (Mandatory): Acknowledgement shall not clear the underlying alarm condition. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-004 | `firmware/src/core_alarm.h`; `firmware/src/main.c`; full refs: living CSV; evidence: `evidence/test-results/firmware-core-alarm-wokwi-20261013.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **ALM-003** (Mandatory): Local buzzer/LED behavior shall be independent from dashboard availability. | PARTIAL | PARTIAL; SIM-003;SIM-010;SIM-012 | `firmware/src/safety_local_alarm.h`; `firmware/src/safety_policy_runtime.h`; full refs: living CSV; evidence: `evidence/test-results/phase5-e4-summary-20261016.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
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
| **NET-001** (Mandatory): Network client shall implement timeout, reconnect and bounded retry/backoff without blocking sampling. | PARTIAL | NOT_RUN; SIM-010;SIM-012;SIM-013 | `firmware/src/network_transport_host_adapter.h`; `firmware/src/phase9_net001_uplink_host_bridge.h`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **NET-002** (Mandatory): Offline mode shall preserve latest state and critical event journal within bounded storage. | PARTIAL | NOT_RUN; SUP-013 | `firmware/src/core_event_journal.h`; `firmware/src/core_runtime_guard.h`; full refs: living CSV; evidence: `evidence/test-results/firmware-core-c4-wokwi-20261013.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **API-001** (Mandatory): Laravel API shall validate authentication, schema, payload size, device identity and value contracts. | PARTIAL | NOT_RUN; SIM-015 | `backend/laravel/routes/api.php`; `backend/laravel/app/Http/Controllers/Api/TelemetryIngestController.php`; full refs: living CSV; evidence: `evidence/test-results/phase9-p3-runtime-http-evidence-audit-summary-20261018.md`; `evidence/test-results/phase9-p3-securityfix-feature-tests-audit-summary-20261018.md`; `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **DB-001** (Mandatory): All schema changes shall use Laravel migrations; no manual database shortcut is accepted. | PARTIAL | NOT_RUN; SUP-014 | `backend/laravel/database/migrations/2026_10_17_100001_create_devices_table.php`; `backend/laravel/database/migrations/2026_10_17_100002_create_telemetry_samples_table.php`; full refs: living CSV; evidence: `evidence/test-results/phase9-p3-migration-rollback-support-summary-20261018.md`; `evidence/test-results/phase9-p3-migration-rollback-support-evidence-audit-summary-20261018.md`; `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **UI-001** (Mandatory): Dashboard shall distinguish live, stale, offline and simulation states visibly. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SIM-010 | `backend/laravel/app/Support/DashboardSignalLabel.php`; `backend/laravel/resources/views/monitoring/index.blade.php`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md` |
| **UI-002** (Mandatory): Dashboard shall provide overview, safety, propulsion, navigation, power, alarms/events, device health and test evidence views. | IMPLEMENTED_UNVERIFIED | NOT_RUN; SUP-015 | `backend/laravel/resources/views/monitoring/index.blade.php`; `backend/laravel/resources/views/monitoring/sections/overview.blade.php`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/device-read-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **SEC-001** (Mandatory): No production secret, real operational route or coordinate, radio frequency, credential, or confidential vessel detail shall be committed to public GitHub. | PARTIAL | PASS; SUP-016 | `scripts/audit_precommit_security.py`; `docs/github-repository-plan.md`; full refs: living CSV; evidence: `evidence/test-results/phase4-closure-summary-20261016.md`; `evidence/test-results/phase9-wave1-sup016-security-review-20261020.txt`; `evidence/test-results/security-php8235-summary-20261025.md` |
| **SEC-002** (Mandatory): Demo API shall use HTTPS/authentication and secrets shall be external to source code. | PARTIAL | NOT_RUN; SIM-015 | `backend/laravel/routes/api.php`; `backend/laravel/app/Http/Middleware/AuthenticateDeviceToken.php`; full refs: living CSV; evidence: `evidence/test-results/phase9-p3-security-review-20261018.txt`; `evidence/test-results/phase9-p3-securityfix-feature-tests-audit-summary-20261018.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md` |
| **TST-001** (Mandatory): Every requirement shall map to code module, automated/manual test and evidence. | PARTIAL | NOT_RUN; SUP-017 | `requirements/traceability-matrix.csv`; `docs/testing/living-requirement-status.csv`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/dashboard-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **TST-002** (Target): CI shall build firmware and backend tests on each pull request; Wokwi CI shall be added if available for the project plan. | PARTIAL | NOT_RUN; SUP-018 | `.github/workflows/phase9-multi-context-ci.yml`; `scripts/run_mysql_integration.py`; full refs: living CSV; evidence: `evidence/test-results/mysql-integration-gate-20261025.md`; `evidence/test-results/mariadb-integration-summary-20261025.md`; `evidence/test-results/security-php8235-summary-20261025.md`; `evidence/test-results/esp32-transport-summary-20261025.md`; `evidence/test-results/offline-nvs-summary-20261025.md`; `evidence/test-results/live-http-summary-20261025.md`; `evidence/test-results/continuous-simulation-summary-20261025.md`; `evidence/test-results/alarm-metadata-summary-20261025.md` |
| **DOC-001** (Mandatory): Repository shall contain architecture, ICD, standards matrix, FMEA, ADRs, traceability matrix, test evidence and limitations. | IMPLEMENTED_UNVERIFIED | PASS; SUP-019 | `docs/architecture/architecture-and-icd.md`; `docs/standards/standards-applicability-matrix.md`; full refs: living CSV; evidence: `evidence/test-results/phase9-wave1-sup019-documentation-review-20261021.txt`; `evidence/test-results/alarm-metadata-summary-20261025.md` |

## Urutan resume dan pengujian berikutnya

1. Verifikasi targeted branch/HEAD/worktree/index dan baca summary metadata, ADR0008, development observations. Jangan mengulang baseline audit, menghapus WIP atau memulai implementasi continuous yang sudah selesai.
2. Selesaikan metadata batch: retained SDK build latest source; rerun continuous source assertions; rerun actual122 integration setelah last firmware log change. PHP362 current service fix sudah PASS; ulang jika source PHP berubah/failure. SDK logs terakhir whitespace-normalization hanya dengan hash inventory. Update summary, SDK config review, current-source evidence.
3. Set child environment `VG_PHP_CLI=C:/tools/php-8.2.35/php.exe`; child native compiler PATH `C:/msys64/ucrt64/bin` bila diperlukan. Harness sendiri memuat approved testing file dan membuat key sementara. Jangan dump env.

```powershell
python -B scripts/test_alarm_transition.py
python -B scripts/test_alarm_offline_metadata.py
python -B scripts/test_continuous_simulation.py
python -B scripts/test_mysql_integration_gate.py
python -B scripts/test_live_http_integration_gate.py
python -B scripts/run_mysql_integration.py --testing-env --execute --existing-schema --php-binary C:/tools/php-8.2.35/php.exe
python -B scripts/run_live_http_integration.py --testing-env --execute --php-binary C:/tools/php-8.2.35/php.exe
python -B scripts/build_esp32_port.py --pio-cli <LOCAL_HOME>/.platformio/penv/Scripts/platformio.exe --environment esp32dev_espidf --evidence-name esp32-transport-sdk-build-alarm-metadata-legacy-final-20261025.txt
python -B scripts/audit_precommit_security.py
```

SDK memerlukan izin cache narrow yang sudah dipakai, tidak mem-flash device. Jangan mengganti existing evidence file bila sudah ada; gunakan nama run baru. `--upgrade-previous` dahulu sudah digunakan, **bukan** opsi current6. Full gate commands/tool context direkam evidence; jalankan runner fail-closed, jangan langsung artisan RefreshDatabase terhadap konfigurasi main.

4. Baca evidence source proof, verify LOCKED/protected/formal hashes, exact diff/security/manual review, manifest scoped. Final scan working+index termasuk evidence/handoff; semua wajib PASS sebelum stage/commit. Belum ada commit metadata pada checkpoint awal ini.
5. Setelah commit update kedua handoff, laporkan hash/evidence/blocker singkat lalu lanjut batch substantif berikut. Prioritas berikut: recovered old-boot replay + authenticated application receipt + crash-safe bounded outbox retirement + backend exact receipt binding/idempotency + real C99/PHP/MariaDB/TLS regression + evidence/security. Tentukan desain dari ICD/locked constraints dan existing historical host receipt primitives; jangan menganggap host receipt prototypes sudah tersambung ke device runtime. Perubahan ini memerlukan invariant baru, bukan melonggarkan retained-prefix guard.
6. Formal completion tetap gated; jalankan dedicated scenarios hanya dengan protocol/dependencies tepat. Catat hardware/hostedCI/productionTLS unavailable dan teruskan software independen aman.

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

> Lanjutkan Goal Integrated Vessel Monitoring & Diagnostic Gateway secara lokal pada develop dari HEAD/worktree aktual. Baca docs/handoff/CODEX_RESUME.md dan CHATGPT_CONTEXT.md, lalu targeted Git verification; baseline audit sudah dilakukan. Jangan ulang continuous simulation committed pada5048525 atau menimpa batch alarm metadata yang masih WIP pada checkpoint awal. Cocokkan status handoff dengan actual Git/evidence. Pakai PHP8.2.35 eksplisit dan approved isolated MariaDB127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex via guarded runner, tanpa mencetak secret. Selesaikan current-source SDK/HTTP/regression/security/manual gates yang pending sebelum exact-scope local commit. Pertahankan LOCKED, mainDB, evidence, AGENTS dan dua firmware untracked. NO PUSH/remote/destructive Git. Update kedua handoff setelah committed batch. Lanjut software prioritas roadmap dalam5-7 related scopes dengan test/evidence, fail-closed pada mandatory failure; jangan tandai formal/hardware/produksi verified atau Goal complete tanpa bukti38requirement. Local TLS/native/SDK bukan physical/formal proof.
