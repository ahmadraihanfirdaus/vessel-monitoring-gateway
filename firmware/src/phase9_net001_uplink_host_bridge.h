#ifndef PHASE9_NET001_UPLINK_HOST_BRIDGE_H
#define PHASE9_NET001_UPLINK_HOST_BRIDGE_H
/* NET-001 host-only uplink handoff. Driver calls MUST be nonblocking.
 * Not HTTPS, no identity/auth acknowledgement; snapshot is never removed.
 * No default retry, timeout, endpoint or certificate. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "network_transport_host_adapter.h"
#include "net002_offline_host_store.h"
typedef struct {
    void *ctx;
    bool (*send)(void *ctx, const uint8_t *bytes, size_t length);
} net001_host_uplink;
typedef enum {
    NET001_SEND_INVALID=0, NET001_SEND_NOT_READY,
    NET001_SEND_REJECTED, NET001_SEND_SUBMITTED
} net001_host_send_result;
static inline net001_host_send_result net001_try_send_latest(
    const net001_host_adapter *network,
    const net002_host_offline_store *store,
    net001_host_uplink uplink)
{
    if (!network || !network->initialized || !store || !uplink.send ||
        !store->has_latest || store->latest_len==0u ||
        store->latest_len>NET002_HOST_LATEST_MAX) return NET001_SEND_INVALID;
    if (network->state!=NET001_HOST_READY) return NET001_SEND_NOT_READY;
    return uplink.send(uplink.ctx,store->latest,store->latest_len) ?
        NET001_SEND_SUBMITTED : NET001_SEND_REJECTED;
}
#endif
