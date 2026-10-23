/* B15: host-only bridge from real volatile journal values, not deployed transport. */
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "core_event_journal.h"

static const char *event_type(vg_event_type_t t)
{
    switch(t) {
        case VG_EVENT_ALARM_RAISED: return "alarm_raised";
        case VG_EVENT_ALARM_ACK: return "alarm_ack";
        case VG_EVENT_ALARM_CLEARED: return "alarm_cleared";
        case VG_EVENT_FAULT: return "fault";
        default: return NULL;
    }
}
static int emit(const vg_journal_event_t *e)
{
    const char *mode=vg_source_mode_to_string(e->source_mode);
    const char *type=event_type(e->type);
    if (mode==NULL || type==NULL) return 0;
    return printf("{\"schema_version\":\"1.0\",\"device_id\":\"b15-demo-device\","
        "\"boot_id\":\"b15-boot\",\"event_id\":%" PRIu64
        ",\"linked_alarm_id\":%" PRIu64 ",\"source_id\":%" PRIu32
        ",\"source_mode\":\"%s\",\"event_type\":\"%s\",\"occurred_at_ms\":%" PRIu64 "}\n",
        e->event_id,e->linked_alarm_id,e->source_id,mode,type,e->occurred_at_ms)>0;
}
int main(void)
{
    vg_event_journal_t journal;
    const vg_event_type_t types[]={VG_EVENT_ALARM_RAISED,VG_EVENT_ALARM_ACK,
        VG_EVENT_ALARM_CLEARED,VG_EVENT_FAULT};
    const vg_source_mode_t modes[]={VG_SOURCE_SIMULATION,VG_SOURCE_SIMULATION,
        VG_SOURCE_BENCH_TEST,VG_SOURCE_SIMULATION};
    size_t i;
    uint64_t id=0;
    if(!vg_journal_init(&journal))return 11;
    for(i=0;i<4u;++i) {
        vg_journal_event_t event;
        if(!vg_journal_append(&journal,UINT64_C(7),(uint32_t)(i+1u),
            modes[i],types[i],UINT64_C(100)+(uint64_t)i,&id))return 12;
        if(id!=(uint64_t)(i+1u))return 13;
        if(!vg_journal_read(&journal,i,&event))return 14;
        if(!emit(&event))return 15;
    }
    if(vg_journal_append(&journal,7u,1u,VG_SOURCE_PHYSICAL,
        VG_EVENT_FAULT,105u,&id))return 16;
    if(journal.count!=4u)return 17;
    return 0;
}
