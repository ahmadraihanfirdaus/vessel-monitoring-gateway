/* B26 cross-process C99 host ABI test. No real authenticated sources. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b26_dual_witness_host.h"
typedef struct {
    vg_b20_slot before[2],after[2];
    vg_b24_ticket ticket;
    uint8_t expected[VG_B19_SLOT_MAX];
    size_t size;
} fixture;
static int prepare_slot(vg_b20_slot *s,uint32_t gen,uint32_t high,uint32_t tag){
    net002_host_offline_store q;phase9_b8_ack_window ack;
    net002_host_init(&q);phase9_b8_ack_init(&ack);
    if(!net002_host_set_latest(&q,"0|null",6u) ||
       !net002_host_add_critical(&q,101u,2u,"alarm"))return 1;
    ack.last_accepted_sequence=high;
    if(!phase9_b8_ack_begin(&ack,high+1u,54u))return 2;
    return vg_b19_wrap(&q,&ack,tag,gen,s->bytes,sizeof(s->bytes),&s->len)?0:3;
}
static int stage(const char *path){
    fixture f;memset(&f,0,sizeof(f));const uint32_t tag=VG_B18_DEVICE_TAG;
    if(prepare_slot(&f.before[0],10u,7u,tag) ||
       prepare_slot(&f.before[1],11u,8u,tag))return 10;
    memcpy(f.after,f.before,sizeof(f.before));
    if(prepare_slot(&f.after[0],12u,9u,tag))return 11;
    f.size=f.after[0].len;
    memcpy(f.expected,f.after[0].bytes,f.size);
    vg_b23_witness old={11u,8u};
    if(!vg_b24_issue_ticket(f.before,f.after,tag,&old,f.expected,f.size,
       0u,12u,9u,&f.ticket))return 12;
    FILE *fp=fopen(path,"wb");if(!fp)return 13;
    bool ok=fwrite(&f,1,sizeof(f),fp)==sizeof(f);
    if(fclose(fp))ok=false;
    if(!ok)return 14;
    puts("B26_STAGE=PASS_HOST_ABI_UNTRUSTED_TWO_SOURCES");return 0;
}
static int verify(const char *path,const char *mode){
    fixture f;FILE *fp=fopen(path,"rb");if(!fp)return 20;
    bool ok=fread(&f,1,sizeof(f),fp)==sizeof(f);
    if(fgetc(fp)!=EOF)ok=false;
    if(fclose(fp))ok=false;
    if(!ok)return 21;
    const uint32_t tag=VG_B18_DEVICE_TAG,da=0xB261u,db=0xB262u;
    vg_b23_witness old={11u,8u};
    vg_b23_witness obs_a=old,obs_b=old;
    vg_b26_dual_guard initial;
    if(!vg_b26_seed(tag,da,db,41u,71u,&old,&initial))return 22;
    uint32_t use_tag=tag,use_da=da,use_db=db;
    uint64_t ea=42u,eb=72u;
    bool success=false;
    if(!strcmp(mode,"both_old"))success=true;
    else if(!strcmp(mode,"both_new")){success=true;obs_a=f.ticket.proposed;obs_b=obs_a;}
    else if(!strcmp(mode,"disagree_new_old"))obs_a=f.ticket.proposed;
    else if(!strcmp(mode,"disagree_old_new"))obs_b=f.ticket.proposed;
    else if(!strcmp(mode,"different_ack")){obs_a=f.ticket.proposed;obs_b=obs_a;obs_b.confirmed_ack--;}
    else if(!strcmp(mode,"different_generation")){obs_a=f.ticket.proposed;obs_b=obs_a;obs_b.generation--;}
    else if(!strcmp(mode,"epoch_a_replay"))ea=41u;
    else if(!strcmp(mode,"epoch_b_replay"))eb=71u;
    else if(!strcmp(mode,"epoch_a_gap"))ea=43u;
    else if(!strcmp(mode,"epoch_b_gap"))eb=73u;
    else if(!strcmp(mode,"epoch_a_zero"))ea=0u;
    else if(!strcmp(mode,"epoch_b_zero"))eb=0u;
    else if(!strcmp(mode,"duplicate_domain"))use_db=use_da;
    else if(!strcmp(mode,"swapped_domains")){use_da=db;use_db=da;}
    else if(!strcmp(mode,"wrong_domain_a"))use_da^=4u;
    else if(!strcmp(mode,"wrong_domain_b"))use_db^=4u;
    else if(!strcmp(mode,"wrong_tag"))use_tag^=1u;
    else if(!strcmp(mode,"bad_candidate"))f.after[0].bytes[20]^=1u;
    else if(!strcmp(mode,"bad_old"))f.after[1].bytes[20]^=1u;
    else if(!strcmp(mode,"bad_receipt"))f.ticket.candidate_crc32^=1u;
    else if(!strcmp(mode,"diverged_guard"))initial.secondary.last_witness.confirmed_ack++;
    else if(!strcmp(mode,"round_overflow"))initial.accepted_round=UINT64_MAX;
    else if(!strcmp(mode,"epoch_overflow"))initial.secondary.last_observation_epoch=UINT64_MAX;
    else if(!strcmp(mode,"missing_source")){obs_b.generation=0u;obs_b.confirmed_ack=0u;}
    else return 23;
    vg_b26_dual_guard next;memset(&next,0x5a,sizeof(next));
    vg_b19_restored restored;memset(&restored,0x5a,sizeof(restored));
    const vg_b26_dual_guard next_pre=next;
    const vg_b19_restored restored_pre=restored;
    bool committed=true;
    bool result=vg_b26_confirm(f.before,f.after,use_tag,&initial,&f.ticket,
        f.expected,f.size,use_da,&obs_a,ea,use_db,&obs_b,eb,
        &next,&restored,&committed);
    if(success){
        uint32_t gen=!strcmp(mode,"both_new")?12u:11u;
        uint32_t ack=!strcmp(mode,"both_new")?9u:8u;
        if(!result || next.accepted_round!=1u ||
           next.primary.last_observation_epoch!=42u ||
           next.secondary.last_observation_epoch!=72u ||
           next.primary.last_witness.generation!=gen ||
           next.secondary.last_witness.confirmed_ack!=ack ||
           restored.generation!=gen ||
           restored.ack.last_accepted_sequence!=ack ||
           restored.ack.pending || restored.ack.pending_sequence ||
           restored.ack.pending_correlation ||
           committed!=(!strcmp(mode,"both_new")))return 24;
        /* Replaying the same per-source epochs against next state is denied. */
        vg_b26_dual_guard more;vg_b19_restored again;bool after_commit=false;
        if(vg_b26_confirm(f.before,f.after,tag,&next,&f.ticket,
           f.expected,f.size,da,&obs_a,ea,db,&obs_b,eb,
           &more,&again,&after_commit))return 25;
    }else if(result || memcmp(&next,&next_pre,sizeof(next))!=0 ||
              memcmp(&restored,&restored_pre,sizeof(restored))!=0 ||
              committed!=true)return 26;
    printf("B26_QUORUM=PASS_%s\n",mode);return 0;
}
static int seed_invalid(const char *mode){
    const uint32_t tag=VG_B18_DEVICE_TAG;vg_b23_witness old={11u,8u};
    uint32_t da=0xB261u,db=0xB262u,use_tag=tag;uint64_t ea=41u,eb=71u;
    vg_b26_dual_guard out;memset(&out,0x5a,sizeof(out));
    vg_b26_dual_guard prev=out;
    if(!strcmp(mode,"seed_same_domain"))db=da;
    else if(!strcmp(mode,"seed_zero_domain"))da=0u;
    else if(!strcmp(mode,"seed_zero_tag"))use_tag=0u;
    else if(!strcmp(mode,"seed_zero_epoch"))ea=0u;
    else if(!strcmp(mode,"seed_overflow_epoch"))eb=UINT64_MAX;
    else return 28;
    if(vg_b26_seed(use_tag,da,db,ea,eb,&old,&out) ||
       memcmp(&prev,&out,sizeof(out))!=0)return 29;
    printf("B26_QUORUM=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    int r=99;
    if(argc==3 && !strcmp(argv[1],"stage"))r=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))r=verify(argv[2],argv[3]);
    else if(argc==3 && !strcmp(argv[1],"seed"))r=seed_invalid(argv[2]);
    if(r)fprintf(stderr,"B26_FAIL=%d\n",r);
    return r;
}
