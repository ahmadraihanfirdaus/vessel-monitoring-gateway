
# 03 - System Architecture and Interface Control Document

**Project:** Vessel Monitoring Gateway

**Document status:** Engineering Design Baseline

**Implementation status:** PLANNED / NOT_IMPLEMENTED

**Verification status:** NOT_RUN

## 1. Architecture Overview

The Vessel Monitoring Gateway is designed as a modular
engineering prototype for sensor monitoring, diagnostic
processing, simulated propulsion, navigation data handling,
local safety-policy evaluation, and telemetry.

The architecture separates data sources, provider interfaces,
edge processing, backend services, and monitoring functions.

The diagram represents the planned system architecture.
It does not indicate installation or validation on an
operational vessel.

```text
SIMULATION / CONTROLLED BENCH ENVIRONMENT

 Safety/Hull          Propulsion       Motion/Power       Navigation/Equipment
 - Hatch/Door         - Engine 1..N    - Roll/Pitch       - NMEA source
 - Fuel Vapor         - RPM            - Vibration        - GPS health
 - Bilge              - Temperature    - Voltage/Current  - Radar provider TBD
 - Compartment Temp   - Runtime        - Device health    - Echo/Radio TBD
          \                 |                 |                    /
           \                |                 |                   /
            +--------- PROVIDER / INTERFACE LAYER --------------+
                                     |
                                     v
                            ESP32 EDGE GATEWAY
                   acquisition -> validation -> quality
                       -> safety policy -> alarm manager
                      -> event journal -> offline buffer
                                     |
                                     v
                       NON-SAFETY UPLINK (HTTPS)
                                     |
                                     v
                            LARAVEL API -> MYSQL
                                     |
                                     v
                       MONITORING / HISTORY / EVIDENCE
```

## 2. Architecture Boundaries

### 2.1 Data Source Classification

Every monitoring channel shall identify its source mode:

- `simulation`: Software-generated development data.
- `bench_test`: Measurements from controlled prototype hardware.
- `physical`: Reserved for future separately verified interfaces.

Defining the `physical` source mode does not imply that
physical integration has been implemented or authorized.

### 2.2 Local Processing

The planned edge gateway is responsible for:

- Data acquisition and validation.
- Per-channel data quality assessment.
- Configurable local safety-policy evaluation.
- Alarm, fault, and event handling.
- Local event journaling.
- Bounded offline data handling.
- Device diagnostics and communication status.

Local monitoring, alarms, and safety-policy evaluation
must remain independent of backend availability.

### 2.3 Backend Boundary

The planned Laravel backend provides:

- Authenticated telemetry ingestion.
- Payload validation.
- Telemetry and event storage.
- Device monitoring information.
- Historical data access.
- Dashboard data services.
- Verification evidence references.

The backend is not a safety-critical controller.
Loss of backend connectivity must not disable local
monitoring or local safety-policy evaluation.

### 2.4 Physical Interface Restrictions

No vessel electrical circuit or operational equipment
shall be connected directly to ESP32 GPIO.

This prohibition includes:

- Vessel 12/24 V power circuits.
- NMEA electrical interfaces.
- CAN or engine communication buses.
- Radar connections.
- Starter and ignition circuits.
- Steering or radio control circuits.

Future physical integration requires appropriate
electrical protection, isolation, transceivers,
interface validation, and separate authorization.

No operational vessel integration is claimed.

## 3. Interface Register

The following interfaces define the planned contracts
between monitoring channels and system modules.

Hardware references identify selected prototype components
or future interface placeholders. They do not represent
completed installation or successful functional testing.

| ID | Interface | Transport | Data | Engineering Notes |
|---|---|---|---|---|
| IF-01 | Door/Hatch -> ESP32 | Digital GPIO | OPEN/CLOSED + quality | Adafruit 375 bench reference; debounce and fail-state handling required. |
| IF-02 | Fuel Vapor -> ESP32 | Analog/digital surrogate | gas_state/value + quality | MQ-2 for bench demonstration only; no calibrated marine vapor measurement claim. |
| IF-03 | Bilge -> ESP32 | Digital | NORMAL/HIGH + quality | Adafruit 4965 bench surrogate; physical marine sensor remains TBD. |
| IF-04 | Temperature -> ESP32 | 1-Wire | temperature_c + quality | DS18B20 bench reference. |
| IF-05 | Attitude -> ESP32 | I2C | roll/pitch + quality | MPU-6050 simulation/bench reference; not a certified stability assessment. |
| IF-06 | Vibration -> ESP32 | I2C/SPI | accel/vibration_index + quality | ADXL345 bench reference; no machinery diagnosis claim. |
| IF-07 | Power Bench -> ESP32 | I2C | voltage/current/power + quality | INA219 for safe low-power bench monitoring; excludes real propulsion-current measurement. |
| IF-08 | NMEA Simulator -> ESP32 | UART text stream | RMC/GGA/VTG development sentences | Physical NMEA requires a protected and isolated receiver. |
| IF-09 | Engine Simulator -> Core | Software provider | N engine states | Configurable engine count; demonstration profile uses engine_count=4. |
| IF-10 | ESP32 -> Backend | HTTPS JSON | telemetry/events/device health | Non-safety-critical telemetry uplink. |
| IF-11 | Backend -> Dashboard | HTTP/JSON/Blade/JS | latest/history/events | Read-oriented monitoring and diagnostic presentation. |

## 4. Interface Implementation Principles

### 4.1 Provider Abstraction

Data acquisition shall remain separated from core
monitoring and safety-policy logic.

Provider implementations may represent simulation,
controlled bench hardware, or future verified interfaces.

Unverified physical providers shall remain placeholders
until their hardware and communication contracts are
established.

### 4.2 Data Quality

Channel data shall carry appropriate quality information.

Invalid, missing, or stale measurements must not be
silently converted into valid or safe values.

### 4.3 Propulsion Model

The propulsion model shall support a configurable number
of simulated engines.

The demonstration profile shall configure four engines.

Physical engine interfaces remain outside the implemented
scope until model and protocol information is verified.

### 4.4 Navigation Interface

NMEA 0183-style development data may be generated and
parsed for simulation and verification.

A navigation reference model does not establish that
the corresponding hardware is installed or connected.

### 4.5 Interface Change Control

Changes affecting interface identifiers, transports,
data contracts, hardware selections, or physical
integration assumptions require documented engineering
review against the approved project baseline.

Items designated TBD must remain unresolved until
supported by verified technical information.

### 4.6 ICD Completeness and Open Design Evidence

The IF-01 through IF-11 register is a **planning-level interface inventory**, not a complete executable ICD, approved wiring plan, or evidence of protocol conformance. The transport and data labels describe intended interface categories. Any parameters already governed by approved requirements remain subject to that baseline; the topics below are review checkpoints, **not new interface contracts or approvals**.

| Review Area | Open Documentation and Verification Boundary |
|---|---|
| Channel contracts (IF-01 through IF-07) | Units, value ranges, sensor-state interpretations, validity/freshness criteria, time references, and error representations require traceable implementation-level definitions and verification. No numeric thresholds or acceptance limits are introduced here. |
| Bench electrical interfaces (IF-01 through IF-08) | GPIO voltage compatibility, signal conditioning, pin mapping, supply design, and protective or isolated receivers must be reviewed against the selected hardware and the BOM cautions before bench wiring. No physical connection is approved by this register. |
| Navigation and engine sources (IF-08 and IF-09) | RMC/GGA/VTG labels and the four-engine profile describe simulated development inputs. The simulation-provider execution location and test-harness connection mode still require implementation-level clarification. These entries do not establish complete NMEA conformance, installed navigation equipment, a physical engine count, or real engine telemetry. |
| Edge-to-backend telemetry (IF-10) | HTTPS is the planned uplink transport. Payload schemas, source provenance, authentication details, event identity, retry/replay handling, and offline-buffer behavior require traceability to approved requirements and implementation evidence; none is represented as implemented. |
| Dashboard delivery (IF-11) | `HTTP/JSON/Blade/JS` describes a planning-level web presentation interface. It does not authorize an unauthenticated or publicly exposed plaintext-HTTP deployment. Access control and deployment transport protections require review against approved security requirements. |
| Local policy and alarms | Local monitoring and alarm evaluation are planned independently of backend availability. Their inclusion does not assert validated fail-safe performance, certified safety protection, or physical engine/steering/ignition actuation. |

These checkpoints identify what must be confirmed during later design and verification. They do not alter the LOCKED hardware list, existing interface IDs, specified transports, TBD classifications, or planned test outcomes.

## 5. Engineering Limitations

- This document describes a planned prototype architecture.
- No completed hardware integration is implied.
- No operational deployment is claimed.
- No external organization or asset affiliation is claimed.
- No certified marine safety or navigation capability is claimed.
- Safety-policy behavior requires implementation and verification.
- Physical interface development requires separate approval.
- Simulation evidence must remain distinguishable from bench evidence.
- Test cases shall not be marked PASS without execution evidence.

## 6. Verification Status

Architecture and interface definitions are available
for development planning.

Firmware, simulation, backend integration, and end-to-end
functional verification have not yet been completed.

Requirement-to-test mappings represent planned coverage,
not successful execution.

**Current verification status: NOT_RUN**

**Final verification approval: NOT_APPROVED**
