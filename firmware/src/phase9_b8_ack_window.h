#ifndef PHASE9_B8_ACK_WINDOW_H
#define PHASE9_B8_ACK_WINDOW_H
/* HOST ONLY: no persistent storage, network authentication or durable ACK. */
#include <stdbool.h>
#include <stdint.h>
typedef struct {
 uint32_t last_accepted_sequence;
 uint32_t pending_sequence;
 uint32_t pending_correlation;
 bool pending;
}phase9_b8_ack_window;
static inline void phase9_b8_ack_init(phase9_b8_ack_window*w){
 if(w){w->last_accepted_sequence=0u;w->pending_sequence=0u;
 w->pending_correlation=0u;w->pending=false;}}
static inline bool phase9_b8_ack_begin(phase9_b8_ack_window*w,
 uint32_t sequence,uint32_t correlation){
 if(!w||w->pending||sequence==0u||correlation==0u||
    sequence<=w->last_accepted_sequence)return false;
 w->pending_sequence=sequence;w->pending_correlation=correlation;
 w->pending=true;return true;
}
static inline bool phase9_b8_ack_commit(phase9_b8_ack_window*w,
 uint32_t sequence,uint32_t correlation,bool response_verified,
 bool server_accepted,bool safety_ok){
 if(!w||!w->pending||!response_verified||!server_accepted||!safety_ok||
    w->pending_sequence!=sequence||w->pending_correlation!=correlation)return false;
 w->last_accepted_sequence=sequence;w->pending=false;
 w->pending_sequence=0u;w->pending_correlation=0u;return true;
}
static inline void phase9_b8_ack_cancel(phase9_b8_ack_window*w){
 if(w){w->pending=false;w->pending_sequence=0u;w->pending_correlation=0u;}}
#endif
