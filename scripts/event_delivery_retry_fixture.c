/* Actual native owner/journal/replay composition. Negative completion is an
 * injected unit stimulus, never a real HTTP/crypto/hardware success claim. */
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include "event_delivery.h"

int main(void)
{
    vg_event_journal_t journal;
    vg_alarm_journal_t metadata = {0};
    vg_alarm_id_allocator_t ids;
    vg_alarm_t alarm = {0};
    vg_alarm_id_allocator_init(&ids);
    assert(vg_journal_init(&journal));
    uint64_t event_id;
    assert(vg_alarm_try_raise(&ids, &alarm, 7u, VG_SOURCE_SIMULATION, 3u, 1001u, 0u));
    assert(vg_alarm_journal_append(&journal, &metadata, &alarm, VG_EVENT_ALARM_RAISED, 0u, &event_id));
    assert(vg_alarm_try_acknowledge(&alarm, 1u));
    assert(vg_alarm_journal_append(&journal, &metadata, &alarm, VG_EVENT_ALARM_ACK, 1u, &event_id));
    vg_event_delivery owner = {0};
    vg_replay_progress progress = {0};
    vg_delivery_context context = {"retry-boot", &journal, &metadata, &progress, NULL, false, 1u};
    assert(vg_delivery_context_valid(&context));
    vg_offline_event record = {0};
    strcpy(record.boot, context.boot);
    record.event = journal.events[0];
    record.has_alarm = true;
    record.alarm = metadata.entries[0].alarm;
    assert(vg_delivery_begin(&owner, VG_NET_EVENT, 1u, &record, VG_REPLAY_CURRENT, 0u, 1u));
    assert(vg_replay_mark(&progress, 0u, journal.count, VG_REPLAY_CURRENT, false));
    assert(progress.current_queued == 1u);
    vg_net_completion failed = {0};
    failed.tag = 1u;
    assert(vg_delivery_receive_http(&owner, &failed) == VG_DELIVERY_NETWORK_FAILED);
    assert(owner.stage == VG_DELIVERY_IDLE && !owner.event_halted);
    assert(journal.count == 2u && metadata.count == 2u && alarm.condition_active);
    assert(vg_delivery_choose(&context) == VG_REPLAY_CURRENT);
    assert(progress.current_queued < journal.count);
    printf("{\"retained\":%u,\"metadata_retained\":%u,\"cursor\":%u,"
        "\"head_event_id\":\"%" PRIu64 "\",\"next_event_id\":\"%" PRIu64 "\","
        "\"active_alarm\":true,\"next_tag\":\"%" PRIu64 "\"}\n",
        (unsigned)journal.count, (unsigned)metadata.count, (unsigned)progress.current_queued,
        journal.events[0].event_id, journal.events[progress.current_queued].event_id,
        vg_delivery_next_tag(&owner));
    return 0;
}
