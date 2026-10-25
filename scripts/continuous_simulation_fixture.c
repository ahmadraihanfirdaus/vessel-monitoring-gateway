#include <assert.h>
#include <stdio.h>
#include "continuous_simulation.h"
#include "offline_transaction.h"

#ifndef VG_CONTINUOUS_FIXTURE_DEVICE
#define VG_CONTINUOUS_FIXTURE_DEVICE "continuous:demo"
#endif

/* Explicit synthetic test policy; not a default or vessel engineering limit. */
static vg_continuous_config_t test_config(void)
{
    vg_continuous_config_t config = {0};
    strcpy(config.device, VG_CONTINUOUS_FIXTURE_DEVICE);
    strcpy(config.boot, "synthetic-continuous-boot");
    config.interval_ms = 200u;
    config.navigation_age = (vg_nav_age_thresholds_t){400u, 800u};
    config.prestart = (vg_prestart_policy_config_t){VG_POLICY_RULE_BLOCK, VG_POLICY_RULE_BLOCK};
    config.monitoring = (vg_monitor_policy_config_t){VG_POLICY_RULE_ALERT_ONLY, VG_POLICY_RULE_ALERT_ONLY, {40.0f, 60.0f}};
    config.engine_deviation.warning_threshold_rpm = 300.0f;
    config.demo_priority = 1u;
    config.demo_engine_reason = 5001u;
    return config;
}

int main(void)
{
    static vg_continuous_simulation_t runtime;
    static vg_offline_state state;
    static vg_offline_state next, scratch, restored;
    static uint8_t raw[VG_OFFLINE_SNAPSHOT_MAX];
    size_t length;
    vg_continuous_config_t config = test_config();
    assert(vg_continuous_init(&runtime, &config, 200u));
    assert(vg_offline_init(&state, config.device));
    /* 24 samples include three complete navigation cycles and journal-full
     * progression. Network is absent throughout. Each wire body is real C99. */
    for (unsigned i = 1u; i <= 24u; ++i) {
        assert(vg_continuous_poll(&runtime, (uint64_t)i * 200u) == VG_CONTINUOUS_ENCODED);
        assert(runtime.working_payload.channel_count == 48u);
        assert(runtime.latest_length <= 4096u);
        assert(vg_offline_merge(&state, config.boot, runtime.latest_sequence, runtime.latest_wire,
            runtime.latest_length, &runtime.journal, &next) == VG_OFFLINE_READY);
        assert(vg_offline_pack(&next, raw, sizeof(raw), &length));
        assert(vg_offline_unpack(raw, length, config.device, &scratch, &restored));
        assert(restored.latest_sequence == i && restored.latest_length == runtime.latest_length);
        assert(!memcmp(restored.latest, runtime.latest_wire, runtime.latest_length));
        state = restored;
        puts(runtime.latest_wire);
    }
    assert(runtime.journal.count == 8u && runtime.journal.rejected_full > 0u);
    assert(runtime.sequence == 24u && runtime.alarm_errors == 0u);
    return 0;
}
