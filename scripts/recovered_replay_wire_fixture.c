/* Compiled after the existing transaction test's shared in-memory IO fixture.
 * The real merge/publish/recover/capture/serializer execute; no physical NVS. */
#include "offline_replay.h"
static vg_recovered_events recovered_events;
static vg_alarm_journal_t recovered_metadata;
static vg_alarm_t recovered_alarm;
static char replay_wire[1024];

int main(void)
{
    setup();
    (void)baseline; (void)sentinel;
    uint64_t event_id;
    assert(vg_journal_append(&journal, 0u, 9u, VG_SOURCE_BENCH_TEST, VG_EVENT_FAULT, 11u, &event_id));
    assert(vg_offline_merge(&tx.current, "boot-a", 2u, "latest", 6u, &journal, &tx.candidate) == VG_OFFLINE_READY);
    assert(vg_offline_publish(&tx));
    /* New boot: alarm/event IDs legitimately restart at one. */
    assert(vg_journal_init(&journal));
    vg_alarm_id_allocator_t ids;
    vg_alarm_id_allocator_init(&ids);
    assert(vg_alarm_try_raise(&ids, &recovered_alarm, 7u, VG_SOURCE_SIMULATION, 3u, 1001u, 0u));
    assert(vg_alarm_journal_append(&journal, &recovered_metadata, &recovered_alarm, VG_EVENT_ALARM_RAISED, 0u, &event_id));
    assert(vg_alarm_try_acknowledge(&recovered_alarm, 0u));
    assert(vg_alarm_journal_append(&journal, &recovered_metadata, &recovered_alarm, VG_EVENT_ALARM_ACK, 0u, &event_id));
    assert(vg_alarm_try_clear_condition(&recovered_alarm, 100u));
    assert(vg_alarm_journal_append(&journal, &recovered_metadata, &recovered_alarm, VG_EVENT_ALARM_CLEARED, 100u, &event_id));
    assert(vg_offline_merge_with_alarms(&tx.current, "replay-boot-b", 1u, "latest", 6u,
        &journal, &recovered_metadata, &tx.candidate) == VG_OFFLINE_READY);
    assert(vg_offline_publish(&tx));
    assert(vg_journal_init(&journal));
    memset(&recovered_metadata, 0, sizeof(recovered_metadata));
    memset(&recovered_alarm, 0, sizeof(recovered_alarm));
    vg_alarm_id_allocator_init(&ids);
    assert(vg_alarm_try_raise(&ids, &recovered_alarm, 8u, VG_SOURCE_BENCH_TEST, 4u, 1002u, 0u));
    assert(vg_alarm_journal_append(&journal, &recovered_metadata, &recovered_alarm, VG_EVENT_ALARM_RAISED, 0u, &event_id));
    assert(vg_offline_merge_with_alarms(&tx.current, "replay-boot-c", 1u, "latest", 6u,
        &journal, &recovered_metadata, &tx.candidate) == VG_OFFLINE_READY);
    assert(vg_offline_publish(&tx));
    /* Discard volatile transaction state, then perform actual two-slot recovery. */
    memset(&tx, 0, sizeof(tx));
    assert(vg_offline_recover(&tx, io, VG_REPLAY_FIXTURE_DEVICE));
    assert(tx.current.generation == 4u && !tx.degraded && tx.current.event_count == 6u);
    assert(vg_recovered_events_capture(&tx.current, tx.degraded, &recovered_events));
    vg_replay_progress progress = {0};
    for (size_t i = 0u; i < recovered_events.event_count; ++i) {
        assert(vg_replay_choose(&progress, recovered_events.event_count, 0u) == VG_REPLAY_RECOVERED);
        assert(vg_recovered_event_json(&recovered_events, progress.recovered_visited,
            replay_wire, sizeof(replay_wire)) == VG_REPLAY_ENCODED);
        puts(replay_wire);
        assert(vg_replay_mark(&progress, recovered_events.event_count, 0u, VG_REPLAY_RECOVERED, false));
    }
    assert(vg_replay_choose(&progress, recovered_events.event_count, 0u) == VG_REPLAY_NONE);
    assert(tx.current.event_count == 6u && tx.current.generation == 4u);
    return 0;
}
