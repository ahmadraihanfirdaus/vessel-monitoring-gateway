/* Two native processes exchange a B24 host fixture file; no DB/network. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "phase9_b24_witness_receipt_host.h"
/* Internal fixture is intentionally same-ABI, NOT a durable/portable format. */
typedef struct {
 vg_b20_slot before[2],after[2];
 vg_b24_ticket ticket;
 uint8_t expected[VG_B19_SLOT_MAX];
 size_t size;
} fixture;
static int slot(vg_b20_slot *s,uint32_t generation,uint32_t ack_value,
                uint32_t tag) {
 net002_host_offline_store q;phase9_b8_ack_window ack;
 net002_host_init(&q);phase9_b8_ack_init(&ack);
 if(!net002_host_set_latest(&q,"0|null",6u) ||
    !net002_host_add_critical(&q,101u,2u,"alarm"))return 1;
 ack.last_accepted_sequence=ack_value;
 if(!phase9_b8_ack_begin(&ack,ack_value+1u,54u))return 2;
 return vg_b19_wrap(&q,&ack,tag,generation,s->bytes,
                    sizeof(s->bytes),&s->len)?0:3;
}
static int stage(const char *path) {
 const uint32_t tag=VG_B18_DEVICE_TAG;
 fixture f;memset(&f,0,sizeof(f));
 if(slot(&f.before[0],10u,7u,tag) || slot(&f.before[1],11u,8u,tag))return 10;
 memcpy(f.after,f.before,sizeof(f.before));
 if(slot(&f.after[0],12u,9u,tag))return 11;
 f.size=f.after[0].len;memcpy(f.expected,f.after[0].bytes,f.size);
 vg_b23_witness old={11u,8u};
 if(!vg_b24_issue_ticket(f.before,f.after,tag,&old,f.expected,f.size,
       0u,12u,9u,&f.ticket))return 12;
 FILE *file=fopen(path,"wb");if(!file)return 13;
 bool ok=fwrite(&f,1,sizeof(f),file)==sizeof(f);
 if(fclose(file)!=0)ok=false;
 if(!ok)return 14;
 puts("B24_STAGE=PASS_TICKET_NOT_COMMITTED");return 0;
}
static int verify(const char *path,const char *scenario) {
 FILE *file=fopen(path,"rb");if(!file)return 20;
 fixture f;
 bool ok=fread(&f,1,sizeof(f),file)==sizeof(f);
 if(fgetc(file)!=EOF)ok=false;
 if(fclose(file)!=0)ok=false;
 if(!ok)return 21;
 const uint32_t tag=VG_B18_DEVICE_TAG;
 vg_b23_witness observed={11u,8u};
 if(strcmp(scenario,"new")==0)observed=f.ticket.proposed;
 else if(strcmp(scenario,"out_of_order")==0){observed.generation=12u;observed.confirmed_ack=8u;}
 else if(strcmp(scenario,"stale")==0){observed.generation=10u;observed.confirmed_ack=7u;}
 else if(strcmp(scenario,"future")==0){observed.generation=13u;observed.confirmed_ack=10u;}
 else if(strcmp(scenario,"tamper_target")==0)f.after[0].bytes[20]^=1u;
 else if(strcmp(scenario,"tamper_previous")==0)f.after[1].bytes[20]^=1u;
 else if(strcmp(scenario,"tamper_expected")==0)f.expected[20]^=1u;
 else if(strcmp(scenario,"tamper_ticket")==0)f.ticket.candidate_crc32^=1u;
 else if(strcmp(scenario,"wrong_tag")==0)f.ticket.device_tag^=1u;
 else if(strcmp(scenario,"wrong_slot")==0)f.ticket.target_slot=1u;
 else if(strcmp(scenario,"partial")==0)f.after[0].len--;
 else if(strcmp(scenario,"rollback_ack")==0)f.ticket.proposed.confirmed_ack=7u;
 else if(strcmp(scenario,"wrap_gen")==0)f.ticket.previous.generation=UINT32_MAX;
 else if(strcmp(scenario,"old")==0){}else return 22;
 vg_b19_restored restored;memset(&restored,0x5a,sizeof(restored));
 vg_b19_restored unchanged=restored;bool committed=true;
 bool result=vg_b24_resolve_observation(f.before,f.after,tag,&f.ticket,
             f.expected,f.size,&observed,&restored,&committed);
 bool good=(strcmp(scenario,"old")==0 || strcmp(scenario,"new")==0);
 if(good) {
  uint32_t wanted=strcmp(scenario,"new")==0?12u:11u;
  uint32_t ack=strcmp(scenario,"new")==0?9u:8u;
  if(!result || restored.generation!=wanted ||
     restored.ack.last_accepted_sequence!=ack ||
     committed!=(strcmp(scenario,"new")==0) ||
     restored.ack.pending || restored.ack.pending_sequence ||
     restored.ack.pending_correlation)return 23;
 } else if(result || memcmp(&restored,&unchanged,sizeof(restored))!=0 ||
           committed!=true)return 24;
 printf("B24_RESOLVE=PASS_%s\n",scenario);
 return 0;
}
int main(int argc,char **argv){
 int r=99;
 if(argc==3 && strcmp(argv[1],"stage")==0)r=stage(argv[2]);
 else if(argc==4 && strcmp(argv[1],"verify")==0)r=verify(argv[2],argv[3]);
 if(r){fprintf(stderr,"B24_FAIL=%d\n",r);return r;}
 return 0;
}
