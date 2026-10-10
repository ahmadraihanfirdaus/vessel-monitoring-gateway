# 02 - Standards Applicability Matrix

**Project:** Vessel Monitoring Gateway

**Document Status:** Engineering Reference and Design Planning

**Implementation Status:** NOT_IMPLEMENTED

**Standards Conformity Assessment:** NOT_ASSESSED

**Verification Status:** NOT_RUN

## 1. Purpose

This document identifies technical standards, industry rules, and guidance relevant to the planned Vessel Monitoring Gateway prototype.

The references provide engineering context for architecture, interface separation, monitoring behavior, data quality, alerts, electrical protection, and cybersecurity.

Their inclusion does not establish compliance, certification, class approval, type approval, or independent verification.

The project remains a development prototype. No operational installation or field validation is claimed.

## 2. Applicability Principles

The following principles govern the use of standards references:

- References are used for engineering research and design planning.
- Reference relevance does not establish compliance.
- Design alignment describes an intended engineering approach, not a completed conformity assessment.
- Requirements must be verified against the applicable source documents before any formal conformity assessment.
- Software simulation and laboratory testing must not be presented as marine certification testing.
- Applicability to any physical installation requires separate technical review.
- No specific vessel classification, approval, or operational configuration is assumed.
- Reference identifiers and editions are retained from the internal engineering baseline. Selected publisher metadata has been independently checked as recorded in Section 7.1; complete applicability and clause-level assessment remain pending.

## 3. Standards Applicability Matrix

| Reference | Engineering Relevance | Baseline Designation | Intended Engineering Use |
|---|---|---|---|
| BKI Rules for High Speed Craft / related BKI small craft rules | Classification and design terminology for applicable craft categories | REFERENCE ONLY | Engineering terminology and general design context. Applicability to any specific craft or contract remains unverified. |
| IEC 60092-504:2026 | Shipboard automation, control, monitoring, alert, safety, and protection concepts | HIGH RELEVANCE / PARTIAL ALIGNMENT | Planned separation of monitoring functions, diagnostics, local alerts, and resilience to backend failure. No conformity assessment has been performed. |
| IEC 61162-1:2024 | Maritime digital interface concepts, including single-talker and multiple-listener communication | HIGH RELEVANCE / DEVELOPMENT ALIGNMENT | Development of NMEA-style parsing, simulation, message validation, data quality, and data-age handling. Physical interface implementation remains FUTURE. |
| NMEA 0183 | Maritime serial data exchange | HIGH RELEVANCE / DEVELOPMENT | Development of simulated navigation sentences and parsing behavior. Furuno GP-39 is a development reference only; no device installation is claimed. |
| IEC 60945 / IEC 60533 | Environmental and electromagnetic compatibility considerations for marine equipment | DESIGN CONSIDERATION | Future engineering assessment topics include temperature, humidity, vibration, shock, corrosion, ingress protection, and electromagnetic compatibility. No qualification testing is claimed. |
| IEC 62923-1 / IMO BAM principles | Bridge alert management terminology and behavior | CONCEPT ALIGNMENT | Planned alert priorities, states, acknowledgement, and clearing behavior. The prototype is not represented as an approved Bridge Alert Management system. |
| ISO 13297:2020 | Electrical installation concepts for small craft | REFERENCE | General low-voltage protection and power architecture considerations. Physical electrical interfaces remain TBD and are outside the current implementation. |
| ISO 9094:2022 | Fire protection considerations for small craft | DOMAIN REFERENCE | General fire, smoke, and fuel-vapor monitoring context. Laboratory sensor surrogates are not represented as approved protection equipment. |
| ISO 12217-1:2022 | Stability and buoyancy assessment concepts for applicable non-sailing craft | CONTEXT ONLY | Clarifies the distinction between prototype roll/pitch monitoring and formal vessel stability assessment. No stability certification is claimed. |
| IMO Maritime Cyber Risk guidance | Cyber-risk management concepts for maritime technology | HIGH RELEVANCE / PARTIAL ALIGNMENT | Planned authentication, secret management, auditability, interface isolation, and protection of sensitive data. No formal cyber-risk conformity assessment is claimed. |

## 4. Interpretation of Baseline Designations

The designations in this matrix describe how each reference is considered during engineering planning.

They are not implementation or certification results.

| Designation | Interpretation |
|---|---|
| REFERENCE ONLY | Provides terminology or contextual information; no direct conformity claim. |
| HIGH RELEVANCE / PARTIAL ALIGNMENT | Selected concepts are considered in the planned design; the extent of actual alignment has not been assessed. |
| HIGH RELEVANCE / DEVELOPMENT ALIGNMENT | Provides guidance for development activities and interface behavior, not formal verification. |
| HIGH RELEVANCE / DEVELOPMENT | Reference used to inform prototype software development. |
| DESIGN CONSIDERATION | Identifies engineering topics requiring future investigation or qualification. |
| CONCEPT ALIGNMENT | Selected functional concepts inform the design; no approval or certification is implied. |
| REFERENCE | Provides general technical context for design planning. |
| DOMAIN REFERENCE | Provides background on a specific engineering risk or application domain. |
| CONTEXT ONLY | Used to explain boundaries and prevent unsupported technical claims. |

## 5. Verification and Evidence Boundaries

The repository must distinguish between the following activities:

**Design reference review:** Identifying concepts that may inform system requirements and architecture.

**Functional software verification:** Executing unit, integration, simulation, and contract tests against the prototype's own requirements.

**Laboratory prototype verification:** Evaluating selected hardware in a controlled bench environment.

**Formal standards conformity assessment:** A separate activity requiring established applicability, appropriate test methods, supporting documentation, and qualified assessment where required.

Passing a prototype simulation or unit test does not constitute compliance with a marine standard.

Formal conformity assessment is not included in the current implementation scope.

## 6. Physical Interface Limitations

The current architecture specifies simulation and controlled laboratory interfaces.

Future physical interfaces require independently established technical information and applicable engineering review.

The following restrictions remain in effect:

- Do not connect operational power or communication lines directly to ESP32 GPIO.
- Do not treat bench sensor surrogates as approved marine safety equipment.
- Do not present simulated navigation data as operational vessel data.
- Do not claim physical equipment integration without verified evidence.
- Do not claim environmental, electromagnetic, stability, or safety qualification from ordinary prototype testing.
- Keep unresolved electrical and device-specific interface requirements designated TBD or FUTURE.

No physical vessel integration is authorized by this document.

## 7. Publication and Reference Control

Public documentation shall not identify an operational asset or imply affiliation with any external organization.

Names of standards bodies, manufacturers, and products are used strictly as technical references.

This document does not reproduce the normative text of the referenced standards.

Before using any listed standard for formal engineering acceptance, the responsible reviewer must independently verify its correct identifier, edition, applicability, and applicable requirements against an authoritative source.

Changes to the approved reference list or engineering scope require documented review.

### 7.1 Publisher Metadata Verification Register

**Metadata check date:** 2026-10-10

The following entries record a limited check of **publisher-page identifiers, editions, and publication status**. These checks do **not** verify full normative clauses, establish applicability to any particular craft, or demonstrate standards conformity. The baseline matrix in Section 3 remains unchanged.

| Baseline Reference | Publisher metadata check | Official publisher record | Status / Limit |
|---|---|---|---|
| IEC 60092-504:2026 | Edition 5.0, published 2026-04 | https://webstore.iec.ch/en/publication/68493 | IDENTIFIER_AND_EDITION_CHECKED; applicability and conformity NOT_ASSESSED |
| IEC 61162-1:2024 | Edition 6.0, published 2024-04 | https://webstore.iec.ch/en/publication/72729 | IDENTIFIER_AND_EDITION_CHECKED; physical-interface compliance NOT_ASSESSED |
| ISO 13297:2020 | Edition 5, published 2020-12; publisher lists Amendment 1:2022 | https://www.iso.org/standard/69551.html | IDENTIFIER_AND_EDITION_CHECKED; amendment relevance and scope review PENDING |
| ISO 13297:2020/Amd 1:2022 | Publisher lists an amendment to ISO 13297:2020, published 2022-09 | https://www.iso.org/standard/83643.html | METADATA_ONLY; amendment is noted for future review, not added as a separate baseline designation |
| ISO 9094:2022 | Edition 2, published 2022-11 | https://www.iso.org/standard/78242.html | IDENTIFIER_AND_EDITION_CHECKED; applicability and conformity NOT_ASSESSED |
| ISO 12217-1:2022 | Edition 4, published 2022-12 | https://www.iso.org/standard/79072.html | IDENTIFIER_AND_EDITION_CHECKED; applicability and conformity NOT_ASSESSED |

The remaining composite or non-edition-specific references in Section 3, including BKI rules, NMEA 0183, IEC 60945 / IEC 60533, IEC 62923-1 / IMO BAM principles, and IMO Maritime Cyber Risk guidance, still require independent source, edition, and applicability confirmation. They are retained as **planning references only**, without implying that a particular rulebook, device, or standard has been formally applied or verified.

No publisher metadata check in this section represents access to the complete licensed text of a standard or permission to reproduce its normative content.

## 8. Current Assessment Status

The matrix is available for planning and engineering reference.

No complete standards applicability study, clause-by-clause conformity assessment, or formal qualification program has been executed.

**Standards Conformity Assessment:** NOT_ASSESSED

**Implementation Status:** NOT_IMPLEMENTED

**Verification Status:** NOT_RUN

**Certification / Type Approval:** NOT_CLAIMED

**Physical Integration:** NOT_AUTHORIZED

**Final Verification Approval:** NOT_APPROVED
