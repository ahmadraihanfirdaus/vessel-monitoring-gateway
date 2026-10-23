/* B19 two-process host fixture; NEVER accesses application DB or ESP flash. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b19_dual_slot_host.h"
static int make_store(net002_host_offline_store *s,phase9_b8_ack_window *ack,uint32_t high) {
    net002_host_init(s);phase9_b8_ack_init(ack);
    if(!net002_host_set_latest(s,"zero=0,null=null",16u))return 1;
    for(uint32_t i=1u;i<=10u;++i) {
        char txt[24];
        if(snprintf(txt,sizeof(txt),"alarm-%u",(unsigned)i)<0 ||
           !net002_host_add_critical(s,i,i*50u,txt))return 2;
    }
    if(!phase9_b8_ack_begin(ack,high,high+1u) ||
       !phase9_b8_ack_commit(ack,high,high+1u,true,true,true) ||
       !phase9_b8_ack_begin(ack,high+1u,high+2u))return 3;
    return 0;
}
static int output_slot(const char *path,uint32_t generation,uint32_t high) {
    net002_host_offline_store s;phase9_b8_ack_window ack;
    if(make_store(&s,&ack,high))return 10;
    uint8_t bytes[VG_B19_SLOT_MAX];size_t len=0;
    if(!vg_b19_wrap(&s,&ack,VG_B18_DEVICE_TAG,generation,bytes,sizeof(bytes),&len))return 11;
    FILE *fp=fopen(path,"wb");if(!fp)return 12;
    bool good=(fwrite(bytes,1u,len,fp)==len && fflush(fp)==0);
    if(fclose(fp)!=0 || !good)return 13;
    return 0;
}
static size_t load(const char *path,uint8_t *out,size_t cap) {
    FILE *fp=fopen(path,"rb");if(!fp)return 0u;
    size_t n=fread(out,1u,cap,fp);
    if(ferror(fp)){fclose(fp);return 0u;}
    if(fclose(fp)!=0)return 0u;
    return n;
}
static int restore(const char *path_a,const char *path_b,int want_fallback) {
    uint8_t a[VG_B19_SLOT_MAX+1u],b[VG_B19_SLOT_MAX+1u];
    size_t na=load(path_a,a,sizeof(a)),nb=load(path_b,b,sizeof(b));
    vg_b19_restored recovered;memset(&recovered,0,sizeof(recovered));
    bool degraded=false;
    if(!vg_b19_select(a,na,b,nb,VG_B18_DEVICE_TAG,&recovered,&degraded))return 22;
    if(degraded!=(want_fallback!=0) || recovered.generation!=(want_fallback ? 10u:11u) ||
        recovered.ack.last_accepted_sequence!=(want_fallback ? 7u:8u) ||
        recovered.ack.pending || recovered.ack.pending_correlation ||
        recovered.ack.pending_sequence || recovered.store.count!=8u ||
        recovered.store.evicted_count!=2u || !recovered.store.has_latest)return 23;
    if(phase9_b8_ack_commit(&recovered.ack,9u,10u,true,true,true))return 24;
    if(!phase9_b8_ack_begin(&recovered.ack,9u,51u) ||
       phase9_b8_ack_commit(&recovered.ack,9u,52u,true,true,true))return 25;
    printf("B19_RESTART=PASS_GEN_%u_DEGRADED_%d_ACK_%u_PENDING_RESET\n",
        (unsigned)recovered.generation,degraded ? 1:0,
        (unsigned)recovered.ack.last_accepted_sequence);
    return 0;
}
static int negatives(void) {
    net002_host_offline_store s;phase9_b8_ack_window ack;
    if(make_store(&s,&ack,7u))return 30;
    uint8_t a[VG_B19_SLOT_MAX],b[VG_B19_SLOT_MAX],tiny[8u];
    size_t na=0u,nb=0u,sentinel=987u;
    memset(tiny,0xa5,sizeof(tiny));
    if(vg_b19_wrap(&s,&ack,VG_B18_DEVICE_TAG,10u,tiny,sizeof(tiny),&sentinel) ||
       sentinel!=987u)return 31;
    for(size_t i=0;i<sizeof(tiny);++i)if(tiny[i]!=0xa5)return 32;
    if(!vg_b19_wrap(&s,&ack,VG_B18_DEVICE_TAG,10u,a,sizeof(a),&na) ||
       !vg_b19_wrap(&s,&ack,VG_B18_DEVICE_TAG,11u,b,sizeof(b),&nb))return 33;
    vg_b19_restored dest;memset(&dest,0xa5,sizeof(dest));
    vg_b19_restored preserved=dest;bool degraded=true;
    uint8_t corrupt[VG_B19_SLOT_MAX];memcpy(corrupt,a,na);corrupt[6]^=1u;
    if(vg_b19_decode(corrupt,na,VG_B18_DEVICE_TAG,&dest) ||
       vg_b19_decode(a,na,VG_B18_DEVICE_TAG+1u,&dest) ||
       vg_b19_decode(a,na-1u,VG_B18_DEVICE_TAG,&dest) ||
       vg_b19_select(corrupt,na,corrupt,na,VG_B18_DEVICE_TAG,&dest,&degraded))return 34;
    if(memcmp(&dest,&preserved,sizeof(dest))!=0 || !degraded)return 35;
    /* Same generation but different valid contents must be rejected atomically. */
    if(!vg_b19_wrap(&s,&ack,VG_B18_DEVICE_TAG,10u,b,sizeof(b),&nb))return 36;
    if(!net002_host_add_critical(&s,11u,550u,"new") ||
       !vg_b19_wrap(&s,&ack,VG_B18_DEVICE_TAG,10u,b,sizeof(b),&nb))return 37;
    if(vg_b19_select(a,na,b,nb,VG_B18_DEVICE_TAG,&dest,&degraded) ||
       memcmp(&dest,&preserved,sizeof(dest))!=0)return 38;
    uint32_t next=777u;
    if(vg_b19_next_generation(UINT32_MAX,&next) || next!=777u ||
       !vg_b19_next_generation(10u,&next) || next!=11u)return 39;
    puts("B19_NEGATIVE=PASS_SIZE_ID_CORRUPT_TRUNCATE_AMBIGUOUS_ATOMIC_WRAP_REFUSAL");
    return 0;
}
int main(int argc,char **argv) {
    if(argc==2 && strcmp(argv[1],"negative")==0)return negatives();
    if(argc==4 && strcmp(argv[1],"write")==0) {
        int r=output_slot(argv[2],10u,7u);
        if(r)return r;
        r=output_slot(argv[3],11u,8u);
        if(!r)puts("B19_WRITE=PASS_GEN_10_11_TWO_SLOTS");
        return r;
    }
    if(argc==5 && strcmp(argv[1],"restore")==0)
        return restore(argv[2],argv[3],strcmp(argv[4],"fallback")==0);
    return 2;
}
