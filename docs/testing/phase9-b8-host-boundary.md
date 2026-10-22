# Phase 9 Batch 8 — bounded host safety / replay admission

Five scoped contexts: SYS-003 local alarm latch; NET-002 correlated ACK; TEL-003 ordered cursor; SEC-002 synthetic time-bound attestation; TST-001 combined integration.

**Host-only simulation:** C99 headers, standalone PHP support, deterministic injected inputs. No physical sensing, ESP32 build, actual actuator channel, durable event journal, real TLS, signed authentication, HTTP endpoint, MySQL access or Laravel route wiring. All five requirements remain FORMAL OPEN.

A verified reply alone cannot advance replay while the local alarm is latched. The host PHP gate refuses expired/future/scope-invalid injected claims, out-of-order/gapped sequences, and conflicting duplicate payloads. This is a deterministic software contract only; it is not end-to-end deployment evidence.
