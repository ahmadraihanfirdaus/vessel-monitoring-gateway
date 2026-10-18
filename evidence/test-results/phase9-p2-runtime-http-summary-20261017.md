# Phase 9 P2 Runtime HTTP Evidence

Date: 2026-10-17

## Scope

Real loopback HTTP verification of:

`POST /api/v1/telemetry`

Checkpoint:

`2c3c563db3c2c9cd403c867eae6819fa12997185`

The Laravel application was started only on:

`127.0.0.1:8091`

with process-local database configuration targeting the dedicated test
database `vessel_monitoring_gateway_test`. The normal ignored local `.env` remained pointed at
`vessel_monitoring_gateway`.

## Result

All 14 planned runtime HTTP scenarios passed with the expected status codes:

- 201 distinct valid sample
- 200 identical duplicate
- 409 conflicting duplicate
- 401 missing authentication
- 401 unknown authentication
- 403 disabled device
- 403 authenticated device identity mismatch
- 422 invalid quality/value contract
- 413 payload greater than 4096 bytes
- 201 unsigned 64-bit maximum sequence and uptime
- 422 quoted top-level uint64 identity
- 422 missing channel value member
- 422 duplicate top-level identity key
- 422 duplicate channel key

Response bodies are represented in evidence by SHA-256 hashes; ephemeral bearer
tokens are not persisted in repository evidence.

Two gate-created device fixtures were created through Laravel models in the
dedicated test database. Before cleanup the expected persisted state was two
devices, two telemetry samples, and ten telemetry channels. On full success,
the same gate deleted only those two devices through Laravel models and the
foreign-key cascade removed their telemetry rows.

Final application data rows: **0**.
Final test data rows: **0**.

## Boundary

This is P2 backend runtime HTTP evidence. It does not execute or close formal
SIM010-SIM015, does not execute physical bench work, and does not establish
production readiness. Phase 9 remains IN_PROGRESS and the total system remains
PARTIAL.
