/* B18 host process-restart fixture. Uses stdio deliberately: no durability claim. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b18_checkpoint_host.h"
#include "phase9_b16_receipt_gate.h"

static int save(const char *path) {
    net002_host_offline_store s;
    net002_host_init(&s);
    const char latest[]="zero=0,null=null;simulated";
    if (!net002_host_set_latest(&s,latest,sizeof(latest)-1u)) return 10;
    for (uint32_t i=1u;i<=10u;++i) {
        char msg[24];
        if (snprintf(msg,sizeof(msg),"critical-%u",(unsigned)i)<0 ||
            !net002_host_add_critical(&s,i,i*50u,msg)) return 11;
    }
    phase9_b8_ack_window a;
    phase9_b8_ack_init(&a);
    if (!phase9_b8_ack_begin(&a,7u,71u) ||
        !phase9_b8_ack_commit(&a,7u,71u,true,true,true) ||
        !phase9_b8_ack_begin(&a,8u,81u)) return 12;
    uint8_t bytes[VG_B18_SNAPSHOT_MAX];size_t len=0u;
    if (!vg_b18_pack(&s,&a,VG_B18_DEVICE_TAG,bytes,sizeof(bytes),&len)) return 13;
    FILE *f=fopen(path,"wb");
    if (!f) return 14;
    int good=(fwrite(bytes,1u,len,f)==len && fflush(f)==0);
    if (fclose(f)!=0 || !good) return 15;
    printf("B18_SAVE=PASS_COUNT_8_EVICTED_2_PENDING_OMITTED_LENGTH_%u\n",(unsigned)len);
    return 0;
}
static int restore(const char *path) {
    uint8_t bytes[VG_B18_SNAPSHOT_MAX+1u];
    FILE *f=fopen(path,"rb");
    if (!f) return 20;
    size_t got=fread(bytes,1u,sizeof(bytes),f);
    int ok=!ferror(f);
    if (fclose(f)!=0 || !ok) return 21;
    net002_host_offline_store s;net002_host_init(&s);
    phase9_b8_ack_window a;phase9_b8_ack_init(&a);
    if (!vg_b18_unpack(bytes,got,VG_B18_DEVICE_TAG,&s,&a)) return 22;
    if (s.count!=8u || s.evicted_count!=2u || !s.has_latest ||
        s.latest_len!=sizeof("zero=0,null=null;simulated")-1u ||
        memcmp(s.latest,"zero=0,null=null;simulated",s.latest_len)!=0 ||
        a.last_accepted_sequence!=7u || a.pending || a.pending_sequence!=0u ||
        a.pending_correlation!=0u) return 23;
    for (size_t i=0u;i<8u;++i) {
        net002_host_critical_event e;
        char expected[24];
        if (!net002_host_get_event(&s,i,&e)) return 24;
        if (snprintf(expected,sizeof(expected),"critical-%u",(unsigned)(i+3u))<0 ||
            e.event_id!=(uint32_t)(i+3u) ||
            e.monotonic_ms!=(uint32_t)((i+3u)*50u) ||
            strcmp(e.text,expected)!=0) return 25;
    }
    /* Old pending correlation must NOT be accepted after simulated restart. */
    if (vg_b16_application_accept(503u,VG_B16_DEPENDENCY_UNAVAILABLE)) return 26;
    if (phase9_b8_ack_commit(&a,8u,81u,true,true,true)) return 27;
    if (!phase9_b8_ack_begin(&a,8u,82u) ||
        phase9_b8_ack_commit(&a,8u,81u,true,true,true) ||
        a.last_accepted_sequence!=7u) return 28;
    printf("B18_RESTART_RESTORE=PASS_8_EVENTS_2_EVICTED_LAST_ACK_7_NEW_PENDING_ONLY\n");
    return 0;
}
static int negatives(void) {
    net002_host_offline_store s;net002_host_init(&s);
    phase9_b8_ack_window a;phase9_b8_ack_init(&a);
    uint8_t sample[VG_B18_SNAPSHOT_MAX]={0};size_t len=0u;
    if (!net002_host_add_critical(&s,1u,2u,"alarm") ||
        !vg_b18_pack(&s,&a,VG_B18_DEVICE_TAG,sample,sizeof(sample),&len)) return 30;
    net002_host_offline_store destination;net002_host_init(&destination);
    phase9_b8_ack_window destack;phase9_b8_ack_init(&destack);
    if (!net002_host_add_critical(&destination,91u,92u,"preserve") ||
        !phase9_b8_ack_begin(&destack,5u,6u)) return 31;
    net002_host_offline_store oldstore=destination;
    phase9_b8_ack_window oldack=destack;
    uint8_t bytes[VG_B18_SNAPSHOT_MAX+1u];memcpy(bytes,sample,len);
    if (vg_b18_unpack(bytes,len,VG_B18_DEVICE_TAG+1u,&destination,&destack)) return 32;
    if (vg_b18_unpack(bytes,len-1u,VG_B18_DEVICE_TAG,&destination,&destack)) return 33;
    bytes[len]=1u;
    if (vg_b18_unpack(bytes,len+1u,VG_B18_DEVICE_TAG,&destination,&destack)) return 34;
    bytes[5u]^=1u;
    if (vg_b18_unpack(bytes,len,VG_B18_DEVICE_TAG,&destination,&destack)) return 35;
    memcpy(bytes,sample,len);bytes[len-1u]^=1u;
    if (vg_b18_unpack(bytes,len,VG_B18_DEVICE_TAG,&destination,&destack)) return 36;
    memcpy(bytes,sample,len);bytes[14u]=255u; /* out-of-bound event count */
    if (vg_b18_unpack(bytes,len,VG_B18_DEVICE_TAG,&destination,&destack)) return 37;
    if (memcmp(&destination,&oldstore,sizeof(oldstore))!=0 ||
        memcmp(&destack,&oldack,sizeof(oldack))!=0) return 38;
    /* Failed serializer must leave caller output and length unchanged. */
    size_t sentinel=987u;uint8_t small[8u];memset(small,0xAA,sizeof(small));
    if (vg_b18_pack(&s,&a,VG_B18_DEVICE_TAG,small,sizeof(small),&sentinel) ||
        sentinel!=987u) return 39;
    for (size_t i=0u;i<sizeof(small);++i) if (small[i]!=0xAA) return 40;
    printf("B18_NEGATIVE=PASS_WRONG_ID_TRUNCATION_TRAILING_CORRUPT_COUNT_ATOMIC\n");
    return 0;
}
int main(int argc,char **argv) {
    if (argc==2 && strcmp(argv[1],"negative")==0) return negatives();
    if (argc!=3) return 2;
    if (strcmp(argv[1],"save")==0) return save(argv[2]);
    if (strcmp(argv[1],"restore")==0) return restore(argv[2]);
    return 3;
}
