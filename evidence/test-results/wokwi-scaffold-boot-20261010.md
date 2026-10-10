# Wokwi ESP32 Scaffold Runtime Evidence

## 1. Identification

- Date: 2026-10-10
- Project: Integrated Vessel Monitoring & Diagnostic Gateway
- Result: SCAFFOLD_WOKWI_BOOT_PASSED
- Environment: Wokwi Simulator, ESP32-DevKitC V4
- Framework: ESP-IDF 6.1.0 (reported runtime)
- Console: UART0, 115200 baud
- Simulated flash: 2 MiB
- Evidence source: Operator-provided Wokwi Terminal output

## 2. Observed Runtime Output

The following messages were observed in Wokwi Terminal:

    I (295) boot: Loaded app from partition at offset 0x10000
    I (237) main_task: Calling app_main()
    Development scaffold only; monitoring and alarms are not implemented.
    I (247) main_task: Returned from app_main()

The output confirms that the ESP32 virtual machine loaded the application and invoked `app_main()`.

## 3. Artifact Identification

- Firmware ELF SHA-256: 9cb3472c75de5542a731a1a12cb157f1fc211372788c71147d78f43db2d1ccbd
- Merged image SHA-256: 2e6fc038e75c0c9ef9db999ac3f28b2f91943099a3b3b41a07f08e61741efc08
- Build-reported application version: 56e8c53-dirty
- Subsequent local development commit: 7960ad9

The firmware image was built before commit 7960ad9. This evidence does not claim that the image was generated from that commit.

## 4. Verification Scope

**Verified:**
- Virtual ESP32 boot sequence
- Application loading
- UART0 serial output
- Execution and return of `app_main()`

**Not verified:**
- Sensor acquisition and data quality
- Alarm and safety-policy operation
- Engine and navigation simulation
- Backend telemetry integration
- Functional SIM/SUP test scenarios
- Physical ESP32 or vessel integration

## 5. Engineering Status

- Scaffold simulation: PASSED
- Functional implementation: NOT_IMPLEMENTED
- Functional verification: NOT_RUN
- Physical integration: NOT_AUTHORIZED
- Safety approval: NOT_GRANTED

This document records operator-provided simulation evidence. It is not an independently reproduced test report or physical safety certification.
