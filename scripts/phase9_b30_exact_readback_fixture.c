/* B30 host-only exact readback fixture; stage and verify are separate OS
 * processes. All external trust is synthetic and explicitly NOT verified. */
#define main b28_reference_fixture_main
#include "phase9_b28_revision_fence_fixture.c"
#undef main
#include "phase9_b30_exact_readback_host.h"

static int verify30(const char *path,const char *mode){
    fixture f;FILE *fp=fopen(path,"rb");if(!fp)return 20;
    bool ok=fread(&f,1,sizeof(f),fp)==sizeof(f);
    if(fgetc(fp)!=EOF)ok=false;
    if(fclose(fp))ok=false;
    if(!ok)return 21;
    uint32_t tag=VG_B18_DEVICE_TAG,da=0xB261u,db=0xB262u;
    vg_b23_witness old={11u,8u};vg_b26_dual_guard guard;
    if(!vg_b26_seed(tag,da,db,41u,71u,&old,&guard))return 22;
    vg_b28_fence fence;if(!vg_b28_seed_fence(&guard,100u,&fence))return 23;
    vg_b27_votes votes[2];memset(votes,0,sizeof(votes));
    for(unsigned i=0u;i<2u;i++){
        votes[i].primary=f.tickets[i].proposed;
        votes[i].secondary=f.tickets[i].proposed;
        votes[i].primary_epoch=42u+i;
        votes[i].secondary_epoch=72u+i;
    }
    const uint8_t *expected[2]={f.expected[0],f.expected[1]};
    vg_b30_pending pending;memset(&pending,0xa5,sizeof(pending));
    vg_b30_pending old_pending=pending;
    uint64_t before_rev=100u;
    if(!strcmp(mode,"prepare_old_rev"))before_rev--;
    if(!strcmp(mode,"prepare_corrupt"))f.after[1].bytes[29]^=1u;
    if(!strcmp(mode,"prepare_bad_ticket"))f.tickets[1].candidate_crc32^=1u;
    if(!strcmp(mode,"prepare_split"))votes[1].secondary=old;
    if(!strcmp(mode,"prepare_bad_domain"))db=da;
    if(!strcmp(mode,"prepare_old_epoch"))votes[1].secondary_epoch--;
    bool prepared=vg_b30_prepare_exact(f.before,f.middle,f.after,tag,
      da,db,&guard,&fence,before_rev,f.tickets,expected,f.size,votes,&pending);
    if(!strncmp(mode,"prepare_",8)){
        if(prepared || memcmp(&pending,&old_pending,sizeof(pending)))return 24;
        printf("B30_READBACK=PASS_%s\n",mode);return 0;
    }
    if(!prepared || !pending.ready || pending.slot_index!=1u ||
       pending.base.next_fence.revision!=101u ||
       pending.base.next_state.ack.last_accepted_sequence!=10u)return 25;
    vg_b29_cas_receipt receipt={0};
    receipt.external_cas_confirmed=true;
    receipt.device_tag=tag;receipt.primary_domain=da;receipt.secondary_domain=db;
    receipt.before_revision=100u;receipt.after_revision=101u;
    receipt.accepted_round=pending.base.next_fence.accepted_round;
    receipt.primary_epoch=pending.base.next_fence.primary_epoch;
    receipt.secondary_epoch=pending.base.next_fence.secondary_epoch;
    receipt.witness=pending.base.next_fence.last_witness;
    vg_b30_readback_receipt r={0};
    r.external_readback_verified=true;r.device_tag=tag;
    r.slot_index=pending.slot_index;r.revision=101u;
    r.image_len=pending.image_len;
    r.image_crc32=vg_b18_crc32(pending.image,pending.image_len);
    uint8_t actual[VG_B19_SLOT_MAX];
    memcpy(actual,pending.image,pending.image_len);
    size_t actual_len=pending.image_len;uint64_t verified=101u;
    bool use_null_pending=false,use_null_cas=false,use_null_rb=false,
         use_null_image=false,use_null_output=false;
    if(!strcmp(mode,"accept")){}
    else if(!strcmp(mode,"no_external_readback"))r.external_readback_verified=false;
    else if(!strcmp(mode,"no_external_cas"))receipt.external_cas_confirmed=false;
    else if(!strcmp(mode,"stale_verified_revision"))verified--;
    else if(!strcmp(mode,"future_verified_revision"))verified++;
    else if(!strcmp(mode,"receipt_wrong_revision"))receipt.after_revision++;
    else if(!strcmp(mode,"receipt_wrong_ack"))receipt.witness.confirmed_ack++;
    else if(!strcmp(mode,"receipt_wrong_device"))receipt.device_tag^=1u;
    else if(!strcmp(mode,"receipt_wrong_domain"))receipt.secondary_domain^=1u;
    else if(!strcmp(mode,"rb_wrong_device"))r.device_tag^=1u;
    else if(!strcmp(mode,"rb_wrong_revision"))r.revision++;
    else if(!strcmp(mode,"rb_wrong_slot"))r.slot_index^=1u;
    else if(!strcmp(mode,"rb_wrong_length"))r.image_len++;
    else if(!strcmp(mode,"rb_wrong_crc"))r.image_crc32^=1u;
    else if(!strcmp(mode,"rb_short_actual"))actual_len--;
    else if(!strcmp(mode,"rb_long_actual"))actual_len++;
    else if(!strcmp(mode,"rb_changed_body"))actual[29]^=1u;
    else if(!strcmp(mode,"rb_changed_ack"))actual[17]^=1u;
    else if(!strcmp(mode,"rb_wrong_generation"))actual[10]^=1u;
    else if(!strcmp(mode,"rb_wrong_journal"))actual[35]^=1u;
    else if(!strcmp(mode,"rb_valid_alternate_telemetry") ||
            !strcmp(mode,"rb_valid_alternate_journal")){
        vg_b19_restored alt,check_alt;
        if(!vg_b19_decode(actual,actual_len,tag,&alt))return 29;
        if(!strcmp(mode,"rb_valid_alternate_telemetry")){
            if(!alt.store.has_latest || !alt.store.latest_len)return 30;
            alt.store.latest[0]^=1u;
        }else{
            if(alt.store.count==0u)return 31;
            alt.store.journal[alt.store.start].text[1]='L';
        }
        size_t written=0u;
        if(!vg_b19_wrap(&alt.store,&alt.ack,tag,alt.generation,
              actual,sizeof(actual),&written) ||
           written!=pending.image_len ||
           !vg_b19_decode(actual,written,tag,&check_alt) ||
           check_alt.generation!=pending.base.next_state.generation ||
           check_alt.ack.last_accepted_sequence!=
             pending.base.next_state.ack.last_accepted_sequence ||
           memcmp(actual,pending.image,written)==0)return 32;
    }
    else if(!strcmp(mode,"pending_changed_journal"))pending.base.next_state.store.evicted_count++;
    else if(!strcmp(mode,"pending_changed_latest"))pending.base.next_state.store.latest[0]^=1u;
    else if(!strcmp(mode,"pending_changed_store_count"))pending.base.next_state.store.count++;
    else if(!strcmp(mode,"pending_wrong_slot"))pending.slot_index^=1u;
    else if(!strcmp(mode,"pending_changed_image"))pending.image[29]^=1u;
    else if(!strcmp(mode,"pending_not_ready"))pending.ready=false;
    else if(!strcmp(mode,"pending_zero_image_len"))pending.image_len=0u;
    else if(!strcmp(mode,"pending_overlong_image_len"))pending.image_len=VG_B19_SLOT_MAX+1u;
    else if(!strcmp(mode,"pending_generation"))pending.base.next_state.generation++;
    else if(!strcmp(mode,"null_pending"))use_null_pending=true;
    else if(!strcmp(mode,"null_cas"))use_null_cas=true;
    else if(!strcmp(mode,"null_readback_receipt"))use_null_rb=true;
    else if(!strcmp(mode,"null_image"))use_null_image=true;
    else if(!strcmp(mode,"null_output"))use_null_output=true;
    else return 26;
    vg_b26_dual_guard pub_g;vg_b28_fence pub_f;vg_b19_restored pub_s;
    memset(&pub_g,0x5a,sizeof(pub_g));
    memset(&pub_f,0x5a,sizeof(pub_f));
    memset(&pub_s,0x5a,sizeof(pub_s));
    vg_b26_dual_guard prior_g=pub_g;vg_b28_fence prior_f=pub_f;
    vg_b19_restored prior_s=pub_s;bool committed=true;
    bool result=vg_b30_finalize_exact(
      use_null_pending?NULL:&pending,use_null_cas?NULL:&receipt,
      use_null_rb?NULL:&r,use_null_image?NULL:actual,actual_len,verified,
      use_null_output?NULL:&pub_g,&pub_f,&pub_s,&committed);
    if(!strcmp(mode,"accept")){
        if(!result || !committed || pub_g.accepted_round!=2u ||
           pub_f.revision!=101u || pub_s.generation!=13u ||
           pub_s.ack.last_accepted_sequence!=10u || pub_s.ack.pending)return 27;
    }else if(result || !committed ||
              memcmp(&prior_g,&pub_g,sizeof(pub_g)) ||
              memcmp(&prior_f,&pub_f,sizeof(pub_f)) ||
              memcmp(&prior_s,&pub_s,sizeof(pub_s)))return 28;
    printf("B30_READBACK=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    int result=99;
    if(argc==3 && !strcmp(argv[1],"stage"))result=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))
        result=verify30(argv[2],argv[3]);
    if(result)fprintf(stderr,"B30_FAIL=%d\n",result);
    return result;
}
