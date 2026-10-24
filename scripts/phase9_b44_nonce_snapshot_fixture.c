/* Standalone C99 fixture for B44 sealed nonce ledger checkpoint. Host only. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b44_nonce_snapshot_host.h"
static int exact_read(const char *name,uint8_t *ptr,size_t n){
    FILE *f=fopen(name,"rb");if(!f)return 0;
    size_t count=fread(ptr,1u,n,f);int end=fgetc(f);
    int ok=count==n&&end==EOF&&!ferror(f);if(fclose(f))ok=0;return ok;
}
static int exact_write(const char *name,const uint8_t *ptr,size_t n){
    FILE *f=fopen(name,"wb");if(!f)return 0;
    int ok=fwrite(ptr,1u,n,f)==n&&!ferror(f);if(fclose(f))ok=0;return ok;
}
static int parse(const char *str,uint64_t *value){
    char *end=NULL;unsigned long long number;
    if(!str||!*str||*str=='-')return 0;
    number=strtoull(str,&end,10);
    if(end==str||*end)return 0;
    *value=(uint64_t)number;return 1;
}
int main(int argc,char **argv){
    if(argc==2&&!strcmp(argv[1],"selftest")){
        uint8_t shared[VG_B44_SNAPSHOT_LENGTH],key[32];
        memset(shared,0xA5,sizeof(shared));memset(key,0x31,sizeof(key));
        vg_b43_nonce_ledger ledger;vg_b43_ledger_init(&ledger);
        uint8_t saved[VG_B44_SNAPSHOT_LENGTH];memcpy(saved,shared,sizeof(saved));
        if(vg_b44_seal_nonce_ledger(&ledger,5u,777u,key,sizeof(key),
               (uint8_t *)(void *)&ledger,sizeof(ledger))||
           vg_b44_seal_nonce_ledger(&ledger,5u,777u,key,sizeof(key),
               shared,sizeof(shared)-1u)||
           memcmp(shared,saved,sizeof(saved)))return 40;
        /* An output overlapping a key or input must not be modified. */
        uint8_t blob[192];
        if(!vg_b44_seal_nonce_ledger(&ledger,5u,777u,key,sizeof(key),blob,sizeof(blob)))return 41;
        memcpy(shared,blob,sizeof(blob));
        uint64_t accepted=UINT64_C(0x1111222233334444);
        if(vg_b44_restore_nonce_ledger(shared,sizeof(shared),1u,777u,key,32u,
              (vg_b43_nonce_ledger *)(void *)shared,&accepted)||
           memcmp(shared,blob,sizeof(blob))||
           accepted!=UINT64_C(0x1111222233334444))return 42;
        vg_b43_nonce_ledger restored;memset(&restored,0xAB,sizeof(restored));
        vg_b43_nonce_ledger orig=restored;
        if(vg_b44_restore_nonce_ledger(blob,sizeof(blob),1u,777u,
            (const uint8_t *)(const void *)&restored,32u,
            &restored,&accepted)||memcmp(&restored,&orig,sizeof(restored)))return 43;
        puts("B44_ALIAS_BOUNDS_FAILURE_IMMUTABLE=PASS");return 0;
    }
    if(argc!=8)return 20;
    const char *mode=argv[1];uint8_t key[32],blob[192],nonces[128];
    uint64_t gen=0u,source=0u,count=0u;
    if(!parse(argv[5],&gen)||!parse(argv[6],&source)||
       !parse(argv[7],&count)||!exact_read(argv[2],key,sizeof(key)))return 21;
    if(!strcmp(mode,"seal")){
        if(!exact_read(argv[3],nonces,sizeof(nonces)))return 22;
        vg_b43_nonce_ledger ledger;vg_b43_ledger_init(&ledger);
        ledger.count=(uint32_t)count;
        memcpy(ledger.used,nonces,sizeof(nonces));
        memset(blob,0xAAu,sizeof(blob));
        if(!vg_b44_seal_nonce_ledger(&ledger,gen,source,key,sizeof(key),blob,sizeof(blob))){
            puts("B44_SEAL_DENIED_TEST_ONLY");return 0;
        }
        if(!exact_write(argv[4],blob,sizeof(blob)))return 23;
        puts("B44_SEAL_ACCEPT_TEST_ONLY");return 0;
    }
    if(!strcmp(mode,"restore")){
        if(!exact_read(argv[3],blob,sizeof(blob)))return 24;
        vg_b43_nonce_ledger ledger;memset(&ledger,0xAA,sizeof(ledger));
        vg_b43_nonce_ledger sentinel=ledger;
        uint64_t accepted=UINT64_C(0xFA11FA11FA11FA11);
        bool ok=vg_b44_restore_nonce_ledger(blob,sizeof(blob),gen,source,key,
                                             sizeof(key),&ledger,&accepted);
        if(!ok){
            if(memcmp(&ledger,&sentinel,sizeof(ledger))||
               accepted!=UINT64_C(0xFA11FA11FA11FA11))return 25;
            puts("B44_RESTORE_DENIED_UNCHANGED_TEST_ONLY");return 0;
        }
        if(!vg_b43_ledger_valid(&ledger)||ledger.count!=count||
           accepted<gen)return 26;
        /* Re-export the decoded ledger to a different file only after success. */
        if(!exact_write(argv[4],(const uint8_t *)ledger.used,sizeof(ledger.used)))return 27;
        printf("B44_RESTORE_ACCEPT_TEST_ONLY_GEN_%llu\n",(unsigned long long)accepted);
        return 0;
    }
    return 28;
}
