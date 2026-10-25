/* Reuse the actual existing synthetic policy, not a parallel implementation. */
#define main vg_legacy_continuous_fixture_entry
#include "continuous_simulation_fixture.c"
#undef main

static vg_offline_state alarm_state, alarm_next, alarm_scratch, alarm_restored;
static uint8_t alarm_raw[VG_OFFLINE_SNAPSHOT_MAX];
static char alarm_wire[1024];

static void persist(const char *device, const char *boot, uint64_t sequence,
    const void *wire, size_t length, const vg_event_journal_t *journal, const vg_alarm_journal_t *metadata)
{
    assert(vg_offline_merge_with_alarms(&alarm_state, boot, sequence, wire, length,
        journal, metadata, &alarm_next) == VG_OFFLINE_READY);
    size_t size;
    assert(vg_offline_pack(&alarm_next, alarm_raw, sizeof(alarm_raw), &size));
    assert(vg_offline_unpack(alarm_raw, size, device, &alarm_scratch, &alarm_restored));
    alarm_state = alarm_restored;
}

static void emit(const char *device)
{
    for (size_t i = 0u; i < alarm_restored.event_count; ++i) {
        const vg_offline_event *stored = &alarm_restored.events[i];
        assert(stored->has_alarm);
        vg_alarm_transition_t transition = {stored->event, stored->alarm};
        assert(vg_alarm_transition_json(&transition, device, stored->boot, alarm_wire, sizeof(alarm_wire)));
        puts(alarm_wire);
    }
}

int main(void)
{
    const char *device = VG_CONTINUOUS_FIXTURE_DEVICE;
    vg_event_journal_t journal;
    vg_alarm_journal_t metadata = {0};
    vg_alarm_t alarm = {0};
    vg_alarm_id_allocator_t ids;
    uint64_t event_id;
    assert(vg_journal_init(&journal));
    vg_alarm_id_allocator_init(&ids);
    assert(vg_alarm_try_raise(&ids, &alarm, 7u, VG_SOURCE_SIMULATION, 3u, 1001u, 0u));
    assert(vg_alarm_journal_append(&journal, &metadata, &alarm, VG_EVENT_ALARM_RAISED, 0u, &event_id));
    assert(vg_alarm_try_acknowledge(&alarm, 0u));
    assert(vg_alarm_journal_append(&journal, &metadata, &alarm, VG_EVENT_ALARM_ACK, 0u, &event_id));
    assert(vg_alarm_try_clear_condition(&alarm, 0u));
    assert(vg_alarm_journal_append(&journal, &metadata, &alarm, VG_EVENT_ALARM_CLEARED, 0u, &event_id));
    /* Independent pure-native store fixtures, never an erase of real NVS. */
    assert(vg_offline_init(&alarm_state, device));
    persist(device, "synthetic-alarm-zero", 1u, "synthetic", 9u, &journal, &metadata);
    emit(device);

    static vg_continuous_simulation_t runtime;
    vg_continuous_config_t config = test_config();
    assert(vg_continuous_init(&runtime, &config, 0u));
    assert(vg_offline_init(&alarm_state, device));
    for (unsigned i = 0u; i < 24u; ++i) {
        uint64_t now = (uint64_t)i * 200u;
        assert(vg_continuous_poll(&runtime, now) == VG_CONTINUOUS_ENCODED);
        if (i == 1u) assert(vg_continuous_acknowledge(&runtime, 0u, now));
        assert(vg_alarm_journal_matches(&runtime.alarm_journal, &runtime.journal));
        persist(device, config.boot, runtime.latest_sequence, runtime.latest_wire,
            runtime.latest_length, &runtime.journal, &runtime.alarm_journal);
    }
    assert(alarm_restored.event_count == 8u && runtime.journal.rejected_full > 0u);
    emit(device);
    return 0;
}
