#ifndef SYS004_NO_ACTUATOR_HOST_GATE_H
#define SYS004_NO_ACTUATOR_HOST_GATE_H
/* Development-only read-only message boundary. NOT integrated into runtime. */
#include <stdbool.h>
#include <string.h>
/* This gate only allows diagnostic messages: no engine/starter/steering/radio. */
static inline bool sys004_host_allow_topic(const char *topic) {
 if(!topic) return false;
 return strcmp(topic,"telemetry.read")==0 ||
        strcmp(topic,"diagnostic.read")==0 ||
        strcmp(topic,"health.read")==0;
}
#endif
