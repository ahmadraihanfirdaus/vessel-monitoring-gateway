"""Actual receipt-authorized transaction IO with independent Python signatures."""
import hashlib
import hmac
import json
from pathlib import Path
import unittest
from phase9_b4_testlib import compile_c
from test_offline_transaction import COMMON

ROOT = Path(__file__).resolve().parents[1]


class AuthenticatedRetirementTest(unittest.TestCase):
    def c(self, source, boot='boot-a', event_id=1, linked_alarm_id=1, source_id=1,
          event_type='alarm_raised', occurred=10, alarm=None, extra_headers=''):
        key = bytes((i*7+11) % 256 for i in range(64))  # Public synthetic oracle input.
        packet = dict(schema_version='1.0', device_id='disk:demo', boot_id=boot, event_id=event_id,
                      linked_alarm_id=linked_alarm_id, source_id=source_id, source_mode='simulation',
                      event_type=event_type, occurred_at_ms=occurred)
        if alarm is not None:
            packet['schema_version'] = '1.1'
            packet['alarm'] = alarm
        raw = json.dumps(packet, separators=(',', ':')).encode()
        digest = hashlib.sha256(raw).hexdigest()
        mac = hmac.new(key, ('VG_EVENT_COMMIT_V1\n201\n'+digest).encode(), hashlib.sha256).hexdigest()
        receipt = ('VGR1:'+digest+':'+mac).encode()
        array = lambda data: ','.join(str(byte) for byte in data)
        prefix = '''#include "offline_retirement.h"
#include "event_receipt_native_crypto.h"
static uint8_t native_key[]={KEY},signed_receipt[]={RECEIPT};
static vg_offline_event target_record;
static char working[1024];
static bool verify(void *ctx,const void *body,size_t n,int status,const void *receipt,size_t rn,uint8_t digest[32]){
(void)ctx;const vg_receipt_crypto crypto=vg_receipt_native_provider();
return vg_event_receipt_verify(&crypto,native_key,sizeof(native_key),body,n,status,receipt,rn,digest);
}
static const vg_event_receipt_verifier verifier={NULL,verify};
static inline bool structural_only(void *ctx,const void *body,size_t n,int status,const void *receipt,size_t rn,uint8_t digest[32]){
(void)ctx;(void)body;(void)n;(void)status;(void)receipt;(void)rn;(void)digest;return true;
}
'''.replace('KEY', array(key)).replace('RECEIPT', array(receipt))
        return compile_c(extra_headers+prefix+COMMON+'target_record=tx.current.events[0];(void)working;(void)verifier;(void)native_key;(void)signed_receipt;\n'+source+'\nreturn 0;}\n',
                         extra_flags=('-Os', '-I', str(ROOT/'scripts')))

    def test_genuine_current_receipt_commits_floor_and_prevents_cumulative_resurrection_after_reboot(self):
        self.c(r'''
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
assert(tx.current.generation==2 && tx.current.confirmed_event_id==1 && tx.current.event_count==0);
assert(tx.current.latest_sequence==1 && tx.current.latest_length==5 && !memcmp(tx.current.latest,"first",5));
assert(vg_offline_recover(&tx,io,"disk:demo"));assert(tx.current.confirmed_event_id==1 && tx.current.event_count==0);
assert(vg_offline_merge(&tx.current,"boot-a",2,"second",6,&journal,&tx.candidate)==VG_OFFLINE_READY);
assert(tx.candidate.event_count==0 && tx.candidate.confirmed_event_id==1);assert(vg_offline_publish(&tx));
unsigned writes=d.writes;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_ALREADY_CONFIRMED);
assert(d.writes==writes);
''')

    def test_old_boot_receipt_preserves_unsupported_other_fact_and_is_idempotent(self):
        self.c(r'''
uint64_t id;assert(vg_journal_append(&journal,0,2,VG_SOURCE_BENCH_TEST,VG_EVENT_RECOVERY,11,&id));
assert(vg_offline_merge(&tx.current,"boot-a",2,"old",3,&journal,&tx.candidate)==VG_OFFLINE_READY);assert(vg_offline_publish(&tx));
assert(vg_journal_init(&journal));
assert(vg_offline_merge(&tx.current,"boot-b",1,"new",3,&journal,&tx.candidate)==VG_OFFLINE_READY);assert(vg_offline_publish(&tx));
assert(vg_offline_retire(&tx,"boot-b",&target_record,NULL,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
assert(tx.current.event_count==1 && tx.current.events[0].event.type==VG_EVENT_RECOVERY && tx.current.confirmed_event_id==0);
unsigned writes=d.writes;
assert(vg_offline_retire(&tx,"boot-b",&target_record,NULL,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_ALREADY_CONFIRMED);
assert(d.writes==writes && tx.current.event_count==1);
''')

    def test_every_receipt_byte_forgery_leaves_published_state_and_io_unchanged(self):
        self.c(r'''
unsigned writes=d.writes;
for(size_t i=0;i<sizeof(signed_receipt);i++){
signed_receipt[i]^=1;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
assert(d.writes==writes && !memcmp(&tx.current,&sentinel,sizeof(sentinel)));signed_receipt[i]^=1;
}
''')

    def test_wrong_key_status_owner_record_and_aliases_do_not_authorize_retirement(self):
        self.c(r'''
unsigned writes=d.writes;
native_key[0]^=1;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);native_key[0]^=1;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,200,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
assert(vg_offline_retire(&tx,"other-boot",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
target_record.event.source_id=2;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);target_record.event.source_id=1;
assert(vg_offline_retire(&tx,"boot-a",&tx.current.events[0],&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),(char*)&tx,sizeof(working))==VG_RETIRE_REJECTED);
assert(d.writes==writes && !memcmp(&tx.current,&sentinel,sizeof(sentinel)));
''')

    def test_valid_later_receipt_cannot_skip_oldest_unconfirmed_prefix_or_stored_fact(self):
        self.c(r'''
uint64_t id;assert(vg_journal_append(&journal,0,2,VG_SOURCE_SIMULATION,VG_EVENT_FAULT,11,&id));
assert(vg_offline_merge(&tx.current,"boot-a",2,"second",6,&journal,&tx.candidate)==VG_OFFLINE_READY);assert(vg_offline_publish(&tx));
target_record=tx.current.events[1];sentinel=tx.current;unsigned writes=d.writes;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
/* Even a falsely shortened caller prefix cannot delete/skip stored event1. */
journal.events[0]=journal.events[1];journal.count=1;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
assert(d.writes==writes && !memcmp(&tx.current,&sentinel,sizeof(sentinel)));
''', event_id=2, linked_alarm_id=0, source_id=2, event_type='fault', occurred=11)

    def test_actual_server_confirmed_current_fact_can_advance_floor_when_old_storage_is_full(self):
        self.c(r'''
assert(vg_journal_init(&journal));uint64_t id;
for(unsigned i=0;i<7;i++)assert(vg_journal_append(&journal,0,2,VG_SOURCE_SIMULATION,VG_EVENT_FAULT,20+i,&id));
assert(vg_offline_merge(&tx.current,"old-boot",1,"old",3,&journal,&tx.candidate)==VG_OFFLINE_READY);assert(vg_offline_publish(&tx));
assert(tx.current.event_count==8);
assert(vg_journal_init(&journal));assert(vg_journal_append(&journal,1,1,VG_SOURCE_SIMULATION,VG_EVENT_ALARM_RAISED,10,&id));
assert(vg_offline_merge(&tx.current,"boot-current",1,"new",3,&journal,&tx.candidate)==VG_OFFLINE_CRITICAL_FULL);assert(vg_offline_publish(&tx));
strcpy(target_record.boot,"boot-current");sentinel=tx.current;
assert(vg_offline_retire(&tx,"boot-current",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
assert(tx.current.event_count==8 && tx.current.confirmed_event_id==1);
for(size_t i=0;i<8;i++)assert(vg_offline_record_equal(&tx.current.events[i],&sentinel.events[i]));
assert(vg_offline_recover(&tx,io,"disk:demo"));assert(tx.current.confirmed_event_id==1);
''', boot='boot-current')

    def test_every_partial_retirement_write_preserves_selected_slot_and_halts_until_recovery(self):
        self.c(r'''
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
size_t size=d.length[tx.selected];
for(size_t cut=0;cut<size;cut++){
d=baseline;assert(vg_offline_recover(&tx,io,"disk:demo"));d.cut=cut;d.fail_write=true;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_IO_HALTED);
assert(tx.halted && tx.current.confirmed_event_id==0 && tx.current.event_count==1);
assert(!memcmp(d.bytes[0],baseline.bytes[0],baseline.length[0]));unsigned writes=d.writes;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);assert(d.writes==writes);
d.fail_write=false;d.cut=SIZE_MAX;assert(vg_offline_recover(&tx,io,"disk:demo"));
assert(tx.current.confirmed_event_id==0 && tx.current.event_count==1);
}
''')

    def test_uncertain_commit_and_readback_require_recovery_without_false_rollback_claim(self):
        self.c(r'''
d.fail_commit=true;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_IO_HALTED);
assert(tx.current.confirmed_event_id==0 && tx.current.event_count==1);
d.fail_commit=false;assert(vg_offline_recover(&tx,io,"disk:demo"));
assert(tx.current.confirmed_event_id==1 && tx.current.event_count==0);
unsigned writes=d.writes;signed_receipt[133]^=1;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);assert(d.writes==writes);
signed_receipt[133]^=1;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_ALREADY_CONFIRMED);assert(d.writes==writes);
d=baseline;assert(vg_offline_recover(&tx,io,"disk:demo"));d.tamper_read=true;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_IO_HALTED);
assert(tx.current.event_count==1 && tx.current.confirmed_event_id==0);
''')

    def test_complete_metadata_receipt_retires_exact_fact_and_retains_legacy_other_boot(self):
        self.c(r'''
vg_alarm_journal_t metadata={0};vg_alarm_t alarm={0};vg_alarm_id_allocator_t ids;
vg_alarm_id_allocator_init(&ids);assert(vg_journal_init(&journal));uint64_t id;
assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-b",1,"new",3,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));target_record=tx.current.events[1];
assert(vg_offline_retire(&tx,"boot-b",&target_record,&journal,&metadata,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
assert(tx.current.confirmed_event_id==1 && tx.current.event_count==1 && !tx.current.events[0].has_alarm);
assert(!strcmp(tx.current.events[0].boot,"boot-a"));
assert(vg_offline_recover(&tx,io,"disk:demo"));
assert(tx.current.confirmed_event_id==1 && tx.current.event_count==1);
assert(vg_offline_release_confirmed_prefix(&journal,&metadata,&target_record));
assert(journal.count==0 && metadata.count==0 && journal.next_id==2 && journal.has_last_time);
assert(alarm.condition_active && alarm.state==VG_ALARM_STATE_ACTIVE_UNACK && !alarm.acknowledged);
assert(vg_alarm_try_acknowledge(&alarm,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,0,&id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-b",2,"later",5,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(tx.candidate.event_count==2 && tx.candidate.events[1].event.event_id==2);
assert(tx.candidate.events[1].alarm.state==VG_ALARM_STATE_ACTIVE_ACK && tx.candidate.events[1].alarm.acknowledged_at==0);
assert(vg_offline_publish(&tx));
''', boot='boot-b', source_id=7, occurred=0,
            alarm=dict(priority_code=3, reason_code=1001, state='active_unack', raised_at_ms=0,
                       acknowledged_at_ms=None, cleared_at_ms=None))

    def test_matching_identity_with_missing_or_changed_full_metadata_cannot_retire(self):
        self.c(r'''
vg_alarm_journal_t metadata={0};vg_alarm_t alarm={0};vg_alarm_id_allocator_t ids;
vg_alarm_id_allocator_init(&ids);assert(vg_journal_init(&journal));uint64_t id;
assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-b",1,"new",3,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));target_record=tx.current.events[1];sentinel=tx.current;unsigned writes=d.writes;
assert(vg_offline_retire(&tx,"boot-b",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
target_record.alarm.reason_code++;
assert(vg_offline_retire(&tx,"boot-b",&target_record,&journal,&metadata,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
target_record.alarm.reason_code--;target_record.has_alarm=false;
assert(vg_offline_retire(&tx,"boot-b",&target_record,&journal,&metadata,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
assert(d.writes==writes && !memcmp(&tx.current,&sentinel,sizeof(sentinel)));
''', boot='boot-b', source_id=7, occurred=0,
            alarm=dict(priority_code=3, reason_code=1001, state='active_unack', raised_at_ms=0,
                       acknowledged_at_ms=None, cleared_at_ms=None))

    def test_structural_true_without_verified_digest_is_not_retirement_authority(self):
        self.c(r'''
const vg_event_receipt_verifier only_precheck={NULL,structural_only};unsigned writes=d.writes;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&only_precheck,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_REJECTED);
assert(d.writes==writes && !memcmp(&tx.current,&sentinel,sizeof(sentinel)));
''')

    def test_confirmed_ram_prefix_release_preserves_ids_clocks_and_refusal_counters(self):
        self.c(r'''
journal.rejected_full=UINT64_MAX;
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
assert(vg_offline_release_confirmed_prefix(&journal,NULL,&target_record));
assert(journal.count==0 && journal.next_id==2 && journal.last_event_ms==10 && journal.has_last_time && journal.rejected_full==UINT64_MAX);
vg_event_journal_t advanced=journal,rewound=journal;
rewound.next_id=1;assert(!vg_offline_journal_follows(&advanced,&rewound));
rewound=advanced;rewound.has_last_time=false;assert(!vg_offline_journal_follows(&advanced,&rewound));
uint64_t id;assert(!vg_journal_append(&journal,0,2,VG_SOURCE_SIMULATION,VG_EVENT_FAULT,9,&id));
assert(vg_journal_append(&journal,0,2,VG_SOURCE_SIMULATION,VG_EVENT_FAULT,10,&id));assert(id==2);
''')

    def test_prefix_release_refuses_wrong_fact_metadata_and_alias_without_mutation(self):
        self.c(r'''
vg_event_journal_t saved=journal;target_record.event.source_id=2;
assert(!vg_offline_release_confirmed_prefix(&journal,NULL,&target_record));assert(!memcmp(&journal,&saved,sizeof(saved)));
target_record.event.source_id=1;target_record.has_alarm=true;
assert(!vg_offline_release_confirmed_prefix(&journal,NULL,&target_record));assert(!memcmp(&journal,&saved,sizeof(saved)));
target_record.has_alarm=false;
assert(!vg_offline_release_confirmed_prefix(NULL,NULL,&target_record));
''')

    def test_older_recovered_confirmed_fact_can_be_reconfirmed_after_ram_prefix_release(self):
        self.c(r'''
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
assert(vg_offline_release_confirmed_prefix(&journal,NULL,&target_record));assert(journal.count==0 && journal.next_id==2);
/* Deterministic older-valid-slot recovery, not a claim about physical rollback. */
d=baseline;assert(vg_offline_recover(&tx,io,"disk:demo"));assert(tx.current.event_count==1 && tx.current.confirmed_event_id==0);
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
assert(tx.current.event_count==0 && tx.current.confirmed_event_id==1 && journal.next_id==2);
''')

    def test_admission_normalization_strips_only_confirmed_prefix_and_keeps_clock_ids(self):
        self.c(r'''
assert(vg_offline_retire(&tx,"boot-a",&target_record,&journal,NULL,&verifier,201,signed_receipt,sizeof(signed_receipt),working,sizeof(working))==VG_RETIRE_COMMITTED);
vg_event_journal_t normalized=journal,saved=journal;vg_offline_event scratch_record;
assert(vg_offline_strip_confirmed_prefix(&normalized,NULL,"boot-a",1,&scratch_record));
assert(normalized.count==0 && normalized.next_id==2 && normalized.has_last_time && normalized.last_event_ms==10);
assert(!memcmp(&journal,&saved,sizeof(saved)));
assert(!vg_offline_strip_confirmed_prefix(&journal,NULL,"boot-a",UINT64_MAX,&scratch_record));
assert(!memcmp(&journal,&saved,sizeof(saved)));
normalized=journal;normalized.next_id=1;assert(!vg_offline_journal_follows(&normalized,&normalized));
normalized=journal;normalized.last_event_ms=9;assert(!vg_offline_journal_follows(&normalized,&normalized));
''')

    def test_queue_admission_waits_for_current_prefix_and_never_authenticates_itself(self):
        self.c(r'''
assert(vg_offline_receipt_queue_admissible(&journal,NULL,"boot-a",0,&target_record));
unsigned writes=d.writes;target_record.event.event_id=2;
assert(!vg_offline_receipt_queue_admissible(&journal,NULL,"boot-a",0,&target_record));
target_record.event.event_id=1;vg_event_journal_t empty;assert(vg_journal_init(&empty));
assert(!vg_offline_receipt_queue_admissible(&empty,NULL,"boot-a",0,&target_record));
assert(vg_offline_receipt_queue_admissible(&empty,NULL,"boot-a",1,&target_record));
strcpy(target_record.boot,"older-boot");assert(vg_offline_receipt_queue_admissible(&empty,NULL,"boot-a",0,&target_record));
assert(d.writes==writes && tx.current.confirmed_event_id==0 && tx.current.event_count==1);
''')

    def test_fresh_start_cannot_reuse_stored_boot_but_running_owner_can_recover(self):
        self.c(r'''
assert(!vg_offline_recovery_owner_valid(&tx.current,"boot-a",false));
assert(vg_offline_recovery_owner_valid(&tx.current,"fresh-boot",false));
assert(vg_offline_recovery_owner_valid(&tx.current,"boot-a",true));
vg_offline_state empty;assert(vg_offline_init(&empty,"disk:demo"));
assert(vg_offline_recovery_owner_valid(&empty,"boot-a",false));
assert(vg_journal_init(&journal));
assert(vg_offline_merge(&tx.current,"boot-b",1,"new",3,&journal,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));
assert(!vg_offline_recovery_owner_valid(&tx.current,"boot-a",false)); /* Retained older namespace. */
assert(vg_offline_recovery_owner_valid(&tx.current,"boot-c",false));
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
