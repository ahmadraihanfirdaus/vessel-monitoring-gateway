#ifndef PHASE9_B7_READONLY_BOUNDARY_H
#define PHASE9_B7_READONLY_BOUNDARY_H
/* SYS-004 host-only read-only boundary. NO actuator command payloads accepted. */
#include <stdbool.h>
#include <stddef.h>
#include "sys004_no_actuator_host_gate.h"
static inline bool phase9_b7_readonly_allow(const char *topic,
                                            const void *body,size_t body_len)
{
    if (!sys004_host_allow_topic(topic)) return false;
    /* This host contract supports GET-like empty queries only. */
    return body == NULL && body_len == 0u;
}
#endif
