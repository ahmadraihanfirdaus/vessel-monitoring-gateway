# ADR-0009 - Recovered critical event replay

Status: implemented and locally tested; all mandatory local gates PASS, exact staged-byte/security review required before local commit. External/formal approval remains open.
Baseline: local develop `70963d463fa5cd2d43914950ef7a9ece5b3185d7`.

The NVS worker already validates/reconstructs VGS1/VGS2 records. Its recovered
critical events currently remain private to the worker; the continuous runtime
publishes only its current-boot RAM journal. Connect this missing actual path.

## Six related scopes

1. Shared pure-C bounded recovered-event snapshot and serializer: preserve each
   original boot, event/alarm ID, source, time and optional complete metadata.
   Known metadata uses event1.1; unknown historical metadata stays event1.0.
2. Dedicated zero-wait recovered-view queue from the actual NVS worker after
   successful recovery. Acquisition never reads NVS or mutable worker state.
3. Native replay progress/fair selection shared with the actual SDK caller;
   advance only on queue acceptance, explicitly expose unpublishable legacy
   types, and preserve retained facts. Do not conflate queueing with delivery.
4. Integrate recovered/current event fairness with latest telemetry in the
   continuous SDK entry, including recovery/degraded diagnostics and local
   progression when transport/storage is unavailable or rejects work.
5. Recovered native cross-boot fixtures through real PHP8.2.35/MariaDB and local
   TLS/read/UI, including duplicates, identity collisions across different boots,
   legacy absence and complete metadata, quality and zero/null preservation.
6. Specific/native/fault/source/SDK/CI/security regression, exact evidence,
   living qualifications and both updated handoffs; cleanup remains read-only.

## Limits and invariants

This is nondestructive replay of retained event facts. No queue/HTTP result is
permission to delete a record, clear an alarm, retire a durable outbox or free
the capacity-eight journal. Authenticated application-receipt binding and
crash-safe retirement remain a separate integration dependency. Full storage
still explicitly refuses new critical retention while sampling proceeds.

No new persistence format, database schema, physical control, credential store,
TLS downgrade, default retry policy or engineering threshold is introduced.
Historical recovery events outside the existing backend event contract must be
reported as unpublishable and remain retained; other supported facts can proceed.
Recovered telemetry is not resubmitted by this event-only path: server receipt
order cannot establish a previous boot's sample as current acquisition.

Successful recovery yields a bounded immutable copy for the single runtime
owner. Explicit later recovery may yield a new copy and cause duplicate replay;
existing exact backend identity deduplication handles it. Invalid/uncertain
storage never becomes an empty successful recovered view. Recovered metadata is
never reconstructed from mutable current alarms. The worker owns all NVS IO.

Physical ESP32/NVS/power loss/WiFi/TLS/clock, current Wokwi, hosted CI, deployed
TLS and new formal SIM/SUP remain NOT_RUN. Local tests do not promote them.
