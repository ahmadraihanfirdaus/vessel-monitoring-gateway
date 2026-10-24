/* B31 isolated publish C99 host fixture: stage and verify separate processes.
 * Exercises input/output overlaps; external receipts are NOT authenticated. */
#define main b30_reference_fixture_main
#include "phase9_b28_revision_fence_fixture.c"
#undef main
#include "phase9_b31_publish_isolation_host.h"

static int verify31(const char *path,const char *mode){
    fixture f;FILE *fp=fopen(path,"rb");if(!fp)return 20;
    bool ok=fread(&f,1,sizeof(f),fp)==sizeof(f);
    if(fgetc(fp)!=EOF)ok=false;
    if(fclose(fp))ok=false;
    if(!ok)return 21;
    const uint32_t tag=VG_B18_DEVICE_TAG,da=0xB261u,db=0xB262u;
    vg_b23_witness old={11u,8u};vg_b26_dual_guard guard;
    if(!vg_b26_seed(tag,da,db,41u,71u,&old,&guard))return 22;
    vg_b28_fence fence;if(!vg_b28_seed_fence(&guard,100u,&fence))return 23;
    vg_b27_votes votes[2];memset(votes,0,sizeof(votes));
    for(unsigned i=0u;i<2u;i++){
        votes[i].primary=f.tickets[i].proposed;
        votes[i].secondary=f.tickets[i].proposed;
        votes[i].primary_epoch=42u+i;votes[i].secondary_epoch=72u+i;
    }
    const uint8_t *expected[2]={f.expected[0],f.expected[1]};
    vg_b30_pending pending={0};
    if(!vg_b30_prepare_exact(f.before,f.middle,f.after,tag,da,db,
        &guard,&fence,100u,f.tickets,expected,f.size,votes,&pending) ||
       !pending.ready || pending.slot_index!=1u)return 24;
    vg_b29_cas_receipt cas={0};
    cas.external_cas_confirmed=true;cas.device_tag=tag;
    cas.primary_domain=da;cas.secondary_domain=db;
    cas.before_revision=100u;cas.after_revision=101u;
    cas.accepted_round=pending.base.next_fence.accepted_round;
    cas.primary_epoch=pending.base.next_fence.primary_epoch;
    cas.secondary_epoch=pending.base.next_fence.secondary_epoch;
    cas.witness=pending.base.next_fence.last_witness;
    vg_b30_readback_receipt rr={0};
    rr.external_readback_verified=true;rr.device_tag=tag;
    rr.slot_index=pending.slot_index;rr.revision=101u;
    rr.image_len=pending.image_len;
    rr.image_crc32=vg_b18_crc32(pending.image,pending.image_len);
    uint8_t actual[VG_B19_SLOT_MAX];
    memcpy(actual,pending.image,pending.image_len);
    const uint8_t *actual_ptr=actual;
    size_t actual_len=pending.image_len;
    vg_b26_dual_guard out_guard;vg_b28_fence out_fence;
    vg_b19_restored out_state;bool committed=true;
    memset(&out_guard,0x5a,sizeof(out_guard));
    memset(&out_fence,0x5a,sizeof(out_fence));
    memset(&out_state,0x5a,sizeof(out_state));
    vg_b26_dual_guard prior_guard=out_guard;
    vg_b28_fence prior_fence=out_fence;
    vg_b19_restored prior_state=out_state;
    vg_b26_dual_guard *guard_ptr=&out_guard;
    vg_b28_fence *fence_ptr=&out_fence;
    vg_b19_restored *state_ptr=&out_state;
    bool *commit_ptr=&committed;
    uint64_t verified=101u;
    if(!strcmp(mode,"accept")){}
    else if(!strcmp(mode,"alias_readback_pending_image"))actual_ptr=pending.image;
    else if(!strcmp(mode,"alias_readback_pending_prefix"))actual_ptr=(const uint8_t *)&pending;
    else if(!strcmp(mode,"alias_readback_cas"))actual_ptr=(const uint8_t *)&cas;
    else if(!strcmp(mode,"alias_readback_rr"))actual_ptr=(const uint8_t *)&rr;
    else if(!strcmp(mode,"alias_guard_pending_guard"))guard_ptr=&pending.base.next_guard;
    else if(!strcmp(mode,"alias_fence_pending_fence"))fence_ptr=&pending.base.next_fence;
    else if(!strcmp(mode,"alias_state_pending_state"))state_ptr=&pending.base.next_state;
    else if(!strcmp(mode,"alias_committed_cas"))commit_ptr=&cas.external_cas_confirmed;
    else if(!strcmp(mode,"alias_committed_receipt"))commit_ptr=&rr.external_readback_verified;
    else if(!strcmp(mode,"alias_guard_fence"))fence_ptr=(vg_b28_fence *)(void *)&out_guard;
    else if(!strcmp(mode,"alias_state_guard"))guard_ptr=(vg_b26_dual_guard *)(void *)&out_state;
    else if(!strcmp(mode,"alias_state_fence"))fence_ptr=(vg_b28_fence *)(void *)&out_state;
    else if(!strcmp(mode,"alias_committed_state"))commit_ptr=(bool *)(void *)&out_state;
    else if(!strcmp(mode,"alias_state_actual"))state_ptr=(vg_b19_restored *)(void *)actual;
    else if(!strcmp(mode,"alias_fence_actual"))fence_ptr=(vg_b28_fence *)(void *)actual;
    else if(!strcmp(mode,"no_external_cas"))cas.external_cas_confirmed=false;
    else if(!strcmp(mode,"no_external_readback"))rr.external_readback_verified=false;
    else if(!strcmp(mode,"wrong_revision"))verified=102u;
    else if(!strcmp(mode,"wrong_readback"))actual[35]^=1u;
    else if(!strcmp(mode,"wrong_ack"))cas.witness.confirmed_ack++;
    else if(!strcmp(mode,"zero_readback_len"))actual_len=0u;
    else if(!strcmp(mode,"overlong_readback_len"))actual_len=VG_B19_SLOT_MAX+1u;
    else if(!strcmp(mode,"null_out_guard"))guard_ptr=NULL;
    else if(!strcmp(mode,"null_out_fence"))fence_ptr=NULL;
    else if(!strcmp(mode,"null_out_state"))state_ptr=NULL;
    else if(!strcmp(mode,"null_out_committed"))commit_ptr=NULL;
    else if(!strcmp(mode,"null_pending")){}
    else if(!strcmp(mode,"null_cas")){}
    else if(!strcmp(mode,"null_rr")){}
    else if(!strcmp(mode,"null_readback"))actual_ptr=NULL;
    else return 25;
    /* For intentional output aliases, the input must be preserved too. */
    vg_b30_pending pending_before=pending;
    vg_b29_cas_receipt cas_before=cas;
    vg_b30_readback_receipt rr_before=rr;
    uint8_t image_before[VG_B19_SLOT_MAX];
    memcpy(image_before,actual,sizeof(actual));
    bool accepted=vg_b31_finalize_isolated(
        !strcmp(mode,"null_pending")?NULL:&pending,
        !strcmp(mode,"null_cas")?NULL:&cas,
        !strcmp(mode,"null_rr")?NULL:&rr,
        actual_ptr,actual_len,verified,guard_ptr,fence_ptr,state_ptr,commit_ptr);
    if(!strcmp(mode,"accept")){
        if(!accepted || !committed || out_fence.revision!=101u ||
           out_state.generation!=13u ||
           out_state.ack.last_accepted_sequence!=10u ||
           out_guard.accepted_round!=2u)return 26;
    }else{
        if(accepted || !committed ||
           memcmp(&out_guard,&prior_guard,sizeof(out_guard)) ||
           memcmp(&out_fence,&prior_fence,sizeof(out_fence)) ||
           memcmp(&out_state,&prior_state,sizeof(out_state)))return 27;
    }
    if(memcmp(&pending,&pending_before,sizeof(pending)) ||
       memcmp(&cas,&cas_before,sizeof(cas)) ||
       memcmp(&rr,&rr_before,sizeof(rr)) ||
       memcmp(actual,image_before,sizeof(actual)))return 28;
    printf("B31_ISOLATION=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    int r=99;
    if(argc==3 && !strcmp(argv[1],"stage"))r=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))r=verify31(argv[2],argv[3]);
    if(r)fprintf(stderr,"B31_FAIL=%d\n",r);
    return r;
}
