"""Deterministic fault injection for the actual transaction engine, not hardware."""
import unittest
from pathlib import Path
from phase9_b4_testlib import compile_c

ROOT = Path(__file__).resolve().parents[1]
COMMON = r'''
#include "offline_transaction.h"
typedef struct {
 uint8_t bytes[2][VG_OFFLINE_SNAPSHOT_MAX];size_t length[2];
 vg_offline_read_result status[2];
 size_t cut;bool fail_write,fail_commit,tamper_read;unsigned writes,last_target;
} disk;
static disk d, baseline;
static vg_offline_transaction tx;
static vg_event_journal_t journal;
static vg_offline_state sentinel;
static vg_offline_read_result read_slot(void *ctx,unsigned slot,uint8_t *out,size_t cap,size_t *n) {
 disk *x=ctx;if(x->status[slot]!=VG_OFFLINE_READ_READY)return x->status[slot];
 assert(x->length[slot]<=cap);memcpy(out,x->bytes[slot],x->length[slot]);*n=x->length[slot];
 if(x->tamper_read) {out[0]^=1u;}
 return VG_OFFLINE_READ_READY;
}
static bool write_slot(void *ctx,unsigned slot,const uint8_t *raw,size_t n) {
 disk *x=ctx;size_t used=n<x->cut?n:x->cut;memcpy(x->bytes[slot],raw,used);
 x->length[slot]=used;x->status[slot]=VG_OFFLINE_READ_READY;x->writes++;x->last_target=slot;
 return !x->fail_write;
}
static bool commit_slot(void *ctx) {return !((disk*)ctx)->fail_commit;}
static vg_offline_io io={&d,read_slot,write_slot,commit_slot};
static void setup(void) {
 memset(&d,0,sizeof(d));d.cut=SIZE_MAX;memset(&tx,0,sizeof(tx));
 assert(vg_journal_init(&journal));uint64_t id;
 assert(vg_journal_append(&journal,1u,1u,VG_SOURCE_SIMULATION,VG_EVENT_ALARM_RAISED,10u,&id));
 assert(vg_offline_recover(&tx,io,"disk:demo"));
 assert(vg_offline_merge(&tx.current,"boot-a",1u,"first",5u,&journal,&tx.candidate)==VG_OFFLINE_READY);
 assert(vg_offline_publish(&tx));baseline=d;sentinel=tx.current;
}
int main(void) { setup();(void)baseline;(void)sentinel;
'''


class OfflineTransactionTest(unittest.TestCase):
    def c(self, source):
        compile_c(COMMON+source+'\nreturn 0;}\n', extra_flags=('-Os',))

    def test_blank_bootstrap_alternates_slots_and_recovers_latest_generation(self):
        self.c(r'''
assert(tx.selected==0&&tx.current.generation==1u&&tx.degraded);
assert(vg_offline_merge(&tx.current,"boot-a",2u,"second",6u,&journal,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));assert(d.last_target==1u&&!tx.degraded);
assert(vg_offline_recover(&tx,io,"disk:demo"));assert(tx.selected==1&&tx.current.generation==2u);
assert(tx.current.latest_length==6u&&!memcmp(tx.current.latest,"second",6u));
''')

    def test_every_partial_write_preserves_selected_slot_and_published_memory(self):
        self.c(r'''
uint8_t full[VG_OFFLINE_WIRE_MAX];memset(full,0x37,sizeof(full));
assert(vg_offline_merge(&tx.current,"boot-a",2u,full,sizeof(full),&journal,&tx.candidate)==VG_OFFLINE_READY);
size_t n=0u;assert(vg_offline_pack(&tx.candidate,tx.raw[1],sizeof(tx.raw[1]),&n));
for(size_t cut=0u;cut<n;cut++) {
 d=baseline;assert(vg_offline_recover(&tx,io,"disk:demo"));
 assert(vg_offline_merge(&tx.current,"boot-a",2u,full,sizeof(full),&journal,&tx.candidate)==VG_OFFLINE_READY);
 d.cut=cut;d.fail_write=true;assert(!vg_offline_publish(&tx));assert(tx.halted);
 assert(d.last_target==1u&&!memcmp(&tx.current,&sentinel,sizeof(sentinel)));
 unsigned writes=d.writes;assert(!vg_offline_publish(&tx));assert(d.writes==writes);
 assert(!memcmp(d.bytes[0],baseline.bytes[0],baseline.length[0]));
 d.fail_write=false;d.cut=SIZE_MAX;assert(vg_offline_recover(&tx,io,"disk:demo"));
 assert(tx.current.generation==1u&&tx.degraded);
}
''')

    def test_commit_failure_can_be_uncertain_and_requires_explicit_recovery(self):
        self.c(r'''
assert(vg_offline_merge(&tx.current,"boot-a",2u,"second",6u,&journal,&tx.candidate)==VG_OFFLINE_READY);
d.fail_commit=true;assert(!vg_offline_publish(&tx));
assert(tx.halted&&tx.current.generation==1u);
d.fail_commit=false;assert(vg_offline_recover(&tx,io,"disk:demo"));
assert(tx.current.generation==2u); /* fake backend already wrote; no false rollback claim */
''')

    def test_readback_corruption_and_io_errors_do_not_publish_or_initialize_empty(self):
        self.c(r'''
assert(vg_offline_merge(&tx.current,"boot-a",2u,"second",6u,&journal,&tx.candidate)==VG_OFFLINE_READY);
d.tamper_read=true;assert(!vg_offline_publish(&tx));assert(tx.current.generation==1u&&tx.halted);
d=baseline;d.status[1]=VG_OFFLINE_READ_ERROR;
assert(!vg_offline_recover(&tx,io,"disk:demo"));assert(tx.current.generation==1u);
d=baseline;d.bytes[0][0]^=1u;
assert(!vg_offline_recover(&tx,io,"disk:demo"));assert(d.writes==baseline.writes);
d=baseline;assert(!vg_offline_recover(&tx,io,"other-device"));
assert(d.writes==baseline.writes);
''')

    def test_equal_generation_conflict_is_rejected_but_identical_slots_are_admitted(self):
        self.c(r'''
d.length[1]=d.length[0];d.status[1]=VG_OFFLINE_READ_READY;memcpy(d.bytes[1],d.bytes[0],d.length[0]);
assert(vg_offline_recover(&tx,io,"disk:demo"));assert(!tx.degraded);
tx.candidate=tx.current;tx.candidate.latest[0]='X';
assert(vg_offline_pack(&tx.candidate,d.bytes[1],sizeof(d.bytes[1]),&d.length[1]));
assert(!vg_offline_recover(&tx,io,"disk:demo"));assert(tx.halted&&!tx.ready);
assert(d.writes==baseline.writes);
''')

    def test_sdk_binding_has_no_erase_network_wait_or_unconditional_queue_eviction(self):
        src = (ROOT/'firmware/src/esp32_offline_store.c').read_text(encoding='utf-8')
        for text in ['nvs_set_blob', 'nvs_commit', 'nvs_get_blob', 'nvs_close',
                     'vg_offline_journal_follows', 'STORAGE_HALTED', 'retry_active',
                     'xSemaphoreTake(storage->lock, 0)', 'xQueueOverwrite', 'vg_offline_publish']:
            self.assertIn(text, src)
        for text in ['nvs_flash_erase(', 'esp_http_client', 'esp_wifi_connect', 'ESP_ERROR_CHECK(']:
            self.assertNotIn(text, src)

    def test_transaction_boundary_rejects_critical_deletion_even_if_merge_is_bypassed(self):
        self.c(r'''
assert(vg_offline_merge(&tx.current,"boot-a",2u,"second",6u,&journal,&tx.candidate)==VG_OFFLINE_READY);
tx.candidate.event_count=0u;unsigned writes=d.writes;
assert(!vg_offline_publish(&tx));assert(d.writes==writes);
assert(!memcmp(&tx.current,&sentinel,sizeof(sentinel)));
assert(vg_offline_merge(&tx.current,"boot-a",2u,"second",6u,&journal,&tx.candidate)==VG_OFFLINE_READY);
tx.candidate.events[0].event.linked_alarm_id=19u;
assert(!vg_offline_publish(&tx));assert(d.writes==writes);
assert(vg_offline_merge(&tx.current,"boot-a",2u,"second",6u,&journal,&tx.candidate)==VG_OFFLINE_READY);
tx.candidate.latest_sequence=tx.current.latest_sequence;
assert(!vg_offline_publish(&tx));assert(d.writes==writes);
tx.current.rejected_critical_attempts=9u;
assert(vg_offline_merge(&tx.current,"boot-a",2u,"second",6u,&journal,&tx.candidate)==VG_OFFLINE_READY);
tx.candidate.rejected_critical_attempts=8u;
assert(!vg_offline_publish(&tx));assert(d.writes==writes);
assert(tx.current.rejected_critical_attempts==9u);
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
