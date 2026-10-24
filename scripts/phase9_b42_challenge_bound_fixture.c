/* B42 host-only fixture. Values, keys and challenges are independent test files. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b42_challenge_bound_host.h"
static int exact_read(const char *path,uint8_t *p,size_t n) {
    FILE *f=fopen(path,"rb");if(!f)return 0;
    size_t got=fread(p,1u,n,f);int tail=fgetc(f);
    int ok=(got==n&&tail==EOF&&!ferror(f));if(fclose(f)!=0)ok=0;
    return ok;
}
static int parse_u64(const char *txt,uint64_t *out) {
    char *end=NULL;unsigned long long value=strtoull(txt,&end,10);
    if(!txt[0]||txt[0]=='-'||!end||*end)return 0;
    *out=(uint64_t)value;return 1;
}
static void setup(vg_b41_observation *s,const char *mode,uint32_t purpose,uint32_t device) {
    memset(s,0,sizeof(*s));s->authority_revision=12u;s->source_id=777u;
    s->scope.purpose_id=purpose;s->scope.device_tag=device;
    if(!strcmp(mode,"pre")){
        s->scope.rotation.active_key_id=101u;
        s->scope.rotation.activation_epoch=1u;
        s->scope.rotation.exclusive_epoch_floor=0u;
    }else{
        s->scope.rotation.active_key_id=202u;
        s->scope.rotation.retired_key_id=101u;
        s->scope.rotation.activation_epoch=40u;
        s->scope.rotation.exclusive_epoch_floor=39u;
    }
    if(!strcmp(mode,"retired"))s->scope.rotation.active_key_id=101u;
    if(!strcmp(mode,"future"))s->scope.rotation.activation_epoch=41u;
    if(!strcmp(mode,"badpurpose"))s->scope.purpose_id=2u;
    if(!strcmp(mode,"baddevice"))s->scope.device_tag=device+1u;
    if(!strcmp(mode,"badsource"))s->source_id=778u;
}
int main(int argc,char **argv) {
    if(argc!=16)return 20;
    uint8_t key[32],sealed[128],wire[72],issued[16],received[16],proof[32];
    if(!exact_read(argv[1],key,sizeof(key))||!exact_read(argv[2],sealed,sizeof(sealed))||
       !exact_read(argv[3],wire,sizeof(wire))||!exact_read(argv[4],issued,sizeof(issued))||
       !exact_read(argv[5],received,sizeof(received))||!exact_read(argv[6],proof,sizeof(proof))){
        puts("B42_CHALLENGE=DENIED_TEST_ONLY");return 0;
    }
    uint64_t pur=0,dev=0,rev0=0,rev1=0,floor=0,source=0;
    if(!parse_u64(argv[7],&pur)||!parse_u64(argv[8],&dev)||
       !parse_u64(argv[11],&rev0)||!parse_u64(argv[12],&rev1)||
       !parse_u64(argv[13],&floor)||!parse_u64(argv[14],&source)||
       pur>UINT32_MAX||dev>UINT32_MAX)return 21;
    vg_b41_observation pre,post;setup(&pre,argv[9],(uint32_t)pur,(uint32_t)dev);
    setup(&post,argv[10],(uint32_t)pur,(uint32_t)dev);
    pre.authority_revision=rev0;post.authority_revision=rev1;
    uint64_t epoch=0x8877665544332211ULL;
    bool ok=vg_b42_verify_challenge(sealed,sizeof(sealed),wire,sizeof(wire),&pre,&post,
             floor,source,(uint32_t)pur,(uint32_t)dev,key,sizeof(key),
             issued,sizeof(issued),received,sizeof(received),proof,sizeof(proof),&epoch);
    if(!strcmp(argv[15],"alias")){
        vg_b41_observation copy=pre;
        bool alias_ok=vg_b42_verify_challenge(sealed,sizeof(sealed),wire,sizeof(wire),&pre,&post,
             floor,source,(uint32_t)pur,(uint32_t)dev,key,sizeof(key),
             issued,sizeof(issued),received,sizeof(received),proof,sizeof(proof),
             (uint64_t *)(void *)&pre);
        if(alias_ok||memcmp(&copy,&pre,sizeof(pre)))return 22;
        puts("B42_CHALLENGE=DENIED_TEST_ONLY");return 0;
    }
    if((!ok&&epoch!=0x8877665544332211ULL)||
       (ok&&epoch!=vg_b36_get64(sealed+16u)))return 23;
    vg_b40_zero(key,sizeof(key));
    puts(ok?"B42_CHALLENGE=ACCEPT_TEST_ONLY":"B42_CHALLENGE=DENIED_TEST_ONLY");
    return 0;
}
