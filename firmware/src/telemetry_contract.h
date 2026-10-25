#ifndef VG_TELEMETRY_CONTRACT_H
#define VG_TELEMETRY_CONTRACT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <math.h>
#include <inttypes.h>

#include "core_types.h"
#include "core_source_mode.h"

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 * Phase 8 H1 telemetry contract foundation.
 *
 * Development contract only.
 *
 * Requirement-derived fields:
 *   TEL-001: schema_version, device_id, firmware_version, boot_id,
 *            sequence, uptime_ms, source_mode and per-channel quality.
 *   TEL-002: invalid/missing numeric values are represented as JSON null
 *            with quality metadata; never silently as numeric zero.
 *
 * Phase 8 v1 design decision:
 *   The stable sample identity is the tuple (device_id, boot_id, sequence).
 *   This tuple is used by the contract-level duplicate classifier.
 *
 * TEL-003 backend/database deduplication and SIM-014 are NOT implemented or
 * claimed here. This module only defines identity and duplicate semantics.
 *
 * A source_mode value of "physical" is only a wire-contract label. Its
 * presence never proves physical acquisition or authorized vessel integration.
 */

#define VG_TELEMETRY_SCHEMA_VERSION "1.0"
#define VG_TELEMETRY_MAX_ID_LEN 48u
#define VG_TELEMETRY_MAX_VERSION_LEN 48u
#define VG_TELEMETRY_MAX_CHANNEL_NAME_LEN 32u
#define VG_TELEMETRY_MAX_CHANNELS 16u
#define VG_TELEMETRY_EXTENDED_MAX_CHANNELS 72u
#define VG_TELEMETRY_JSON_MAX 4096u
#define VG_TELEMETRY_KEY_MAX 128u

typedef struct {
    char name[VG_TELEMETRY_MAX_CHANNEL_NAME_LEN + 1u];
    vg_data_quality_t quality;
    bool has_value;
    double value;
} vg_telemetry_channel_t;

typedef struct {
    char device_id[VG_TELEMETRY_MAX_ID_LEN + 1u];
    char firmware_version[VG_TELEMETRY_MAX_VERSION_LEN + 1u];
    char boot_id[VG_TELEMETRY_MAX_ID_LEN + 1u];
    uint64_t sequence;
    uint64_t uptime_ms;
    vg_source_mode_t source_mode;
    size_t channel_count;
    vg_telemetry_channel_t channels[VG_TELEMETRY_MAX_CHANNELS];
} vg_telemetry_payload_t;

typedef enum {
    VG_TEL_DUPLICATE_INVALID = 0,
    VG_TEL_DUPLICATE_DISTINCT,
    VG_TEL_DUPLICATE_IDENTICAL,
    VG_TEL_DUPLICATE_CONFLICTING
} vg_telemetry_duplicate_result_t;

static inline bool vg_tel_safe_token(const char *s, size_t max_len)
{
    if (s == NULL || s[0] == '\0') {
        return false;
    }

    size_t n = 0u;
    for (const unsigned char *p = (const unsigned char *)s; *p != '\0'; ++p) {
        ++n;
        if (n > max_len) {
            return false;
        }

        const bool ok =
            (*p >= 'a' && *p <= 'z') ||
            (*p >= 'A' && *p <= 'Z') ||
            (*p >= '0' && *p <= '9') ||
            *p == '.' || *p == '_' || *p == ':' || *p == '-';

        if (!ok) {
            return false;
        }
    }

    return true;
}

static inline const char *vg_tel_quality_to_string(vg_data_quality_t q)
{
    switch (q) {
        case VG_QUALITY_VALID:
            return "valid";
        case VG_QUALITY_INVALID:
            return "invalid";
        case VG_QUALITY_MISSING:
            return "missing";
        case VG_QUALITY_STALE:
            return "stale";
        case VG_QUALITY_UNKNOWN:
            return "unknown";
        default:
            return NULL;
    }
}

static inline bool vg_tel_channel_is_consistent(
    const vg_telemetry_channel_t *channel)
{
    if (channel == NULL ||
        !vg_tel_safe_token(channel->name, VG_TELEMETRY_MAX_CHANNEL_NAME_LEN) ||
        vg_tel_quality_to_string(channel->quality) == NULL) {
        return false;
    }

    if (channel->has_value && !isfinite(channel->value)) {
        return false;
    }

    switch (channel->quality) {
        case VG_QUALITY_VALID:
            return channel->has_value;

        case VG_QUALITY_STALE:
            return !channel->has_value || isfinite(channel->value);

        case VG_QUALITY_INVALID:
        case VG_QUALITY_MISSING:
        case VG_QUALITY_UNKNOWN:
            return !channel->has_value;

        default:
            return false;
    }
}

/* Shared vector admission; the legacy payload retains its 16-channel bound. */
static inline bool vg_tel_vector_is_consistent(const char *device, const char *firmware,
    const char *boot, vg_source_mode_t mode, const vg_telemetry_channel_t *channels,
    size_t count, size_t limit)
{
    if (!vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_tel_safe_token(firmware, VG_TELEMETRY_MAX_VERSION_LEN) ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) ||
        vg_source_mode_to_string(mode) == NULL || !channels || count == 0u ||
        count > limit || (limit != VG_TELEMETRY_MAX_CHANNELS && limit != VG_TELEMETRY_EXTENDED_MAX_CHANNELS)) return false;
    for (size_t i = 0u; i < count; ++i) {
        if (!vg_tel_channel_is_consistent(&channels[i])) return false;
    }
    for (size_t i = 0u; i < count; ++i) {
        for (size_t j = i + 1u; j < count; ++j)
            if (strcmp(channels[i].name, channels[j].name) == 0) return false;
    }
    return true;
}

static inline bool vg_tel_payload_is_consistent(const vg_telemetry_payload_t *payload)
{
    return payload != NULL && vg_tel_vector_is_consistent(payload->device_id,
        payload->firmware_version, payload->boot_id, payload->source_mode,
        payload->channels, payload->channel_count, VG_TELEMETRY_MAX_CHANNELS);
}

static inline bool vg_tel_same_identity(
    const vg_telemetry_payload_t *a,
    const vg_telemetry_payload_t *b)
{
    if (!vg_tel_payload_is_consistent(a) ||
        !vg_tel_payload_is_consistent(b)) {
        return false;
    }

    return strcmp(a->device_id, b->device_id) == 0 &&
           strcmp(a->boot_id, b->boot_id) == 0 &&
           a->sequence == b->sequence;
}

static inline bool vg_tel_build_identity_key(
    const vg_telemetry_payload_t *payload,
    char *out,
    size_t out_size)
{
    if (!vg_tel_payload_is_consistent(payload) ||
        out == NULL || out_size == 0u) {
        return false;
    }

    const int n = snprintf(
        out,
        out_size,
        "%s|%s|%" PRIu64,
        payload->device_id,
        payload->boot_id,
        payload->sequence);

    return n > 0 && (size_t)n < out_size;
}

static inline const vg_telemetry_channel_t *vg_tel_find_channel(
    const vg_telemetry_payload_t *payload,
    const char *name)
{
    if (payload == NULL || name == NULL ||
        payload->channel_count == 0u ||
        payload->channel_count > VG_TELEMETRY_MAX_CHANNELS) {
        return NULL;
    }

    for (size_t i = 0u; i < payload->channel_count; ++i) {
        if (strcmp(payload->channels[i].name, name) == 0) {
            return &payload->channels[i];
        }
    }

    return NULL;
}

static inline bool vg_tel_channel_semantic_equal(
    const vg_telemetry_channel_t *a,
    const vg_telemetry_channel_t *b)
{
    if (!vg_tel_channel_is_consistent(a) ||
        !vg_tel_channel_is_consistent(b)) {
        return false;
    }

    if (a->quality != b->quality || a->has_value != b->has_value) {
        return false;
    }

    return !a->has_value || a->value == b->value;
}

static inline bool vg_tel_payload_semantic_equal(
    const vg_telemetry_payload_t *a,
    const vg_telemetry_payload_t *b)
{
    if (!vg_tel_payload_is_consistent(a) ||
        !vg_tel_payload_is_consistent(b) ||
        !vg_tel_same_identity(a, b) ||
        strcmp(a->firmware_version, b->firmware_version) != 0 ||
        a->uptime_ms != b->uptime_ms ||
        a->source_mode != b->source_mode ||
        a->channel_count != b->channel_count) {
        return false;
    }

    for (size_t i = 0u; i < a->channel_count; ++i) {
        const vg_telemetry_channel_t *peer =
            vg_tel_find_channel(b, a->channels[i].name);
        if (peer == NULL ||
            !vg_tel_channel_semantic_equal(&a->channels[i], peer)) {
            return false;
        }
    }

    return true;
}

static inline vg_telemetry_duplicate_result_t vg_tel_classify_duplicate(
    const vg_telemetry_payload_t *existing,
    const vg_telemetry_payload_t *incoming)
{
    if (!vg_tel_payload_is_consistent(existing) ||
        !vg_tel_payload_is_consistent(incoming)) {
        return VG_TEL_DUPLICATE_INVALID;
    }

    if (!vg_tel_same_identity(existing, incoming)) {
        return VG_TEL_DUPLICATE_DISTINCT;
    }

    if (vg_tel_payload_semantic_equal(existing, incoming)) {
        return VG_TEL_DUPLICATE_IDENTICAL;
    }

    return VG_TEL_DUPLICATE_CONFLICTING;
}

static inline bool vg_tel_append(
    char *out,
    size_t out_size,
    size_t *used,
    const char *fmt,
    ...)
{
    if (out == NULL || used == NULL || fmt == NULL || *used >= out_size) {
        return false;
    }

    va_list ap;
    va_start(ap, fmt);
    const int n = vsnprintf(out + *used, out_size - *used, fmt, ap);
    va_end(ap);

    if (n < 0 || (size_t)n >= out_size - *used) {
        return false;
    }

    *used += (size_t)n;
    return true;
}

/* Validated versioned vector formatter. False means output must not be used;
 * callers needing atomic publication provide a separate working wire buffer. */
static inline bool vg_tel_serialize_vector_json(const char *schema, const char *device,
    const char *firmware, const char *boot, uint64_t sequence, uint64_t uptime_ms,
    vg_source_mode_t mode, const vg_telemetry_channel_t *channels, size_t count,
    char *out, size_t out_size)
{
    if (!schema || !out || out_size == 0u) return false;
    size_t limit = 0u;
    if (strcmp(schema, "1.0") == 0) limit = VG_TELEMETRY_MAX_CHANNELS;
    else if (strcmp(schema, "1.1") == 0) {
        limit = VG_TELEMETRY_EXTENDED_MAX_CHANNELS;
        if (out_size > VG_TELEMETRY_JSON_MAX + 1u) out_size = VG_TELEMETRY_JSON_MAX + 1u;
    }
    else return false;
    if (!vg_tel_vector_is_consistent(device, firmware, boot, mode, channels, count, limit)) return false;
    const char *source = vg_source_mode_to_string(mode);

    size_t used = 0u;
    if (!vg_tel_append(
            out, out_size, &used,
            "{\"schema_version\":\"%s\","
            "\"device_id\":\"%s\","
            "\"firmware_version\":\"%s\","
            "\"boot_id\":\"%s\","
            "\"sequence\":%" PRIu64 ","
            "\"uptime_ms\":%" PRIu64 ","
            "\"source_mode\":\"%s\","
            "\"channels\":{",
            schema,
            device,
            firmware,
            boot,
            sequence,
            uptime_ms,
            source)) {
        return false;
    }

    for (size_t i = 0u; i < count; ++i) {
        const vg_telemetry_channel_t *ch = &channels[i];
        const char *quality = vg_tel_quality_to_string(ch->quality);
        if (quality == NULL) {
            return false;
        }

        if (i > 0u && !vg_tel_append(out, out_size, &used, ",")) {
            return false;
        }

        if (!vg_tel_append(out, out_size, &used,
                           "\"%s\":{\"value\":", ch->name)) {
            return false;
        }

        if (ch->has_value) {
            if (!vg_tel_append(out, out_size, &used, "%.17g", ch->value)) {
                return false;
            }
        } else {
            if (!vg_tel_append(out, out_size, &used, "null")) {
                return false;
            }
        }

        if (!vg_tel_append(out, out_size, &used,
                           ",\"quality\":\"%s\"}", quality)) {
            return false;
        }
    }

    return vg_tel_append(out, out_size, &used, "}}");
}

static inline bool vg_tel_serialize_json(const vg_telemetry_payload_t *payload,
    char *out, size_t out_size)
{
    if (!vg_tel_payload_is_consistent(payload)) return false;
    return vg_tel_serialize_vector_json(VG_TELEMETRY_SCHEMA_VERSION, payload->device_id,
        payload->firmware_version, payload->boot_id, payload->sequence, payload->uptime_ms,
        payload->source_mode, payload->channels, payload->channel_count, out, out_size);
}

#endif /* VG_TELEMETRY_CONTRACT_H */
