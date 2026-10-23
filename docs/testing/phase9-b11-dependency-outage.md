# Phase 9 Batch 11 — typed HTTP dependency outage (scoped)

Baseline: `develop@a8c7f790840fe6759692291ba484a0758bfcc96e`, based on user Git Bash output after B10 local commit. Batch 11 does not inspect or write live MySQL.

- `SEC-002`: token *lookup* `QueryException` returns sanitized HTTP 503; rejected/absent tokens remain HTTP 401/403.
- `NET-001`/`NET-002`: persistence exception from real telemetry and event ingest controller is sanitized HTTP 503 + advisory `Retry-After: 5`. This is not proof of firmware automatic retry/backoff or offline journal durability.
- `UI-002`: state/history/health read dependency outage is HTTP 503 (not client validation 422). Actual dashboard remains fixture/static.
- `SYS-003`: typed database exception is treated as a remote dependency outage; unrelated runtime errors remain 500 and local alarms/safety are not asserted by this test.
- `API-001`: no SQL, credentials, token, endpoint hostname, query or exception detail in JSON error body.
- `TST-001`/`TST-002`: 9 Laravel HTTP cases with Mockery service doubles + JUnit exact count, Python contract/CI checks, 49 historical Python suites, prior B9 17 and B10 8 HTTP cases, native core 226/226. No MySQL connection or migration is planned by local runner.

`QueryException` is classified only for MySQL connection/disconnect codes (2002, 2003, 2006, 2013, 2055) or SQLSTATE class 08; other SQL errors are rethrown. This is a scoped heuristic, not exhaustive fault handling. This does not prove TLS/auth deployment, hardware, DB integration, durable queue, real reboot reliability, or formal SIM/SUP closure. Do not mark system production ready.
