# C99 safety-host fixture. No network, no database, no repository writes.
from phase9_b3_host_fixture import compile_and_run
COMMON=r'''
#include <assert.h>
#include <string.h>
#include "phase9_b7_gateway_cycle.h"
typedef struct {int samples,evals,alarms,begins;int order;net001_host_link link;}b7_ctx;
static void sample(void *x){b7_ctx*c=(b7_ctx*)x;assert(c->order==0||c->order==3);c->order=1;c->samples++;}
static void eval(void *x){b7_ctx*c=(b7_ctx*)x;assert(c->order==1);c->order=2;c->evals++;}
static void alarm(void *x){b7_ctx*c=(b7_ctx*)x;assert(c->order==2);c->order=3;c->alarms++;}
static bool begin(void *x){b7_ctx*c=(b7_ctx*)x;assert(c->order==3);c->begins++;return true;}
static net001_host_link observe(void *x){b7_ctx*c=(b7_ctx*)x;assert(c->order==3);return c->link;}
static void cancel(void *x){(void)x;}
static void demo_payload(vg_telemetry_payload_t*p){memset(p,0,sizeof(*p));
 strcpy(p->device_id,"fixture");strcpy(p->boot_id,"boot");
 strcpy(p->firmware_version,"host");p->source_mode=VG_SOURCE_SIMULATION;
 p->channel_count=1u;strcpy(p->channels[0].name,"rpm");
 p->channels[0].quality=VG_QUALITY_VALID;p->channels[0].has_value=true;
 p->channels[0].value=0.0;}
'''
