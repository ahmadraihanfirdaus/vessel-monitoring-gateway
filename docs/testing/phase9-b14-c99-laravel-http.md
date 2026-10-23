# Phase 9 Batch 14 — C99 wire into Laravel HTTP (development only)

- TEL-001/TEL-002: strict C99 serializer outputs exact synthetic JSON bytes; 0 versus null, uint64 limit, and physical-mode denial are checked.
- API-001/SEC-002: bytes are passed unchanged into Laravel's actual POST /api/v1/telemetry route, middleware, authentication and request validation, with in-memory strict device and ingestion service doubles.
- NET-002/TEL-003: HTTP receipts for created / identical duplicate / conflicting duplicate. Receipt service is simulated; persistence and replay durability NOT VERIFIED.
- TST-001/TST-002: gcc -Werror generation and Laravel JUnit gate in no-DB job, with all B1–B13 regression gates and exact-scope local commit.

No live HTTPS socket, MySQL, production token, firmware flash, ESP32, or calibrated sensor is exercised. No acceptance SIM/SUP is closed; full E2E still OPEN.
