/* Host ABI-only cross-process fixture; no real authenticated witness source. */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b25_observation_epoch_host.h"
typedef struct {
    vg_b20_slot before[2],after[2];
    vg_b24_ticket ticket;
    uint8_t expected[VG_B19_SLOT_MAX];
    size_t size;
} fixture;
static int slot(vg_b20_slot *s,uint32_t generation,uint32_t ack_value,uint32_t tag){
    net002_host_offline_store q;phase9_b8_ack_window ack;
    net002_host_init(&q);phase9_b8_ack_init(&ack);
    if(!net002_host_set_latest(&q,"0|null",6u) ||
       !net002_host_add_critical(&q,101u,2u,"alarm"))return 1;
    ack.last_accepted_sequence=ack_value;
    if(!phase9_b8_ack_begin(&ack,ack_value+1u,54u))return 2;
    return vg_b19_wrap(&q,&ack,tag,generation,s->bytes,
                       sizeof(s->bytes),&s->len)?0:3;
}
static int stage(const char *path){
    fixture f;memset(&f,0,sizeof(f));const uint32_t tag=VG_B18_DEVICE_TAG;
    if(slot(&f.before[0],10u,7u,tag) ||
       slot(&f.before[1],11u,8u,tag))return 10;
    memcpy(f.after,f.before,sizeof(f.before));
    if(slot(&f.after[0],12u,9u,tag))return 11;
    f.size=f.after[0].len;
    memcpy(f.expected,f.after[0].bytes,f.size);
    vg_b23_witness old={11u,8u};
    if(!vg_b24_issue_ticket(f.before,f.after,tag,&old,f.expected,f.size,
                             0u,12u,9u,&f.ticket))return 12;
    FILE *fp=fopen(path,"wb");if(!fp)return 13;
    bool ok=fwrite(&f,1,sizeof(f),fp)==sizeof(f);
    if(fclose(fp)!=0)ok=false;
    if(!ok)return 14;
    puts("B25_STAGE=PASS_HOST_ABI_UNTRUSTED_FIXTURE");return 0;
}
static int verify(const char *path,const char *mode){
    fixture f;FILE *fp=fopen(path,"rb");if(!fp)return 20;
    bool ok=fread(&f,1,sizeof(f),fp)==sizeof(f);
    if(fgetc(fp)!=EOF)ok=false;
    if(fclose(fp)!=0)ok=false;
    if(!ok)return 21;
    const uint32_t tag=VG_B18_DEVICE_TAG,domain=0xB251u;
    vg_b23_witness old={11u,8u},observed=old;
    vg_b25_observation_guard initial;
    if(!vg_b25_guard_seed(tag,domain,41u,&old,&initial))return 22;
    uint32_t use_tag=tag,use_domain=domain;
    uint64_t epoch=42u;
    bool good=false,repeat=false,second_old=false;
    if(!strcmp(mode,"old"))good=true;
    else if(!strcmp(mode,"new")){good=true;observed=f.ticket.proposed;}
    else if(!strcmp(mode,"repeat_new")){repeat=true;observed=f.ticket.proposed;}
    else if(!strcmp(mode,"repeat_old")){repeat=true;second_old=true;}
    else if(!strcmp(mode,"epoch_replay"))epoch=41u;
    else if(!strcmp(mode,"epoch_gap"))epoch=43u;
    else if(!strcmp(mode,"epoch_zero"))epoch=0u;
    else if(!strcmp(mode,"wrong_domain"))use_domain^=1u;
    else if(!strcmp(mode,"wrong_tag"))use_tag^=1u;
    else if(!strcmp(mode,"guard_witness"))initial.last_witness.confirmed_ack++;
    else if(!strcmp(mode,"bad_receipt"))f.ticket.candidate_crc32^=1u;
    else if(!strcmp(mode,"bad_slot"))f.after[0].bytes[20]^=1u;
    else if(!strcmp(mode,"bad_previous"))f.after[1].bytes[20]^=1u;
    else if(!strcmp(mode,"out_of_order")){observed.generation=12u;observed.confirmed_ack=8u;}
    else if(!strcmp(mode,"future")){observed.generation=13u;observed.confirmed_ack=10u;}
    else if(!strcmp(mode,"overflow"))initial.last_observation_epoch=UINT64_MAX;
    else if(!strcmp(mode,"zero_device"))use_tag=0u;
    else if(!strcmp(mode,"zero_domain"))use_domain=0u;
    else return 23;
    if(repeat){
        vg_b25_observation_guard intermediate;vg_b19_restored mid;bool yes=false;
        vg_b23_witness first=second_old?old:f.ticket.proposed;
        if(!vg_b25_observe(f.before,f.after,tag,domain,&initial,&f.ticket,
           f.expected,f.size,&first,42u,&intermediate,&mid,&yes))return 24;
        initial=intermediate;epoch=42u;
    }
    vg_b25_observation_guard next;memset(&next,0x5a,sizeof(next));
    vg_b19_restored recovered;memset(&recovered,0x5a,sizeof(recovered));
    vg_b25_observation_guard next_before=next;
    vg_b19_restored recovered_before=recovered;bool committed=true;
    bool result=vg_b25_observe(f.before,f.after,use_tag,use_domain,&initial,
        &f.ticket,f.expected,f.size,&observed,epoch,&next,&recovered,&committed);
    if(good){
        uint32_t want_generation=!strcmp(mode,"new")?12u:11u;
        uint32_t want_ack=!strcmp(mode,"new")?9u:8u;
        if(!result || next.last_observation_epoch!=42u ||
           next.last_witness.generation!=want_generation ||
           recovered.generation!=want_generation ||
           recovered.ack.last_accepted_sequence!=want_ack ||
           committed!=(!strcmp(mode,"new")) ||
           recovered.ack.pending || recovered.ack.pending_sequence ||
           recovered.ack.pending_correlation)return 25;
    } else if(result || memcmp(&next,&next_before,sizeof(next))!=0 ||
              memcmp(&recovered,&recovered_before,sizeof(recovered))!=0 ||
              committed!=true)return 26;
    printf("B25_OBSERVATION=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    int r=99;
    if(argc==3 && !strcmp(argv[1],"stage"))r=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))r=verify(argv[2],argv[3]);
    if(r)fprintf(stderr,"B25_FAIL=%d\n",r);
    return r;
}
