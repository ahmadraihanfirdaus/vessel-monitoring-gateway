#ifndef VG_PHASE8_H1_SELFTEST_H
#define VG_PHASE8_H1_SELFTEST_H

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "telemetry_contract.h"

static inline void vg_h1_check(
    const char *name,
    bool ok,
    unsigned *passed,
    unsigned *total)
{
    (*total)++;
    if (ok) {
        (*passed)++;
    }

#if defined(ESP_PLATFORM)
    /*
     * Target/Wokwi output is intentionally compact.
     *
     * Earlier H1 target execution hit the ESP-IDF interrupt watchdog while
     * repeatedly flushing per-check PASS lines through console_write().
     * Emit only failing case detail on target; the final aggregate
     * PASS (62/62) remains the target-side evidence marker.
     *
     * Host builds retain per-check output for detailed contract evidence.
     */
    if (!ok) {
        printf("H1_TELEMETRY_TEST %s: FAIL\n", name);
    }
#else
    printf("H1_TELEMETRY_TEST %s: %s\n", name, ok ? "PASS" : "FAIL");
#endif
}

static inline vg_telemetry_payload_t vg_h1_base_payload(void)
{
    /*
     * Keep the large telemetry fixture out of the ESP app_main stack.
     * This self-test is single-threaded and boot-scoped, so static scratch
     * storage is deterministic and appropriate for the development harness.
     */
    static vg_telemetry_payload_t p;
    memset(&p, 0, sizeof(p));

    strcpy(p.device_id, "demo-device-001");
    strcpy(p.firmware_version, "f78e172-dev");
    strcpy(p.boot_id, "boot-demo-0001");
    p.sequence = 42u;
    p.uptime_ms = 123456u;
    p.source_mode = VG_SOURCE_SIMULATION;
    p.channel_count = 5u;

    strcpy(p.channels[0].name, "temperature_c");
    p.channels[0].quality = VG_QUALITY_VALID;
    p.channels[0].has_value = true;
    p.channels[0].value = 31.25;

    strcpy(p.channels[1].name, "bilge_level");
    p.channels[1].quality = VG_QUALITY_MISSING;
    p.channels[1].has_value = false;

    strcpy(p.channels[2].name, "vibration_index");
    p.channels[2].quality = VG_QUALITY_INVALID;
    p.channels[2].has_value = false;

    strcpy(p.channels[3].name, "battery_voltage");
    p.channels[3].quality = VG_QUALITY_STALE;
    p.channels[3].has_value = true;
    p.channels[3].value = 12.4;

    strcpy(p.channels[4].name, "zero_test");
    p.channels[4].quality = VG_QUALITY_VALID;
    p.channels[4].has_value = true;
    p.channels[4].value = 0.0;

    return p;
}

static inline void run_phase8_h1_telemetry_contract_selftest(void)
{
    unsigned p = 0u;
    unsigned t = 0u;

    vg_h1_check("SCHEMA_VERSION_V1",
                strcmp(VG_TELEMETRY_SCHEMA_VERSION, "1.0") == 0, &p, &t);
    vg_h1_check("SOURCE_SIMULATION_STRING",
                strcmp(vg_source_mode_to_string(VG_SOURCE_SIMULATION),
                       "simulation") == 0, &p, &t);
    vg_h1_check("SOURCE_BENCH_STRING",
                strcmp(vg_source_mode_to_string(VG_SOURCE_BENCH_TEST),
                       "bench_test") == 0, &p, &t);
    vg_h1_check("SOURCE_PHYSICAL_LABEL_STRING",
                strcmp(vg_source_mode_to_string(VG_SOURCE_PHYSICAL),
                       "physical") == 0, &p, &t);
    vg_h1_check("SOURCE_UNKNOWN_NOT_SERIALIZABLE",
                vg_source_mode_to_string(VG_SOURCE_UNKNOWN) == NULL, &p, &t);

    vg_h1_check("QUALITY_VALID_STRING",
                strcmp(vg_tel_quality_to_string(VG_QUALITY_VALID),
                       "valid") == 0, &p, &t);
    vg_h1_check("QUALITY_INVALID_STRING",
                strcmp(vg_tel_quality_to_string(VG_QUALITY_INVALID),
                       "invalid") == 0, &p, &t);
    vg_h1_check("QUALITY_MISSING_STRING",
                strcmp(vg_tel_quality_to_string(VG_QUALITY_MISSING),
                       "missing") == 0, &p, &t);
    vg_h1_check("QUALITY_STALE_STRING",
                strcmp(vg_tel_quality_to_string(VG_QUALITY_STALE),
                       "stale") == 0, &p, &t);
    vg_h1_check("QUALITY_UNKNOWN_STRING",
                strcmp(vg_tel_quality_to_string(VG_QUALITY_UNKNOWN),
                       "unknown") == 0, &p, &t);

    vg_h1_check("TOKEN_VALID",
                vg_tel_safe_token("demo-device_01:v1.0",
                                  VG_TELEMETRY_MAX_ID_LEN), &p, &t);
    vg_h1_check("TOKEN_QUOTE_REJECTED",
                !vg_tel_safe_token("bad\"token",
                                   VG_TELEMETRY_MAX_ID_LEN), &p, &t);
    vg_h1_check("TOKEN_EMPTY_REJECTED",
                !vg_tel_safe_token("", VG_TELEMETRY_MAX_ID_LEN), &p, &t);

    vg_telemetry_channel_t c = {0};
    strcpy(c.name, "test");
    c.quality = VG_QUALITY_VALID;
    c.has_value = true;
    c.value = 1.25;
    vg_h1_check("CHANNEL_VALID_VALUE",
                vg_tel_channel_is_consistent(&c), &p, &t);

    c.value = 0.0;
    vg_h1_check("CHANNEL_VALID_ZERO",
                vg_tel_channel_is_consistent(&c), &p, &t);

    c.quality = VG_QUALITY_MISSING;
    c.has_value = false;
    vg_h1_check("CHANNEL_MISSING_NULL",
                vg_tel_channel_is_consistent(&c), &p, &t);

    c.quality = VG_QUALITY_INVALID;
    vg_h1_check("CHANNEL_INVALID_NULL",
                vg_tel_channel_is_consistent(&c), &p, &t);

    c.quality = VG_QUALITY_UNKNOWN;
    vg_h1_check("CHANNEL_UNKNOWN_NULL",
                vg_tel_channel_is_consistent(&c), &p, &t);

    c.quality = VG_QUALITY_STALE;
    c.has_value = true;
    c.value = 9.5;
    vg_h1_check("CHANNEL_STALE_VALUE",
                vg_tel_channel_is_consistent(&c), &p, &t);

    c.has_value = false;
    vg_h1_check("CHANNEL_STALE_NULL",
                vg_tel_channel_is_consistent(&c), &p, &t);

    c.quality = VG_QUALITY_MISSING;
    c.has_value = true;
    c.value = 0.0;
    vg_h1_check("CHANNEL_MISSING_WITH_VALUE_REJECTED",
                !vg_tel_channel_is_consistent(&c), &p, &t);

    c.quality = VG_QUALITY_INVALID;
    vg_h1_check("CHANNEL_INVALID_WITH_VALUE_REJECTED",
                !vg_tel_channel_is_consistent(&c), &p, &t);

    c.quality = VG_QUALITY_VALID;
    c.has_value = false;
    vg_h1_check("CHANNEL_VALID_WITHOUT_VALUE_REJECTED",
                !vg_tel_channel_is_consistent(&c), &p, &t);

    c.has_value = true;
    c.value = NAN;
    vg_h1_check("CHANNEL_NAN_REJECTED",
                !vg_tel_channel_is_consistent(&c), &p, &t);

    /*
     * Large Phase 8 fixture workspaces are static so the target self-test
     * does not consume several kilobytes of the already tight app_main stack.
     */
    static vg_telemetry_payload_t base;
    base = vg_h1_base_payload();
    vg_h1_check("PAYLOAD_BASE_VALID",
                vg_tel_payload_is_consistent(&base), &p, &t);

    static vg_telemetry_payload_t x;
    x = base;
    x.device_id[0] = '\0';
    vg_h1_check("PAYLOAD_DEVICE_REQUIRED",
                !vg_tel_payload_is_consistent(&x), &p, &t);

    x = base;
    x.firmware_version[0] = '\0';
    vg_h1_check("PAYLOAD_FIRMWARE_REQUIRED",
                !vg_tel_payload_is_consistent(&x), &p, &t);

    x = base;
    x.boot_id[0] = '\0';
    vg_h1_check("PAYLOAD_BOOT_REQUIRED",
                !vg_tel_payload_is_consistent(&x), &p, &t);

    x = base;
    x.source_mode = VG_SOURCE_UNKNOWN;
    vg_h1_check("PAYLOAD_UNKNOWN_SOURCE_REJECTED",
                !vg_tel_payload_is_consistent(&x), &p, &t);

    x = base;
    strcpy(x.channels[1].name, x.channels[0].name);
    vg_h1_check("PAYLOAD_DUPLICATE_CHANNEL_REJECTED",
                !vg_tel_payload_is_consistent(&x), &p, &t);

    static char key[VG_TELEMETRY_KEY_MAX];
    memset(key, 0, sizeof(key));
    vg_h1_check("IDENTITY_KEY_BUILD",
                vg_tel_build_identity_key(&base, key, sizeof(key)) &&
                strcmp(key, "demo-device-001|boot-demo-0001|42") == 0,
                &p, &t);

    x = base;
    vg_h1_check("IDENTITY_SAME_EXACT",
                vg_tel_same_identity(&base, &x), &p, &t);

    x.sequence++;
    vg_h1_check("IDENTITY_SEQUENCE_DIFF",
                !vg_tel_same_identity(&base, &x), &p, &t);

    x = base;
    strcpy(x.boot_id, "boot-demo-0002");
    vg_h1_check("IDENTITY_BOOT_DIFF",
                !vg_tel_same_identity(&base, &x), &p, &t);

    x = base;
    strcpy(x.device_id, "demo-device-002");
    vg_h1_check("IDENTITY_DEVICE_DIFF",
                !vg_tel_same_identity(&base, &x), &p, &t);

    x = base;
    vg_h1_check("DUPLICATE_IDENTICAL",
                vg_tel_classify_duplicate(&base, &x) ==
                    VG_TEL_DUPLICATE_IDENTICAL, &p, &t);

    x = base;
    x.uptime_ms++;
    vg_h1_check("DUPLICATE_CONFLICT_UPTIME",
                vg_tel_classify_duplicate(&base, &x) ==
                    VG_TEL_DUPLICATE_CONFLICTING, &p, &t);

    x = base;
    strcpy(x.firmware_version, "f78e172-other");
    vg_h1_check("DUPLICATE_CONFLICT_FIRMWARE",
                vg_tel_classify_duplicate(&base, &x) ==
                    VG_TEL_DUPLICATE_CONFLICTING, &p, &t);

    x = base;
    x.channels[0].value = 32.0;
    vg_h1_check("DUPLICATE_CONFLICT_CHANNEL",
                vg_tel_classify_duplicate(&base, &x) ==
                    VG_TEL_DUPLICATE_CONFLICTING, &p, &t);

    x = base;
    x.sequence++;
    vg_h1_check("DUPLICATE_DISTINCT_SEQUENCE",
                vg_tel_classify_duplicate(&base, &x) ==
                    VG_TEL_DUPLICATE_DISTINCT, &p, &t);

    x = base;
    x.channels[1].has_value = true;
    vg_h1_check("DUPLICATE_INVALID_PAYLOAD",
                vg_tel_classify_duplicate(&base, &x) ==
                    VG_TEL_DUPLICATE_INVALID, &p, &t);

    x = base;
    vg_telemetry_channel_t tmp = x.channels[0];
    x.channels[0] = x.channels[4];
    x.channels[4] = tmp;
    vg_h1_check("DUPLICATE_CHANNEL_ORDER_INDEPENDENT",
                vg_tel_classify_duplicate(&base, &x) ==
                    VG_TEL_DUPLICATE_IDENTICAL, &p, &t);

    static char json[VG_TELEMETRY_JSON_MAX];
    memset(json, 0, sizeof(json));
    const bool serialized =
        vg_tel_serialize_json(&base, json, sizeof(json));
    vg_h1_check("SERIALIZE_BASE", serialized, &p, &t);

    vg_h1_check("JSON_SCHEMA_VERSION",
                serialized &&
                strstr(json, "\"schema_version\":\"1.0\"") != NULL,
                &p, &t);
    vg_h1_check("JSON_REQUIRED_IDENTITY",
                serialized &&
                strstr(json, "\"device_id\":\"demo-device-001\"") != NULL &&
                strstr(json, "\"firmware_version\":\"f78e172-dev\"") != NULL &&
                strstr(json, "\"boot_id\":\"boot-demo-0001\"") != NULL &&
                strstr(json, "\"sequence\":42") != NULL &&
                strstr(json, "\"uptime_ms\":123456") != NULL,
                &p, &t);
    vg_h1_check("JSON_SOURCE_MODE",
                serialized &&
                strstr(json, "\"source_mode\":\"simulation\"") != NULL,
                &p, &t);
    vg_h1_check("JSON_VALID_VALUE",
                serialized &&
                strstr(json,
                       "\"temperature_c\":{\"value\":31.25,"
                       "\"quality\":\"valid\"}") != NULL,
                &p, &t);
    vg_h1_check("JSON_MISSING_IS_NULL",
                serialized &&
                strstr(json,
                       "\"bilge_level\":{\"value\":null,"
                       "\"quality\":\"missing\"}") != NULL,
                &p, &t);
    vg_h1_check("JSON_INVALID_IS_NULL",
                serialized &&
                strstr(json,
                       "\"vibration_index\":{\"value\":null,"
                       "\"quality\":\"invalid\"}") != NULL,
                &p, &t);
    vg_h1_check("JSON_STALE_VALUE_KEPT",
                serialized &&
                strstr(json,
                       "\"battery_voltage\":{\"value\":12.4,"
                       "\"quality\":\"stale\"}") != NULL,
                &p, &t);
    vg_h1_check("JSON_VALID_ZERO_IS_NUMERIC_ZERO",
                serialized &&
                strstr(json,
                       "\"zero_test\":{\"value\":0,"
                       "\"quality\":\"valid\"}") != NULL,
                &p, &t);
    vg_h1_check("JSON_MISSING_NOT_ZERO",
                serialized &&
                strstr(json,
                       "\"bilge_level\":{\"value\":0") == NULL,
                &p, &t);
    vg_h1_check("JSON_INVALID_NOT_ZERO",
                serialized &&
                strstr(json,
                       "\"vibration_index\":{\"value\":0") == NULL,
                &p, &t);

    x = base;
    x.source_mode = VG_SOURCE_PHYSICAL;
    memset(json, 0, sizeof(json));
    vg_h1_check("SYNTHETIC_PHYSICAL_LABEL_SERIALIZABLE",
                vg_tel_serialize_json(&x, json, sizeof(json)) &&
                strstr(json, "\"source_mode\":\"physical\"") != NULL,
                &p, &t);

    x = base;
    strcpy(x.device_id, "bad id");
    vg_h1_check("SERIALIZE_UNSAFE_ID_REJECTED",
                !vg_tel_serialize_json(&x, json, sizeof(json)), &p, &t);

    static char tiny[32];
    memset(tiny, 0, sizeof(tiny));
    vg_h1_check("SERIALIZE_TINY_BUFFER_REJECTED",
                !vg_tel_serialize_json(&base, tiny, sizeof(tiny)), &p, &t);

    vg_h1_check("SERIALIZE_NULL_PAYLOAD_REJECTED",
                !vg_tel_serialize_json(NULL, json, sizeof(json)), &p, &t);
    vg_h1_check("SERIALIZE_NULL_OUTPUT_REJECTED",
                !vg_tel_serialize_json(&base, NULL, sizeof(json)), &p, &t);

    x = base;
    x.channel_count = 0u;
    vg_h1_check("PAYLOAD_ZERO_CHANNELS_REJECTED",
                !vg_tel_payload_is_consistent(&x), &p, &t);

    x = base;
    x.channel_count = VG_TELEMETRY_MAX_CHANNELS + 1u;
    vg_h1_check("PAYLOAD_TOO_MANY_CHANNELS_REJECTED",
                !vg_tel_payload_is_consistent(&x) &&
                vg_tel_find_channel(&x, "temperature_c") == NULL,
                &p, &t);

    vg_h1_check("IDENTITY_KEY_TINY_BUFFER_REJECTED",
                !vg_tel_build_identity_key(&base, tiny, 8u), &p, &t);

    vg_h1_check("CASE_COUNT_EXACT", t == 61u, &p, &t);

    printf("PHASE8_H1_TELEMETRY_CONTRACT_SELFTEST: %s (%u/%u)\n",
           p == t ? "PASS" : "FAIL", p, t);
}

#endif /* VG_PHASE8_H1_SELFTEST_H */
