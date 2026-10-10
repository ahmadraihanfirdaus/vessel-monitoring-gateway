# Firmware Scaffold Build Evidence

## Identification

- Evidence ID: EVD-FW-SCAFFOLD-20261010-01
- Date recorded: 2026-10-10
- Project: Integrated Vessel Monitoring & Diagnostic Gateway
- Development branch: develop
- Baseline HEAD: 56e8c53dc4bd8aa27059f8dece9c290f3e123ed0
- Evidence status: SCAFFOLD_BUILD_PASSED
- Scope: Software scaffold compilation only

This evidence summarizes results from the development terminal
output. It is not a signed laboratory report or an independent
reproduction of the build.

## Build Configuration

- PlatformIO Core: 6.2.0
- Espressif32 platform: 7.1.3
- Framework: ESP-IDF
- PlatformIO framework package: framework-espidf 4.60100.0
- Environment: esp32dev_espidf
- Board definition: esp32dev (provisional)
- Locked hardware: ESP32-DevKitC V4 / ESP32-WROOM-32E
- Build command: platformio run --project-dir firmware --environment esp32dev_espidf

The development build included local firmware files not yet
committed to the baseline HEAD. The commit alone therefore
does not reproduce this build.

## Build Result

- PlatformIO result: SUCCESS
- Exit code: 0
- Reported build duration: 173.43 seconds
- Firmware ELF: generated
- Firmware BIN: generated
- RAM usage: 13,612 / 327,680 bytes (4.2%)
- Reported application flash usage: 141,917 / 1,048,576 bytes (13.5%)

The reported application size limit does not establish
the physical module flash capacity.

## Artifact Identification

### firmware.elf

- Path: firmware/.pio/build/esp32dev_espidf/firmware.elf
- Size: 2,844,784 bytes
- SHA-256: 9cb3472c75de5542a731a1a12cb157f1fc211372788c71147d78f43db2d1ccbd

### firmware.bin

- Path: firmware/.pio/build/esp32dev_espidf/firmware.bin
- Size: 142,352 bytes
- SHA-256: bdcaa53952345ede89bdf4a3956f468d5ff2a9200dc6912884dbd027361d4c85

Both artifacts are generated locally and ignored by Git.

## Verification Boundary

Verified:

- The development scaffold compiled successfully.
- The ELF and BIN files were generated.
- Basic ELF and ESP32 image signatures were checked.
- Artifact sizes and SHA-256 hashes were rechecked.
- Git protection for generated artifacts was verified.

Not verified:

- Execution on physical ESP32 hardware.
- Exact physical flash capacity or GPIO assignments.
- Sensor acquisition and data quality behavior.
- Alarm and local safety-policy operation.
- Telemetry ingestion and backend integration.
- Wokwi simulation or end-to-end functionality.
- Functional SIM/SUP test outcomes.

## Engineering Status

- Firmware functional implementation: NOT_IMPLEMENTED
- Functional verification: NOT_RUN
- Physical integration: NOT_AUTHORIZED
- Safety approval: NOT_GRANTED

SCAFFOLD_BUILD_PASSED records build readiness only.
It does not replace requirements traceability,
functional testing, or engineering approval.
