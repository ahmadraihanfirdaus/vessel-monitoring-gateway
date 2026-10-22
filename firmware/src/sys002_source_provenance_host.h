#ifndef SYS002_SOURCE_PROVENANCE_HOST_H
#define SYS002_SOURCE_PROVENANCE_HOST_H
/* SYS-002 narrow host provenance validation; no automatic promotion to PHYSICAL. */
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
typedef enum {SYS002_SIMULATION=0,SYS002_BENCH_TEST=1,SYS002_PHYSICAL=2} sys002_source_mode;
static inline bool sys002_parse_source(const char *label,sys002_source_mode *out) {
 if(!label || !out) return false;
 if(strcmp(label,"simulation")==0){*out=SYS002_SIMULATION;return true;}
 if(strcmp(label,"bench_test")==0){*out=SYS002_BENCH_TEST;return true;}
 if(strcmp(label,"physical")==0){*out=SYS002_PHYSICAL;return true;}
 return false;
}
static inline const char *sys002_source_label(sys002_source_mode mode) {
 switch(mode){case SYS002_SIMULATION:return "simulation";case SYS002_BENCH_TEST:return "bench_test";case SYS002_PHYSICAL:return "physical";default:return NULL;}
}
#endif
