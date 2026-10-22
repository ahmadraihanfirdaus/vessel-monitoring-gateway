#ifndef PHASE9_SYS003_OUTAGE_CYCLE_HOST_H
#define PHASE9_SYS003_OUTAGE_CYCLE_HOST_H
/* SYS-003 local safety FIRST for every host cycle. Even if network is NULL,
 * local callbacks run. No real timing/nonblocking proof without bench tests.
 * NOT integrated with firmware main.c or any actuator. */
#include <stdbool.h>
#include <stdint.h>
#include "network_outage_local_guard.h"
typedef struct {
    bool local_ok;
    bool network_attempted;
    net001_host_state link_state;
} sys003_host_cycle_result;
static inline sys003_host_cycle_result sys003_host_cycle(
    sys003_local_driver local, net001_host_adapter *network, uint32_t now_ms)
{
    sys003_host_cycle_result out={false,false,NET001_HOST_IDLE};
    out.local_ok=sys003_local_step(local,NET001_HOST_IDLE);
    if (network && network->initialized) {
        out.network_attempted=true;
        out.link_state=net001_host_step(network,now_ms);
    }
    return out;
}
#endif
