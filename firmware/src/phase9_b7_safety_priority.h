#ifndef PHASE9_B7_SAFETY_PRIORITY_H
#define PHASE9_B7_SAFETY_PRIORITY_H
/* SYS-003: local callbacks before link state step; missing callbacks block network.
 * This proves only ordering in injected HOST fixtures, not real-time guarantees. */
#include "phase9_sys003_outage_cycle_host.h"
static inline sys003_host_cycle_result phase9_b7_safety_priority(
    sys003_local_driver local,net001_host_adapter *network,uint32_t now_ms)
{
    sys003_host_cycle_result r={false,false,NET001_HOST_IDLE};
    r.local_ok=sys003_local_step(local,NET001_HOST_IDLE);
    if (!r.local_ok) return r;
    if (network && network->initialized) {
        r.network_attempted=true;
        r.link_state=net001_host_step(network,now_ms);
    }
    return r;
}
#endif
