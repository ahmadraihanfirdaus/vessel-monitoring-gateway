/* HOST-only independent monotonic witness and split-brain regression. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "phase9_b22_guarded_restore_host.h"
static int slot(vg_b20_slot *s,uint32_t gen,uint32_t ackval,uint32_t tag){
 net002_host_offline_store q;phase9_b8_ack_window ack;
 net002_host_init(&q);phase9_b8_ack_init(&ack);
 if(!net002_host_set_latest(&q,"0|null",6u) ||
    !net002_host_add_critical(&q,101u,2u,"alarm"))return 1;
 ack.last_accepted_sequence=ackval;
 if(!phase9_b8_ack_begin(&ack,ackval+1u,43u))return 2;
 return vg_b19_wrap(&q,&ack,tag,gen,s->bytes,sizeof(s->bytes),&s->len)?0:3;
}
int main(void){
 vg_b20_slot s[2];memset(s,0,sizeof(s));
 const uint32_t tag=VG_B18_DEVICE_TAG;
 if(slot(&s[0],10u,7u,tag)||slot(&s[1],11u,8u,tag))return 10;
 vg_b22_floor strict={11u,8u},lenient={10u,7u};
 vg_b19_restored result;bool degraded=true;
 if(!vg_b22_restore_guarded(s,tag,&strict,&result,&degraded)||
    result.generation!=11u || result.ack.last_accepted_sequence!=8u ||
    result.ack.pending || degraded)return 11;
 vg_b20_slot bad[2];memcpy(bad,s,sizeof(s));bad[1].bytes[20]^=1u;
 if(!vg_b22_restore_guarded(bad,tag,&lenient,&result,&degraded)||
    result.generation!=10u || result.ack.last_accepted_sequence!=7u ||
    result.ack.pending || !degraded)return 12;
 /* A stricter trusted witness must reject the older fallback. */
 vg_b19_restored sentinel=result;bool old_degraded=degraded;
 if(vg_b22_restore_guarded(bad,tag,&strict,&result,&degraded)||
    memcmp(&sentinel,&result,sizeof(result))!=0||degraded!=old_degraded)return 13;
 vg_b22_floor bad_ack_floor={10u,9u},future={12u,0u},zero={0u,0u};
 if(vg_b22_restore_guarded(s,tag,&bad_ack_floor,&result,&degraded)||
    vg_b22_restore_guarded(s,tag,&future,&result,&degraded)||
    vg_b22_restore_guarded(s,tag,&zero,&result,&degraded))return 14;
 /* Both good at same generation but different payload is split brain. */
 vg_b20_slot conflict[2];memcpy(conflict,s,sizeof(s));
 if(slot(&conflict[0],11u,9u,tag) ||
    vg_b22_restore_guarded(conflict,tag,&strict,&result,&degraded))return 15;
 /* Exactly identical replicas are acceptable. */
 memcpy(conflict,s,sizeof(s));conflict[0]=s[1];
 if(!vg_b22_restore_guarded(conflict,tag,&strict,&result,&degraded)||
    result.generation!=11u || degraded)return 16;
 /* Identity rejection is mandatory despite checksum-valid slots. */
 if(vg_b22_restore_guarded(s,tag+1u,&strict,&result,&degraded)||
    vg_b22_restore_guarded(s,0u,&strict,&result,&degraded)||
    vg_b22_restore_guarded(s,tag,NULL,&result,&degraded)||
    vg_b22_restore_guarded(s,tag,&strict,NULL,&degraded))return 17;
 /* Prepare generation 12 without regressing the authenticated witness. */
 net002_host_offline_store q;phase9_b8_ack_window ack;
 net002_host_init(&q);phase9_b8_ack_init(&ack);
 if(!net002_host_set_latest(&q,"0|null",6u) ||
    !net002_host_add_critical(&q,101u,2u,"alarm"))return 18;
 ack.last_accepted_sequence=9u;
 uint8_t candidate[VG_B19_SLOT_MAX];size_t n=0u;
 unsigned target=99u;uint32_t generation=0u;
 if(!vg_b22_prepare_guarded(s,tag,&strict,&q,&ack,candidate,
    sizeof(candidate),&n,&target,&generation) || target!=0u ||
    generation!=12u || !vg_b20_verify_readback(candidate,n,candidate,n,
    tag,12u,9u))return 19;
 /* A replayed lower trusted witness cannot authorize ACK regression. */
 ack.last_accepted_sequence=7u;
 if(vg_b22_prepare_guarded(s,tag,&strict,&q,&ack,candidate,
    sizeof(candidate),&n,&target,&generation))return 20;
 /* Restored generation 12 must satisfy a newly advanced witness. */
 vg_b20_slot updated[2];memcpy(updated,s,sizeof(s));
 ack.last_accepted_sequence=9u;
 size_t candidate_n=0u;
 if(!vg_b22_prepare_guarded(s,tag,&strict,&q,&ack,candidate,
    sizeof(candidate),&candidate_n,&target,&generation))return 21;
 updated[target].len=candidate_n;
 memcpy(updated[target].bytes,candidate,candidate_n);
 vg_b22_floor advanced={12u,9u};
 if(!vg_b22_restore_guarded(updated,tag,&advanced,&result,&degraded)||
    result.generation!=12u||result.ack.last_accepted_sequence!=9u)return 22;
 if(vg_b22_restore_guarded(s,tag,&advanced,&result,&degraded))return 23;
 /* Wrap is never silently accepted by generation update logic. */
 uint32_t next=0u;
 if(vg_b19_next_generation(UINT32_MAX,&next))return 24;
 puts("B22_GUARDED=PASS_14_HOST_SCENARIOS_FLOOR_ROLLBACK_SPLIT_BRAIN_ACK");
 puts("B22_WITNESS=EXTERNAL_TRUSTED_INPUT_NOT_CRYPTOGRAPHICALLY_VERIFIED");
 puts("B22_STORAGE_HARDWARE_NETWORK=NOT_VERIFIED");
 return 0;
}
