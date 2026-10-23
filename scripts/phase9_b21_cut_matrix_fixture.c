/* Host C99 exhaustive prefix and one-bit fault matrix. No disk/ESP IO. */
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b21_cut_matrix_host.h"
static int init(net002_host_offline_store *store,phase9_b8_ack_window *ack,uint32_t n){
    net002_host_init(store);phase9_b8_ack_init(ack);
    if(!net002_host_set_latest(store,"0|null",6u))return 1;
    for(uint32_t i=1u;i<=5u;++i)
        if(!net002_host_add_critical(store,i,i*7u,"alarm"))return 2;
    ack->last_accepted_sequence=n;
    if(!phase9_b8_ack_begin(ack,n+1u,90u))return 3;
    return 0;
}
int main(void){
    net002_host_offline_store store;phase9_b8_ack_window ack;
    vg_b20_slot slots[2];memset(slots,0,sizeof(slots));
    if(init(&store,&ack,7u)||!vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,10u,
        slots[0].bytes,sizeof(slots[0].bytes),&slots[0].len))return 10;
    if(init(&store,&ack,8u)||!vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,11u,
        slots[1].bytes,sizeof(slots[1].bytes),&slots[1].len))return 11;
    vg_b20_slot older=slots[0],latest=slots[1];
    if(init(&store,&ack,9u))return 12;
    uint8_t candidate[VG_B19_SLOT_MAX];size_t size=0u;
    unsigned target=99u;uint32_t generation=0u;
    if(!vg_b20_prepare(slots,VG_B18_DEVICE_TAG,&store,&ack,candidate,
        sizeof(candidate),&size,&target,&generation) ||
        target!=0u || generation!=12u || size<=VG_B19_SLOT_OVERHEAD)return 13;
    uint32_t truncs=0u,tails=0u,flips=0u;
    for(size_t cut=0u;cut<size;++cut){
        vg_b20_slot damaged;
        if(!vg_b21_inject_prefix(&older,candidate,size,cut,false,&damaged)||
           !vg_b21_fallback_is_conservative(&damaged,&latest,VG_B18_DEVICE_TAG,11u,8u)||
           vg_b20_verify_readback(candidate,size,damaged.bytes,damaged.len,
               VG_B18_DEVICE_TAG,12u,9u))return 20;
        ++truncs;
        if(!vg_b21_inject_prefix(&older,candidate,size,cut,true,&damaged)||
           !vg_b21_fallback_is_conservative(&damaged,&latest,VG_B18_DEVICE_TAG,11u,8u)||
           vg_b20_verify_readback(candidate,size,damaged.bytes,damaged.len,
               VG_B18_DEVICE_TAG,12u,9u))return 21;
        ++tails;
        /* The latest good slot remains unmodified for every injected cut. */
        if(memcmp(latest.bytes,slots[1].bytes,latest.len))return 22;
    }
    for(size_t off=0u;off<size;++off){
        for(unsigned bit=0u;bit<8u;++bit){
            vg_b20_slot damaged;memset(&damaged,0,sizeof(damaged));
            memcpy(damaged.bytes,candidate,size);damaged.len=size;
            damaged.bytes[off]^=(uint8_t)(1u<<bit);
            if(!vg_b21_fallback_is_conservative(&damaged,&latest,VG_B18_DEVICE_TAG,11u,8u)||
               vg_b20_verify_readback(candidate,size,damaged.bytes,damaged.len,
                    VG_B18_DEVICE_TAG,12u,9u))return 23;
            ++flips;
        }
    }
    vg_b20_slot good;
    if(!vg_b21_inject_prefix(&older,candidate,size,size,false,&good)||
       !vg_b20_verify_readback(candidate,size,good.bytes,good.len,
           VG_B18_DEVICE_TAG,12u,9u))return 24;
    vg_b19_restored selected;bool degraded=false;
    if(!vg_b19_select(good.bytes,good.len,latest.bytes,latest.len,
       VG_B18_DEVICE_TAG,&selected,&degraded) ||
       selected.generation!=12u || selected.ack.last_accepted_sequence!=9u ||
       selected.ack.pending || degraded)return 25;
    /* Guard output immutability for malformed injection arguments. */
    vg_b20_slot sentinel=older,unchanged=older;
    if(vg_b21_inject_prefix(&older,candidate,size,size+1u,true,&sentinel)||
       memcmp(&sentinel,&unchanged,sizeof(sentinel))!=0)return 26;
    if(vg_b21_inject_prefix(&older,candidate,size,0u,false,NULL))return 27;
    printf("B21_MATRIX=PASS_TRUNC_%" PRIu32 "_STALE_TAIL_%" PRIu32 "_ONE_BIT_%" PRIu32 "\n",truncs,tails,flips);
    printf("B21_BASELINE=PASS_OLD_GEN11_ACK8_ACTIVE_UNTOUCHED_CANDIDATE_GEN12_ACK9\n");
    printf("B21_LIMIT=HOST_MEMORY_FAULT_MODEL_NOT_DISK_ATOMICITY_NVS_POWERLOSS\n");
    return 0;
}
