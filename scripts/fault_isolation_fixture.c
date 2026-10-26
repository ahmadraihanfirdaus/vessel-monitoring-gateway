/* Dedicated SIM011 host protocol: actual synthetic providers/domain codec.
 * No SDK worker/physical/shared-bus fault injection or DB/network operation. */
#define main unused_continuous_fixture_main
#include "continuous_simulation_fixture.c"
#undef main

static vg_continuous_simulation_t isolated;
static vg_telemetry_snapshot_v11_t payload;
static char output[VG_TELEMETRY_JSON_MAX + 1u];

int main(void)
{
    const vg_continuous_config_t config = test_config();
    assert(vg_continuous_init(&isolated, &config, 200u));
    for (unsigned step = 0u; step < 4u; ++step) {
        const uint64_t now = (uint64_t)(step + 1u) * 200u;
        /* Repeat actual first-step providers, refreshed by the shared observer;
         * only the actual temperature provider stimulus is varied below.
         * Outer packet identity advances independently of provider cycle index. */
        isolated.sequence = 1u;
        assert(vg_continuous_observe(&isolated, now));
        vg_temperature_sim_t temperature;
        assert(vg_temperature_sim_init(&temperature, 0u, 1u));
        const size_t stimulus = step == 0u ? 0u : (step == 3u ? 7u : 5u);
        assert(vg_temperature_sim_sample_for_step(&temperature, stimulus, &isolated.sample.temperature));
        isolated.sample.temperature.meta.sampled_at_ms = now;
        isolated.sample.temperature.meta.sequence = step + 1u;
        isolated.sample.engines.engines[0].rpm += (float)step;
        assert(vg_domain_build(&isolated.sample, "fault:demo", "fault-sim-1.1",
            "synthetic-isolation", step + 1u, now, &payload));
        assert(payload.channel_count == 44u);
        assert(vg_tel_v11_serialize_json(&payload, output, sizeof(output)));
        assert(strlen(output) <= 4096u);
        puts(output);
    }
    return 0;
}
