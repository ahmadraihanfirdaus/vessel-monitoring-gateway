#ifndef VG_TELEMETRY_SNAPSHOT_V11_H
#define VG_TELEMETRY_SNAPSHOT_V11_H

#include "telemetry_contract.h"

#define VG_TELEMETRY_V11_SCHEMA_VERSION "1.1"
#define VG_TELEMETRY_V11_MAX_CHANNELS VG_TELEMETRY_EXTENDED_MAX_CHANNELS

/* Separate storage: never enlarge legacy payloads or their boot-test frames.
 * Own this bounded working object in a caller context, not a small task stack. */
typedef struct {
    char device_id[VG_TELEMETRY_MAX_ID_LEN + 1u];
    char firmware_version[VG_TELEMETRY_MAX_VERSION_LEN + 1u];
    char boot_id[VG_TELEMETRY_MAX_ID_LEN + 1u];
    uint64_t sequence;
    uint64_t uptime_ms;
    vg_source_mode_t source_mode;
    size_t channel_count;
    vg_telemetry_channel_t channels[VG_TELEMETRY_V11_MAX_CHANNELS];
} vg_telemetry_snapshot_v11_t;

static inline bool vg_tel_v11_is_consistent(const vg_telemetry_snapshot_v11_t *payload)
{
    return payload && vg_tel_vector_is_consistent(payload->device_id, payload->firmware_version,
        payload->boot_id, payload->source_mode, payload->channels, payload->channel_count,
        VG_TELEMETRY_V11_MAX_CHANNELS);
}

static inline bool vg_tel_v11_serialize_json(const vg_telemetry_snapshot_v11_t *payload,
    char *out, size_t capacity)
{
    if (!vg_tel_v11_is_consistent(payload)) return false;
    return vg_tel_serialize_vector_json(VG_TELEMETRY_V11_SCHEMA_VERSION, payload->device_id,
        payload->firmware_version, payload->boot_id, payload->sequence, payload->uptime_ms,
        payload->source_mode, payload->channels, payload->channel_count, out, capacity);
}

#endif
