/* Deterministic two-round quorum fixture across host processes, no DB. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b27_quorum_sequence_host.h"

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
    puts("B27_STAGE=PASS_TWO_SEQUENTIAL_PROPOSALS_NO_TRUST");return 0;
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
    vg_b27_votes votes[2];memset(votes,0,sizeof(votes));
    for(unsigned i=0;i<2u;i++){
        votes[i].primary=f.tickets[i].proposed;
        votes[i].secondary=f.tickets[i].proposed;
        votes[i].primary_epoch=42u+i;
        votes[i].secondary_epoch=72u+i;
    }
    bool allow=false;
    if(!strcmp(mode,"both_rounds_new"))allow=true;
    else if(!strcmp(mode,"first_old")){votes[0].primary=old;votes[0].secondary=old;}
    else if(!strcmp(mode,"first_split"))votes[0].secondary=old;
    else if(!strcmp(mode,"first_ack_mismatch"))votes[0].secondary.confirmed_ack--;
    else if(!strcmp(mode,"first_gen_mismatch"))votes[0].secondary.generation--;
    else if(!strcmp(mode,"first_primary_replay"))votes[0].primary_epoch=41u;
    else if(!strcmp(mode,"first_secondary_replay"))votes[0].secondary_epoch=71u;
    else if(!strcmp(mode,"first_primary_skip"))votes[0].primary_epoch=44u;
    else if(!strcmp(mode,"first_secondary_skip"))votes[0].secondary_epoch=74u;
    else if(!strcmp(mode,"first_corrupt_middle"))f.middle[0].bytes[22]^=1u;
    else if(!strcmp(mode,"first_corrupt_old"))f.before[1].bytes[22]^=1u;
    else if(!strcmp(mode,"first_bad_ticket"))f.tickets[0].candidate_crc32^=1u;
    else if(!strcmp(mode,"second_old")){votes[1].primary=f.tickets[0].proposed;votes[1].secondary=votes[1].primary;}
    else if(!strcmp(mode,"second_split"))votes[1].secondary=f.tickets[0].proposed;
    else if(!strcmp(mode,"second_ack_mismatch"))votes[1].secondary.confirmed_ack--;
    else if(!strcmp(mode,"second_gen_mismatch"))votes[1].secondary.generation--;
    else if(!strcmp(mode,"second_primary_replay"))votes[1].primary_epoch=42u;
    else if(!strcmp(mode,"second_secondary_replay"))votes[1].secondary_epoch=72u;
    else if(!strcmp(mode,"second_primary_skip"))votes[1].primary_epoch=44u;
    else if(!strcmp(mode,"second_secondary_skip"))votes[1].secondary_epoch=74u;
    else if(!strcmp(mode,"second_corrupt_after"))f.after[1].bytes[22]^=1u;
    else if(!strcmp(mode,"second_bad_ticket"))f.tickets[1].candidate_crc32^=1u;
    else if(!strcmp(mode,"second_bad_link"))f.tickets[1].previous.confirmed_ack--;
    else if(!strcmp(mode,"second_bad_expected"))f.expected[1][22]^=1u;
    else if(!strcmp(mode,"wrong_domain"))da^=1u;
    else if(!strcmp(mode,"swapped_domains")){uint32_t t=da;da=db;db=t;}
    else if(!strcmp(mode,"wrong_tag"))tag^=1u;
    else if(!strcmp(mode,"round_overflow"))guard.accepted_round=UINT64_MAX-1u;
    else if(!strcmp(mode,"first_epoch_overflow"))guard.primary.last_observation_epoch=UINT64_MAX;
    else if(!strcmp(mode,"domain_dup"))db=da;
    else return 23;
    const uint8_t *exp[2]={f.expected[0],f.expected[1]};
    vg_b26_dual_guard next;memset(&next,0x5a,sizeof(next));
    vg_b19_restored out;memset(&out,0x5a,sizeof(out));
    const vg_b26_dual_guard nx=next;const vg_b19_restored ox=out;
    bool committed=false;
    bool result=vg_b27_confirm_sequence(f.before,f.middle,f.after,tag,
      da,db,&guard,f.tickets,exp,f.size,votes,&next,&out,&committed);
    if(allow){
       if(!result || !committed || next.accepted_round!=2u ||
          next.primary.last_observation_epoch!=43u ||
          next.secondary.last_observation_epoch!=73u ||
          next.primary.last_witness.generation!=13u ||
          next.secondary.last_witness.confirmed_ack!=10u ||
          out.generation!=13u || out.ack.last_accepted_sequence!=10u ||
          out.ack.pending || out.ack.pending_sequence ||
          out.ack.pending_correlation)return 24;
       vg_b26_dual_guard again;vg_b19_restored out2;bool c=false;
       if(vg_b27_confirm_sequence(f.before,f.middle,f.after,tag,da,db,
           &next,f.tickets,exp,f.size,votes,&again,&out2,&c))return 25;
    }else if(result || memcmp(&next,&nx,sizeof(nx))!=0 ||
            memcmp(&out,&ox,sizeof(ox))!=0 || committed!=false)return 26;
    printf("B27_SEQUENCE=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    int r=99;
    if(argc==3 && !strcmp(argv[1],"stage"))r=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))r=verify(argv[2],argv[3]);
    if(r)fprintf(stderr,"B27_FAIL=%d\n",r);
    return r;
}
