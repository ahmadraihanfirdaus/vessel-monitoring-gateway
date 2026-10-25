# Continuous all-domain simulation integration

Continuation baseline: `develop` `054cfa5f7f00362e3246d46e9bf5dce9309f9059`.
The actual finite demo/self-test remains. The optional continuous candidate
composes existing providers, engine model, narrow NMEA parser, scheduler and
policies; it acquires no physical data and drives no GPIO. See ADR-0007.

## Versioned full-domain contract

Telemetry **1.0 remains 16 channels**, with unchanged schema and old wire bytes.
Optional **1.1 allows 72 channels**, the same eight top-level fields, strict
raw-key/uint64 admission and identity `(device_id, boot_id, sequence)`. The body
limit remains **4,096 bytes** regardless of version or channel count. Event
schema stays 1.0. No database schema change is needed. Unknown versions reject;
different versions with the same identity conflict rather than create duplicates.

The typed mapping has six fields per engine (`state`, `rpm`, `temperature_c`,
`runtime_s`, `alarm`, `comm`), six navigation fields, five safety fields, six
attitude/vibration fields and three power fields. Four engines give 44 domain
channels; eight give 68. Continuous four-engine demo adds journal retained,
journal rejected, skipped periods and logical alarm indication: 48 channels.
An arbitrary 68/72-channel object can exceed the byte limit. Encoder failure
must not publish partial bytes; the latest successful RAM packet stays intact.
The eight-engine type is supported by mapping, not by an invented eight-engine
stimulus profile. The continuous candidate uses the existing four-engine demo.

Engine communication loss/unknown produces null/missing measurements, while its
communication code remains explicit. A stopped, communicating engine has valid
zero RPM. Runtime/age integers above 2^53-1 are null/invalid numeric channels,
never rounded silently; identity sequence/uptime and journal IDs stay uint64.
Navigation has valid/stale/offline age transitions, no-fix null/invalid position,
and uninitialized null/unknown. Invalid checksum does not replace last-valid data.
Navigation demo coordinates are the explicitly synthetic origin, never private
vessel coordinates. Vapor surrogate is unitless; attitude is not stability and
vibration is not machinery diagnosis.

## Continuous local behavior and bounded losses

The single-owner coordinator repeats existing finite SIMULATION provider
stimuli with current diagnostic timestamps. It uses explicit sampling, navigation
age, prestart/monitoring and engine-deviation policy. Hatch/vapor virtual rules
retain DISABLED/ALERT_ONLY/BLOCK; bilge/temperature reject BLOCK. Thresholds and
opaque demo priority/reason codes are supplied externally, not operational defaults.

Local policy/alarm evaluation proceeds independently of network/storage queues.
Eight retained journal entries are never evicted. Full-journal new transitions
are explicitly refused and counted, while sampling, current conditions and
logical local indications continue. This is bounded, incomplete event retention,
not a lossless claim. Existing `core_flow` rollback/finite guards are unchanged.
ACK requires a separately retained event, never clears the condition, and is
refused if full. Changed condition reasons clear the old alarm and raise a new
unacknowledged one using a shared per-boot allocator. Backward time is rejected;
missed periods are counted without a catch-up storm; counters saturate and
sequence/deadline exhaustion requires explicit restart. Allocator errors remain
explicit and keep a logical alarm indication; no physical safe-state is inferred.

## Optional SDK candidate and read-only provisioning contract

`esp32dev_espidf` retains the complete legacy self-test image and existing Wokwi
target. `esp32dev_continuous` is opt-in and compiles the separate continuous entry.
Both keep the pinned platform/framework candidate, 1 MiB application partition,
full TLS roots/hostname/date validation, assertions and compiler stack gate.
Neither build uploads anything.

The candidate requires an externally provisioned, read-only NVS namespace
`vgw_demo`. It never provisions or erases NVS and has no policy fallback:

| Key | NVS type | Meaning/validation |
|---|---|---|
| device | string | Safe 1..48-character identity |
| interval_ms | u32 | Explicit positive sampling interval |
| nav_stale_ms / nav_offline_ms | u32 | Positive stale, offline greater than stale |
| hatch_rule / vapor_rule | u32 | Existing enum 0..2 |
| bilge_rule / temp_rule | u32 | Existing enum 0..1; BLOCK rejected |
| temp_warn_mc / temp_alarm_mc | i32 | Demo millidegrees C converted to finite thresholds; warning less than alarm |
| rpm_deviation | u32 | Positive demo RPM-deviation threshold |
| demo_priority / demo_reason | u32 | Nonzero opaque demo alarm codes |

Boot ID is fresh startup entropy before Wi-Fi. Optional existing `vgw_net` cloud
profile must match the local device identity; absent/invalid/mismatched network
configuration disables cloud submission while local simulation can proceed.
Existing NVS and network workers accept zero-wait bounded copies. Latest RAM
state may replace pending latest state; critical journal prefixes stay cumulative.
Storage/network refusal and IO halt do not wait inside acquisition. Completed
HTTP is not application ACK. Durable replay/deletion, authenticated receipt
integration, trusted device wall clock and actual NVS provisioning remain gaps.
SDK calls/flash cache effects and real deadline/stack/heap behavior need hardware.

## Backend and explicit UI presentation

Set `MONITORING_PRESENTATION_PROFILE=continuous_simulation_v11` only when this
known vocabulary is desired. It is effective only for schema 1.1 **simulation**
data. Default section mappings remain empty. Explicit nonempty section mappings
take precedence. Raw names/values/quality remain visible and escaped; known
enums/units are added only to valid/stale non-null values. Unknown enum codes
are labeled UNRECOGNIZED, never silently safe. Engine demo alarm flag is distinct
from the coordinator's local alarm indication and persisted lifecycle events.

Real network replay exposed ambient PHP float-to-string precision loss before
DOUBLE storage. Persistence now binds a locale-independent 17-digit binary64
round-trip string. Duplicate comparison remains exact, without an epsilon.
Regression sets PHP precision/serialize_precision to 2 and proves bit-preserving
storage, identical replay, and one-ULP conflict rejection in both versions.

## Gates and evidence boundaries

`test_continuous_simulation.py` compiles real strict C99 and tests 2,000 local
cycles, boundaries, full journal, ACK/reason changes, null/zero/source and legacy
wire identity. `continuous_simulation_wire_bridge.py` generates 24 actual full
domain packets, each merged/packed/recovered by the real native snapshot codec.
The guarded MySQL runner now creates this fixture before any schema mutation.
Laravel tests use real approved MariaDB and transaction rollback. The real
loopback TLS runner uses a fixed synthetic identity override to feed the same
native coordinator into its existing exact-owned lease, then checks read APIs,
labels and replay. No additional device ownership exemption is introduced.

Invocation remains explicit PHP 8.2.35, approved testing-file opt-in and
`--execute --existing-schema`. No migration roundtrip is needed for this
schema-free change. Both SDK image builds and all legacy/scanner gates remain
mandatory local checks. Results, failures and exact files are recorded in
`evidence/test-results/continuous-simulation-summary-20261025.md`.

Host/SDK/local TCP/HTML evidence is not ESP32/NVS/power-loss, graphical browser,
deployed TLS or formal protocol execution. SIM/SUP registries remain unchanged;
system PARTIAL and final approval NOT_APPROVED.
