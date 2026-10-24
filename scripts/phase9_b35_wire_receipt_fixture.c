/* B35 C99 cross-process canonical receipt with B34 trusted envelope. */
/* B34 host fixture: checkpoint publication as one checked envelope.
 * Inputs are synthetic from earlier deterministic B28 two-round fixture. */
/* B33 C99 host fixture: two independent revision reads & input stability.
 * Exercises input/output overlaps; external receipts are NOT authenticated. */
#define main b30_reference_fixture_main
#include "phase9_b28_revision_fence_fixture.c"
#undef main
#include "phase9_b33_stable_revision_host.h"

typedef struct {
    const char *mode;
    unsigned calls;
    vg_b30_pending *pending;
    vg_b29_cas_receipt *cas;
    vg_b30_readback_receipt *rr;
    uint8_t *readback;
} b33_probe_ctx;
static bool b33_probe(void *context,uint64_t *observed){
    b33_probe_ctx *c=(b33_probe_ctx *)context;
    if(!c || !observed)return false;
    ++c->calls;
    const bool first=c->calls==1u,second=c->calls==2u;
    if(!first && !second)return false;
    if(first && !strcmp(c->mode,"probe_first_fail"))return false;
    if(second && !strcmp(c->mode,"probe_second_fail"))return false;
    *observed=101u;
    if(first && !strcmp(c->mode,"probe_first_wrong_revision"))*observed=100u;
    if(second && !strcmp(c->mode,"probe_second_wrong_revision"))*observed=102u;
    if(first && !strcmp(c->mode,"probe_first_mutate_pending"))c->pending->base.next_fence.revision++;
    if(second && !strcmp(c->mode,"probe_second_mutate_pending"))c->pending->base.next_fence.revision++;
    if(first && !strcmp(c->mode,"probe_first_mutate_cas"))c->cas->before_revision++;
    if(second && !strcmp(c->mode,"probe_second_mutate_cas"))c->cas->before_revision++;
    if(first && !strcmp(c->mode,"probe_first_mutate_rr"))c->rr->revision++;
    if(second && !strcmp(c->mode,"probe_second_mutate_rr"))c->rr->revision++;
    if(first && !strcmp(c->mode,"probe_first_mutate_readback"))c->readback[45u]^=1u;
    if(second && !strcmp(c->mode,"probe_second_mutate_readback"))c->readback[45u]^=1u;
    return true;
}

static int verify33(const char *path,const char *mode){
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
    const vg_b30_pending *pending_ptr=&pending;
    const vg_b29_cas_receipt *cas_ptr=&cas;
    const vg_b30_readback_receipt *rr_ptr=&rr;
    uint64_t verified=101u;
    b33_probe_ctx probe_ctx={mode,0u,&pending,&cas,&rr,actual};
    vg_b33_revision_probe probe_ptr=b33_probe;
    if(!strcmp(mode,"accept")){}
    else if(!strcmp(mode,"alias_cas_pending"))cas_ptr=(const vg_b29_cas_receipt *)(const void *)&pending;
    else if(!strcmp(mode,"alias_rr_pending"))rr_ptr=(const vg_b30_readback_receipt *)(const void *)&pending;
    else if(!strcmp(mode,"alias_rr_cas"))rr_ptr=(const vg_b30_readback_receipt *)(const void *)&cas;
    else if(!strcmp(mode,"alias_cas_rr"))cas_ptr=(const vg_b29_cas_receipt *)(const void *)&rr;
    else if(!strcmp(mode,"alias_pending_cas"))pending_ptr=(const vg_b30_pending *)(const void *)&cas;
    else if(!strcmp(mode,"alias_pending_rr"))pending_ptr=(const vg_b30_pending *)(const void *)&rr;
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
    else if(!strcmp(mode,"probe_first_fail")){}
    else if(!strcmp(mode,"probe_second_fail")){}
    else if(!strcmp(mode,"probe_first_wrong_revision")){}
    else if(!strcmp(mode,"probe_second_wrong_revision")){}
    else if(!strcmp(mode,"probe_first_mutate_pending")){}
    else if(!strcmp(mode,"probe_second_mutate_pending")){}
    else if(!strcmp(mode,"probe_first_mutate_cas")){}
    else if(!strcmp(mode,"probe_second_mutate_cas")){}
    else if(!strcmp(mode,"probe_first_mutate_rr")){}
    else if(!strcmp(mode,"probe_second_mutate_rr")){}
    else if(!strcmp(mode,"probe_first_mutate_readback")){}
    else if(!strcmp(mode,"probe_second_mutate_readback")){}
    else if(!strcmp(mode,"null_probe"))probe_ptr=NULL;
    else if(!strcmp(mode,"null_context")){}
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
    bool accepted=vg_b33_finalize_stable_revision(
        !strcmp(mode,"null_pending")?NULL:pending_ptr,
        !strcmp(mode,"null_cas")?NULL:cas_ptr,
        !strcmp(mode,"null_rr")?NULL:rr_ptr,
        actual_ptr,actual_len,verified,probe_ptr,
        !strcmp(mode,"null_context")?NULL:&probe_ctx,guard_ptr,fence_ptr,state_ptr,commit_ptr);
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
    /* Intentional callback injection mutates the caller-owned input itself;
     * this is a trusted-adapter failure test, never a claim of unchanged
     * caller storage. Only the four output values must remain unchanged. */
    const bool injected=!strncmp(mode,"probe_",6) && strstr(mode,"mutate_")!=NULL;
    if(!injected &&
       (memcmp(&pending,&pending_before,sizeof(pending)) ||
       memcmp(&cas,&cas_before,sizeof(cas)) ||
       memcmp(&rr,&rr_before,sizeof(rr)) ||
       memcmp(actual,image_before,sizeof(actual))))return 28;
    printf("B33_REVISION=PASS_%s\n",mode);return 0;
}
int b33_reference_fixture_main(int argc,char **argv){
    int r=99;
    if(argc==3 && !strcmp(argv[1],"stage"))r=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))r=verify33(argv[2],argv[3]);
    if(r)fprintf(stderr,"B33_FAIL=%d\n",r);
    return r;
}

#include "phase9_b34_publish_envelope_host.h"

static int verify34(const char *path,const char *mode){
    fixture f; FILE *fp=fopen(path,"rb"); if(!fp)return 20;
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
    const vg_b30_pending *pending_ptr=&pending;
    const vg_b29_cas_receipt *cas_ptr=&cas;
    const vg_b30_readback_receipt *rr_ptr=&rr;
    uint64_t revision=101u;
    b33_probe_ctx probe_ctx={mode,0u,&pending,&cas,&rr,actual};
    vg_b33_revision_probe probe_ptr=b33_probe;
    vg_b34_envelope output;memset(&output,0x5a,sizeof(output));
    vg_b34_envelope before_output=output;
    vg_b34_envelope *output_ptr=&output;
    if(!strcmp(mode,"accept")){}
    else if(!strcmp(mode,"wrong_revision"))revision++;
    else if(!strcmp(mode,"wrong_ack"))cas.witness.confirmed_ack++;
    else if(!strcmp(mode,"wrong_readback"))actual[35u]^=1u;
    else if(!strcmp(mode,"wrong_readback_crc"))rr.image_crc32++;
    else if(!strcmp(mode,"wrong_readback_len"))rr.image_len++;
    else if(!strcmp(mode,"wrong_device"))cas.device_tag++;
    else if(!strcmp(mode,"wrong_domain"))cas.primary_domain++;
    else if(!strcmp(mode,"wrong_epoch"))cas.primary_epoch++;
    else if(!strcmp(mode,"wrong_slot"))rr.slot_index++;
    else if(!strcmp(mode,"no_external_cas"))cas.external_cas_confirmed=false;
    else if(!strcmp(mode,"no_external_readback"))rr.external_readback_verified=false;
    else if(!strcmp(mode,"null_pending"))pending_ptr=NULL;
    else if(!strcmp(mode,"null_cas"))cas_ptr=NULL;
    else if(!strcmp(mode,"null_rr"))rr_ptr=NULL;
    else if(!strcmp(mode,"null_readback"))actual_ptr=NULL;
    else if(!strcmp(mode,"null_probe"))probe_ptr=NULL;
    else if(!strcmp(mode,"null_context")){}
    else if(!strcmp(mode,"null_output"))output_ptr=NULL;
    else if(!strcmp(mode,"alias_output_pending"))output_ptr=(vg_b34_envelope *)(void *)&pending;
    else if(!strcmp(mode,"alias_output_cas"))output_ptr=(vg_b34_envelope *)(void *)&cas;
    else if(!strcmp(mode,"alias_output_rr"))output_ptr=(vg_b34_envelope *)(void *)&rr;
    else if(!strcmp(mode,"alias_output_readback"))output_ptr=(vg_b34_envelope *)(void *)actual;
    else if(!strcmp(mode,"alias_pending_cas"))pending_ptr=(const vg_b30_pending *)(const void *)&cas;
    else if(!strcmp(mode,"alias_rr_pending"))rr_ptr=(const vg_b30_readback_receipt *)(const void *)&pending;
    else if(!strcmp(mode,"alias_readback_pending"))actual_ptr=(const uint8_t *)(const void *)&pending;
    else if(!strcmp(mode,"zero_len"))actual_len=0u;
    else if(!strcmp(mode,"overlong_len"))actual_len=VG_B19_SLOT_MAX+1u;
    else if(!strcmp(mode,"probe_first_fail")){}
    else if(!strcmp(mode,"probe_second_fail")){}
    else if(!strcmp(mode,"probe_first_wrong_revision")){}
    else if(!strcmp(mode,"probe_second_wrong_revision")){}
    else if(!strcmp(mode,"probe_first_mutate_pending")){}
    else if(!strcmp(mode,"probe_second_mutate_cas")){}
    else if(!strcmp(mode,"probe_second_mutate_readback")){}
    else return 25;
    vg_b30_pending pending_before=pending;
    vg_b29_cas_receipt cas_before=cas;
    vg_b30_readback_receipt rr_before=rr;
    uint8_t image_before[VG_B19_SLOT_MAX];memcpy(image_before,actual,sizeof(actual));
    bool accepted=vg_b34_finalize_envelope(
         pending_ptr,cas_ptr,rr_ptr,actual_ptr,actual_len,revision,
         probe_ptr,!strcmp(mode,"null_context")?NULL:&probe_ctx,output_ptr);
    if(!strcmp(mode,"accept")){
        if(!accepted || output.version!=VG_B34_ENVELOPE_VERSION ||
           output.valid_marker!=VG_B34_ENVELOPE_VALID ||
           output.checkpoint_generation!=13u ||
           output.last_accepted_sequence!=10u ||
           output.externally_confirmed_revision!=101u ||
           output.checkpoint_crc32!=vg_b18_crc32(actual,actual_len) ||
           output.guard.accepted_round!=2u)return 26;
    }else if(accepted || memcmp(&output,&before_output,sizeof(output)))return 27;
    /* Deliberate revision callback input mutation is an adversarial injection. */
    const bool injected=!strncmp(mode,"probe_",6) && strstr(mode,"mutate_")!=NULL;
    if(!injected &&
       (memcmp(&pending,&pending_before,sizeof(pending)) ||
        memcmp(&cas,&cas_before,sizeof(cas)) ||
        memcmp(&rr,&rr_before,sizeof(rr)) ||
        memcmp(actual,image_before,sizeof(actual))))return 28;
    printf("B34_ENVELOPE=PASS_%s\n",mode);return 0;
}
int b34_reference_fixture_main(int argc,char **argv){
    int r=99;
    if(argc==3 && !strcmp(argv[1],"stage"))r=stage(argv[2]);
    else if(argc==4 && !strcmp(argv[1],"verify"))r=verify34(argv[2],argv[3]);
    if(r)fprintf(stderr,"B34_FAIL=%d\n",r);
    return r;
}

#include "phase9_b35_wire_receipt_host.h"

static int build35(const char *path,vg_b34_envelope *envelope,
                   uint8_t *snapshot,size_t *snapshot_len) {
    fixture f;FILE *fp=fopen(path,"rb");if(!fp)return 20;
    bool ok=fread(&f,1,sizeof(f),fp)==sizeof(f) && fgetc(fp)==EOF;
    if(fclose(fp))ok=false;
    if(!ok)return 21;
    const uint32_t tag=VG_B18_DEVICE_TAG,da=0xB261u,db=0xB262u;
    vg_b23_witness old={11u,8u};vg_b26_dual_guard guard;
    if(!vg_b26_seed(tag,da,db,41u,71u,&old,&guard))return 22;
    vg_b28_fence fence;if(!vg_b28_seed_fence(&guard,100u,&fence))return 23;
    vg_b27_votes votes[2];memset(votes,0,sizeof(votes));
    for(unsigned i=0u;i<2u;++i){
        votes[i].primary=f.tickets[i].proposed;
        votes[i].secondary=f.tickets[i].proposed;
        votes[i].primary_epoch=42u+i;votes[i].secondary_epoch=72u+i;
    }
    const uint8_t *expected[2]={f.expected[0],f.expected[1]};
    vg_b30_pending pending={0};
    if(!vg_b30_prepare_exact(f.before,f.middle,f.after,tag,da,db,
         &guard,&fence,100u,f.tickets,expected,f.size,votes,&pending) ||
         !pending.ready || pending.image_len>VG_B19_SLOT_MAX)return 24;
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
    memcpy(snapshot,pending.image,pending.image_len);
    *snapshot_len=pending.image_len;
    b33_probe_ctx probe_ctx={"accept",0u,&pending,&cas,&rr,snapshot};
    return vg_b34_finalize_envelope(&pending,&cas,&rr,snapshot,*snapshot_len,
            101u,b33_probe,&probe_ctx,envelope)?0:25;
}
static int stage35(const char *input,const char *outpath){
    vg_b34_envelope e;uint8_t snap[VG_B19_SLOT_MAX];size_t n=0u;
    int result=build35(input,&e,snap,&n);if(result)return result;
    uint8_t b[VG_B35_WIRE_LENGTH];size_t written=0u;
    if(!vg_b35_encode(&e,snap,n,b,sizeof(b),&written) ||
       written!=VG_B35_WIRE_LENGTH)return 26;
    FILE *f=fopen(outpath,"wb");if(!f)return 27;
    bool ok=fwrite(b,1,sizeof(b),f)==sizeof(b);
    if(fclose(f))ok=false;
    if(!ok)return 28;
    puts("B35_STAGE=PASS_CANONICAL_72_BYTES");return 0;
}
static void recalc35(uint8_t *bytes){
    uint32_t c=vg_b18_crc32(bytes,68u);
    for(unsigned i=0u;i<4u;i++)bytes[68u+i]=(uint8_t)(c>>(8u*i));
}
static int verify35(const char *input,const char *serialized,const char *mode){
    vg_b34_envelope e;uint8_t snapshot[VG_B19_SLOT_MAX];size_t n=0u;
    int result=build35(input,&e,snapshot,&n);if(result)return result;
    uint8_t raw[VG_B35_WIRE_LENGTH+1u]={0};
    FILE *fp=fopen(serialized,"rb");if(!fp)return 30;
    size_t length=fread(raw,1,sizeof(raw),fp);
    if(ferror(fp) || fclose(fp))return 31;
    const uint8_t *rawp=raw;
    const vg_b34_envelope *ep=&e;
    const uint8_t *snapshotp=snapshot;
    vg_b35_receipt verified;memset(&verified,0x5a,sizeof(verified));
    vg_b35_receipt before=verified,*dest=&verified;
    size_t data_len=n;
    bool encoded_case=false,expect_accept=!strcmp(mode,"accept");
    if(expect_accept){}
    else if(!strcmp(mode,"wrong_magic")){raw[0]^=1u;recalc35(raw);}
    else if(!strcmp(mode,"wrong_version")){raw[4]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_length_field")){raw[8]--;recalc35(raw);}
    else if(!strcmp(mode,"wrong_device")){raw[12]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_primary_domain")){raw[16]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_secondary_domain")){raw[20]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_generation")){raw[24]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_ack")){raw[28]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_snapshot_crc")){raw[32]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_revision")){raw[36]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_round")){raw[44]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_primary_epoch")){raw[52]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_secondary_epoch")){raw[60]++;recalc35(raw);}
    else if(!strcmp(mode,"wrong_footer")){raw[68]++;}
    else if(!strcmp(mode,"truncated")){length--;}
    else if(!strcmp(mode,"trailing")){raw[length++]=0u;}
    else if(!strcmp(mode,"empty")){length=0u;}
    else if(!strcmp(mode,"null_raw")){rawp=NULL;}
    else if(!strcmp(mode,"null_envelope")){ep=NULL;}
    else if(!strcmp(mode,"null_snapshot")){snapshotp=NULL;}
    else if(!strcmp(mode,"null_dest")){dest=NULL;}
    else if(!strcmp(mode,"zero_snapshot_len")){data_len=0u;}
    else if(!strcmp(mode,"snapshot_mutation")){snapshot[20u]^=1u;}
    else if(!strcmp(mode,"envelope_revision")){e.externally_confirmed_revision++;}
    else if(!strcmp(mode,"envelope_ack")){e.last_accepted_sequence++;}
    else if(!strcmp(mode,"envelope_generation")){e.checkpoint_generation++;}
    else if(!strcmp(mode,"envelope_marker")){e.valid_marker=0u;}
    else if(!strcmp(mode,"envelope_domain")){e.fence.primary_domain++;}
    else if(!strcmp(mode,"envelope_witness")){e.guard.primary.last_witness.confirmed_ack++;}
    else if(!strcmp(mode,"envelope_pending")){e.state.ack.pending=true;}
    else if(!strcmp(mode,"alias_dest_raw")){dest=(vg_b35_receipt *)(void *)raw;}
    else if(!strcmp(mode,"alias_dest_snapshot")){dest=(vg_b35_receipt *)(void *)snapshot;}
    else if(!strcmp(mode,"alias_dest_envelope")){dest=(vg_b35_receipt *)(void *)&e;}
    else if(!strcmp(mode,"alias_raw_snapshot")){rawp=snapshot;}
    else if(!strcmp(mode,"alias_raw_envelope")){rawp=(const uint8_t *)(const void *)&e;}
    else if(!strcmp(mode,"encode_null_output")){encoded_case=true;}
    else if(!strcmp(mode,"encode_tiny_capacity")){encoded_case=true;}
    else if(!strcmp(mode,"encode_alias_output_snapshot")){encoded_case=true;}
    else if(!strcmp(mode,"encode_alias_written_output")){encoded_case=true;}
    else if(!strcmp(mode,"encode_wrong_snapshot")){encoded_case=true;}
    else return 32;
    uint8_t snapshot_before[VG_B19_SLOT_MAX],raw_before[sizeof(raw)];
    vg_b34_envelope envelope_before=e;
    memcpy(snapshot_before,snapshot,sizeof(snapshot));
    memcpy(raw_before,raw,sizeof(raw));
    if(encoded_case){
        uint8_t output[VG_B35_WIRE_LENGTH];memset(output,0x7a,sizeof(output));
        uint8_t output_before[sizeof(output)];memcpy(output_before,output,sizeof(output));
        size_t written=0x5151u;
        uint8_t *ptr=!strcmp(mode,"encode_null_output")?NULL:output;
        size_t cap=!strcmp(mode,"encode_tiny_capacity")?VG_B35_WIRE_LENGTH-1u:VG_B35_WIRE_LENGTH;
        if(!strcmp(mode,"encode_alias_output_snapshot"))ptr=snapshot;
        size_t *wp=!strcmp(mode,"encode_alias_written_output")?(size_t *)(void *)output:&written;
        if(!strcmp(mode,"encode_wrong_snapshot"))snapshot[22u]^=1u;
        memcpy(snapshot_before,snapshot,sizeof(snapshot));
        bool accept=vg_b35_encode(&e,snapshot,n,ptr,cap,wp);
        if(accept || written!=0x5151u ||
           memcmp(output,output_before,sizeof(output))!=0 ||
           memcmp(snapshot,snapshot_before,sizeof(snapshot))!=0)return 33;
    }else{
        bool accept=vg_b35_verify(rawp,length,ep,snapshotp,data_len,dest);
        if(accept!=expect_accept)return 34;
        if(expect_accept){
            if(verified.device_tag!=VG_B18_DEVICE_TAG ||
               verified.checkpoint_generation!=13u ||
               verified.last_accepted_sequence!=10u ||
               verified.confirmed_revision!=101u ||
               verified.accepted_round!=2u ||
               verified.primary_epoch!=43u || verified.secondary_epoch!=73u)return 35;
        }else if(memcmp(&verified,&before,sizeof(verified))!=0)return 36;
    }
    if(memcmp(&e,&envelope_before,sizeof(e))!=0 ||
       memcmp(raw,raw_before,sizeof(raw))!=0 ||
       memcmp(snapshot,snapshot_before,sizeof(snapshot))!=0)return 37;
    printf("B35_WIRE=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    if(argc==3 && !strcmp(argv[1],"stage"))return b34_reference_fixture_main(argc,argv);
    if(argc==4 && !strcmp(argv[1],"stage"))return stage35(argv[2],argv[3]);
    if(argc==5 && !strcmp(argv[1],"verify")){
        int result=verify35(argv[2],argv[3],argv[4]);
        if(result)fprintf(stderr,"B35_FAIL=%d\n",result);
        return result;
    }
    return 3;
}
