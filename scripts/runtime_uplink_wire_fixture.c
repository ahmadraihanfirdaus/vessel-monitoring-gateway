#include <assert.h>
#include <stdio.h>
#include "core_runtime_guard.h"
#include "runtime_uplink_frame.h"

/* Executes the real finite core scheduler/diagnostics/journal before producing
 * the same wire builder used by the ESP32 acquisition hook. Synthetic only. */
int main(void)
{
    vg_runtime_sim_t runtime = {0};
    vg_runtime_guard_t guard = {0};
    vg_telemetry_payload_t payload;
    char wire[4097];
    assert(vg_runtime_sim_init(&runtime, 101u, 200u, 200u));
    assert(vg_guard_init(&guard, &runtime));
    for (size_t i = 0u; i < VG_RUNTIME_SIM_STEPS; ++i) {
        uint64_t skipped = 0u;
        vg_diag_result_t diagnostic;
        uint64_t tick = ((uint64_t)i + 1u) * 200u;
        assert(vg_guard_poll(&guard, &runtime, tick, &skipped, &diagnostic) == VG_GUARD_PROCESSED);
        assert(skipped == 0u);
        vg_measurement_t sample;
        assert(vg_runtime_sim_measurement(i, &sample));
        assert(vg_runtime_uplink_frame("runtime:demo", "synthetic-runtime-boot", (uint64_t)i + 1u,
            tick, &sample, &payload, wire, sizeof(wire)));
        assert(strlen(wire) <= VG_TELEMETRY_JSON_MAX);
        puts(wire);
    }
    assert(runtime.flow.journal.count == 4u);
    assert(guard.processed_count == VG_RUNTIME_SIM_STEPS);
    return 0;
}
