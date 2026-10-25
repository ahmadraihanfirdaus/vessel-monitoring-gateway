#ifndef VG_ESP32_CONTINUOUS_MAIN_H
#define VG_ESP32_CONTINUOUS_MAIN_H

#ifndef ESP_PLATFORM
#error Continuous SDK entry requires ESP-IDF; native tests use the pure coordinator.
#endif

#include "continuous_simulation.h"
#include "esp32_network_client.h"
#include "esp32_offline_store.h"
#include "esp_timer.h"
#include "esp_random.h"
#include "bootloader_random.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "mbedtls/platform_util.h"

static vg_continuous_simulation_t continuous;
static vg_continuous_config_t continuous_config;
static vg_net_profile continuous_network_profile;
static char continuous_alarm_wire[1024];
static vg_recovered_events continuous_recovered;
static vg_replay_progress continuous_replay;

/* Explicit nonsecret demonstration policy in read-only namespace vgw_demo.
 * Provisioning is external and NOT performed by this firmware. No fallback
 * policy, physical driver, NVS erase, clock fabrication or credentials log. */
static bool load_continuous_config(vg_continuous_config_t *config)
{
    if (!config || nvs_flash_init() != ESP_OK) return false;
    nvs_handle_t handle;
    if (nvs_open("vgw_demo", NVS_READONLY, &handle) != ESP_OK) return false;
    size_t length = sizeof(config->device);
    uint32_t interval, stale, offline, hatch, vapor, bilge, temperature, deviation;
    int32_t warning_mc, alarm_mc;
    bool valid = nvs_get_str(handle, "device", config->device, &length) == ESP_OK &&
        length > 1u && length <= sizeof(config->device) &&
        nvs_get_u32(handle, "interval_ms", &interval) == ESP_OK &&
        nvs_get_u32(handle, "nav_stale_ms", &stale) == ESP_OK &&
        nvs_get_u32(handle, "nav_offline_ms", &offline) == ESP_OK &&
        nvs_get_u32(handle, "hatch_rule", &hatch) == ESP_OK &&
        nvs_get_u32(handle, "vapor_rule", &vapor) == ESP_OK &&
        nvs_get_u32(handle, "bilge_rule", &bilge) == ESP_OK &&
        nvs_get_u32(handle, "temp_rule", &temperature) == ESP_OK &&
        nvs_get_i32(handle, "temp_warn_mc", &warning_mc) == ESP_OK &&
        nvs_get_i32(handle, "temp_alarm_mc", &alarm_mc) == ESP_OK &&
        nvs_get_u32(handle, "rpm_deviation", &deviation) == ESP_OK &&
        nvs_get_u32(handle, "demo_priority", &config->demo_priority) == ESP_OK &&
        nvs_get_u32(handle, "demo_reason", &config->demo_engine_reason) == ESP_OK &&
        hatch <= (uint32_t)VG_POLICY_RULE_BLOCK && vapor <= (uint32_t)VG_POLICY_RULE_BLOCK &&
        bilge <= (uint32_t)VG_POLICY_RULE_ALERT_ONLY && temperature <= (uint32_t)VG_POLICY_RULE_ALERT_ONLY;
    nvs_close(handle);
    if (!valid) return false;
    config->interval_ms = interval;
    config->navigation_age = (vg_nav_age_thresholds_t){stale, offline};
    config->prestart = (vg_prestart_policy_config_t){(vg_policy_rule_mode_t)hatch, (vg_policy_rule_mode_t)vapor};
    config->monitoring = (vg_monitor_policy_config_t){(vg_policy_rule_mode_t)bilge,
        (vg_policy_rule_mode_t)temperature, {(float)warning_mc / 1000.0f, (float)alarm_mc / 1000.0f}};
    config->engine_deviation.warning_threshold_rpm = (float)deviation;
    return vg_continuous_config_valid(config);
}

void app_main(void)
{
    puts("CONTINUOUS_SIMULATION: CANDIDATE_ONLY_NO_PHYSICAL_CONTROL");
    uint8_t entropy[16];
    bootloader_random_enable();
    esp_fill_random(entropy, sizeof(entropy));
    bootloader_random_disable();
    for (size_t i = 0u; i < sizeof(entropy); ++i)
        (void)snprintf(continuous_config.boot + i * 2u, 3u, "%02x", (unsigned)entropy[i]);
    mbedtls_platform_zeroize(entropy, sizeof(entropy));
    int64_t now_us = esp_timer_get_time();
    if (now_us < 0 || !load_continuous_config(&continuous_config) ||
        !vg_continuous_init(&continuous, &continuous_config, (uint64_t)now_us / 1000u)) {
        puts("CONTINUOUS_SIMULATION: NOT_CONFIGURED_OR_INVALID_POLICY");
        return;
    }
    /* Local configuration is independent of optional cloud credentials. */
    bool storage = vg_storage_start(continuous.config.device, continuous.config.boot);
    bool network = vg_net_load_profile(&continuous_network_profile) == VG_NET_PROFILE_READY &&
        strcmp(continuous_network_profile.device_id, continuous.config.device) == 0 &&
        vg_net_start(&continuous_network_profile);
    mbedtls_platform_zeroize(&continuous_network_profile, sizeof(continuous_network_profile));
    puts("CONTINUOUS_SIMULATION: CONFIGURED_HARDWARE_UNVERIFIED");
    puts(storage ? "CONTINUOUS_STORAGE: STARTED_UNVERIFIED" : "CONTINUOUS_STORAGE: UNAVAILABLE_LOCAL_RAM_ONLY");
    puts(network ? "CONTINUOUS_NETWORK: STARTED_UNVERIFIED" : "CONTINUOUS_NETWORK: NOT_CONFIGURED_OR_UNAVAILABLE");
    bool pending = false;
    bool prefer_event = true, event_encoding_halted = false;
    bool recovered_ready = false;
    uint64_t storage_refused = 0u, network_refused = 0u;
    uint64_t storage_full_reports = 0u, storage_rejected_reports = 0u;
    bool storage_degraded_reported = false;
    for (;;) {
        now_us = esp_timer_get_time();
        if (now_us < 0) {
            puts("CONTINUOUS_SIMULATION: CLOCK_REFUSED");
            break;
        }
        vg_continuous_result_t result = vg_continuous_poll(&continuous, (uint64_t)now_us / 1000u);
        if (result == VG_CONTINUOUS_ENCODED) {
            pending = network;
            if (storage && !vg_storage_submit_with_alarms(continuous.config.boot, continuous.latest_sequence,
                continuous.latest_wire, continuous.latest_length, &continuous.journal, &continuous.alarm_journal))
                vg_continuous_increment(&storage_refused);
            if (continuous.sequence % 256u == 0u)
                printf("CONTINUOUS_DIAGNOSTICS: samples=%llu journal_full=%llu storage_refused=%llu network_refused=%llu storage_full_reports=%llu storage_rejected_reports=%llu events_queued_not_acked=%u recovered_visited=%u recovered_unpublishable=%u\n",
                    (unsigned long long)continuous.sequence, (unsigned long long)continuous.journal.rejected_full,
                    (unsigned long long)storage_refused, (unsigned long long)network_refused,
                    (unsigned long long)storage_full_reports, (unsigned long long)storage_rejected_reports,
                    (unsigned)continuous_replay.current_queued, (unsigned)continuous_replay.recovered_visited,
                    (unsigned)continuous_replay.recovered_unpublishable);
        } else if (result == VG_CONTINUOUS_ENCODING_REFUSED) {
            if (continuous.encoding_refused == 1u || continuous.encoding_refused % 256u == 0u)
                puts("CONTINUOUS_ENCODING: REFUSED_LATEST_PACKET_RETAINED_LOCAL_EVALUATION_CONTINUES");
        } else if (result == VG_CONTINUOUS_EXHAUSTED || result == VG_CONTINUOUS_REJECTED) {
            puts("CONTINUOUS_SIMULATION: SEQUENCE_OR_CLOCK_HALTED_EXPLICIT_RESTART_REQUIRED");
            break;
        }
        vg_net_completion completion;
        if (network && vg_net_take_completion(&completion))
            puts(completion.completed ? "CONTINUOUS_HTTP: COMPLETED_NOT_APPLICATION_ACK" : "CONTINUOUS_HTTP: FAILED");
        vg_storage_completion stored;
        if (storage && vg_storage_take_completion(&stored)) {
            if (stored.status == VG_STORAGE_IO_HALTED)
                puts("CONTINUOUS_STORAGE: IO_HALTED_LOCAL_SIMULATION_CONTINUES");
            else if (stored.status == VG_STORAGE_CRITICAL_FULL) {
                vg_continuous_increment(&storage_full_reports);
                if (storage_full_reports == 1u || storage_full_reports % 256u == 0u)
                    puts("CONTINUOUS_STORAGE: BOUNDED_CAPACITY_FULL_NEW_CRITICAL_NOT_RETAINED");
            } else if (stored.status == VG_STORAGE_REJECTED) {
                vg_continuous_increment(&storage_rejected_reports);
                if (storage_rejected_reports == 1u || storage_rejected_reports % 256u == 0u)
                    puts("CONTINUOUS_STORAGE: REJECTED_SUBMISSION_LATEST_REMAINS_RAM");
            }
            if (stored.degraded_recovery && !storage_degraded_reported) {
                storage_degraded_reported = true;
                puts("CONTINUOUS_STORAGE: DEGRADED_STORAGE_OLDER_DATA_POSSIBLE");
            }
        }
        if (storage && vg_storage_take_recovered_events(&continuous_recovered)) {
            recovered_ready = vg_recovered_events_valid(&continuous_recovered) &&
                !strcmp(continuous_recovered.device, continuous.config.device);
            continuous_replay.recovered_visited = 0u;
            continuous_replay.recovered_unpublishable = 0u;
            continuous_replay.prefer_recovered = true;
            if (recovered_ready)
                printf("CONTINUOUS_REPLAY: RECOVERED_EVENTS=%u GENERATION=%llu DEGRADED=%u NO_DELETION_RECEIPT\n",
                    (unsigned)continuous_recovered.event_count,
                    (unsigned long long)continuous_recovered.generation, (unsigned)continuous_recovered.degraded);
            else puts("CONTINUOUS_REPLAY: INVALID_RECOVERY_VIEW_NOT_PUBLISHED");
        }
        /* Fair bounded queueing of immutable recovered/current facts. Explicit
         * recovery may replay duplicates. No queue/HTTP completion deletes a
         * retained fact, advances a durable ACK or changes an alarm condition. */
        size_t recovered_count = recovered_ready ? continuous_recovered.event_count : 0u;
        vg_replay_choice choice = vg_replay_choose(&continuous_replay, recovered_count, continuous.alarm_journal.count);
        if (network && !event_encoding_halted && choice == VG_REPLAY_CHOICE_INVALID) {
            vg_continuous_increment(&continuous.alarm_errors);
            event_encoding_halted = true;
            puts("CONTINUOUS_REPLAY: INVALID_PROGRESS_RETAINED_FACTS_NOT_SKIPPED");
        }
        bool event_pending = network && !event_encoding_halted && choice > VG_REPLAY_NONE;
        if (event_pending && (prefer_event || !pending)) {
            uint64_t event_id;
            vg_replay_encode_result encoded;
            if (choice == VG_REPLAY_RECOVERED) {
                size_t index = continuous_replay.recovered_visited;
                event_id = continuous_recovered.events[index].event.event_id;
                encoded = vg_recovered_event_json(&continuous_recovered, index,
                    continuous_alarm_wire, sizeof(continuous_alarm_wire));
            } else {
                const vg_alarm_transition_t *transition =
                    &continuous.alarm_journal.entries[continuous_replay.current_queued];
                event_id = transition->event.event_id;
                encoded = vg_alarm_transition_json(transition, continuous.config.device, continuous.config.boot,
                    continuous_alarm_wire, sizeof(continuous_alarm_wire)) ? VG_REPLAY_ENCODED : VG_REPLAY_BUFFER_REFUSED;
            }
            if (encoded == VG_REPLAY_UNSUPPORTED_TYPE) {
                puts("CONTINUOUS_REPLAY: UNSUPPORTED_LEGACY_TYPE_RETAINED_NOT_PUBLISHED");
                if (!vg_replay_mark(&continuous_replay, recovered_count,
                    continuous.alarm_journal.count, choice, true)) event_encoding_halted = true;
            } else if (encoded != VG_REPLAY_ENCODED) {
                vg_continuous_increment(&continuous.alarm_errors);
                event_encoding_halted = true;
                puts("CONTINUOUS_EVENT: ENCODING_HALTED_RETAINED_FACT_NOT_SKIPPED");
            } else if (vg_net_submit(VG_NET_EVENT, continuous_alarm_wire, strlen(continuous_alarm_wire), event_id)) {
                if (!vg_replay_mark(&continuous_replay, recovered_count,
                    continuous.alarm_journal.count, choice, false)) event_encoding_halted = true;
                prefer_event = false;
            } else vg_continuous_increment(&network_refused);
        } else if (pending) {
            if (vg_net_submit(VG_NET_TELEMETRY, continuous.latest_wire, continuous.latest_length, continuous.latest_sequence))
                { pending = false; prefer_event = true; }
            else vg_continuous_increment(&network_refused);
        }
        TickType_t ticks = pdMS_TO_TICKS(10u);
        vTaskDelay(ticks > 0 ? ticks : 1);
    }
}

#endif
