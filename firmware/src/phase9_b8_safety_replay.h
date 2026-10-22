#ifndef PHASE9_B8_SAFETY_REPLAY_H
#define PHASE9_B8_SAFETY_REPLAY_H
/* Host simulation only: local alarm must be cleared before accepting replay ACK. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b8_alarm_latch.h"
#include "phase9_b8_ack_window.h"
typedef struct {bool local_safe;bool ack_applied;bool alarm_latched;}phase9_b8_safety_replay_result;
static inline phase9_b8_safety_replay_result phase9_b8_safety_replay_step(
 phase9_b8_alarm_latch*alarm,phase9_b8_ack_window*window,
 bool sampled,bool evaluated,bool alarm_present,bool explicit_operator_ack,
 uint32_t sequence,uint32_t correlation,bool response_verified,bool server_accepted){
 phase9_b8_safety_replay_result r={false,false,true};
 if(!alarm||!window)return r;
 r.local_safe=phase9_b8_alarm_observe(alarm,sampled,evaluated,alarm_present);
 if(alarm->latched&&explicit_operator_ack){
  (void)phase9_b8_alarm_clear(alarm,true);
  r.local_safe=!alarm->latched;
 }
 r.alarm_latched=alarm->latched;
 if(!r.local_safe)return r;
 r.ack_applied=phase9_b8_ack_commit(window,sequence,correlation,
   response_verified,server_accepted,true);
 return r;
}
#endif
