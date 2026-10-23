# Phase 9 Batch 17 — Laravel JSON response to C99 ACK policy (host-only)

This suite records **actual in-process Laravel route responses** using service doubles, writes raw response JSON into an evidence directory outside the repository, validates exact status/result/error pairs using a duplicate-key rejecting Python decoder, and passes typed predecoded outcomes to the existing bounded B16 C99 ACK decision header.

Contexts: API-001, SEC-002, TEL-003, NET-002, SYS-003, TST-001, TST-002. Eight route responses are collected: telemetry created/identical/conflict, event persisted/identical/conflict, missing Bearer, and simulated database connectivity fault. Eight Laravel test methods accompany the capture.

The **origin_verified** field in the captured receipt is deliberately **false**. The C99 test only enables an explicitly simulated, hypothetical external verification flag after proving an unverified response cannot advance the ACK cursor. This is NOT TLS validation, JSON parsing in ESP32 firmware, actual network transport, verified provenance, durable ACK, DB persistence, or a vessel safety certification. On any malformed receipt, skip, DB attempt, unexpected status, cursor mismatch, unsafe state, or test failure: fail closed with no stage/commit.

All data generated are synthetic. The runner explicitly pins base Git HEAD/tree, 11 anchors, two local untracked firmware paths, tests, exact-stage, local commit and postcommit. No migrations, no DB writes, no push. Formal SIM/SUP and total system readiness remain OPEN.
