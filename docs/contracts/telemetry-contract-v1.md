# Telemetry Development Contract v1.0

## Status

Phase 8 H1 development contract.

This document defines the development wire contract required by the Phase 8
roadmap. It is not a production network protocol, backend API, or claim of
physical vessel integration.

## Requirement-derived fields

TEL-001 requires every payload to carry:

- `schema_version`
- `device_id`
- `firmware_version`
- `boot_id`
- `sequence`
- `uptime_ms`
- `source_mode`
- per-channel `quality`

TEL-002 requires invalid/missing channel values to remain `null` or absent with
quality metadata, never silently converted to numeric zero.

The v1 serializer chooses **explicit `null`** for invalid/missing/unknown
numeric channel values. A genuine valid numeric zero remains `0` with
`quality: "valid"`.

## Phase 8 v1 design decision: stable sample identity

The locked requirement states that backend deduplication must use a stable
identity key, but does not prescribe the key composition.

For the v1 development contract, the stable sample identity is defined as:

`(device_id, boot_id, sequence)`

Rationale:

- `device_id` separates devices;
- `boot_id` separates device boots;
- `sequence` identifies a sample within a boot.

`firmware_version`, `uptime_ms`, `source_mode`, channel values and quality are
payload content, not part of the identity key. If two payloads have the same
identity tuple but semantically different content, the contract classifies
them as a **conflicting duplicate**.

This is a Phase 8 design decision, not text added to the LOCKED requirement.

## Duplicate classifications

- **DISTINCT** — identity tuple differs.
- **IDENTICAL** — identity tuple is equal and semantic payload content is equal.
- **CONFLICTING** — identity tuple is equal but semantic payload content differs.
- **INVALID** — either payload violates the v1 contract.

This contract-level classifier does not insert, update or reject database rows.
TEL-003 backend/database behavior and formal SIM-014 remain outside H1.

## Source mode

Wire labels:

- `simulation`
- `bench_test`
- `physical`

A `physical` label in a development fixture is synthetic metadata only and does
not demonstrate real physical acquisition or authorized vessel integration.

## Quality

Wire labels:

- `valid`
- `invalid`
- `missing`
- `stale`
- `unknown`

Numeric value policy:

- `valid` -> finite numeric value required;
- `stale` -> finite numeric value may be retained, or `null`;
- `invalid` -> `null`;
- `missing` -> `null`;
- `unknown` -> `null`.

## Bounds

The v1 development implementation uses bounded identifiers and up to 16
channels. These are contract-version implementation limits, not vessel-specific
operational limits.

## Non-scope

H1 does not implement:

- MQTT, HTTP, broker or cloud endpoint selection;
- network reconnect/retry/backoff;
- Laravel/backend ingestion;
- database deduplication;
- authentication/HTTPS;
- physical radio/modem/GNSS integration;
- production readiness.
