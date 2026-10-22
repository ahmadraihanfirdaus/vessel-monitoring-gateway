#ifndef PHASE9_B8_ALARM_LATCH_H
#define PHASE9_B8_ALARM_LATCH_H
/* HOST ONLY: deterministic local alarm persistence; no physical safety claim. */
#include <stdbool.h>
#include <stdint.h>
typedef struct {bool latched;bool last_clean;uint8_t clean_streak;}phase9_b8_alarm_latch;
static inline void phase9_b8_alarm_init(phase9_b8_alarm_latch *s){
 if(s){s->latched=false;s->last_clean=false;s->clean_streak=0u;}}
static inline bool phase9_b8_alarm_observe(phase9_b8_alarm_latch *s,
 bool sampled,bool evaluated,bool alarm_present){
 if(!s)return false;
 if(!sampled||!evaluated||alarm_present){
  s->latched=true;s->last_clean=false;s->clean_streak=0u;return false;
 }
 s->last_clean=true;
 if(s->clean_streak<3u)s->clean_streak++;
 return !s->latched;
}
static inline bool phase9_b8_alarm_clear(phase9_b8_alarm_latch *s,bool explicit_ack){
 if(!s||!explicit_ack||!s->last_clean||s->clean_streak<3u)return false;
 s->latched=false;s->clean_streak=0u;return true;
}
#endif
