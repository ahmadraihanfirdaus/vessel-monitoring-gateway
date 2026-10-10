# 06 - Prototype Bill of Materials and TBD Register

**Project:** Vessel Monitoring Gateway

**Document Status:** Engineering Design Reference

**Implementation Status:** PLANNED / NOT_IMPLEMENTED

**Verification Status:** NOT_RUN

## 1. Purpose

This document identifies the selected prototype hardware, development references, and unresolved physical interface requirements for the Vessel Monitoring Gateway.

The component list follows the approved internal engineering baseline.

A component marked **LOCKED** represents a selected engineering specification. It does not indicate that the component has been purchased, assembled, integrated, or successfully tested.

Components marked **FUTURE** or **TBD** remain outside the implemented physical integration scope until sufficient technical information is available.

## 2. Prototype Bill of Materials

| Function | Brand | Model / Code | Technical Description | Baseline Status | Intended Use |
|---|---|---|---|---|---|
| Edge gateway | Espressif | ESP32-DevKitC V4 | ESP32-WROOM-32E variant | LOCKED - prototype | Main microcontroller for prototype edge processing, USB development, and Wi-Fi demonstration; not marine-qualified equipment. |
| Door/Hatch sensor | Adafruit | Product ID 375 | Magnetic contact switch | LOCKED - bench | Open/closed input for simulated ventilation hatch or access-state monitoring. |
| Fuel vapor surrogate | Winsen | MQ-2 | Semiconductor flammable gas/smoke sensor | LOCKED - bench only | Demonstration of gas-state and sensor-fault handling; not a certified marine vapor detector. |
| Bilge/high-water surrogate | Adafruit | Product ID 4965 | Water detection sensor | LOCKED - bench only | Controlled wet/dry high-water simulation; physical marine sensor selection remains TBD. |
| Compartment temperature | Analog Devices | DS18B20 | 1-Wire digital thermometer | LOCKED - bench | Prototype temperature acquisition; marine probe and installation requirements remain TBD. |
| Attitude / motion | Adafruit | Product ID 3886 | MPU-6050 breakout | LOCKED - simulation/bench | Prototype roll and pitch measurement; not a certified vessel stability assessment. |
| Vibration / shock | Adafruit / Analog Devices | Product ID 1231 / ADXL345 | Three-axis accelerometer breakout | LOCKED - bench | Demonstration vibration/shock indicator; no validated machinery diagnosis claim. |
| Power monitoring | Adafruit / Texas Instruments | Product ID 904 / INA219 | High-side voltage/current measurement breakout | LOCKED - bench only | Safe low-power circuit measurement; excludes propulsion battery-current measurement. |
| Navigation reference | Furuno | GP-39 | GPS navigator / NMEA development reference | LOCKED as reference only | Reference for developing and testing NMEA-style simulation and parser behavior; no hardware installation is claimed. |
| Outboard propulsion | Yamaha | TBD | Software engine-provider abstraction; four-engine demonstration profile | SIMULATION + FUTURE | Configurable N-engine simulation; future physical model, protocol, and interface remain unverified. |
| Radar | Furuno | TBD | Future interface placeholder | FUTURE | Provider abstraction only; no radar hardware installation, data acquisition, or operational integration is claimed. |
| Local alarm | Generic bench | LED + piezo buzzer | Three status LEDs and buzzer | LOCKED - bench | Prototype local alert output independent of backend availability. |
| Start request input | Generic bench | Momentary pushbutton | Virtual start-request input | LOCKED - bench | Exercises configurable pre-start safety policies; never controls a physical engine starter. |
| Ship power interface | TBD marine design | TBD | Potential 12/24 V input design requiring fusing, protection, DC/DC conversion, and isolation | FUTURE | Requires separately verified power architecture and electrical design; no physical power connection is authorized. |
| NMEA physical receiver | TBD industrial/marine interface | TBD | Protected/isolated RS-422/NMEA 0183 receiver | FUTURE | Physical interface concept only; direct connection of NMEA electrical lines to ESP32 GPIO is prohibited. |

## 3. Hardware Status Interpretation

The baseline statuses have the following meanings:

| Status | Interpretation |
|---|---|
| LOCKED - prototype | Selected development hardware specification; changes require engineering review. |
| LOCKED - bench | Selected hardware for controlled laboratory demonstrations. |
| LOCKED - bench only | Laboratory surrogate; not equivalent to approved operational equipment. |
| LOCKED - simulation/bench | Selected for software simulation or controlled laboratory use. |
| LOCKED as reference only | Reference model for interface or protocol development, not evidence of installation. |
| SIMULATION + FUTURE | Software functionality planned first; physical interface remains unresolved. |
| FUTURE | Reserved for separately reviewed development outside the current prototype implementation. |
| TBD | Technical information has not been verified and must not be assumed. |

The hardware list represents engineering selections, not an inventory of completed assemblies.

### 3.1 Manufacturer-Referenced Bench Interface Cautions

The notes below are **planning checks**, not approved wiring instructions, completed electrical validation, or additions to the LOCKED component list. Pin assignments, power distribution, interface protection, and test evidence still require separate review before any laboratory assembly.

| Selected Reference | Planning Caution | Verification Boundary |
|---|---|---|
| ESP32-DevKitC V4 / ESP32-WROOM-32E | ESP32 GPIO uses 3.3 V logic. External signal voltages must be checked against Espressif GPIO limits; a 5 V sensor output must not be wired directly to an unprotected ESP32 GPIO. | No pin mapping, protection circuit, or electrical compatibility test has been approved or executed. |
| Winsen MQ-2 | The manufacturer's standard circuit specifies a 5 V heater and 5 V loop supply. Power, heating, signal conditioning, and interface protection must be reviewed before laboratory connection. | Bench gas-state surrogate only; it does not establish a fuel-specific detector, safe-atmosphere decision, or certified alarm. |
| Adafruit Product ID 4965 | This is a wet/dry water-detection breakout, not a calibrated water-depth or marine high-water instrument. Output level depends on the supply and interface. | The proposed high-water condition remains a controlled demonstration event, not a measured vessel water level. |
| Adafruit Product ID 375 | The magnetic contact sensor uses a normally-open reed switch. Open/closed interpretation depends on the selected magnet placement and input configuration. | No physical hatch position, installation, or fail-safe behavior has been verified. |
| Adafruit Product ID 3886 / Product ID 1231 | Inertial and acceleration readings require defined processing, reference frames, and validation before interpreting tilt or vibration indicators. | No vessel stability assessment or machinery fault diagnosis is claimed. |
| Adafruit Product ID 904 / INA219 | The listed breakout is intended for limited low-power DC monitoring; manufacturer ratings and the selected test circuit must be checked before any bench measurement. | No propulsion current measurement or approval for connection to vessel electrical systems is implied. |
| DS18B20 | The sensor uses a 1-Wire interface; its supply and data pull-up must be designed for GPIO-compatible operation. | No probe enclosure, calibration, marine placement, or installed performance is claimed. |

This document is a **prototype selection and unresolved-interface register**, not a procurement-ready parts list. Quantities, pricing, detailed pin assignments, power budget, calibration methods, and evidence of acquisition or assembly are not established here.

### 3.2 Manufacturer Documentation References

These links are provided for component identification and future bench-level design review only. They do not demonstrate that any selected hardware has been purchased or tested.

- [Espressif ESP32-DevKitC V4 user guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) and [Espressif GPIO voltage guidance](https://docs.espressif.com/projects/esp-faq/en/latest/hardware-related/hardware-design.html)
- [Winsen MQ-2 manufacturer manual](https://www.winsen-sensor.com/d/files/newpdf/mq-2-%28ver1_6%29---manual.pdf)
- Adafruit product pages: [375 — magnetic contact switch](https://www.adafruit.com/product/375), [4965 — water detection](https://www.adafruit.com/product/4965), [3886 — MPU-6050](https://www.adafruit.com/product/3886), [1231 — ADXL345](https://www.adafruit.com/product/1231), and [904 — INA219](https://www.adafruit.com/product/904)
- [Analog Devices DS18B20 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ds18b20.pdf)
- [Furuno GP-39 manufacturer product reference](https://www.furuno.com/en/products/chartplotter/gp-39/index.html)

## 4. Unresolved Technical Information

The following information remains subject to future technical verification.

| ID | Technical Area | Unresolved Information | Current Treatment |
|---|---|---|---|
| TBD-01 | Physical platform | Asset-specific identification and structural configuration | Internal verification only if separately authorized; no specific identity is included in public documentation. |
| TBD-02 | Propulsion interface | Exact Yamaha model information, physical engine quantity, communication system, and diagnostic interface | Simulated N-engine abstraction; four-engine development profile. |
| TBD-03 | Navigation and equipment interfaces | Exact GPS, radar, echo-sounder models and associated physical connections | NMEA development simulator and unimplemented provider placeholders. |
| TBD-04 | Ventilation/access monitoring | Physical access-point selection, operating procedure, and verified pre-start conditions | Configurable demonstration safety-policy rules. |
| TBD-05 | Fuel and ventilation systems | Fuel arrangement, ventilation characteristics, and appropriate detector interfaces | MQ-2 bench surrogate; no operational fuel-system assessment. |
| TBD-06 | Electrical power | Physical supply voltage, protection, isolation, grounding, and acceptable interface points | Safe low-power laboratory measurements only. |
| TBD-07 | Water, fire, and smoke monitoring | Suitable physical sensing equipment and available data interfaces | Laboratory surrogate and simulated fault channels. |
| TBD-08 | Information disclosure | Authorization and classification of any future real-world engineering or operational data | Synthetic public data only; operational details remain outside the repository. |

These items document open engineering questions. They do not establish the existence, configuration, or condition of equipment on any specific vessel.

## 5. Prototype and Physical Integration Boundaries

The current development scope includes simulation and controlled laboratory prototype hardware.

The following restrictions apply:

- No direct connection to operational vessel electrical or communication circuits.
- No physical engine starter, ignition, steering, radar, or radio control.
- No unverified device interface shall be represented as implemented.
- No laboratory surrogate shall be described as certified marine safety equipment.
- No real-world measurements shall be inferred from simulated data.
- No future interface shall be assigned an invented model, protocol, or installation status.
- Physical integration requires separate technical verification, electrical protection, isolation, and authorization.

The `physical` source classification may exist in the software contract, but its definition does not imply that physical integration has been completed.

## 6. Brand and Reference Disclaimer

Manufacturer and product names are included solely to identify selected prototype components or development references.

Their inclusion does not imply:

- Manufacturer endorsement or partnership.
- Integration with equipment owned by a third party.
- Installation on an operational vessel.
- Successful hardware testing or field verification.
- Certification, type approval, or regulatory acceptance.

## 7. Engineering Change Control

Changes to the selected hardware, interface contracts, or technical scope shall follow the approved engineering change-control process.

In particular:

1. LOCKED hardware shall not be substituted without documented approval.
2. FUTURE interfaces shall remain unimplemented until separately authorized.
3. TBD fields shall not be populated using assumptions.
4. Simulation evidence shall remain separate from bench-test evidence.
5. Test outcomes shall not be marked PASS without execution evidence.
6. Internal reference materials shall remain separate from public documentation.

## 8. Current Verification Status

The Bill of Materials and TBD register are available for design and development planning.

Hardware procurement, assembly, driver implementation, laboratory verification, and physical integration have not been established as completed by this document.

**Implementation Status:** NOT_IMPLEMENTED

**Verification Status:** NOT_RUN

**Physical Integration:** NOT_AUTHORIZED

**Final Verification Approval:** NOT_APPROVED
