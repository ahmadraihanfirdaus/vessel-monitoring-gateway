/* Native host update/readback/restart fixture; NOT filesystem atomicity proof. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b20_slot_prepare_host.h"

static int setup(net002_host_offline_store *store,phase9_b8_ack_window *ack,
    uint32_t accepted) {
    net002_host_init(store);phase9_b8_ack_init(ack);
    if(!net002_host_set_latest(store,"0|null",6u))return 1;
    for(uint32_t i=1u;i<=5u;++i)
        if(!net002_host_add_critical(store,i,i*7u,"alarm"))return 2;
    ack->last_accepted_sequence=accepted;
    if(!phase9_b8_ack_begin(ack,accepted+1u,90u))return 3;
    return 0;
}
static bool save(const char *path,const uint8_t *raw,size_t n) {
    FILE *f=fopen(path,"wb");if(!f)return false;
    bool ok=fwrite(raw,1u,n,f)==n && fflush(f)==0;
    if(fclose(f)!=0)ok=false;
    return ok;
}
static bool read_slot(const char *path,vg_b20_slot *slot) {
    memset(slot,0,sizeof(*slot));
    FILE *f=fopen(path,"rb");if(!f)return false;
    size_t n=fread(slot->bytes,1u,VG_B19_SLOT_MAX,f);
    bool ok=!ferror(f) && feof(f);
    if(fclose(f)!=0)ok=false;
    slot->len=n;
    return ok;
}
static int bootstrap(const char *a,const char *b) {
    net002_host_offline_store store;phase9_b8_ack_window ack;
    uint8_t raw[VG_B19_SLOT_MAX];size_t n=0;
    if(setup(&store,&ack,7u)||!vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,10u,raw,sizeof(raw),&n)||!save(a,raw,n))return 10;
    if(setup(&store,&ack,8u)||!vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,11u,raw,sizeof(raw),&n)||!save(b,raw,n))return 11;
    puts("B20_BOOTSTRAP=PASS_10_11");return 0;
}
static int update(const char *a,const char *b,const char *mode) {
    vg_b20_slot slots[2];
    if(!read_slot(a,&slots[0])||!read_slot(b,&slots[1]))return 12;
    net002_host_offline_store store;phase9_b8_ack_window ack;
    if(setup(&store,&ack,9u))return 13;
    uint8_t candidate[VG_B19_SLOT_MAX]={0};size_t n=0u;
    unsigned target=99u;uint32_t generation=0u;
    if(!vg_b20_prepare(slots,VG_B18_DEVICE_TAG,&store,&ack,
        candidate,sizeof(candidate),&n,&target,&generation) ||
        target!=0u || generation!=12u)return 14;
    const char *path=target==0u?a:b;
    if(strcmp(mode,"torn")==0) {
        if(!save(path,candidate,n-2u))return 15;
        puts("B20_UPDATE=INJECT_TORN_TARGET0");return 0;
    }
    if(strcmp(mode,"bitflip")==0) {
        candidate[23]^=1u;
        if(!save(path,candidate,n))return 16;
        puts("B20_UPDATE=INJECT_BITFLIP_TARGET0");return 0;
    }
    if(strcmp(mode,"good")!=0)return 17;
    if(!save(path,candidate,n))return 18;
    vg_b20_slot written;
    if(!read_slot(path,&written) ||
       !vg_b20_verify_readback(candidate,n,written.bytes,written.len,
       VG_B18_DEVICE_TAG,generation,9u))return 19;
    puts("B20_UPDATE=PASS_GEN_12_TARGET0_READBACK_VERIFIED");return 0;
}
static int recovery(const char *a,const char *b,int generation,int degraded) {
    vg_b20_slot slots[2];
    if(!read_slot(a,&slots[0])||!read_slot(b,&slots[1]))return 20;
    vg_b19_restored restored;bool is_degraded=false;
    if(!vg_b19_select(slots[0].bytes,slots[0].len,slots[1].bytes,
        slots[1].len,VG_B18_DEVICE_TAG,&restored,&is_degraded))return 21;
    if(restored.generation!=(uint32_t)generation ||
       restored.ack.last_accepted_sequence!=(generation==12 ? 9u : 8u) ||
       is_degraded!=(degraded!=0) || restored.ack.pending ||
       restored.ack.pending_sequence || restored.ack.pending_correlation)
       return 22;
    printf("B20_RESTART=PASS_GEN_%u_DEGRADED_%d_ACK_%u_PENDING_RESET\n",
      (unsigned)restored.generation,is_degraded?1:0,
      (unsigned)restored.ack.last_accepted_sequence);
    return 0;
}
static int negatives(void) {
    net002_host_offline_store store;phase9_b8_ack_window ack;
    if(setup(&store,&ack,8u))return 30;
    vg_b20_slot slots[2];memset(slots,0,sizeof(slots));
    uint8_t out[VG_B19_SLOT_MAX];memset(out,0xaa,sizeof(out));
    size_t n=321u;unsigned target=88u;uint32_t generation=444u;
    if(vg_b20_prepare(slots,VG_B18_DEVICE_TAG,&store,&ack,
       out,sizeof(out),&n,&target,&generation) ||
       n!=321u||target!=88u||generation!=444u)return 31;
    for(size_t i=0;i<sizeof(out);++i)if(out[i]!=0xaa)return 32;
    if(!vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,UINT32_MAX,
       slots[0].bytes,sizeof(slots[0].bytes),&slots[0].len))return 33;
    if(vg_b20_prepare(slots,VG_B18_DEVICE_TAG,&store,&ack,
       out,sizeof(out),&n,&target,&generation))return 34;
    if(!vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,8u,
       slots[0].bytes,sizeof(slots[0].bytes),&slots[0].len))return 35;
    ack.last_accepted_sequence=7u;
    if(vg_b20_prepare(slots,VG_B18_DEVICE_TAG,&store,&ack,
       out,sizeof(out),&n,&target,&generation))return 36;
    ack.last_accepted_sequence=9u;
    if(!vg_b20_prepare(slots,VG_B18_DEVICE_TAG,&store,&ack,
       out,sizeof(out),&n,&target,&generation)||target!=1u||generation!=9u)return 37;
    if(vg_b20_verify_readback(out,n,out,n-1u,VG_B18_DEVICE_TAG,9u,9u))return 38;
    uint8_t altered[VG_B19_SLOT_MAX];memcpy(altered,out,n);altered[8]^=1u;
    if(vg_b20_verify_readback(out,n,altered,n,VG_B18_DEVICE_TAG,9u,9u))return 39;
    if(!vg_b20_verify_readback(out,n,out,n,VG_B18_DEVICE_TAG,9u,9u))return 40;
    /* Same generation with divergent valid payloads = split-brain, refuse. */
    if(!vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,8u,
       slots[1].bytes,sizeof(slots[1].bytes),&slots[1].len))return 41;
    if(!net002_host_add_critical(&store,6u,7u,"different") ||
       !vg_b19_wrap(&store,&ack,VG_B18_DEVICE_TAG,8u,
       slots[1].bytes,sizeof(slots[1].bytes),&slots[1].len))return 42;
    if(vg_b20_prepare(slots,VG_B18_DEVICE_TAG,&store,&ack,
       out,sizeof(out),&n,&target,&generation))return 43;
    puts("B20_NEGATIVE=PASS_NO_BOOTSTRAP_NO_WRAP_NO_ACK_ROLLBACK_READBACK_SPLIT_BRAIN");
    return 0;
}
int main(int argc,char **argv) {
    if(argc==2 && strcmp(argv[1],"negative")==0)return negatives();
    if(argc==4 && strcmp(argv[1],"bootstrap")==0)return bootstrap(argv[2],argv[3]);
    if(argc==5 && strcmp(argv[1],"update")==0)return update(argv[2],argv[3],argv[4]);
    if(argc==6 && strcmp(argv[1],"recover")==0)return recovery(argv[2],argv[3],atoi(argv[4]),atoi(argv[5]));
    return 2;
}
