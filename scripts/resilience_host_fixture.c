/* Dedicated NO_DB_WRITE host actor. stdin supplies monotonic supervisor ticks
 * and controlled provider/API observations; callbacks perform no IO or waits.
 * Actual HTTP runs in a separate supervisor worker. Not ESP32/RTOS evidence. */
#define main unused_continuous_fixture_main
#include "continuous_simulation_fixture.c"
#undef main
#include "network_transport_host_adapter.h"

typedef struct { unsigned begin, cancel; net001_host_link observed; } host_link;
static bool begin(void *p) { ++((host_link *)p)->begin; return true; }
static net001_host_link observe(void *p) { return ((host_link *)p)->observed; }
static void cancel(void *p) { ++((host_link *)p)->cancel; }
static vg_continuous_simulation_t actor;
static vg_telemetry_snapshot_v11_t packet;
static char wire[VG_TELEMETRY_JSON_MAX + 1u];

static bool parse_command(const char *line, uint32_t values[4])
{
    const uint32_t limits[4] = {UINT32_MAX, 3u, 3u, 1u};
    if (line[0] != 'T' || line[1] != ' ') return false;
    const char *p = line + 2;
    for (size_t i = 0u; i < 4u; ++i) {
        uint32_t value = 0u;
        if (*p < '0' || *p > '9') return false;
        while (*p >= '0' && *p <= '9') {
            uint32_t digit = (uint32_t)(*p++ - '0');
            if (value > limits[i] / 10u ||
                (value == limits[i] / 10u && digit > limits[i] % 10u)) return false;
            value = value * 10u + digit;
        }
        values[i] = value;
        if (*p++ != (i == 3u ? '\n' : ' ')) return false;
    }
    return *p == '\0';
}

int main(void)
{
    vg_continuous_config_t config = test_config();
    config.interval_ms = 100u;
    assert(vg_continuous_init(&actor, &config, 0u));
    host_link link = {0};
    net001_host_adapter network;
    net001_host_policy policy = {2000u, 250u, 3u};
    assert(net001_host_init(&network, policy, (net001_host_driver){&link, begin, observe, cancel}));
    char command[128];
    uint32_t fields[4];
    uint64_t sequence = 0u, last_now = 0u;
    bool has_time = false;
    while (fgets(command, sizeof(command), stdin)) {
        /* Strict finite protocol, never arbitrary paths/code/credentials. */
        if (!strchr(command, '\n') || !parse_command(command, fields) ||
            (has_time && (uint64_t)fields[0] <= last_now)) return 3;
        const uint64_t now = fields[0];
        const unsigned phase = fields[1], observed = fields[2], reset = fields[3];
        uint64_t skipped;
        if (vg_scheduler_poll(&actor.scheduler, now, &skipped) != VG_SCHED_DUE) return 3;
        last_now = now; has_time = true; ++sequence;
        /* Shared actual synthetic providers, first stable profile, not copied
         * policy/quality logic. Only temperature and engine stimulus change. */
        actor.sequence = 1u;
        assert(vg_continuous_observe(&actor, now));
        vg_temperature_sim_t temperature;
        assert(vg_temperature_sim_init(&temperature, 0u, 1u));
        const size_t step = phase == 0u ? 0u : (phase == 1u ? 5u : (phase == 2u ? 3u : 7u));
        assert(vg_temperature_sim_sample_for_step(&temperature, step, &actor.sample.temperature));
        actor.sample.temperature.meta.sampled_at_ms = now;
        actor.sample.temperature.meta.sequence = (uint32_t)sequence;
        assert(vg_engine_demo_four_profile(&actor.sample.engines, phase == 1u || phase == 2u));
        actor.sample.engines.engines[0].runtime_s += now / 1000u;
        assert(vg_continuous_evaluate(&actor, now));
        actor.sequence = sequence;
        assert(vg_alarm_journal_matches(&actor.alarm_journal, &actor.journal));
        assert(actor.alarm_errors == 0u && actor.journal.rejected_full == 0u);
        assert(vg_domain_build(&actor.sample, "resilience:demo", "resilience-host-1.1",
            "synthetic-resilience", sequence, now, &packet));
        assert(vg_tel_v11_serialize_json(&packet, wire, sizeof(wire)));
        link.observed = (net001_host_link)observed;
        if (reset) net001_host_reset(&network);
        (void)net001_host_step(&network, (uint32_t)now);
        printf("{\"sequence\":%" PRIu64 ",\"now_ms\":%" PRIu64 ",\"skipped\":%" PRIu64
            ",\"begin\":%u,\"cancel\":%u,\"network_state\":%u,\"exhausted\":%s,\"local_alarm\":%s,\"events\":[",
            sequence, now, skipped, link.begin, link.cancel, (unsigned)network.state,
            network.exhausted ? "true" : "false", actor.logical_alarm_active ? "true" : "false");
        for (size_t i = 0u; i < actor.alarm_journal.count; ++i) {
            char event_wire[1024];
            assert(vg_alarm_transition_json(&actor.alarm_journal.entries[i], "resilience:demo",
                "synthetic-resilience", event_wire, sizeof(event_wire)));
            printf("%s%s", i ? "," : "", event_wire);
        }
        printf("],\"packet\":%s}\n", wire);
        if (fflush(stdout)) return 3;
    }
    return ferror(stdin) ? 3 : 0;
}
