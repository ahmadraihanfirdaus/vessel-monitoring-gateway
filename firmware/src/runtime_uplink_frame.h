#ifndef VG_RUNTIME_UPLINK_FRAME_H
#define VG_RUNTIME_UPLINK_FRAME_H

#include "core_measurement.h"
#include "telemetry_contract.h"

/* Actual finite simulation source -> existing v1 serializer. No new wire
 * schema, numeric threshold, hardware sample or fallback-to-zero behavior. */
static inline bool vg_runtime_uplink_frame(const char *device, const char *boot,
    uint64_t sequence, uint64_t uptime_ms, const vg_measurement_t *sample,
    vg_telemetry_payload_t *payload, char *wire, size_t capacity)
{
    if (!sample || !payload || !wire || sample->source_mode != VG_SOURCE_SIMULATION ||
        !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN)) return false;
    uintptr_t a = (uintptr_t)payload, b = (uintptr_t)wire;
    if (capacity == 0u || a > UINTPTR_MAX - sizeof(*payload) || b > UINTPTR_MAX - capacity ||
        (a < b + capacity && b < a + sizeof(*payload))) return false;
    vg_telemetry_payload_t next = {0};
    memcpy(next.device_id, device, strlen(device) + 1u);
    memcpy(next.boot_id, boot, strlen(boot) + 1u);
    memcpy(next.firmware_version, "demo-https-v1", sizeof("demo-https-v1"));
    next.sequence = sequence;
    next.uptime_ms = uptime_ms;
    next.source_mode = VG_SOURCE_SIMULATION;
    next.channel_count = 1u;
    memcpy(next.channels[0].name, "demo_channel", sizeof("demo_channel"));
    next.channels[0].quality = sample->quality;
    next.channels[0].has_value = sample->has_value &&
        (sample->quality == VG_QUALITY_VALID || sample->quality == VG_QUALITY_STALE);
    next.channels[0].value = next.channels[0].has_value ? (double)sample->value : 0.0;
    char encoded[512]; /* One bounded channel with fixed demo metadata. */
    if (!vg_tel_payload_is_consistent(&next) || !vg_tel_serialize_json(&next, encoded, sizeof(encoded))) return false;
    size_t length = strlen(encoded);
    if (length + 1u > capacity) return false;
    memcpy(wire, encoded, length + 1u);
    *payload = next;
    return true;
}

#endif
