/* Dedicated real-module host observations; all data are public synthetic tests.
 * No hardware, database, file persistence, credentials or physical control. */
#include <stdio.h>
#include <string.h>
#include "alarm_transition.h"
#include "engine_model.h"
#include "navigation_nmea.h"
#include "provider_attitude.h"
#include "provider_vibration.h"
#include "provider_power.h"
#define main unused_formal_continuous_main
#include "continuous_simulation_fixture.c"
#undef main

static vg_continuous_simulation_t domain_runtime;

static unsigned checks;
#define REQUIRE(expression) do { ++checks; if (!(expression)) { \
    fprintf(stderr,"NATIVE_CHECK_FAILED_LINE=%u\n",(unsigned)__LINE__); return 2; } } while(0)
static const char *boolean(bool value) { return value ? "true" : "false"; }

static int alarm_case(void)
{
    vg_alarm_id_allocator_t ids;vg_alarm_id_allocator_init(&ids);
    vg_alarm_t alarm={0};vg_event_journal_t journal;vg_alarm_journal_t metadata={0};uint64_t id;
    REQUIRE(vg_journal_init(&journal));
    REQUIRE(vg_alarm_try_raise(&ids,&alarm,2,VG_SOURCE_SIMULATION,3,1001,0));
    REQUIRE(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&id));
    REQUIRE(vg_alarm_try_acknowledge(&alarm,0));
    vg_alarm_t acknowledged=alarm;
    REQUIRE(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,0,&id));
    REQUIRE(!vg_alarm_try_acknowledge(&alarm,0));REQUIRE(vg_alarm_metadata_equal(&alarm,&acknowledged));
    REQUIRE(metadata.entries[0].alarm.state==VG_ALARM_STATE_ACTIVE_UNACK);
    REQUIRE(vg_alarm_try_clear_condition(&alarm,10));
    REQUIRE(!vg_alarm_try_acknowledge(&alarm,11));
    REQUIRE(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_CLEARED,10,&id));
    REQUIRE(vg_alarm_journal_matches(&metadata,&journal));
    vg_alarm_t later={0};REQUIRE(vg_alarm_try_raise(&ids,&later,2,VG_SOURCE_SIMULATION,3,1001,20));
    vg_alarm_t saved=later;REQUIRE(!vg_alarm_try_acknowledge(&later,19));
    REQUIRE(vg_alarm_metadata_equal(&later,&saved));
    printf("{\"case\":\"SUP-004\",\"checks\":%u,\"active_after_ack\":%s,\"acknowledged\":%s,\"ack_state\":%u,"
        "\"raised\":%llu,\"ack_time_present\":%s,\"ack_time\":%llu,\"cleared_time_present_after_ack\":%s,"
        "\"raised_fact_state\":%u,\"condition_after_explicit_clear\":%s,\"next_alarm_id\":%llu,\"next_event_id\":%llu}\n",
        checks,boolean(acknowledged.condition_active),boolean(acknowledged.acknowledged),(unsigned)acknowledged.state,
        (unsigned long long)acknowledged.raised_at,boolean(acknowledged.has_acknowledged_at),
        (unsigned long long)acknowledged.acknowledged_at,boolean(acknowledged.has_cleared_at),
        (unsigned)metadata.entries[0].alarm.state,boolean(alarm.condition_active),
        (unsigned long long)ids.next_id,(unsigned long long)journal.next_id);
    return 0;
}
static int engine_case(void)
{
    vg_engine_model_t model={0},saved;vg_engine_snapshot_t profile[4],out;
    REQUIRE(vg_engine_demo_four_profile(&model,false));
    for(size_t i=0u;i<4u;i++){REQUIRE(vg_engine_model_get(&model,i,&profile[i]));REQUIRE(vg_engine_snapshot_is_consistent(&profile[i]));}
    saved=model;REQUIRE(!vg_engine_model_init(&model,0));REQUIRE(!memcmp(&model,&saved,sizeof(model)));
    REQUIRE(!vg_engine_model_init(&model,9));REQUIRE(!memcmp(&model,&saved,sizeof(model)));
    REQUIRE(vg_engine_model_init(&model,1));REQUIRE(model.engine_count==1);
    REQUIRE(vg_engine_model_init(&model,8));REQUIRE(model.engine_count==8);
    model=saved;out=profile[0];out.rpm=NAN;REQUIRE(!vg_engine_model_set(&model,0,&out));
    out=profile[0];out.rpm=-1;REQUIRE(!vg_engine_model_set(&model,0,&out));
    out=profile[0];out.engine_id=2;REQUIRE(!vg_engine_model_set(&model,0,&out));
    out=profile[0];out.source_mode=VG_SOURCE_PHYSICAL;REQUIRE(!vg_engine_model_set(&model,0,&out));
    out=profile[0];out.communication_quality=VG_ENGINE_COMM_LOST;REQUIRE(!vg_engine_model_set(&model,0,&out));
    REQUIRE(!memcmp(&model,&saved,sizeof(model)));
    out.state=VG_ENGINE_STATE_UNKNOWN;out.rpm=0;out.alarm_active=false;
    REQUIRE(vg_engine_model_set(&model,0,&out));REQUIRE(!memcmp(&model.engines[1],&saved.engines[1],3u*sizeof(out)));
    REQUIRE(!vg_engine_model_get(&model,4,&out));
    printf("{\"case\":\"SUP-005\",\"checks\":%u,\"engines\":[",checks);
    for(size_t i=0u;i<4u;i++){
        const vg_engine_snapshot_t *e=&profile[i];
        printf("%s{\"id\":%u,\"source\":\"%s\",\"state\":%u,\"rpm\":%.9g,\"temperature\":%.9g,\"runtime\":%llu,\"alarm\":%s,\"communication\":%u}",
            i?",":"",(unsigned)e->engine_id,vg_source_mode_to_string(e->source_mode),(unsigned)e->state,
            (double)e->rpm,(double)e->temperature_c,(unsigned long long)e->runtime_s,boolean(e->alarm_active),(unsigned)e->communication_quality);
    }
    printf("],\"lost_state\":%u,\"lost_rpm\":%.9g,\"lost_alarm\":%s}\n",(unsigned)model.engines[0].state,
        (double)model.engines[0].rpm,boolean(model.engines[0].alarm_active));return 0;
}
static int navigation_case(const char *const *sentences)
{
    const char *sentence=sentences[0];
    vg_navigation_state_t nav={0};const vg_nav_age_thresholds_t thresholds={100,300};
    REQUIRE(sentence && strlen(sentence)<VG_NAV_SENTENCE_MAX);
    REQUIRE(vg_nav_ingest_sentence(&nav,sentence,100,VG_SOURCE_SIMULATION));
    vg_navigation_state_t initial=nav,aged,saved;char corrupt[VG_NAV_SENTENCE_MAX];strcpy(corrupt,sentence);
    corrupt[strlen(corrupt)-1u]^=1;REQUIRE(!vg_nav_ingest_sentence(&nav,corrupt,150,VG_SOURCE_SIMULATION));
    REQUIRE(!memcmp(&initial,&nav,sizeof(nav)));
    for(size_t i=1u;i<=3u;i++) {
        REQUIRE(!vg_nav_ingest_sentence(&nav,sentences[i],150,VG_SOURCE_SIMULATION));
        REQUIRE(!memcmp(&initial,&nav,sizeof(nav)));
    }
    REQUIRE(!vg_nav_ingest_sentence(&nav,sentence,150,VG_SOURCE_PHYSICAL));
    REQUIRE(!memcmp(&initial,&nav,sizeof(nav)));
    REQUIRE(vg_nav_update_age(&nav,199,&thresholds));unsigned before=(unsigned)nav.age_state;
    REQUIRE(vg_nav_update_age(&nav,200,&thresholds));unsigned stale=(unsigned)nav.age_state;
    REQUIRE(vg_nav_update_age(&nav,400,&thresholds));aged=nav;
    bool ingest_rewound=vg_nav_ingest_sentence(&nav,sentence,50,VG_SOURCE_SIMULATION);
    bool ingest_unchanged=!memcmp(&nav,&aged,sizeof(nav));
    nav=aged;bool ingest_behind_observed=vg_nav_ingest_sentence(&nav,sentence,250,VG_SOURCE_SIMULATION);
    bool observed_unchanged=!memcmp(&nav,&aged,sizeof(nav));
    nav=aged;bool age_rewound=vg_nav_update_age(&nav,250,&thresholds);
    bool age_unchanged=!memcmp(&nav,&aged,sizeof(nav));
    nav=aged;REQUIRE(vg_nav_ingest_sentence(&nav,sentence,400,VG_SOURCE_SIMULATION));
    REQUIRE(nav.last_valid_ms==400 && nav.data_age_ms==0);
    saved=nav;REQUIRE(!vg_nav_update_age(&nav,399,&thresholds));REQUIRE(!memcmp(&nav,&saved,sizeof(nav)));
    nav=(vg_navigation_state_t){0};REQUIRE(vg_nav_ingest_sentence(&nav,sentence,UINT64_MAX,VG_SOURCE_SIMULATION));
    REQUIRE(vg_nav_update_age(&nav,UINT64_MAX,&thresholds));REQUIRE(nav.data_age_ms==0);
    vg_continuous_config_t config=test_config();
    REQUIRE(vg_continuous_init(&domain_runtime,&config,200));
    REQUIRE(vg_continuous_poll(&domain_runtime,200)==VG_CONTINUOUS_ENCODED);
    vg_navigation_state_t nofix={0};
    REQUIRE(vg_nav_ingest_sentence(&nofix,sentences[4],200,VG_SOURCE_SIMULATION));
    REQUIRE(!nofix.fix_valid);domain_runtime.sample.navigation=nofix;
    REQUIRE(vg_domain_build(&domain_runtime.sample,config.device,"formal-host",config.boot,1,200,&domain_runtime.working_payload));
    const vg_telemetry_channel_t *position=NULL;
    for(size_t i=0u;i<domain_runtime.working_payload.channel_count;i++)
        if(!strcmp(domain_runtime.working_payload.channels[i].name,"nav_latitude_deg"))position=&domain_runtime.working_payload.channels[i];
    REQUIRE(position!=NULL);
    printf("{\"case\":\"SUP-007\",\"checks\":%u,\"synthetic_only\":true,\"latitude\":%.17g,\"longitude\":%.17g,\"sog\":%.9g,\"cog\":%.9g,\"fix\":%s,"
        "\"source\":\"%s\",\"quality\":\"%s\",\"initial_age\":%llu,\"before_age_state\":%u,\"stale_state\":%u,\"offline_state\":%u,\"offline_age\":%llu,"
        "\"ingest_rewound\":%s,\"ingest_unchanged\":%s,\"ingest_behind_observed\":%s,\"observed_unchanged\":%s,\"age_rewound\":%s,\"age_unchanged\":%s,"
        "\"nofix_position_quality\":\"%s\",\"nofix_position_present\":%s}\n",
        checks,initial.latitude_deg,initial.longitude_deg,(double)initial.sog_knots,(double)initial.cog_deg,boolean(initial.fix_valid),
        vg_source_mode_to_string(initial.source_mode),vg_tel_quality_to_string(initial.quality),(unsigned long long)initial.data_age_ms,
        before,stale,(unsigned)aged.age_state,(unsigned long long)aged.data_age_ms,boolean(ingest_rewound),boolean(ingest_unchanged),
        boolean(ingest_behind_observed),boolean(observed_unchanged),boolean(age_rewound),boolean(age_unchanged),
        vg_tel_quality_to_string(position->quality),boolean(position->has_value));return 0;
}

static int attitude_case(void)
{
    vg_attitude_sim_t sim;vg_attitude_sample_t samples[8],out,saved;
    REQUIRE(vg_attitude_sim_init(&sim,0,100));
    for(size_t i=0u;i<8u;i++)REQUIRE(vg_attitude_sim_sample_for_step(&sim,i,&samples[i]));
    saved=out=samples[0];
    REQUIRE(!vg_attitude_bench_build_sample(&out,VG_QUALITY_VALID,true,NAN,0,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(!vg_attitude_bench_build_sample(&out,VG_QUALITY_VALID,false,0,0,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(vg_attitude_bench_build_sample(&out,VG_QUALITY_VALID,true,0,0,0,1));REQUIRE(out.meta.source_mode==VG_SOURCE_BENCH_TEST);
    out.meta.source_mode=VG_SOURCE_PHYSICAL;REQUIRE(!vg_attitude_sample_is_consistent(&out));
    printf("{\"case\":\"SUP-008\",\"checks\":%u,\"label\":\"%s\",\"scope\":\"%s\",\"steps\":[",checks,vg_attitude_channel_label(),vg_attitude_scope_note());
    for(size_t i=0u;i<8u;i++){
        const vg_attitude_sample_t *s=&samples[i];printf("%s{\"quality\":\"%s\",\"source\":\"%s\",\"present\":%s,\"current\":%s,\"time\":%llu,\"sequence\":%u,\"values\":[%.9g,%.9g]}",
            i?",":"",vg_tel_quality_to_string(s->meta.quality),vg_source_mode_to_string(s->meta.source_mode),boolean(s->has_value),boolean(vg_attitude_sample_is_current(s)),
            (unsigned long long)s->meta.sampled_at_ms,(unsigned)s->meta.sequence,(double)s->roll_deg,(double)s->pitch_deg);
    }puts("]}");return 0;
}
static int vibration_case(void)
{
    vg_vibration_sim_t sim;vg_vibration_sample_t samples[8],out,saved;
    REQUIRE(vg_vibration_sim_init(&sim,0,100));
    for(size_t i=0u;i<8u;i++)REQUIRE(vg_vibration_sim_sample_for_step(&sim,i,&samples[i]));
    saved=out=samples[0];
    REQUIRE(!vg_vibration_bench_build_sample(&out,VG_QUALITY_VALID,true,0,0,1,-1,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(!vg_vibration_bench_build_sample(&out,VG_QUALITY_VALID,true,0,0,1,NAN,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(!vg_vibration_bench_build_sample(&out,VG_QUALITY_VALID,false,0,0,1,0,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(vg_vibration_bench_build_sample(&out,VG_QUALITY_VALID,true,0,0,1,0,0,1));REQUIRE(out.meta.source_mode==VG_SOURCE_BENCH_TEST);
    out.meta.source_mode=VG_SOURCE_PHYSICAL;REQUIRE(!vg_vibration_sample_is_consistent(&out));
    printf("{\"case\":\"SUP-009\",\"checks\":%u,\"label\":\"%s\",\"scope\":\"%s\",\"steps\":[",checks,vg_vibration_channel_label(),vg_vibration_scope_note());
    for(size_t i=0u;i<8u;i++){
        const vg_vibration_sample_t *s=&samples[i];printf("%s{\"quality\":\"%s\",\"source\":\"%s\",\"present\":%s,\"current\":%s,\"time\":%llu,\"sequence\":%u,\"values\":[%.9g,%.9g,%.9g,%.9g]}",
            i?",":"",vg_tel_quality_to_string(s->meta.quality),vg_source_mode_to_string(s->meta.source_mode),boolean(s->has_value),boolean(vg_vibration_sample_is_current(s)),
            (unsigned long long)s->meta.sampled_at_ms,(unsigned)s->meta.sequence,(double)s->accel_x_g,(double)s->accel_y_g,(double)s->accel_z_g,(double)s->vibration_index);
    }puts("]}");return 0;
}
static int power_case(void)
{
    vg_power_sim_t sim;vg_power_sample_t samples[8],out,saved;
    REQUIRE(vg_power_sim_init(&sim,0,100));
    for(size_t i=0u;i<8u;i++)REQUIRE(vg_power_sim_sample_for_step(&sim,i,&samples[i]));
    saved=out=samples[0];
    REQUIRE(!vg_power_bench_build_sample(&out,VG_QUALITY_VALID,true,-1,0,0,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(!vg_power_bench_build_sample(&out,VG_QUALITY_VALID,true,5,NAN,0,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(!vg_power_bench_build_sample(&out,VG_QUALITY_VALID,false,0,0,0,0,1));REQUIRE(!memcmp(&out,&saved,sizeof(out)));
    REQUIRE(vg_power_bench_build_sample(&out,VG_QUALITY_VALID,true,0,0,0,0,1));REQUIRE(out.has_value && vg_power_sample_is_current(&out));
    bool zero_present=out.has_value;out.meta.source_mode=VG_SOURCE_PHYSICAL;REQUIRE(!vg_power_sample_is_consistent(&out));
    printf("{\"case\":\"SUP-010\",\"checks\":%u,\"label\":\"%s\",\"scope\":\"%s\",\"hazard\":\"%s\",\"zero_present\":%s,\"steps\":[",checks,vg_power_channel_label(),vg_power_scope_note(),vg_power_hazard_note(),boolean(zero_present));
    for(size_t i=0u;i<8u;i++){
        const vg_power_sample_t *s=&samples[i];printf("%s{\"quality\":\"%s\",\"source\":\"%s\",\"present\":%s,\"current\":%s,\"time\":%llu,\"sequence\":%u,\"values\":[%.9g,%.9g,%.9g]}",
            i?",":"",vg_tel_quality_to_string(s->meta.quality),vg_source_mode_to_string(s->meta.source_mode),boolean(s->has_value),boolean(vg_power_sample_is_current(s)),
            (unsigned long long)s->meta.sampled_at_ms,(unsigned)s->meta.sequence,(double)s->voltage_v,(double)s->current_a,(double)s->power_w);
    }puts("]}");return 0;
}
int main(int argc,char **argv)
{
    if(argc<2 || argc>7)return 2;
    if(!strcmp(argv[1],"SUP-004") && argc==2)return alarm_case();
    if(!strcmp(argv[1],"SUP-005") && argc==2)return engine_case();
    if(!strcmp(argv[1],"SUP-007") && argc==7)return navigation_case((const char *const *)(argv+2));
    if(!strcmp(argv[1],"SUP-008") && argc==2)return attitude_case();
    if(!strcmp(argv[1],"SUP-009") && argc==2)return vibration_case();
    if(!strcmp(argv[1],"SUP-010") && argc==2)return power_case();
    return 2;
}
