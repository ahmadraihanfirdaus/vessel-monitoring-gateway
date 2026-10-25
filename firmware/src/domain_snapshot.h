#ifndef VG_DOMAIN_SNAPSHOT_H
#define VG_DOMAIN_SNAPSHOT_H

#include "telemetry_snapshot_v11.h"
#include "engine_model.h"
#include "navigation_nmea.h"
#include "provider_door.h"
#include "provider_fuel_vapor.h"
#include "provider_bilge.h"
#include "provider_temperature.h"
#include "provider_attitude.h"
#include "provider_vibration.h"
#include "provider_power.h"

/* Typed composition of existing models. SIMULATION only; no physical drivers.
 * Large output belongs to caller-owned storage. False forbids publication. */
typedef struct {
    vg_engine_model_t engines;
    vg_navigation_state_t navigation;
    vg_door_sample_t door;
    vg_fuel_vapor_sample_t vapor;
    vg_bilge_sample_t bilge;
    vg_temperature_sample_t temperature;
    vg_attitude_sample_t attitude;
    vg_vibration_sample_t vibration;
    vg_power_sample_t power;
} vg_domain_sample_t;

#define VG_EXACT_DOUBLE_UINT64_MAX UINT64_C(9007199254740991)

static inline bool vg_domain_numeric_quality(vg_data_quality_t quality)
{
    return quality == VG_QUALITY_VALID || quality == VG_QUALITY_STALE;
}

static inline bool vg_domain_add(vg_telemetry_snapshot_v11_t *out, const char *name,
    vg_data_quality_t quality, bool has_value, double value)
{
    if (!out || out->channel_count >= VG_TELEMETRY_V11_MAX_CHANNELS ||
        !vg_tel_safe_token(name, VG_TELEMETRY_MAX_CHANNEL_NAME_LEN)) return false;
    vg_telemetry_channel_t channel = {0};
    memcpy(channel.name, name, strlen(name) + 1u);
    channel.quality = quality;
    channel.has_value = has_value;
    channel.value = has_value ? value : 0.0;
    if (!vg_tel_channel_is_consistent(&channel)) return false;
    out->channels[out->channel_count++] = channel;
    return true;
}

static inline bool vg_domain_navigation_valid(const vg_navigation_state_t *nav, uint64_t now)
{
    if (!nav) return false;
    if (!nav->initialized) return true; /* explicit unknown, never default zero */
    return nav->source_mode == VG_SOURCE_SIMULATION && nav->last_valid_ms <= now &&
        nav->data_age_ms == now - nav->last_valid_ms &&
        isfinite(nav->latitude_deg) && fabs(nav->latitude_deg) <= 90.0 &&
        isfinite(nav->longitude_deg) && fabs(nav->longitude_deg) <= 180.0 &&
        isfinite(nav->sog_knots) && nav->sog_knots >= 0.0f &&
        isfinite(nav->cog_deg) && nav->cog_deg >= 0.0f && nav->cog_deg < 360.0f &&
        ((nav->age_state == VG_NAV_AGE_VALID && nav->quality == VG_QUALITY_VALID) ||
         (nav->age_state == VG_NAV_AGE_STALE && nav->quality == VG_QUALITY_STALE) ||
         (nav->age_state == VG_NAV_AGE_OFFLINE && nav->quality == VG_QUALITY_MISSING));
}

static inline bool vg_domain_build(const vg_domain_sample_t *sample, const char *device,
    const char *firmware, const char *boot, uint64_t sequence, uint64_t now,
    vg_telemetry_snapshot_v11_t *out)
{
    if (!sample || !out || !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_tel_safe_token(firmware, VG_TELEMETRY_MAX_VERSION_LEN) ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) ||
        !sample->engines.initialized || sample->engines.engine_count == 0u ||
        sample->engines.engine_count > VG_ENGINE_MODEL_MAX_ENGINES ||
        !vg_domain_navigation_valid(&sample->navigation, now)) return false;
#define VG_DOMAIN_CHECK(member, predicate) \
    if (!(predicate)(&sample->member) || sample->member.meta.source_mode != VG_SOURCE_SIMULATION || \
        sample->member.meta.sampled_at_ms > now) return false
    VG_DOMAIN_CHECK(door, vg_door_sample_is_consistent);
    VG_DOMAIN_CHECK(vapor, vg_fuel_vapor_sample_is_consistent);
    VG_DOMAIN_CHECK(bilge, vg_bilge_sample_is_consistent);
    VG_DOMAIN_CHECK(temperature, vg_temperature_sample_is_consistent);
    VG_DOMAIN_CHECK(attitude, vg_attitude_sample_is_consistent);
    VG_DOMAIN_CHECK(vibration, vg_vibration_sample_is_consistent);
    VG_DOMAIN_CHECK(power, vg_power_sample_is_consistent);
#undef VG_DOMAIN_CHECK
    for (size_t i = 0u; i < sample->engines.engine_count; ++i)
        if (!vg_engine_snapshot_is_consistent(&sample->engines.engines[i]) ||
            sample->engines.engines[i].engine_id != i + 1u) return false;
    memset(out, 0, sizeof(*out));
    memcpy(out->device_id, device, strlen(device) + 1u);
    memcpy(out->firmware_version, firmware, strlen(firmware) + 1u);
    memcpy(out->boot_id, boot, strlen(boot) + 1u);
    out->source_mode = VG_SOURCE_SIMULATION;
    out->sequence = sequence;
    out->uptime_ms = now;
#define VG_DOMAIN_ADD(name, quality, has, value) \
    do { if (!vg_domain_add(out, name, quality, has, value)) return false; } while (0)
    for (size_t i = 0u; i < sample->engines.engine_count; ++i) {
        const vg_engine_snapshot_t *e = &sample->engines.engines[i];
        const bool known = e->communication_quality == VG_ENGINE_COMM_GOOD ||
            e->communication_quality == VG_ENGINE_COMM_DEGRADED;
        const vg_data_quality_t q = known ? VG_QUALITY_VALID : VG_QUALITY_MISSING;
        const char *suffix[] = {"state", "rpm", "temperature_c", "runtime_s", "alarm", "comm"};
        const double values[] = {(double)e->state, e->rpm, e->temperature_c,
            e->runtime_s <= VG_EXACT_DOUBLE_UINT64_MAX ? (double)e->runtime_s : 0.0,
            e->alarm_active ? 1.0 : 0.0, (double)e->communication_quality};
        for (size_t field = 0u; field < 6u; ++field) {
            char name[VG_TELEMETRY_MAX_CHANNEL_NAME_LEN + 1u];
            int length = snprintf(name, sizeof(name), "engine_%u_%s", (unsigned)e->engine_id, suffix[field]);
            if (length <= 0 || (size_t)length >= sizeof(name)) return false;
            vg_data_quality_t field_quality = field == 5u ? VG_QUALITY_VALID : q;
            if (field == 3u && known && e->runtime_s > VG_EXACT_DOUBLE_UINT64_MAX)
                field_quality = VG_QUALITY_INVALID;
            VG_DOMAIN_ADD(name, field_quality, field_quality == VG_QUALITY_VALID, values[field]);
        }
    }
    const vg_navigation_state_t *nav = &sample->navigation;
    vg_data_quality_t nq = !nav->initialized ? VG_QUALITY_UNKNOWN :
        (!nav->fix_valid ? VG_QUALITY_INVALID : nav->quality);
    const bool position = vg_domain_numeric_quality(nq);
    VG_DOMAIN_ADD("nav_latitude_deg", nq, position, nav->latitude_deg);
    VG_DOMAIN_ADD("nav_longitude_deg", nq, position, nav->longitude_deg);
    VG_DOMAIN_ADD("nav_sog_knots", nq, position, nav->sog_knots);
    VG_DOMAIN_ADD("nav_cog_deg", nq, position, nav->cog_deg);
    VG_DOMAIN_ADD("nav_fix", nav->initialized ? VG_QUALITY_VALID : VG_QUALITY_UNKNOWN,
        nav->initialized, nav->fix_valid ? 1.0 : 0.0);
    vg_data_quality_t age_quality = !nav->initialized ? VG_QUALITY_UNKNOWN :
        (nav->data_age_ms <= VG_EXACT_DOUBLE_UINT64_MAX ? VG_QUALITY_VALID : VG_QUALITY_INVALID);
    VG_DOMAIN_ADD("nav_age_ms", age_quality, age_quality == VG_QUALITY_VALID, (double)nav->data_age_ms);
#define VG_DOMAIN_FIELD(name, member, value) \
    VG_DOMAIN_ADD(name, sample->member.meta.quality, \
        vg_domain_numeric_quality(sample->member.meta.quality), value)
    VG_DOMAIN_FIELD("hatch_state", door, sample->door.state);
    VG_DOMAIN_FIELD("vapor_state", vapor, sample->vapor.state);
    VG_DOMAIN_FIELD("vapor_surrogate", vapor, sample->vapor.surrogate_value);
    VG_DOMAIN_FIELD("bilge_state", bilge, sample->bilge.state);
    VG_DOMAIN_FIELD("compartment_temperature_c", temperature, sample->temperature.temperature_c);
    VG_DOMAIN_FIELD("attitude_roll_deg", attitude, sample->attitude.roll_deg);
    VG_DOMAIN_FIELD("attitude_pitch_deg", attitude, sample->attitude.pitch_deg);
    VG_DOMAIN_FIELD("acceleration_x_g", vibration, sample->vibration.accel_x_g);
    VG_DOMAIN_FIELD("acceleration_y_g", vibration, sample->vibration.accel_y_g);
    VG_DOMAIN_FIELD("acceleration_z_g", vibration, sample->vibration.accel_z_g);
    VG_DOMAIN_FIELD("vibration_index", vibration, sample->vibration.vibration_index);
    VG_DOMAIN_FIELD("power_voltage_v", power, sample->power.voltage_v);
    VG_DOMAIN_FIELD("power_current_a", power, sample->power.current_a);
    VG_DOMAIN_FIELD("power_w", power, sample->power.power_w);
#undef VG_DOMAIN_FIELD
#undef VG_DOMAIN_ADD
    return vg_tel_v11_is_consistent(out);
}

#endif
