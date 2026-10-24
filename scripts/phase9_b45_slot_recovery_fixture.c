/* Standalone C99 B45 two-slot snapshot recovery fixture; host only. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b45_slot_recovery_host.h"

static int read_blob(const char *name,uint8_t *out,size_t *length){
    if(!strcmp(name,"-")){*length=0u;return 1;}
    FILE *f=fopen(name,"rb");if(!f)return 0;
    size_t n=fread(out,1u,VG_B44_SNAPSHOT_LENGTH+1u,f);int end=fgetc(f);
    int ok=!ferror(f)&&end==EOF;
    if(fclose(f))ok=0;
    *length=n;return ok;
}
static int read_key(const char *name,uint8_t *key){
    FILE *f=fopen(name,"rb");if(!f)return 0;
    size_t n=fread(key,1u,32u,f);int eof=fgetc(f);
    int ok=n==32u&&eof==EOF&&!ferror(f);
    if(fclose(f))ok=0;
    return ok;
}
static int number(const char *string,uint64_t *out){
    char *end=NULL;if(!string||!*string||*string=='-')return 0;
    unsigned long long v=strtoull(string,&end,10);
    if(end==string||*end)return 0;
    *out=(uint64_t)v;return 1;
}
static int selftest(void){
    uint8_t key[32],slot[192];memset(key,0x22,sizeof(key));
    vg_b43_nonce_ledger ledger;vg_b43_ledger_init(&ledger);
    if(!vg_b44_seal_nonce_ledger(&ledger,123u,777u,key,32u,slot,sizeof(slot)))return 40;
    uint64_t gen=0xABCDABCDu;uint8_t index=0xEEu;
    if(vg_b45_select_two_slot(slot,192u,NULL,0u,1u,777u,key,32u,
        (vg_b43_nonce_ledger *)(void *)slot,&gen,&index)||
        gen!=0xABCDABCDu||index!=0xEEu)return 41;
    vg_b43_nonce_ledger out;memset(&out,0x55,sizeof(out));
    vg_b43_nonce_ledger prior=out;
    if(vg_b45_select_two_slot(slot,192u,NULL,0u,1u,777u,key,32u,&out,
         (uint64_t *)(void *)&out,&index)||memcmp(&out,&prior,sizeof(out)))return 42;
    if(vg_b45_select_two_slot(slot,192u,NULL,0u,1u,777u,key,32u,&out,
          &gen,(uint8_t *)(void *)&gen)||memcmp(&out,&prior,sizeof(out)))return 43;
    if(vg_b45_select_two_slot(slot,191u,NULL,0u,1u,777u,key,32u,&out,
          &gen,&index)||memcmp(&out,&prior,sizeof(out)))return 44;
    if(vg_b45_select_two_slot(slot,192u,slot,192u,1u,777u,key,32u,&out,
          &gen,&index)||memcmp(&out,&prior,sizeof(out)))return 45;
    if(vg_b45_select_two_slot(NULL,0u,NULL,0u,1u,777u,key,32u,&out,
          &gen,&index)||memcmp(&out,&prior,sizeof(out)))return 46;
    puts("B45_ALIAS_LENGTH_IMMUTABLE=PASS");return 0;
}
int main(int argc,char **argv){
    if(argc==2&&!strcmp(argv[1],"selftest"))return selftest();
    if(argc!=7)return 20;
    uint8_t slot0[193],slot1[193],key[32];size_t n0=0u,n1=0u;
    uint64_t floor=0u,source=0u;
    if(!read_blob(argv[1],slot0,&n0)||!read_blob(argv[2],slot1,&n1)||
       !read_key(argv[3],key)||!number(argv[5],&floor)||!number(argv[6],&source))return 21;
    vg_b43_nonce_ledger ledger;memset(&ledger,0xA5,sizeof(ledger));
    vg_b43_nonce_ledger original=ledger;
    uint64_t gen=UINT64_C(0xFA11FA11FA11FA11);
    uint8_t index=0xAAu;
    bool selected=vg_b45_select_two_slot(strcmp(argv[1],"-")?slot0:NULL,n0,
                                         strcmp(argv[2],"-")?slot1:NULL,n1,
                                         floor,source,key,sizeof(key),&ledger,&gen,&index);
    if(!selected){
        if(memcmp(&original,&ledger,sizeof(ledger))||gen!=UINT64_C(0xFA11FA11FA11FA11)||
           index!=0xAAu)return 22;
        puts("B45_SELECT_DENIED_UNCHANGED_TEST_ONLY");return 0;
    }
    FILE *f=fopen(argv[4],"wb");if(!f)return 23;
    uint8_t result[141];result[0]=index;
    vg_b40_put_le64(result+1u,gen);
    vg_b40_put_le32(result+9u,ledger.count);
    memcpy(result+13u,ledger.used,sizeof(ledger.used));
    int ok=fwrite(result,1u,sizeof(result),f)==sizeof(result)&&!ferror(f);
    if(fclose(f))ok=0;
    if(!ok)return 24;
    printf("B45_SELECT_ACCEPT_SLOT_%u_GEN_%llu_TEST_ONLY\n",(unsigned int)index,
           (unsigned long long)gen);return 0;
}
