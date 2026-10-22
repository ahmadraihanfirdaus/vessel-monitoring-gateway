#ifndef PHASE9_NET002_REPLAY_CURSOR_HOST_H
#define PHASE9_NET002_REPLAY_CURSOR_HOST_H
/* NET-002 host-only replay cursor. Acknowledgement is a caller-provided
 * development fixture, not durable remote delivery. Refuses mutation during
 * replay, and never removes stored critical events. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "net002_offline_host_store.h"
typedef struct {
    size_t offset, snapshot_count;
    uint32_t snapshot_evicted;
    bool initialized;
} net002_host_replay_cursor;
static inline bool net002_replay_begin(const net002_host_offline_store *store,
                                       net002_host_replay_cursor *cursor)
{
    if (!store || !cursor || store->count>NET002_HOST_JOURNAL_CAP) return false;
    cursor->offset=0u;cursor->snapshot_count=store->count;
    cursor->snapshot_evicted=store->evicted_count;cursor->initialized=true;
    return true;
}
static inline bool net002_replay_unchanged(const net002_host_offline_store *store,
                                           const net002_host_replay_cursor *cursor)
{
    return store && cursor && cursor->initialized &&
        store->count==cursor->snapshot_count &&
        store->evicted_count==cursor->snapshot_evicted &&
        cursor->offset<=cursor->snapshot_count;
}
static inline bool net002_replay_peek(const net002_host_offline_store *store,
                                      const net002_host_replay_cursor *cursor,
                                      net002_host_critical_event *out)
{
    return net002_replay_unchanged(store,cursor) &&
        cursor->offset<cursor->snapshot_count &&
        net002_host_get_event(store,cursor->offset,out);
}
static inline bool net002_replay_ack(const net002_host_offline_store *store,
                                     net002_host_replay_cursor *cursor,
                                     uint32_t event_id)
{
    net002_host_critical_event current;
    if (!net002_replay_peek(store,cursor,&current) ||
        event_id==0u || current.event_id!=event_id) return false;
    ++cursor->offset;
    return true;
}
#endif
