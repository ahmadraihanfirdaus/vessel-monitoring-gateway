"""B15 host source contract - never treats fixture as deployed ESP32 transport."""
import importlib.util, pathlib, tempfile, json
R=pathlib.Path(__file__).resolve().parents[1]
source=(R/'scripts/phase9_b15_event_wire_fixture.c').read_text()
php=(R/'backend/laravel/tests/Feature/Phase9B15JournalWireHttpTest.php').read_text()
bridge=(R/'scripts/phase9_b15_event_bridge.py').read_text()
assert '#include "core_event_journal.h"' in source
assert 'vg_journal_append' in source and 'vg_journal_read' in source
assert 'VG_SOURCE_PHYSICAL' in source
assert all(x in source for x in ['VG_EVENT_ALARM_RAISED','VG_EVENT_ALARM_ACK','VG_EVENT_ALARM_CLEARED','VG_EVENT_FAULT'])
assert 'VG_B15_EVENT_JSONL' in php and 'DeviceTokenAuthenticator' in php and 'EventIngestService' in php
assert 'Mockery::mock' in php and 'RefreshDatabase' not in php and 'DatabaseMigrations' not in php
assert "'-Werror'" in bridge and "'-pedantic'" in bridge and "crlfs in (0,count)" in bridge
spec=importlib.util.spec_from_file_location('bridge',R/'scripts/phase9_b15_event_bridge.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
raw=module.build_bytes();module.validate(raw)
with tempfile.TemporaryDirectory() as td:
    dst=pathlib.Path(td)/'events.jsonl'
    dst.write_bytes(raw)
    assert dst.read_bytes()==raw
    assert len([json.loads(l) for l in raw.splitlines()])==4
print('B15_CONTRACT=PASS_C99_REAL_JOURNAL_4_EVENTS_NO_DB')
