
# Firmware Core Types - Build and Wokwi Runtime Evidence

## Identification

- Date: 2026-10-10
- Project: Integrated Vessel Monitoring & Diagnostic Gateway
- Result: CORE_TYPES_BUILD_AND_BOOT_PASSED
- Target: ESP32 virtual / Wokwi Simulator
- Framework: ESP-IDF 6.1.0
- Source branch: develop
- Build-reported version: c9cb2fb-dirty
- Physical hardware testing: NOT_RUN

## Implemented Scope

- Added core_types.h
- Defined vg_source_mode_t
- Defined vg_data_quality_t
- Set VG_QUALITY_UNKNOWN to zero
- Added compile-time assertions in main.c
- Preserved the scaffold bootstrap message

## Build Result

- PlatformIO ESP-IDF build: PASSED
- Build duration: 84.28 seconds
- ELF SHA-256:
  1d465f595843e36f5f6f3ffc4f5e3a0b314f546c4dbb026f3de4693f14226f71
- BIN SHA-256:
  c126e9429e7ea4aa13d765fdcbb9ca368a807d0c8428f300133eb59bcbabbae4
- Merged image SHA-256:
  d8c795450f40fe1b114cb8b4140874cd1f7e2d002a114d572c3e8c9c0115db0e

## Observed Wokwi Runtime

Operator-provided terminal output:

    I (176) app_init: ELF file SHA256: 1d465f595...
    I (237) main_task: Calling app_main()
    Development scaffold only; monitoring and alarms are not implemented.
    I (247) main_task: Returned from app_main()

## Result and Limitations

- Core types compilation: PASSED
- Compile-time assertions: PASSED
- Virtual ESP32 bootstrap: PASSED
- Functional data-quality behavior: NOT_RUN
- Sensor acquisition: NOT_IMPLEMENTED
- Alarm and safety-policy evaluation: NOT_IMPLEMENTED
- Telemetry integration: NOT_IMPLEMENTED
- Physical vessel integration: NOT_AUTHORIZED

The runtime observations were supplied by the operator.
This evidence does not establish physical hardware
performance or safety certification.
