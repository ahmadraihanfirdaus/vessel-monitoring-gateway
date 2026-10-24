/* B41 C99 host-only double observation fixture, no DB/hardware/network. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b41_rotation_fence_host.h"
static int exact_read(const char *path,uint8_t *p,size_t n) {
    FILE *f=fopen(path,"rb"); if(!f)return 0;
    size_t got=fread(p,1u,n,f);int tail=fgetc(f);
    int ok=(got==n && tail==EOF && !ferror(f));
    if(fclose(f)!=0)ok=0;
    return ok;
}
static int parse_u64(const char *txt,uint64_t *out) {
    char *end=NULL; unsigned long long value=strtoull(txt,&end,10);
    if(!txt[0]||!end||*end)return 0;
    *out=(uint64_t)value;return 1;
}
static void setup(vg_b41_observation *s,const char *mode,uint32_t purpose,uint32_t device) {
    memset(s,0,sizeof(*s));s->authority_revision=12u;s->source_id=777u;
    s->scope.purpose_id=purpose;s->scope.device_tag=device;
    if(!strcmp(mode,"pre")) {
        s->scope.rotation.active_key_id=101u;
        s->scope.rotation.activation_epoch=1u;
        s->scope.rotation.exclusive_epoch_floor=0u;
    } else {
        s->scope.rotation.active_key_id=202u;
        s->scope.rotation.retired_key_id=101u;
        s->scope.rotation.activation_epoch=40u;
        s->scope.rotation.exclusive_epoch_floor=39u;
    }
    if(!strcmp(mode,"retired"))s->scope.rotation.active_key_id=101u;
    if(!strcmp(mode,"future"))s->scope.rotation.activation_epoch=41u;
    if(!strcmp(mode,"floor"))s->scope.rotation.exclusive_epoch_floor=40u;
    if(!strcmp(mode,"badpurpose"))s->scope.purpose_id=2u;
    if(!strcmp(mode,"baddevice"))s->scope.device_tag=device+1u;
    if(!strcmp(mode,"badsource"))s->source_id=778u;
    if(!strcmp(mode,"zerokey"))s->scope.rotation.active_key_id=0u;
}
int main(int argc,char **argv) {
    if(argc!=13)return 20;
    uint8_t key[32],sealed[128],wire[72];
    if(!exact_read(argv[1],key,sizeof(key))||
       !exact_read(argv[2],sealed,sizeof(sealed))||
       !exact_read(argv[3],wire,sizeof(wire))) {
        puts("B41_ROTATION_FENCE=DENIED_TEST_ONLY");return 0;
    }
    uint64_t pur=0,dev=0,pre_rev=0,post_rev=0,floor=0,source=0;
    if(!parse_u64(argv[4],&pur)||!parse_u64(argv[5],&dev)||
       !parse_u64(argv[8],&pre_rev)||!parse_u64(argv[9],&post_rev)||
       !parse_u64(argv[10],&floor)||!parse_u64(argv[11],&source)||
       pur>UINT32_MAX||dev>UINT32_MAX)return 21;
    vg_b41_observation before,after;
    setup(&before,argv[6],(uint32_t)pur,(uint32_t)dev);
    setup(&after,argv[7],(uint32_t)pur,(uint32_t)dev);
    before.authority_revision=pre_rev;after.authority_revision=post_rev;
    uint64_t verified=0x8877665544332211ULL;
    bool ok=vg_b41_verify_rotation_fence(sealed,sizeof(sealed),wire,sizeof(wire),
                &before,&after,floor,source,(uint32_t)pur,(uint32_t)dev,
                key,sizeof(key),&verified);
    if(!strcmp(argv[12],"alias")) {
        vg_b41_observation copy=before;
        bool alias_ok=vg_b41_verify_rotation_fence(sealed,sizeof(sealed),wire,sizeof(wire),
                &before,&after,floor,source,(uint32_t)pur,(uint32_t)dev,
                key,sizeof(key),(uint64_t *)(void *)&before);
        if(alias_ok || memcmp(&copy,&before,sizeof(copy)))return 22;
        puts("B41_ROTATION_FENCE=DENIED_TEST_ONLY");return 0;
    }
    if((!ok&&verified!=0x8877665544332211ULL)||
       (ok&&verified!=vg_b36_get64(sealed+16u)))return 23;
    vg_b40_zero(key,sizeof(key));
    puts(ok?"B41_ROTATION_FENCE=ACCEPT_TEST_ONLY":"B41_ROTATION_FENCE=DENIED_TEST_ONLY");
    return 0;
}
