/* B17 host-only: response statuses/tags predecoded strictly by test harness.
 * Origin verification is deliberately simulated and never inferred from JSON. */
#include <stdio.h>
#include <stdint.h>
#include "phase9_b16_receipt_gate.h"
int main(int argc,char **argv){
    if(argc!=2)return 1;
    FILE *f=fopen(argv[1],"rb");
    if(!f)return 2;
    char line[160]; unsigned n=0u, accepted=0u, held=0u;
    phase9_b8_ack_window w;
    phase9_b8_ack_init(&w);
    while(fgets(line,sizeof line,f)!=NULL){
        unsigned status,tag,seq,corr,eligible;
        int pos=0;
        if(++n>8u || sscanf(line,"%u|%u|%u|%u|%u%n",&status,&tag,&seq,&corr,&eligible,&pos)!=5 ||
           pos<=0 || !((line[pos]=='\n' && line[pos+1]=='\0') ||
                       (line[pos]=='\r' && line[pos+1]=='\n' && line[pos+2]=='\0'))){fclose(f);return 3;}
        if(status>65535u || tag>VG_B16_UNAUTHORIZED || eligible>1u || seq==0u || corr==0u){fclose(f);return 4;}
        if(!phase9_b8_ack_begin(&w,(uint32_t)seq,(uint32_t)corr)){fclose(f);return 5;}
        vg_b16_receipt_t receipt={(uint16_t)status,(vg_b16_result_t)tag,(uint32_t)seq,(uint32_t)corr,false,true};
        if(vg_b16_commit_receipt(&w,receipt) || (w.last_accepted_sequence!=0u && accepted==0u)){fclose(f);return 6;}
        receipt.authenticated_response_verified=true;
        receipt.local_safety_pass=false;
        if(vg_b16_commit_receipt(&w,receipt)){fclose(f);return 7;}
        receipt.local_safety_pass=true;
        receipt.correlation++;
        if(vg_b16_commit_receipt(&w,receipt)){fclose(f);return 8;}
        receipt.correlation--;
        if(vg_b16_commit_receipt(&w,receipt)!=(eligible==1u)){fclose(f);return 9;}
        if(eligible==1u){
            if(w.pending || w.last_accepted_sequence!=seq){fclose(f);return 10;}
            accepted++;
        }else{
            if(!w.pending || w.pending_sequence!=seq){fclose(f);return 11;}
            phase9_b8_ack_cancel(&w);
            held++;
        }
    }
    fclose(f);
    if(n!=8u || accepted!=4u || held!=4u)return 12;
    puts("B17_ACK=PASS_8_CASES_4_ACCEPT_4_HOLD");
    return 0;
}
