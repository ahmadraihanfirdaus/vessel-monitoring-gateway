# Device read API development contract

This additive read contract supports the Phase 10 dashboard prerequisite. It
does not change the LOCKED requirements or supply operator/device ownership,
login provisioning, freshness thresholds, a connected dashboard, or formal
SIM/SUP closure. It reuses the existing device bearer authentication. Never put
bearers in URLs, browser storage, public examples, or evidence.

## Event history

`GET /api/v1/device/events`

Only the enabled device resolved from the Authorization header is queried.
Missing/unknown authentication returns 401; a disabled device returns 403.
The endpoint is read-only: it cannot acknowledge/clear alarms, change device
last-seen metadata, or drive physical outputs.

Accepted query parameters:

| Parameter | Meaning |
|---|---|
| `limit` | Integer 1..100, default 50 |
| `cursor` | Canonical Laravel cursor, maximum 2048 characters |
| `event_type` | Optional exact match: `alarm_raised`, `alarm_ack`, `alarm_cleared`, `fault` |
| `source_mode` | Optional exact match: `simulation`, `bench_test` |

Empty, array-shaped, invalid, and unsupported parameters return 422. There is
no device selector. `physical` remains outside the authorized ingestion modes.
Filters combine with AND and the authenticated-device constraint. Filtering
changes neither stored events nor their meaning.

The response contains `device_id`, `items`, and nullable `next_cursor`. Empty
history returns `items: []` and `next_cursor: null`. Each item contains exactly
`schema_version`, `device_id`, `boot_id`, `event_id`, `linked_alarm_id`,
`source_id`, `source_mode`, `event_type`, `occurred_at_ms`, and `received_at`.
The four integer fields (`event_id`, `linked_alarm_id`, `source_id`,
`occurred_at_ms`) are JSON decimal **strings**, including small values and zero.
This prevents browser number precision loss at uint64 boundaries. No credential,
token digest, inferred alarm state, or internal row ID is an item field.

Rows order by server `received_at DESC, id DESC`. A late replay or a boot clock
reset is not a reliable global occurrence ordering. `occurred_at_ms` remains the
original firmware fact. An `alarm_ack` event never implies `alarm_cleared`.
Neither the list nor a filtered subset establishes current active-alarm state.

Use `next_cursor` with the same filters. Cursors are validated positions, not
authorization grants or signed snapshots. Pagination is device-scoped even if
a position is forged/copied. Tied timestamps use the unique row ID; newly
received rows ahead of a cursor are visible on refresh, rather than inserted
into an already traversed page. There is no snapshot or retention guarantee.

Successful and handled validation/auth/dependency responses use `no-store,
private`, `Pragma: no-cache`, and `Vary: Authorization`. Recognized connection
failures return sanitized 503 with `Retry-After: 5`. Programming errors are not
silently converted into retryable failures. TLS deployment, rate/volume testing,
hosted CI and physical transport verification remain outside local proof.

## Telemetry history hydration

The existing `/api/v1/device/state`, `/history`, and `/health` response contracts
remain in place. History now loads all channels for the returned page in one
query rather than one query per sample. Only the returned sample IDs are
hydrated, at most 100; an empty page performs no channel query. A pagination
lookahead row is not hydrated. Zero, null, quality, source provenance and channel
name ordering are preserved. Receipt order still does not establish cross-boot
measurement chronology. No schema or automatic pruning is introduced.

## Verification

The guarded real MariaDB suite exercises authentication, cross-device isolation,
combined filters, pagination ties/concurrent arrivals, bounds, malformed
cursors, no read-side writes, uint64 precision, and C99 wire ingestion/readback.
Failure-injection tests additionally exercise sanitized dependency errors without
claiming a real server outage. See the [execution matrix and remaining gaps](../../evidence/test-results/device-read-summary-20261025.md).
