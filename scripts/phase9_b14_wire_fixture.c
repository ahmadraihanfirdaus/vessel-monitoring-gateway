/* B14: deterministic synthetic C99 telemetry emitted to stdout as raw JSONL. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b6_wire_gate.h"
int main(void)
{
    vg_telemetry_payload_t p = {0};
    char json[VG_TELEMETRY_JSON_MAX];
    strcpy(p.device_id, "b14-demo-device");
    strcpy(p.boot_id, "b14-boot");
    strcpy(p.firmware_version, "b14-host-only");
    p.sequence = UINT64_C(42);
    p.uptime_ms = UINT64_C(0);
    p.source_mode = VG_SOURCE_SIMULATION;
    p.channel_count = 2u;
    strcpy(p.channels[0].name, "zero_test");
    p.channels[0].quality = VG_QUALITY_VALID;
    p.channels[0].has_value = true;
    p.channels[0].value = 0.0;
    strcpy(p.channels[1].name, "bilge_level");
    p.channels[1].quality = VG_QUALITY_MISSING;
    p.channels[1].has_value = false;
    if (!phase9_b6_wire_export(&p, json, sizeof(json))) return 11;
    if (puts(json) < 0) return 12;
    p.sequence = UINT64_MAX;
    p.uptime_ms = UINT64_MAX;
    if (!phase9_b6_wire_export(&p, json, sizeof(json))) return 13;
    if (puts(json) < 0) return 14;
    p.source_mode = VG_SOURCE_PHYSICAL;
    if (phase9_b6_wire_export(&p, json, sizeof(json))) return 15;
    if (json[0] != '\0') return 16;
    return 0;
}
