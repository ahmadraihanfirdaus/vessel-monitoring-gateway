#ifndef VG_CONTINUOUS_SIMULATION_H
#define VG_CONTINUOUS_SIMULATION_H

#include "domain_snapshot.h"
#include "core_scheduler.h"
#include "core_alarm.h"
#include "core_event_journal.h"
#include "alarm_transition.h"
#include "safety_local_alarm.h"
#include "safety_policy.h"
#include "safety_monitor_policy.h"

#define VG_CONTINUOUS_ALARMS (4u + VG_ENGINE_DEMO_FOUR_COUNT)
typedef struct {
    char device[VG_TELEMETRY_MAX_ID_LEN + 1u];
    char boot[VG_TELEMETRY_MAX_ID_LEN + 1u];
    uint64_t interval_ms;
    vg_nav_age_thresholds_t navigation_age;
    vg_prestart_policy_config_t prestart;
    vg_monitor_policy_config_t monitoring;
    vg_engine_deviation_config_t engine_deviation;
    uint32_t demo_priority;
    uint32_t demo_engine_reason;
} vg_continuous_config_t;

typedef enum {
    VG_CONTINUOUS_REJECTED = 0, VG_CONTINUOUS_WAIT, VG_CONTINUOUS_ENCODED,
    VG_CONTINUOUS_ENCODING_REFUSED, VG_CONTINUOUS_EXHAUSTED
} vg_continuous_result_t;

/* Single caller/boot. Own this context statically, never on a small task stack.
 * Sampling and logical alarms never wait for network/storage acceptance. */
typedef struct {
    bool initialized;
    vg_continuous_config_t config;
    vg_scheduler_t scheduler;
    vg_domain_sample_t sample;
    vg_alarm_id_allocator_t alarm_ids;
    vg_alarm_t alarms[VG_CONTINUOUS_ALARMS];
    vg_event_journal_t journal;
    vg_alarm_journal_t alarm_journal;
    uint64_t sequence;
    uint64_t skipped;
    uint64_t encoding_refused;
    uint64_t alarm_errors;
    bool virtual_start_permitted;
    bool logical_alarm_active;
    vg_telemetry_snapshot_v11_t working_payload;
    char working_wire[VG_TELEMETRY_JSON_MAX + 1u];
    char latest_wire[VG_TELEMETRY_JSON_MAX + 1u];
    size_t latest_length;
    uint64_t latest_sequence;
} vg_continuous_simulation_t;

static inline void vg_continuous_increment(uint64_t *value)
{
    if (*value != UINT64_MAX) ++*value;
}

static inline bool vg_continuous_config_valid(const vg_continuous_config_t *config)
{
    return config && memchr(config->device, 0, sizeof(config->device)) &&
        memchr(config->boot, 0, sizeof(config->boot)) &&
        vg_tel_safe_token(config->device, VG_TELEMETRY_MAX_ID_LEN) &&
        vg_tel_safe_token(config->boot, VG_TELEMETRY_MAX_ID_LEN) && config->interval_ms > 0u &&
        vg_nav_age_thresholds_valid(&config->navigation_age) &&
        vg_prestart_policy_config_is_consistent(&config->prestart) &&
        vg_monitor_policy_config_is_consistent(&config->monitoring) &&
        isfinite(config->engine_deviation.warning_threshold_rpm) &&
        config->engine_deviation.warning_threshold_rpm > 0.0f &&
        config->demo_priority != 0u && config->demo_engine_reason != 0u;
}

static inline bool vg_continuous_init(vg_continuous_simulation_t *runtime,
    const vg_continuous_config_t *config, uint64_t first_due_ms)
{
    if (!runtime || !vg_continuous_config_valid(config)) return false;
    /* Configuration must be external; do not alias it into the cleared context. */
    vg_continuous_config_t saved = *config;
    memset(runtime, 0, sizeof(*runtime));
    runtime->config = saved;
    if (!vg_scheduler_init(&runtime->scheduler, saved.interval_ms, first_due_ms) ||
        !vg_journal_init(&runtime->journal)) return false;
    vg_alarm_id_allocator_init(&runtime->alarm_ids);
    runtime->initialized = true;
    return true;
}

/* Repeat the existing finite provider stimuli explicitly as synthetic cycles;
 * refresh their diagnostic metadata, never masquerade as physical acquisition. */
static inline bool vg_continuous_observe(vg_continuous_simulation_t *runtime, uint64_t now)
{
    const uint64_t cycle = runtime->sequence - 1u;
    const uint32_t diagnostic_sequence = runtime->sequence > UINT32_MAX ? UINT32_MAX : (uint32_t)runtime->sequence;
#define VG_CONTINUOUS_PROVIDER(member, type, prefix, steps) \
    do { type sim; if (!prefix##_sim_init(&sim, 0u, 1u) || \
        !prefix##_sim_sample_for_step(&sim, (size_t)(cycle % (steps)), &runtime->sample.member)) return false; \
        runtime->sample.member.meta.sampled_at_ms = now; \
        runtime->sample.member.meta.sequence = diagnostic_sequence; } while (0)
    VG_CONTINUOUS_PROVIDER(door, vg_door_sim_t, vg_door, VG_DOOR_SIM_STEPS);
    VG_CONTINUOUS_PROVIDER(vapor, vg_fuel_vapor_sim_t, vg_fuel_vapor, VG_FUEL_VAPOR_SIM_STEPS);
    VG_CONTINUOUS_PROVIDER(bilge, vg_bilge_sim_t, vg_bilge, VG_BILGE_SIM_STEPS);
    VG_CONTINUOUS_PROVIDER(temperature, vg_temperature_sim_t, vg_temperature, VG_TEMPERATURE_SIM_STEPS);
    VG_CONTINUOUS_PROVIDER(attitude, vg_attitude_sim_t, vg_attitude, VG_ATTITUDE_SIM_STEPS);
    VG_CONTINUOUS_PROVIDER(vibration, vg_vibration_sim_t, vg_vibration, VG_VIBRATION_SIM_STEPS);
    VG_CONTINUOUS_PROVIDER(power, vg_power_sim_t, vg_power, VG_POWER_SIM_STEPS);
#undef VG_CONTINUOUS_PROVIDER
    if (!vg_engine_demo_four_profile(&runtime->sample.engines, (cycle % 8u) >= 3u)) return false;
    for (size_t i = 0u; i < runtime->sample.engines.engine_count; ++i)
        runtime->sample.engines.engines[i].runtime_s += now / 1000u;
    if (cycle % 8u == 0u) {
        /* Public synthetic origin; never vessel coordinates. */
        const vg_nav_rmc_data_t nav = {0.0, 0.0, 0.0f, 0.0f, true};
        char sentence[VG_NAV_SENTENCE_MAX];
        if (!vg_nav_format_rmc_development(&nav, sentence, sizeof(sentence)) ||
            !vg_nav_ingest_sentence(&runtime->sample.navigation, sentence, now, VG_SOURCE_SIMULATION)) return false;
    }
    return vg_nav_update_age(&runtime->sample.navigation, now, &runtime->config.navigation_age);
}

static inline void vg_continuous_record(vg_continuous_simulation_t *runtime,
    const vg_alarm_t *alarm, vg_event_type_t type, uint64_t now)
{
    uint64_t event_id = 0u;
    if (!vg_alarm_journal_matches(&runtime->alarm_journal, &runtime->journal) ||
        runtime->journal.next_id == 0u || runtime->journal.next_id == UINT64_MAX) {
        vg_continuous_increment(&runtime->alarm_errors);
        return;
    }
    if (!vg_alarm_journal_append(&runtime->journal, &runtime->alarm_journal,
        alarm, type, now, &event_id) && runtime->journal.count != VG_JOURNAL_CAPACITY)
        vg_continuous_increment(&runtime->alarm_errors);
}

static inline void vg_continuous_condition(vg_continuous_simulation_t *runtime,
    size_t slot, bool condition, uint32_t reason, uint64_t now)
{
    vg_alarm_t *alarm = &runtime->alarms[slot];
    if (alarm->id != 0u && alarm->condition_active && (!condition || alarm->reason_code != reason)) {
        if (!vg_alarm_try_clear_condition(alarm, now)) {
            vg_continuous_increment(&runtime->alarm_errors);
            return;
        }
        vg_continuous_record(runtime, alarm, VG_EVENT_ALARM_CLEARED, now);
    }
    if (condition && (alarm->id == 0u || !alarm->condition_active)) {
        vg_alarm_t next = {0};
        if (!vg_alarm_try_raise(&runtime->alarm_ids, &next, (uint32_t)slot + 1u,
            VG_SOURCE_SIMULATION, runtime->config.demo_priority, reason, now)) {
            vg_continuous_increment(&runtime->alarm_errors);
            return;
        }
        *alarm = next;
        vg_continuous_record(runtime, alarm, VG_EVENT_ALARM_RAISED, now);
    }
}

static inline bool vg_continuous_evaluate(vg_continuous_simulation_t *runtime, uint64_t now)
{
    vg_prestart_decision_t hatch, vapor;
    vg_monitor_decision_t bilge, temperature;
    if (!vg_prestart_evaluate_hatch(&runtime->config.prestart, &runtime->sample.door, &hatch) ||
        !vg_prestart_evaluate_fuel_vapor(&runtime->config.prestart, &runtime->sample.vapor, &vapor) ||
        !vg_monitor_evaluate_bilge(&runtime->config.monitoring, &runtime->sample.bilge, &bilge) ||
        !vg_monitor_evaluate_temperature(&runtime->config.monitoring, &runtime->sample.temperature, &temperature)) return false;
    runtime->virtual_start_permitted = hatch.start_permitted && vapor.start_permitted;
    vg_continuous_condition(runtime, 0u, hatch.condition_present, (uint32_t)hatch.reason_code, now);
    vg_continuous_condition(runtime, 1u, vapor.condition_present, (uint32_t)vapor.reason_code, now);
    vg_continuous_condition(runtime, 2u, bilge.condition_present, (uint32_t)bilge.reason_code, now);
    vg_continuous_condition(runtime, 3u, temperature.condition_present, (uint32_t)temperature.reason_code, now);
    bool any_condition = hatch.condition_present || vapor.condition_present || bilge.condition_present || temperature.condition_present;
    for (size_t i = 0u; i < VG_ENGINE_DEMO_FOUR_COUNT; ++i) {
        vg_engine_deviation_result_t deviation;
        if (!vg_engine_evaluate_rpm_deviation(&runtime->sample.engines, i,
            &runtime->config.engine_deviation, &deviation)) return false;
        any_condition |= deviation.warning;
        vg_continuous_condition(runtime, 4u + i, deviation.warning, runtime->config.demo_engine_reason, now);
    }
    runtime->logical_alarm_active = any_condition || runtime->alarm_errors != 0u;
    for (size_t i = 0u; i < VG_CONTINUOUS_ALARMS; ++i) {
        vg_local_alarm_output_t local;
        if (runtime->alarms[i].id != 0u) {
            if (!vg_local_alarm_from_alarm(&runtime->alarms[i], &local)) return false;
            runtime->logical_alarm_active |= local.led_active || local.buzzer_active;
        }
    }
    return true;
}

/* ACK is a separate explicit local command. It is refused when its journal
 * record cannot be retained, and it never clears the underlying condition. */
static inline bool vg_continuous_acknowledge(vg_continuous_simulation_t *runtime,
    size_t slot, uint64_t now)
{
    if (!runtime || !runtime->initialized || slot >= VG_CONTINUOUS_ALARMS ||
        !runtime->scheduler.has_last_now || now < runtime->scheduler.last_now_ms ||
        runtime->journal.count >= VG_JOURNAL_CAPACITY) return false;
    vg_alarm_t next = runtime->alarms[slot];
    if (!vg_alarm_try_acknowledge(&next, now)) return false;
    uint64_t event_id;
    if (!vg_alarm_journal_append(&runtime->journal, &runtime->alarm_journal,
        &next, VG_EVENT_ALARM_ACK, now, &event_id)) return false;
    runtime->alarms[slot] = next;
    /* Advance monotonic input watermark; a later poll cannot precede this ACK. */
    runtime->scheduler.last_now_ms = now;
    return true;
}

static inline vg_continuous_result_t vg_continuous_poll(vg_continuous_simulation_t *runtime, uint64_t now)
{
    if (!runtime || !runtime->initialized || !vg_continuous_config_valid(&runtime->config)) return VG_CONTINUOUS_REJECTED;
    if (runtime->sequence == UINT64_MAX) return VG_CONTINUOUS_EXHAUSTED;
    uint64_t skipped = 0u;
    vg_schedule_result_t scheduled = vg_scheduler_poll(&runtime->scheduler, now, &skipped);
    if (scheduled == VG_SCHED_WAIT) return VG_CONTINUOUS_WAIT;
    if (scheduled == VG_SCHED_EXHAUSTED) return VG_CONTINUOUS_EXHAUSTED;
    if (scheduled != VG_SCHED_DUE) return VG_CONTINUOUS_REJECTED;
    runtime->skipped = UINT64_MAX - runtime->skipped < skipped ? UINT64_MAX : runtime->skipped + skipped;
    ++runtime->sequence;
    if (!vg_continuous_observe(runtime, now) || !vg_continuous_evaluate(runtime, now) ||
        !vg_domain_build(&runtime->sample, runtime->config.device, "continuous-sim-1.1",
            runtime->config.boot, runtime->sequence, now, &runtime->working_payload)) {
        vg_continuous_increment(&runtime->encoding_refused);
        return VG_CONTINUOUS_ENCODING_REFUSED;
    }
    const char *names[] = {"runtime_journal_retained", "runtime_journal_rejected", "runtime_skipped", "local_alarm_active"};
    const uint64_t values[] = {runtime->journal.count, runtime->journal.rejected_full,
        runtime->skipped, runtime->logical_alarm_active ? 1u : 0u};
    for (size_t i = 0u; i < 4u; ++i) {
        bool exact = values[i] <= VG_EXACT_DOUBLE_UINT64_MAX;
        if (!vg_domain_add(&runtime->working_payload, names[i], exact ? VG_QUALITY_VALID : VG_QUALITY_INVALID,
            exact, exact ? (double)values[i] : 0.0)) return VG_CONTINUOUS_ENCODING_REFUSED;
    }
    if (!vg_tel_v11_serialize_json(&runtime->working_payload, runtime->working_wire, sizeof(runtime->working_wire))) {
        vg_continuous_increment(&runtime->encoding_refused);
        return VG_CONTINUOUS_ENCODING_REFUSED;
    }
    runtime->latest_length = strlen(runtime->working_wire);
    memcpy(runtime->latest_wire, runtime->working_wire, runtime->latest_length + 1u);
    runtime->latest_sequence = runtime->sequence;
    return VG_CONTINUOUS_ENCODED;
}

#endif
