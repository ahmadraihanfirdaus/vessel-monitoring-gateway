# ESP32/Wokwi Build Configuration Review — Open Hardware Boundary

**Batch:** A2 — static engineering audit, not a hardware verification.

- The prototype selection is **ESP32-DevKitC V4 / ESP32-WROOM-32E**. `esp32dev` is a **candidate PlatformIO board definition**, not proof of matching physical module capabilities.
- `firmware/platformio.ini` selects `espressif32@7.1.3`, `esp32dev`, and ESP-IDF.
- `firmware/wokwi.toml` points to local `firmware.merged.bin` and `.elf` simulation artifacts.
- The existing Wokwi evidence records a merged 2 MiB image. A local ignored SDK configuration may specify `CONFIG_ESPTOOLPY_FLASHSIZE="2MB"`; actual module flash size is **TBD**.
- A board-definition flash-size default, merged-image flash header, partition layout, and physical flash capacity are **different claims**. They must be checked independently. Neither a small firmware binary nor a successful Wokwi boot verifies the flash size of an unexamined physical module.
- The prior firmware app-version/ELF identity discrepancy remains a separate evidence-review item; compare SHA-256 and the build's actual source state when new images are produced.

## Read-only check

```bash
python scripts/audit_esp32_build_config.py
```

The script verifies documented static choices and reports available ignored runtime configuration. It does not change PlatformIO files and does not give authorization to flash a board or connect vessel equipment.

## Exit gate for future bench work

Identify exact physical module and flash capacity; verify partition tables, bootloader flash headers, electrical and GPIO compatibility, pinout, isolation/protection, and reviewed bench-power design. Document measured evidence under separate authorization. Until then: **PHYSICAL FLASH CONFIGURATION = NOT_VERIFIED; BENCH INTEGRATION = NOT_AUTHORIZED.**

## Local transport/storage build continuation, 2026-10-25

The [actual SDK build evidence](../../evidence/test-results/offline-nvs-summary-20261025.md)
records a 1,041,904-byte application within the existing 1 MiB factory partition,
66,436 bytes static RAM, source-stability digest and offline merged-image hash.
TLS chain/hostname/date validation and assertions remain enabled. The merge
contains blank NVS; its SDK-configured 2 MiB size still proves no physical flash
capacity. Full stack/heap/flash-cache behavior, wear, secret provisioning and
power-loss recovery require actual device evidence. No upload was performed.
