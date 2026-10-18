# Phase 9 P3 Design — Event Persistence, State/History and Device Health

**Status:** SOURCE APPLY PLANNED — database execution not authorized by this document.

## Scope

P3 completes the remaining backend design slice needed after P2 telemetry
ingestion:

1. backend event persistence;
2. read-oriented telemetry state/history;
3. derived device-health reporting;
4. authenticated API validation.

P3 does not close formal SIM-010 through SIM-015, SUP-013, SUP-014, physical
bench work, certification, vessel integration, or production readiness.

## Event identity

Firmware `event_id` is per-journal/per-boot. The backend stable event identity
is therefore `(device_id, boot_id, event_id)`.

## Event endpoint

`POST /api/v1/events`

Authentication uses the existing device-scoped bearer credential.

Required schema version: `1.0`.

Required fields are `schema_version`, `device_id`, `boot_id`, `event_id`,
`linked_alarm_id`, `source_id`, `source_mode`, `event_type`, and
`occurred_at_ms`.

`event_id`, `linked_alarm_id`, and `occurred_at_ms` are unsigned 64-bit JSON
integers. `source_id` is unsigned 32-bit and greater than zero.

Allowed source modes are `simulation` and `bench_test`. Physical is rejected.

Allowed event types are `alarm_raised`, `alarm_ack`, `alarm_cleared`, and
`fault`.

## Event persistence

Table: `monitoring_events`.

Stable unique key:

`UNIQUE(device_id, boot_id, event_id)`

Device deletion cascades event rows.

Response contract:

- 201 distinct event;
- 200 identical duplicate;
- 409 conflicting duplicate;
- 401 missing/malformed/unknown bearer;
- 403 disabled device or device identity mismatch;
- 413 payload over 4096 bytes;
- 422 schema/value/identity validation failure.

## State and history

No duplicate state/history table is introduced. Existing `telemetry_samples`
and `telemetry_channels` remain the sole telemetry history store.

Endpoints:

- `GET /api/v1/device/state`
- `GET /api/v1/device/history`

Reads are own-device only. History is newest-first, cursor-paginated, defaults
to 50 rows and is capped at 100 rows.

## Device health

Endpoint:

`GET /api/v1/device/health`

No separate `device_health` table is created. The read model reuses
`devices.last_seen_at`, `devices.last_boot_id`, `devices.last_sequence`, plus
the latest telemetry sample.

The response exposes raw last-seen facts and `age_seconds`. P3 does not invent
online/stale/offline thresholds; that remains Phase 10 presentation policy.

## Retention and NET-002 boundary

P3 introduces no automatic backend event pruning. Backend event history is not
the bounded offline firmware journal required by NET-002. SUP-013 remains
NOT_RUN.

## Migration control

Exactly one new Laravel migration is planned:
`create_monitoring_events_table`.

No manual database schema shortcut is accepted.
