"""Shared SDK owner: real authenticated transaction precedes every positive release."""
import unittest
import test_offline_authenticated_retirement as retirement

SETUP = r'''
vg_alarm_journal_t metadata={0};vg_alarm_t alarm={0};vg_alarm_id_allocator_t ids;
vg_alarm_id_allocator_init(&ids);assert(vg_journal_init(&journal));uint64_t event_id;
assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&event_id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-b",1,"new",3,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));target_record=tx.current.events[1];
vg_event_delivery owner={0};vg_replay_progress progress={0};vg_recovered_events recovered={0};
vg_delivery_context context={"boot-b",&journal,&metadata,&progress,&recovered,false,1};
vg_net_completion http={0};http.tag=1;http.completed=true;http.http_status=201;
http.event_receipt_media_valid=true;http.response_length=sizeof(signed_receipt);
memcpy(http.response,signed_receipt,sizeof(signed_receipt));
vg_storage_retirement_completion done={0};done.tag=1;
assert(vg_delivery_context_valid(&context));
(void)http;(void)done;
'''
BEGIN = r'''
assert(vg_delivery_begin(&owner,VG_NET_EVENT,1,&target_record,VG_REPLAY_CURRENT,0,1));
progress.current_queued=1;
'''
READY = BEGIN+r'''
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_RECEIPT_READY);
assert(journal.count==1 && metadata.count==1 && tx.current.confirmed_event_id==0);
assert(vg_delivery_receipt_submitted(&owner));
'''
RETIRE = r'''
done.result=vg_offline_retire(&tx,"boot-b",&owner.record,&journal,&metadata,&verifier,
 owner.status,owner.receipt,sizeof(owner.receipt),working,sizeof(working));
done.generation=tx.current.generation;done.confirmed_event_id=tx.current.confirmed_event_id;
'''


class EventDeliveryTest(unittest.TestCase):
    def c(self, source):
        return retirement.AuthenticatedRetirementTest().c(SETUP+source, boot='boot-b', source_id=7, occurred=0,
            alarm=dict(priority_code=3, reason_code=1001, state='active_unack', raised_at_ms=0,
                       acknowledged_at_ms=None, cleared_at_ms=None), extra_headers='#include "event_delivery.h"\n')

    def test_only_genuine_durable_receipt_releases_exact_prefix_and_preserves_active_alarm(self):
        self.c(READY+RETIRE+r'''
assert(done.result==VG_RETIRE_COMMITTED);
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_CONFIRMED);
assert(owner.stage==VG_DELIVERY_IDLE && !owner.event_halted && owner.last_tag==1);
assert(journal.count==0 && metadata.count==0 && progress.current_queued==0 && journal.next_id==2);
assert(alarm.condition_active && !alarm.acknowledged && alarm.state==VG_ALARM_STATE_ACTIVE_UNACK);
assert(vg_alarm_try_acknowledge(&alarm,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,0,&event_id));assert(event_id==2);
assert(vg_delivery_next_tag(&owner)==2 && vg_delivery_context_valid(&context));
assert(vg_offline_recover(&tx,io,"disk:demo"));assert(tx.current.confirmed_event_id==1);
''')

    def test_failed_http_retries_original_prefix_then_genuine_receipt_unblocks_next_event(self):
        self.c(r'''
assert(vg_alarm_try_acknowledge(&alarm,1));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,1,&event_id));
assert(event_id==2 && journal.count==2 && alarm.condition_active);
assert(vg_offline_merge_with_alarms(&tx.current,"boot-b",2,"newer",5,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));
assert(vg_delivery_begin(&owner,VG_NET_EVENT,1,&target_record,VG_REPLAY_CURRENT,0,1));
assert(vg_replay_mark(&progress,0,journal.count,VG_REPLAY_CURRENT,false));
http.completed=false;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_NETWORK_FAILED);
assert(progress.current_queued==0 && journal.count==2 && metadata.count==2);
assert(vg_delivery_choose(&context)==VG_REPLAY_CURRENT && journal.events[progress.current_queued].event_id==1);
assert(vg_delivery_begin(&owner,VG_NET_EVENT,2,&target_record,VG_REPLAY_CURRENT,0,1));
assert(vg_replay_mark(&progress,0,journal.count,VG_REPLAY_CURRENT,false));
assert(vg_offline_record_equal(&owner.record,&target_record));
http.tag=2;http.completed=true;done.tag=2;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_RECEIPT_READY);
assert(vg_delivery_receipt_submitted(&owner));
'''+RETIRE+r'''
assert(done.result==VG_RETIRE_COMMITTED && done.confirmed_event_id==1);
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_CONFIRMED);
assert(journal.count==1 && metadata.count==1 && journal.events[0].event_id==2 && progress.current_queued==0);
assert(alarm.condition_active && alarm.acknowledged && vg_delivery_next_tag(&owner)==3);
assert(vg_offline_recover(&tx,io,"disk:demo") && tx.current.confirmed_event_id==1);
bool retained_next=false;for(size_t i=0;i<tx.current.event_count;i++)
 if(!strcmp(tx.current.events[i].boot,"boot-b") && tx.current.events[i].event.event_id==2)retained_next=true;
assert(retained_next);
''')

    def test_failed_recovered_event_rewinds_matching_epoch_but_never_a_new_view(self):
        self.c(r'''
assert(vg_recovered_events_capture(&tx.current,false,&recovered));context.recovered_ready=true;
target_record=recovered.events[0];assert(!target_record.has_alarm);
progress.prefer_recovered=true;
assert(vg_delivery_begin(&owner,VG_NET_EVENT,1,&target_record,VG_REPLAY_RECOVERED,0,1));
assert(vg_replay_mark(&progress,recovered.event_count,journal.count,VG_REPLAY_RECOVERED,false));
http.completed=false;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_NETWORK_FAILED);
assert(progress.recovered_visited==0 && recovered.event_count==2 && journal.count==1);
assert(vg_delivery_begin(&owner,VG_NET_EVENT,2,&target_record,VG_REPLAY_RECOVERED,0,1));
context.recovery_epoch=2;progress.recovered_visited=1;http.tag=2;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_NETWORK_FAILED);
assert(progress.recovered_visited==1 && !owner.event_halted && recovered.event_count==2);
assert(vg_delivery_begin(&owner,VG_NET_EVENT,3,&target_record,VG_REPLAY_RECOVERED,0,3));http.tag=3;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_REJECTED);
assert(progress.recovered_visited==1 && owner.event_halted && journal.count==1);
''')

    def test_failed_current_reply_requires_exact_identity_metadata_and_valid_context(self):
        self.c(r'''
vg_event_journal_t before_journal=journal;vg_alarm_journal_t before_metadata=metadata;
for(unsigned variant=0;variant<7;variant++) {
 memset(&owner,0,sizeof(owner));memset(&progress,0,sizeof(progress));context.boot="boot-b";
 assert(vg_delivery_begin(&owner,VG_NET_EVENT,1,&target_record,VG_REPLAY_CURRENT,0,1));
 progress.current_queued=1;http.completed=false;http.tag=1;
 if(variant==0)context.boot="other-boot";
 if(variant==1)owner.record.alarm.reason_code++;
 if(variant==2)owner.record.event.source_id++;
 if(variant==3)owner.source_index=journal.count;
 if(variant==4)owner.recovery_epoch=2;
 if(variant==5)progress.current_queued=journal.count+1;
 vg_replay_progress before_progress=progress;
 assert(vg_delivery_receive_http(&owner,&http,variant==6?NULL:&context)==VG_DELIVERY_REJECTED);
 assert(owner.event_halted && owner.stage==VG_DELIVERY_IDLE);
 assert(!memcmp(&journal,&before_journal,sizeof(journal)) && !memcmp(&metadata,&before_metadata,sizeof(metadata)));
 assert(!memcmp(&progress,&before_progress,sizeof(progress)));
}
''')

    def test_stale_failed_tag_cannot_rewind_and_already_reset_cursor_never_advances(self):
        self.c(BEGIN+r'''
http.completed=false;http.tag=2;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_IGNORED);
assert(progress.current_queued==1 && owner.stage==VG_DELIVERY_HTTP && owner.last_tag==1);
progress.current_queued=0;http.tag=1;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_NETWORK_FAILED);
assert(progress.current_queued==0 && owner.stage==VG_DELIVERY_IDLE && journal.count==1 && metadata.count==1);
''')

    def test_overlapping_failure_context_is_rejected_without_overwriting_owner_or_facts(self):
        self.c(BEGIN+r'''
http.completed=false;vg_event_delivery before_owner=owner;
vg_event_journal_t before_journal=journal;vg_alarm_journal_t before_metadata=metadata;
context.progress=(vg_replay_progress *)&owner;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_REJECTED);
assert(!memcmp(&owner,&before_owner,sizeof(owner)));
assert(!memcmp(&journal,&before_journal,sizeof(journal)) && !memcmp(&metadata,&before_metadata,sizeof(metadata)));
''')

    def test_tags_single_inflight_and_unrelated_completions_cannot_release(self):
        self.c(BEGIN+r'''
assert(!vg_delivery_next_tag(&owner));
assert(!vg_delivery_begin(&owner,VG_NET_TELEMETRY,2,NULL,VG_REPLAY_NONE,0,1));
http.tag=2;assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_IGNORED);
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_IGNORED);
assert(journal.count==1 && owner.stage==VG_DELIVERY_HTTP);
http.tag=1;http.completed=false;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_NETWORK_FAILED);
assert(journal.count==1 && metadata.count==1 && vg_delivery_next_tag(&owner)==2);
assert(vg_delivery_begin(&owner,VG_NET_TELEMETRY,2,NULL,VG_REPLAY_NONE,0,1));
http.tag=2;http.completed=true;http.event_receipt_media_valid=false;http.response_length=0;
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_TELEMETRY_DONE);
assert(journal.count==1 && vg_delivery_next_tag(&owner)==3);
owner.last_tag=UINT64_MAX;assert(!vg_delivery_next_tag(&owner));
''')

    def test_missing_truncated_or_wrong_media_receipt_retains_facts_and_halts_only_events(self):
        self.c(r'''
for(unsigned i=0;i<3;i++){
 memset(&owner,0,sizeof(owner));assert(vg_delivery_begin(&owner,VG_NET_EVENT,1,&target_record,VG_REPLAY_CURRENT,0,1));
 http.response_length=i==0?0:i==1?133:134;http.event_receipt_media_valid=i!=2;
 assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_REJECTED);
 assert(owner.event_halted && journal.count==1 && metadata.count==1 && owner.stage==VG_DELIVERY_IDLE);
 assert(!vg_delivery_begin(&owner,VG_NET_EVENT,2,&target_record,VG_REPLAY_CURRENT,0,1));
 assert(vg_delivery_begin(&owner,VG_NET_TELEMETRY,2,NULL,VG_REPLAY_NONE,0,1));
}
''')

    def test_genuine_crypto_rejection_is_not_an_ack(self):
        self.c(READY+r'''
owner.receipt[133]^=1;
'''+RETIRE+r'''
assert(done.result==VG_RETIRE_REJECTED);
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_REJECTED);
assert(owner.event_halted && journal.count==1 && metadata.count==1 && tx.current.confirmed_event_id==0);
''')

    def test_uncertain_io_never_frees_ram_and_allows_bounded_unretired_publication(self):
        self.c(READY+r'''
d.fail_commit=true;
'''+RETIRE+r'''
assert(done.result==VG_RETIRE_IO_HALTED);
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_UNRETIRED);
assert(journal.count==1 && metadata.count==1 && progress.current_queued==1 && !owner.event_halted);
assert(owner.stage==VG_DELIVERY_IDLE && vg_delivery_next_tag(&owner)==2);
''')

    def test_recovery_prerequisites_reschedule_and_epoch_prevents_wrong_view_rewind(self):
        self.c(READY+r'''
assert(vg_recovered_events_capture(&tx.current,false,&recovered));
context.recovered_ready=true;context.recovery_epoch=2;progress.current_queued=0;
/* In-flight target is now newer than a restored current-boot predecessor. */
owner.record.event.event_id=2;
assert(vg_delivery_prior_fact_pending(&owner.record,&context));
done.result=VG_RETIRE_REJECTED;
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_RESCHEDULED);
assert(!owner.event_halted && journal.count==1 && progress.current_queued==0);
assert(vg_delivery_begin(&owner,VG_NET_EVENT,2,&target_record,VG_REPLAY_RECOVERED,0,1));
http.tag=2;assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_RECEIPT_READY);
progress.recovered_visited=1;assert(vg_delivery_reschedule(&owner,&context));
assert(progress.recovered_visited==1); /* New epoch cannot inherit old cursor. */
assert(vg_delivery_begin(&owner,VG_NET_EVENT,3,&target_record,VG_REPLAY_RECOVERED,0,2));
http.tag=3;assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_RECEIPT_READY);
assert(vg_delivery_reschedule(&owner,&context));assert(progress.recovered_visited==0);
''')

    def test_recovered_current_predecessor_overrides_alternation_without_skipping_other_boot(self):
        self.c(r'''
assert(vg_recovered_events_capture(&tx.current,false,&recovered));context.recovered_ready=true;
/* RAM has advanced after a previous real receipt; recovery restored old fact1. */
assert(vg_delivery_begin(&owner,VG_NET_EVENT,1,&target_record,VG_REPLAY_CURRENT,0,1));
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_RECEIPT_READY);assert(vg_delivery_receipt_submitted(&owner));
'''+RETIRE+r'''
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_CONFIRMED);
assert(vg_alarm_try_acknowledge(&alarm,0));assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,0,&event_id));
progress.prefer_recovered=false;
assert(vg_delivery_choose(&context)==VG_REPLAY_RECOVERED && progress.prefer_recovered);
assert(vg_replay_mark(&progress,recovered.event_count,journal.count,VG_REPLAY_RECOVERED,false));
assert(vg_delivery_choose(&context)==VG_REPLAY_RECOVERED); /* Restored current fact1 before new fact2. */
''')

    def test_bad_completion_floor_or_generation_retains_exact_ram_fact(self):
        self.c(READY+r'''
done.result=VG_RETIRE_COMMITTED;done.generation=0;done.confirmed_event_id=1;
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_REJECTED);
assert(owner.event_halted && journal.count==1);
memset(&owner,0,sizeof(owner));assert(vg_delivery_begin(&owner,VG_NET_EVENT,1,&target_record,VG_REPLAY_CURRENT,0,1));
assert(vg_delivery_receive_http(&owner,&http,&context)==VG_DELIVERY_RECEIPT_READY);assert(vg_delivery_receipt_submitted(&owner));
done.generation=2;done.confirmed_event_id=0;
assert(vg_delivery_receive_storage(&owner,&done,&context)==VG_DELIVERY_REJECTED);
assert(journal.count==1 && metadata.count==1 && owner.event_halted);
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
