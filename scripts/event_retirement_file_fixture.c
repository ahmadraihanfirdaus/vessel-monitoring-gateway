/* Host-only real file IO / actual shared owner + transaction + native crypto.
 * The Python wrapper restricts all file operations to its fresh private temp
 * root. Host fflush/commit/readback is NOT ESP32 power-loss evidence. */
#include <assert.h>
#include <errno.h>
#include <stdlib.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#else
#include <unistd.h>
#endif
#define VG_CONTINUOUS_FIXTURE_DEVICE "runtime:demo"
#define main unused_continuous_fixture_main
#include "continuous_simulation_fixture.c"
#undef main
#include "event_delivery.h"
#include "event_receipt_native_crypto.h"

#include "host_offline_file_io.h"
static file_disk disk;
static vg_offline_transaction transaction;
static vg_continuous_simulation_t runtime, old_runtime;
static vg_offline_event record;
static vg_event_journal_t cumulative;
static vg_alarm_journal_t cumulative_metadata;
static char wire[1024];
static uint8_t input_body[4096], input_receipt[512];

static bool verify(void *context,const void *body,size_t n,int status,const void *receipt,size_t rn,uint8_t digest[32])
{
    (void)context;const char *key=getenv("VG_LIVE_DEVICE_TOKEN");if(!key)return false;
    size_t length=0u;while(length<=256u && key[length])++length;
    const vg_receipt_crypto crypto=vg_receipt_native_provider();
    return vg_event_receipt_verify(&crypto,(const uint8_t *)key,length,body,n,status,receipt,rn,digest);
}
static void start_runtime(vg_continuous_simulation_t *r,const char *boot)
{
    vg_continuous_config_t config=test_config();assert(vg_tel_safe_token(boot,VG_TELEMETRY_MAX_ID_LEN));
    strcpy(config.boot,boot);assert(vg_continuous_init(r,&config,200u));
    for(unsigned i=1u;i<=24u && !r->journal.count;++i)
        assert(vg_continuous_poll(r,(uint64_t)i*200u)==VG_CONTINUOUS_ENCODED);
    assert(r->journal.count && r->working_payload.channel_count==48u);
}
static void first_record(const vg_continuous_simulation_t *r,vg_offline_event *out)
{
    assert(r->journal.count && vg_alarm_journal_matches(&r->alarm_journal,&r->journal));
    memset(out,0,sizeof(*out));strcpy(out->boot,r->config.boot);
    out->event=r->journal.events[0];out->has_alarm=true;out->alarm=r->alarm_journal.entries[0].alarm;
}
static void persist(void)
{
    vg_offline_merge_result result=vg_offline_merge_with_alarms(&transaction.current,runtime.config.boot,
        runtime.latest_sequence,runtime.latest_wire,runtime.latest_length,&runtime.journal,&runtime.alarm_journal,&transaction.candidate);
    assert(result==VG_OFFLINE_READY || result==VG_OFFLINE_CRITICAL_FULL);
    assert(transaction.candidate.event_count<=VG_OFFLINE_EVENT_CAP);
    assert(vg_offline_publish(&transaction));
}
static void emit_record(void)
{
    first_record(&runtime,&record);
    assert(vg_offline_event_json(&record,runtime.config.device,wire,sizeof(wire))==VG_REPLAY_ENCODED);
    puts(wire);
}
static uint32_t little32(const uint8_t *v)
{ return (uint32_t)v[0]|((uint32_t)v[1]<<8u)|((uint32_t)v[2]<<16u)|((uint32_t)v[3]<<24u); }

int main(int argc,char **argv)
{
    assert(argc==6); /* phase, owned folder, old boot, next boot, HTTP status */
    for(unsigned i=0u;i<2u;i++) {
        int n=snprintf(disk.paths[i],sizeof(disk.paths[i]),"%s/receipt-slot%u.bin",argv[2],i);
        assert(n>0 && (size_t)n<sizeof(disk.paths[i]));
    }
    vg_offline_io io={&disk,file_read,file_write,file_commit};
    assert(vg_offline_recover(&transaction,io,"runtime:demo"));
    if(!strcmp(argv[1],"prepare")) {
        assert(transaction.current.generation==0u);start_runtime(&runtime,argv[3]);persist();emit_record();return 0;
    }
    if(!strcmp(argv[1],"inspect")) {
        assert(!strcmp(transaction.current.latest_boot,argv[4]) && transaction.current.confirmed_event_id==1u);
        assert(!vg_offline_recovery_owner_valid(&transaction.current,argv[4],false));
        assert(vg_offline_recovery_owner_valid(&transaction.current,"another-fresh-host-boot",false));
        bool next=false;
        for(size_t i=0u;i<transaction.current.event_count;i++)
            if(!strcmp(transaction.current.events[i].boot,argv[4])) {
                assert(transaction.current.events[i].event.event_id>1u);next=true;
            }
        assert(next && transaction.current.latest_length>0u);puts("CHECKED");return 0;
    }
    assert(!strcmp(argv[1],"old") || !strcmp(argv[1],"current") || !strcmp(argv[1],"tamper"));
    start_runtime(&runtime,argv[4]);
    bool old=!strcmp(argv[1],"old"), tamper=!strcmp(argv[1],"tamper");
    if(old){start_runtime(&old_runtime,argv[3]);first_record(&old_runtime,&record);persist();}
    else {assert(!strcmp(transaction.current.latest_boot,argv[4]));first_record(&runtime,&record);}
    assert(vg_offline_event_json(&record,"runtime:demo",wire,sizeof(wire))==VG_REPLAY_ENCODED);
#ifdef _WIN32
    assert(_setmode(_fileno(stdin),_O_BINARY)!=-1);
#endif
    uint8_t header[8];assert(fread(header,1u,8u,stdin)==8u);
    size_t bn=little32(header),rn=little32(header+4u);
    assert(bn>0u && bn<=sizeof(input_body) && rn==VG_EVENT_RECEIPT_LENGTH);
    assert(fread(input_body,1u,bn,stdin)==bn && fread(input_receipt,1u,rn,stdin)==rn && fgetc(stdin)==EOF);
    assert(bn==strlen(wire) && !memcmp(input_body,wire,bn));
    assert(!strcmp(argv[5],"200") || !strcmp(argv[5],"201"));
    vg_event_delivery owner={0};vg_replay_progress progress={0};
    vg_delivery_context context={runtime.config.boot,&runtime.journal,&runtime.alarm_journal,&progress,NULL,false,1u};
    assert(vg_delivery_begin(&owner,VG_NET_EVENT,1u,&record,old?VG_REPLAY_RECOVERED:VG_REPLAY_CURRENT,0u,1u));
    if(!old)progress.current_queued=1u;
    vg_net_completion http={0};http.tag=1u;http.completed=true;http.http_status=atoi(argv[5]);
    http.event_receipt_media_valid=true;http.response_length=rn;memcpy(http.response,input_receipt,rn);
    assert(vg_delivery_receive_http(&owner,&http)==VG_DELIVERY_RECEIPT_READY);
    size_t retained=runtime.journal.count;uint64_t generation=transaction.current.generation;
    cumulative=runtime.journal;cumulative_metadata=runtime.alarm_journal;
    assert(vg_delivery_receipt_submitted(&owner));
    const vg_event_receipt_verifier verifier={NULL,verify};
    vg_storage_retirement_completion done={0};done.tag=1u;
    done.result=vg_offline_retire(&transaction,runtime.config.boot,&owner.record,&runtime.journal,&runtime.alarm_journal,
        &verifier,owner.status,owner.receipt,sizeof(owner.receipt),wire,sizeof(wire));
    done.generation=transaction.current.generation;done.confirmed_event_id=transaction.current.confirmed_event_id;
    if(tamper) {
        assert(done.result==VG_RETIRE_REJECTED && transaction.current.generation==generation);
        assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_REJECTED && owner.event_halted);
        assert(runtime.journal.count==retained);puts("REFUSED");return 0;
    }
    assert(done.result==VG_RETIRE_COMMITTED && transaction.current.generation==generation+1u);
    assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_CONFIRMED);
    assert(runtime.journal.count==retained-(old?0u:1u));
    assert(vg_offline_recover(&transaction,io,"runtime:demo"));
    for(size_t i=0u;i<transaction.current.event_count;i++)
        assert(strcmp(transaction.current.events[i].boot,record.boot) || transaction.current.events[i].event.event_id!=record.event.event_id);
    if(!old) {
        assert(transaction.current.confirmed_event_id==1u && runtime.journal.next_id==cumulative.next_id);
        /* An actual stale cumulative merge cannot resurrect the confirmed fact. */
        assert(vg_offline_merge_with_alarms(&transaction.current,runtime.config.boot,runtime.latest_sequence+1u,
            runtime.latest_wire,runtime.latest_length,&cumulative,&cumulative_metadata,&transaction.candidate)==VG_OFFLINE_READY);
        for(size_t i=0u;i<transaction.candidate.event_count;i++)
            assert(strcmp(transaction.candidate.events[i].boot,runtime.config.boot) || transaction.candidate.events[i].event.event_id>1u);
        for(unsigned i=0u;i<2u;i++)assert(vg_continuous_poll(&runtime,(runtime.sequence+1u)*200u)==VG_CONTINUOUS_ENCODED);
        persist();assert(runtime.journal.count && runtime.journal.events[0].event_id>1u);
    }
    emit_record();return 0;
}
