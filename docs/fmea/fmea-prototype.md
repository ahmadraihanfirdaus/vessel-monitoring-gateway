# Preliminary FMEA — Software Prototype / Simulation Boundary

**Document class:** Development-stage qualitative failure-mode register; **NOT APPROVED** for operational vessel safety, installation, or certification.

**Related requirements:** SYS-002, SYS-003, SAF-001..006, ALM-001..003, ENG-002/003, NAV-003/004, NET-001/002, TEL-001..003, SEC-002. This register does not alter the LOCKED requirements or create acceptance thresholds.

The preliminary FMEA identifies plausible functional failure modes to guide tests. Likelihood, severity rankings, numerical detection limits, hardware protection ratings and residual-risk acceptability are **TBD**, pending appropriate design review and verifiable context. The proposed mitigations are *not* considered implemented or effective until linked to executed evidence.

| ID | Failure mode | Potential effect | Planned detection | Intended containment / test link | Evidence status |
|---|---|---|---|---|---|
| FMEA-01 | Hatch input stuck or missing | Unsafe inference about a configured virtual-start prerequisite | UNKNOWN/invalid/missing quality, simulated plausibility/debounce | Configurable demo fail-safe, SIM-002/011 | NOT_RUN |
| FMEA-02 | Vapor-surrogate channel missing or faulty | Missing data misreported NORMAL | Quality/state distinction, fault diagnostics | Do not treat missing as safe; SIM-003/004 | NOT_RUN |
| FMEA-03 | High-water surrogate indication | Missed monitoring event or invented start interlock | Water state + quality | Configurable ALERT_ONLY behavior; SIM-005 | NOT_RUN |
| FMEA-04 | Temperature/bench power out of range | False normal display or wrong interpretation | Finite/current-valid/range checks | Invalid state retained, no operational vessel inference; SIM-006, SUP-010 | NOT_RUN |
| FMEA-05 | Navigation checksum corruption or stream loss | Old/faulty GPS values shown live | Checksum validation, age/quality | Reject invalid input and age last valid; SIM-008/009 | NOT_RUN |
| FMEA-06 | One simulated engine communication failure | Other engine states may be obscured or falsely inferred | Per-engine quality/fault | Isolate failure; SUP-005/006, SIM-012 | NOT_RUN |
| FMEA-07 | Backend disconnected/network stalled | Local monitoring or journaling stops | Bounded timeout, offline health and event counter | Local independence, bounded queue, SIM-010/012/013 | NOT_RUN |
| FMEA-08 | ESP32 reset or loss of journal state | Event loss or missed reboot | Boot ID and startup marker | Explicit reboot and bounded journal policy; SUP-013 | NOT_RUN |
| FMEA-09 | Duplicate or altered telemetry replay | Duplicate history or inconsistent records | Stable identity, duplicate-conflict detection | Idempotent backend/reject conflict; SIM-014 | NOT_RUN |
| FMEA-10 | Missing/bad API authentication | Unauthorized telemetry accepted | Server validation | Authentication and reject behavior; SIM-015 | NOT_RUN |
| FMEA-11 | Acknowledgement accidentally clears live alarm | Safety indication suppressed | Separate condition vs acknowledgement | State-machine transition tests; SUP-004 | NOT_RUN |
| FMEA-12 | Numeric invalid/NaN or stale data treated as current | False measurement confidence | Quality, provenance, finite and freshness checks | Preserve quality and non-numeric absent semantics; SUP-002/012 | NOT_RUN |

## Required follow-up before closing the FMEA

1. Define failure ownership, observable output, detectability, and test fixture for each row.
2. Review common-cause failures (e.g., shared sensor bus): SIM-011 alone tests an isolated bad channel, not full-bus outage.
3. Add fault-injection observations and residual-risk reviews after implementing each module; never infer their success from unit tests of adjacent components.
4. Distinguish simulated, controlled bench, and future physical interfaces. **No physical integration is authorized.**
5. Obtain technical review of any numerical severity/probability approach before using it. None is introduced here.

**Disposition:** Preliminary FMEA document PRESENT; hazard-analysis acceptance and operational effectiveness NOT_VERIFIED.

## Local storage observations, 2026-10-25

FMEA-07/08 now have additional scoped software evidence in the
[NVS continuation](../../evidence/test-results/offline-nvs-summary-20261025.md):
actual NVS worker source compiles, and native transaction fault injection checks
selected-slot preservation, uncertain commits, corrupt/ambiguous recovery and
explicit journal-full behavior. These observations do not close either FMEA row
or execute its formal protocol. Critical capacity exhaustion refuses new records
explicitly; degraded recovery may restore older data. Flash/cache effects on
sampling, physical power cuts, wear, confidential provisioning and residual-risk
acceptance remain unverified. No likelihood/severity threshold is assigned.

## Continuous simulation observations, 2026-10-25

The continuous coordinator has native evidence that journal-full rejection does
not roll back observation/local indication, preserves all eight old events and
counts rejected attempts. This is explicitly incomplete retention; no FMEA row
is closed. SDK queue submission compiles, but flash/cache blocking, actual outage
timing, power loss and residual-risk acceptance remain unverified. Physical
controls are absent. See the continuous integration summary for the scoped tests.
