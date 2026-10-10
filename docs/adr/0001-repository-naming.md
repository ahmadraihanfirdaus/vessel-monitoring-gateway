# ADR-0001: Repository Naming

- **Status:** Accepted
- **Decision Date:** 2026-10-09
- **Public Documentation Revision:** 2026-10-10
- **Decision Type:** Repository Identity
- **Scope Impact:** None

## 1. Context

The project requires a consistent repository identity that communicates its primary engineering purpose: integrated monitoring, diagnostics, edge processing, and telemetry.

The repository name must be suitable for public engineering documentation without implying installation on an operational vessel, affiliation with an external organization, or certification of marine equipment.

Technical requirements are governed by a versioned internal engineering baseline. The internal baseline is maintained separately and is not distributed as part of the public repository.

## 2. Decision

The selected repository name is:

`vessel-monitoring-gateway`

The public project title is:

**Integrated Vessel Monitoring & Diagnostic Gateway**

The local development directory follows the same repository naming convention.

This naming decision is accepted for development and preparation of public documentation. It does not authorize repository publication.

## 3. Rationale

The selected name:

- Describes the monitoring and diagnostic gateway function.
- Supports a modular embedded systems and IoT architecture.
- Remains applicable to different vessel monitoring use cases.
- Provides a neutral identity for engineering documentation and portfolio presentation.
- Does not imply deployment, external affiliation, or regulatory approval.
- Does not modify the approved technical scope.

The repository identity is independent of any specific operational asset.

## 4. Engineering Constraints

This decision does not modify:

- LOCKED prototype hardware components.
- Functional and nonfunctional system requirements.
- System architecture and interface contracts.
- Configurable safety-policy requirements.
- The N-engine model and four-engine simulation profile.
- NMEA 0183 development and verification requirements.
- Telemetry schemas and data quality contracts.
- Simulation, bench_test, and physical source-mode definitions.
- FUTURE physical integration boundaries.
- Unresolved TBD items.
- Verification requirements and evidence criteria.

No operational deployment or physical vessel integration is authorized by this decision.

## 5. Public Documentation Boundaries

Public documentation shall use neutral technical terminology.

It shall not imply:

- Affiliation with an external organization.
- Ownership of or authorization to access an operational vessel.
- Installation of prototype hardware on operational equipment.
- Completion of physical integration or field verification.
- Marine certification or regulatory approval.
- Successful implementation or testing without supporting evidence.

Public demonstrations shall use synthetic data or separately authorized controlled laboratory data.

The internal engineering baseline remains the authoritative reference for scope control.

## 6. Consequences

### Positive Consequences

- Consistent project and repository identification.
- Clearer presentation of engineering objectives.
- Separation between public documentation and internal reference materials.
- Reduced risk of unsupported operational or affiliation claims.
- Preservation of the existing technical baseline.

### Trade-offs

- The public project description intentionally excludes specific operational context.
- Internal reference materials are not available to public repository readers.
- Public documentation must provide sufficient technical context independently.

## 7. Required Actions

- Use `vessel-monitoring-gateway` consistently as the repository identifier.
- Use **Integrated Vessel Monitoring & Diagnostic Gateway** as the public presentation title.
- Preserve internal engineering baseline files without unauthorized changes.
- Maintain neutral descriptions across public documentation.
- Review repository content for sensitive identifiers before publication.
- Maintain requirement, implementation, test, and evidence traceability.
- Record future changes affecting scope through the applicable engineering change-control process.

## 8. Verification Criteria

This decision is considered correctly applied when:

1. The repository directory uses the selected identifier.
2. Public project documentation uses the approved presentation title.
3. No specific operational asset or external affiliation is asserted.
4. The internal engineering baseline remains unchanged.
5. Technical requirements, hardware constraints, and interface contracts remain intact.
6. Public documentation does not claim unverified implementation, deployment, or certification.

## 9. References

- Internal Engineering Baseline — maintained outside the public repository.
- `README.md`
- `docs/github-repository-plan.md`
- `requirements/system-requirements.md`

---

**Decision Status:** Accepted

**Technical Scope Change:** None

**Operational Deployment Claim:** None