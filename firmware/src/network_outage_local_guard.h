#ifndef PHASE9_SYS003_NETWORK_OUTAGE_LOCAL_GUARD_H
#define PHASE9_SYS003_NETWORK_OUTAGE_LOCAL_GUARD_H
/* SYS-003 development-only host adapter. NOT integrated with production main.c.
 * Local sampling/evaluation/alarms MUST execute independently of cloud state.
 * Each injected callback MUST return promptly; no blocking network call here.
 */
#include <stdbool.h>
#include "network_transport_host_adapter.h"
typedef struct {
    void *context;
    void (*sample)(void *context);
    void (*safety_evaluate)(void *context);
    void (*local_alarm)(void *context);
} sys003_local_driver;

static inline bool sys003_local_step(sys003_local_driver driver,
                                     net001_host_state network_state)
{
    (void)network_state; /* Network MUST NOT gate local safety steps. */
    if (!driver.sample || !driver.safety_evaluate || !driver.local_alarm) {
        return false;
    }
    driver.sample(driver.context);
    driver.safety_evaluate(driver.context);
    driver.local_alarm(driver.context);
    return true;
}
#endif
