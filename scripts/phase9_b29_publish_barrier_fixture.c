/* Host-only fixture: the B28 stage helper yields identical checkpoint bytes. */
#define main b28_reference_fixture_main
#include "phase9_b28_revision_fence_fixture.c"
#undef main
#include "phase9_b29_publish_barrier_host.h"

static int verify29(const char *path,const char *mode){
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
    const uint8_t *expected[2]={f.expected[0],f.expected[1]};
    vg_b29_pending pending;memset(&pending,0x5a,sizeof(pending));
    vg_b29_pending original=pending;
    uint64_t pre_revision=100u;
    if(!strcmp(mode,"prepare_stale"))pre_revision=99u;
    else if(!strcmp(mode,"prepare_future"))pre_revision=101u;
    else if(!strcmp(mode,"prepare_corrupt"))f.after[1].bytes[21]^=1u;
    else if(!strcmp(mode,"prepare_split"))votes[1].secondary=old;
    else if(!strcmp(mode,"prepare_replay"))votes[0].primary_epoch--;
    else if(!strcmp(mode,"prepare_overflow")){
        fence.revision=UINT64_MAX-1u;pre_revision=fence.revision;
    }
    bool prepared=vg_b29_prepare(f.before,f.middle,f.after,tag,da,db,
        &guard,&fence,pre_revision,f.tickets,expected,f.size,votes,&pending);
    bool fail_prepare=!strncmp(mode,"prepare_",8);
    if(fail_prepare){
        if(prepared || memcmp(&pending,&original,sizeof(pending)))return 24;
        printf("B29_BARRIER=PASS_%s\n",mode);return 0;
    }
    if(!prepared || !pending.ready || pending.before_revision!=100u ||
       pending.next_fence.revision!=101u ||
       pending.next_state.ack.last_accepted_sequence!=10u ||
       pending.next_state.ack.pending)return 25;
    vg_b29_cas_receipt receipt={0};
    receipt.external_cas_confirmed=true;
    receipt.device_tag=tag;receipt.primary_domain=da;receipt.secondary_domain=db;
    receipt.before_revision=100u;receipt.after_revision=101u;
    receipt.accepted_round=pending.next_fence.accepted_round;
    receipt.primary_epoch=pending.next_fence.primary_epoch;
    receipt.secondary_epoch=pending.next_fence.secondary_epoch;
    receipt.witness=pending.next_fence.last_witness;
    uint64_t external_after=101u;
    if(!strcmp(mode,"accept")){}
    else if(!strcmp(mode,"missing_cas"))receipt.external_cas_confirmed=false;
    else if(!strcmp(mode,"stale_after"))external_after=100u;
    else if(!strcmp(mode,"advanced_after"))external_after=102u;
    else if(!strcmp(mode,"receipt_old_rev"))receipt.before_revision--;
    else if(!strcmp(mode,"receipt_future_rev"))receipt.after_revision++;
    else if(!strcmp(mode,"receipt_wrong_tag"))receipt.device_tag^=1u;
    else if(!strcmp(mode,"receipt_wrong_primary"))receipt.primary_domain^=1u;
    else if(!strcmp(mode,"receipt_wrong_secondary"))receipt.secondary_domain^=1u;
    else if(!strcmp(mode,"receipt_wrong_round"))receipt.accepted_round++;
    else if(!strcmp(mode,"receipt_primary_epoch"))receipt.primary_epoch++;
    else if(!strcmp(mode,"receipt_secondary_epoch"))receipt.secondary_epoch++;
    else if(!strcmp(mode,"receipt_generation"))receipt.witness.generation++;
    else if(!strcmp(mode,"receipt_ack"))receipt.witness.confirmed_ack++;
    else if(!strcmp(mode,"pending_not_ready"))pending.ready=false;
    else if(!strcmp(mode,"pending_wrong_tag"))pending.device_tag^=1u;
    else if(!strcmp(mode,"pending_wrong_domain"))pending.secondary_domain^=1u;
    else if(!strcmp(mode,"pending_next_rev"))pending.next_fence.revision++;
    else if(!strcmp(mode,"pending_next_round"))pending.next_guard.accepted_round++;
    else if(!strcmp(mode,"pending_next_witness"))pending.next_guard.primary.last_witness.generation++;
    else if(!strcmp(mode,"pending_pending_ack"))pending.next_state.ack.pending=true;
    else if(!strcmp(mode,"pending_generation"))pending.next_state.generation++;
    else if(!strcmp(mode,"pending_overflow"))pending.before_revision=UINT64_MAX;
    else if(!strcmp(mode,"duplicate_receipt"))receipt.before_revision=99u;
    else if(!strcmp(mode,"null_receipt")){}
    else return 26;
    vg_b26_dual_guard published_guard;vg_b28_fence published_fence;
    vg_b19_restored published_state;
    memset(&published_guard,0xa5,sizeof(published_guard));
    memset(&published_fence,0xa5,sizeof(published_fence));
    memset(&published_state,0xa5,sizeof(published_state));
    vg_b26_dual_guard guard_original=published_guard;
    vg_b28_fence fence_original=published_fence;
    vg_b19_restored state_original=published_state;
    bool committed=true;
    bool result=vg_b29_finalize(&pending,
        !strcmp(mode,"null_receipt")?NULL:&receipt,external_after,
        &published_guard,&published_fence,&published_state,&committed);
    if(!strcmp(mode,"accept")){
        if(!result || !committed || published_guard.accepted_round!=2u ||
           published_fence.revision!=101u ||
           published_state.generation!=13u ||
           published_state.ack.last_accepted_sequence!=10u ||
           published_state.ack.pending)return 27;
    }else if(result || committed!=true ||
            memcmp(&published_guard,&guard_original,sizeof(published_guard)) ||
            memcmp(&published_fence,&fence_original,sizeof(published_fence)) ||
            memcmp(&published_state,&state_original,sizeof(published_state)))return 28;
    printf("B29_BARRIER=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    int status=99;
    if(argc==3 && !strcmp(argv[1],"stage"))status=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))status=verify29(argv[2],argv[3]);
    if(status)fprintf(stderr,"B29_FAIL=%d\n",status);
    return status;
}
