/* B23 exact-witness readback and interrupted external-witness commit tests. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "phase9_b23_witness_commit_host.h"
static int make(vg_b20_slot *s,uint32_t gen,uint32_t confirmed,uint32_t tag) {
    net002_host_offline_store q;phase9_b8_ack_window ack;
    net002_host_init(&q);phase9_b8_ack_init(&ack);
    if(!net002_host_set_latest(&q,"0|null",6u) ||
       !net002_host_add_critical(&q,101u,2u,"alarm"))return 1;
    ack.last_accepted_sequence=confirmed;
    if(!phase9_b8_ack_begin(&ack,confirmed+1u,54u))return 2;
    return vg_b19_wrap(&q,&ack,tag,gen,s->bytes,sizeof(s->bytes),&s->len)?0:3;
}
static int test(void) {
    const uint32_t tag=VG_B18_DEVICE_TAG;
    vg_b20_slot before[2];memset(before,0,sizeof(before));
    if(make(&before[0],10u,7u,tag)||make(&before[1],11u,8u,tag))return 10;
    vg_b23_witness w={11u,8u};vg_b19_restored result;bool newer=true;
    if(!vg_b23_restore_witnessed(before,tag,&w,&result,&newer) || newer ||
       result.generation!=11u || result.ack.last_accepted_sequence!=8u ||
       result.ack.pending)return 11;
    net002_host_offline_store q;phase9_b8_ack_window ack;
    net002_host_init(&q);phase9_b8_ack_init(&ack);
    if(!net002_host_set_latest(&q,"0|null",6u) ||
       !net002_host_add_critical(&q,101u,2u,"alarm"))return 12;
    ack.last_accepted_sequence=9u;
    uint8_t candidate[VG_B19_SLOT_MAX];size_t n=0u;
    unsigned target=99u;uint32_t generation=0u;
    if(!vg_b23_prepare_witnessed(before,tag,&w,&q,&ack,candidate,
       sizeof(candidate),&n,&target,&generation) ||
       target!=0u || generation!=12u || n==0u)return 13;
    vg_b20_slot after[2];memcpy(after,before,sizeof(before));
    memcpy(after[target].bytes,candidate,n);after[target].len=n;
    /* Witness is still old even when the newer candidate is complete. */
    if(!vg_b23_restore_witnessed(after,tag,&w,&result,&newer) || !newer ||
       result.generation!=11u || result.ack.last_accepted_sequence!=8u)return 14;
    vg_b23_witness proposed={97u,97u};
    if(!vg_b23_propose_after_readback(before,after,tag,&w,candidate,n,
       target,generation,9u,&proposed) || proposed.generation!=12u ||
       proposed.confirmed_ack!=9u)return 15;
    /* External witness update failed: no silent ACK promotion. */
    if(!vg_b23_restore_witnessed(after,tag,&w,&result,&newer) ||
       result.generation!=11u || result.ack.last_accepted_sequence!=8u)return 16;
    /* With an independently advanced external witness, select new data. */
    if(!vg_b23_restore_witnessed(after,tag,&proposed,&result,&newer) || newer ||
       result.generation!=12u || result.ack.last_accepted_sequence!=9u ||
       result.ack.pending)return 17;
    /* Never start a second candidate with a prior, unconfirmed witness. */
    size_t old_n=n;unsigned old_t=target;uint32_t old_g=generation;
    if(vg_b23_prepare_witnessed(after,tag,&w,&q,&ack,candidate,
       sizeof(candidate),&n,&target,&generation) ||
       old_n!=n || old_t!=target || old_g!=generation)return 18;
    /* Half write, bit flip, stale tail and other-slot tamper reject proposal. */
    vg_b20_slot bad[2];vg_b23_witness sentinel={97u,97u};
    memcpy(bad,after,sizeof(bad));bad[0].len=n-1u;
    if(vg_b23_propose_after_readback(before,bad,tag,&w,candidate,n,
       target,generation,9u,&sentinel) || sentinel.generation!=97u)return 19;
    memcpy(bad,after,sizeof(bad));bad[0].bytes[n/2u]^=1u;
    if(vg_b23_propose_after_readback(before,bad,tag,&w,candidate,n,
       target,generation,9u,&sentinel) || sentinel.confirmed_ack!=97u)return 20;
    memcpy(bad,after,sizeof(bad));bad[1].bytes[20]^=1u;
    if(vg_b23_propose_after_readback(before,bad,tag,&w,candidate,n,
       target,generation,9u,&sentinel))return 21;
    if(vg_b23_propose_after_readback(before,after,tag,&w,candidate,n,
       1u,generation,9u,&sentinel) ||
       vg_b23_propose_after_readback(before,after,tag,&w,candidate,n,
       2u,generation,9u,&sentinel) ||
       vg_b23_propose_after_readback(before,after,tag,&w,candidate,n,
       0u,generation,7u,&sentinel))return 22;
    /* Old trusted witness after old slot loss must not choose newer data. */
    memcpy(bad,after,sizeof(bad));bad[1].len=0u;
    vg_b19_restored keep=result;bool keep_newer=newer;
    if(vg_b23_restore_witnessed(bad,tag,&w,&result,&newer) ||
       memcmp(&keep,&result,sizeof(result))!=0 || newer!=keep_newer)return 23;
    /* Split-brain same-generation but divergent byte content is invalid. */
    memcpy(bad,before,sizeof(bad));
    if(make(&bad[0],11u,9u,tag) ||
       vg_b23_restore_witnessed(bad,tag,&w,&result,&newer))return 24;
    /* No witness = no trust, and failed inputs cannot mutate outputs. */
    if(vg_b23_restore_witnessed(before,tag,NULL,&result,&newer) ||
       vg_b23_restore_witnessed(before,tag+1u,&w,&result,&newer) ||
       vg_b23_restore_witnessed(before,tag,&(vg_b23_witness){0u,0u},
       &result,&newer))return 25;
    vg_b23_witness max={UINT32_MAX,8u};
    if(vg_b23_prepare_witnessed(before,tag,&max,&q,&ack,candidate,
       sizeof(candidate),&n,&target,&generation))return 26;
    /* Corrupted candidate with newer witness is never promoted. */
    memcpy(bad,after,sizeof(bad));bad[0].bytes[15]^=0x80u;
    if(vg_b23_restore_witnessed(bad,tag,&proposed,&result,&newer))return 27;
    return 0;
}
int main(void){int r=test();if(r){fprintf(stderr,"B23_FAIL=%d\n",r);return r;}
 puts("B23_WITNESS_COMMIT=PASS_HOST_STAGE_READBACK_EXACT_WITNESS_INTERRUPTED_UPDATE");
 puts("B23_EXTERNAL_WITNESS=CALLER_MUST_AUTHENTICATE_AND_PERSIST_INDEPENDENTLY");
 puts("B23_ESP_NVS_POWERLOSS_NETWORK_DB=NOT_VERIFIED");return 0;
}
