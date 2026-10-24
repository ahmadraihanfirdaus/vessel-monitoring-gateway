/* C99 two-round guard revision-fence fixture, separate stage/verify processes. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b28_revision_fence_host.h"
typedef struct {
    vg_b20_slot before[2],middle[2],after[2];
    vg_b24_ticket tickets[2];
    uint8_t expected[2][VG_B19_SLOT_MAX];
    size_t size[2];
} fixture;
static int slot(vg_b20_slot *s,uint32_t gen,uint32_t ack,uint32_t tag){
    net002_host_offline_store q;phase9_b8_ack_window w;
    net002_host_init(&q);phase9_b8_ack_init(&w);
    if(!net002_host_set_latest(&q,"0|null",6u) ||
       !net002_host_add_critical(&q,101u,2u,"alarm"))return 1;
    w.last_accepted_sequence=ack;
    if(!phase9_b8_ack_begin(&w,ack+1u,54u))return 2;
    return vg_b19_wrap(&q,&w,tag,gen,s->bytes,sizeof(s->bytes),&s->len)?0:3;
}
static int stage(const char *path){
    fixture f;memset(&f,0,sizeof(f));uint32_t tag=VG_B18_DEVICE_TAG;
    if(slot(&f.before[0],10u,7u,tag) || slot(&f.before[1],11u,8u,tag))return 10;
    memcpy(f.middle,f.before,sizeof(f.before));
    if(slot(&f.middle[0],12u,9u,tag))return 11;
    memcpy(f.after,f.middle,sizeof(f.middle));
    if(slot(&f.after[1],13u,10u,tag))return 12;
    f.size[0]=f.middle[0].len;f.size[1]=f.after[1].len;
    memcpy(f.expected[0],f.middle[0].bytes,f.size[0]);
    memcpy(f.expected[1],f.after[1].bytes,f.size[1]);
    vg_b23_witness old={11u,8u};
    if(!vg_b24_issue_ticket(f.before,f.middle,tag,&old,f.expected[0],
         f.size[0],0u,12u,9u,&f.tickets[0]))return 13;
    if(!vg_b24_issue_ticket(f.middle,f.after,tag,&f.tickets[0].proposed,
         f.expected[1],f.size[1],1u,13u,10u,&f.tickets[1]))return 14;
    FILE *fp=fopen(path,"wb");if(!fp)return 15;
    bool ok=fwrite(&f,1,sizeof(f),fp)==sizeof(f);
    if(fclose(fp))ok=false;
    if(!ok)return 16;
    puts("B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE");return 0;
}
static int verify(const char *path,const char *mode){
    fixture f;FILE *fp=fopen(path,"rb");if(!fp)return 20;
    bool ok=fread(&f,1,sizeof(f),fp)==sizeof(f);
    if(fgetc(fp)!=EOF)ok=false;
    if(fclose(fp))ok=false;
    if(!ok)return 21;
    uint32_t tag=VG_B18_DEVICE_TAG,da=0xB261u,db=0xB262u;
    vg_b23_witness old={11u,8u};vg_b26_dual_guard guard;
    if(!vg_b26_seed(tag,da,db,41u,71u,&old,&guard))return 22;
    vg_b28_fence fence;
    if(!vg_b28_seed_fence(&guard,100u,&fence))return 23;
    vg_b27_votes votes[2];memset(votes,0,sizeof(votes));
    for(unsigned i=0;i<2u;i++){
        votes[i].primary=f.tickets[i].proposed;
        votes[i].secondary=f.tickets[i].proposed;
        votes[i].primary_epoch=42u+i;
        votes[i].secondary_epoch=72u+i;
    }
    bool allow=false;
    uint64_t observed_revision=100u;
    if(!strcmp(mode,"accept"))allow=true;
    else if(!strcmp(mode,"stale_observed"))observed_revision=99u;
    else if(!strcmp(mode,"future_observed"))observed_revision=101u;
    else if(!strcmp(mode,"fence_revision_zero"))fence.revision=0u;
    else if(!strcmp(mode,"fence_revision_overflow"))fence.revision=UINT64_MAX;
    else if(!strcmp(mode,"fence_wrong_tag"))fence.device_tag^=1u;
    else if(!strcmp(mode,"fence_wrong_primary"))fence.primary_domain^=1u;
    else if(!strcmp(mode,"fence_wrong_secondary"))fence.secondary_domain^=1u;
    else if(!strcmp(mode,"fence_round_ahead"))fence.accepted_round++;
    else if(!strcmp(mode,"fence_primary_epoch"))fence.primary_epoch++;
    else if(!strcmp(mode,"fence_secondary_epoch"))fence.secondary_epoch++;
    else if(!strcmp(mode,"fence_generation"))fence.last_witness.generation++;
    else if(!strcmp(mode,"fence_ack"))fence.last_witness.confirmed_ack++;
    else if(!strcmp(mode,"guard_primary_epoch"))guard.primary.last_observation_epoch++;
    else if(!strcmp(mode,"guard_secondary_epoch"))guard.secondary.last_observation_epoch++;
    else if(!strcmp(mode,"guard_primary_witness"))guard.primary.last_witness.confirmed_ack++;
    else if(!strcmp(mode,"guard_secondary_witness"))guard.secondary.last_witness.confirmed_ack++;
    else if(!strcmp(mode,"guard_round"))guard.accepted_round++;
    else if(!strcmp(mode,"guard_round_overflow")){guard.accepted_round=UINT64_MAX-1u;fence.accepted_round=guard.accepted_round;}
    else if(!strcmp(mode,"first_primary_replay"))votes[0].primary_epoch--;
    else if(!strcmp(mode,"second_secondary_replay"))votes[1].secondary_epoch--;
    else if(!strcmp(mode,"first_split"))votes[0].secondary=old;
    else if(!strcmp(mode,"second_split"))votes[1].secondary=f.tickets[0].proposed;
    else if(!strcmp(mode,"corrupt_after"))f.after[1].bytes[20]^=1u;
    else if(!strcmp(mode,"corrupt_expected"))f.expected[1][20]^=1u;
    else if(!strcmp(mode,"wrong_ticket"))f.tickets[0].candidate_crc32^=1u;
    else if(!strcmp(mode,"domain_collision"))db=da;
    else if(!strcmp(mode,"swap_domains")){uint32_t t=da;da=db;db=t;}
    else if(!strcmp(mode,"wrong_device"))tag^=1u;
    else if(!strcmp(mode,"alias_fence")){} /* handled at invocation */
    else if(!strcmp(mode,"alias_guard")){} /* handled at invocation */
    else return 24;
    const uint8_t *expected[2]={f.expected[0],f.expected[1]};
    vg_b26_dual_guard next_guard;memset(&next_guard,0x5a,sizeof(next_guard));
    vg_b28_fence next_fence;memset(&next_fence,0x5a,sizeof(next_fence));
    vg_b19_restored restored;memset(&restored,0x5a,sizeof(restored));
    vg_b26_dual_guard old_guard=next_guard;
    vg_b28_fence old_fence=next_fence;
    vg_b19_restored old_restored=restored;
    bool committed=true; /* rejection must preserve a non-default output */
    bool result=vg_b28_confirm_with_fence(f.before,f.middle,f.after,tag,
        da,db,&guard,&fence,observed_revision,f.tickets,expected,f.size,
        votes,!strcmp(mode,"alias_guard")?&guard:&next_guard,
        !strcmp(mode,"alias_fence")?&fence:&next_fence,&restored,&committed);
    if(allow){
       if(!result || !committed || next_guard.accepted_round!=2u ||
          next_fence.revision!=101u || next_fence.accepted_round!=2u ||
          next_fence.primary_epoch!=43u || next_fence.secondary_epoch!=73u ||
          next_fence.last_witness.generation!=13u ||
          next_fence.last_witness.confirmed_ack!=10u ||
          restored.generation!=13u || restored.ack.last_accepted_sequence!=10u ||
          restored.ack.pending || restored.ack.pending_sequence ||
          restored.ack.pending_correlation)return 25;
       vg_b26_dual_guard gx;vg_b28_fence fx;vg_b19_restored rx;
       memset(&gx,0xa5,sizeof(gx));memset(&fx,0xa5,sizeof(fx));
       memset(&rx,0xa5,sizeof(rx));bool cx=true;
       if(vg_b28_confirm_with_fence(f.before,f.middle,f.after,tag,da,db,
          &guard,&next_fence,101u,f.tickets,expected,f.size,votes,
          &gx,&fx,&rx,&cx))return 26; /* stale guard under NEW fence */
       if(vg_b28_confirm_with_fence(f.before,f.middle,f.after,tag,da,db,
          &next_guard,&fence,100u,f.tickets,expected,f.size,votes,
          &gx,&fx,&rx,&cx))return 27; /* NEW guard under old fence */
       if(vg_b28_confirm_with_fence(f.before,f.middle,f.after,tag,da,db,
          &next_guard,&next_fence,101u,f.tickets,expected,f.size,votes,
          &gx,&fx,&rx,&cx))return 28; /* old votes replay after promotion */
       if(cx!=true)return 29;
    }else if(result || memcmp(&next_guard,&old_guard,sizeof(old_guard)) ||
             memcmp(&next_fence,&old_fence,sizeof(old_fence)) ||
             memcmp(&restored,&old_restored,sizeof(old_restored)) ||
             committed!=true)return 30;
    printf("B28_FENCE=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    int code=99;
    if(argc==3 && !strcmp(argv[1],"stage"))code=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))code=verify(argv[2],argv[3]);
    if(code)fprintf(stderr,"B28_FAIL=%d\n",code);
    return code;
}
