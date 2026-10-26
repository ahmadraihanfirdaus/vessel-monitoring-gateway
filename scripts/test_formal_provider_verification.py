"""Actual dedicated execution plus adversarial oracle and monotonic-time faults."""
from contextlib import redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import run_formal_provider_verification as gate
from phase9_b4_testlib import compile_c


class FormalProviderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run([sys.executable,'-B',str(Path(gate.__file__)),'--execute'],
                                cwd=gate.ROOT,capture_output=True,text=True,timeout=90)
        if result.returncode:
            raise AssertionError('ACTUAL_DEDICATED_EXECUTION_FAILED_NO_RAW_DIAGNOSTICS')
        cls.output = result.stdout
        rows = [gate.strict_json(line.removeprefix('NATIVE_OBSERVATION='))
                for line in result.stdout.splitlines() if line.startswith('NATIVE_OBSERVATION=')]
        if len(rows) != 6 or {r['case'] for r in rows} != set(gate.CASES):
            raise AssertionError('EXACT_SIX_UNIQUE_DEDICATED_CASES_REQUIRED')
        cls.observations = {r['case']:r for r in rows}

    def test_real_six_case_execution_source_stability_and_no_registry_write(self):
        self.assertEqual(self.output.count('=PASS_HOST_ONLY'), 6)
        self.assertIn('FORMAL_PROVIDER_SOURCE_STABILITY=PASS_SHA256_', self.output)
        self.assertIn('PASS_SIX_HOST_CASES_NO_HARDWARE_OR_REGISTRY_MUTATION', self.output)
        for case, value in self.observations.items():
            errors, comparisons = gate.observe(case,value)
            self.assertFalse(errors)
            self.assertGreaterEqual(len(comparisons), 13)

    def test_read_only_default_never_launches_compiler_or_subprocess(self):
        output = io.StringIO()
        with patch.object(sys,'argv',['gate']), patch.object(gate.subprocess,'run') as process, redirect_stdout(output):
            self.assertEqual(gate.main(),0)
        process.assert_not_called()
        self.assertIn('NOT_RUN_READ_ONLY',output.getvalue())

    def test_missing_protocol_review_blocks_before_execution(self):
        output = io.StringIO()
        with patch.object(sys,'argv',['gate','--execute']), patch.object(gate,'PROTOCOL') as protocol, \
             patch.object(gate.subprocess,'run') as process, redirect_stdout(output):
            protocol.read_text.return_value = 'unreviewed synthetic protocol'
            self.assertEqual(gate.main(),3)
        process.assert_not_called()
        self.assertIn('BLOCKED_PROTOCOL_REVIEW_REQUIRED',output.getvalue())

    def test_unavailable_prerequisite_never_becomes_pass(self):
        output = io.StringIO()
        with patch.object(sys,'argv',['gate','--execute']), \
             patch.object(gate.subprocess,'run',side_effect=OSError('synthetic unavailable')), redirect_stdout(output):
            self.assertEqual(gate.main(),3)
        self.assertIn('BLOCKED_OSError_NO_UNREDACTED_DIAGNOSTICS',output.getvalue())
        self.assertNotIn('=PASS_HOST_ONLY',output.getvalue())

    def test_missing_or_undecodable_protocol_blocks_without_path_or_subprocess_output(self):
        for error in [OSError('synthetic unavailable'), UnicodeError('synthetic encoding')]:
            output = io.StringIO()
            with patch.object(sys,'argv',['gate','--execute']), patch.object(gate,'PROTOCOL') as protocol, \
                 patch.object(gate.subprocess,'run') as process, redirect_stdout(output):
                protocol.read_text.side_effect = error
                self.assertEqual(gate.main(),3)
            protocol.read_text.assert_called_once_with(encoding='utf-8')
            process.assert_not_called()
            self.assertIn('BLOCKED_PROTOCOL_UNAVAILABLE',output.getvalue())

    def test_source_drift_cannot_be_certified_by_six_passing_observations(self):
        output = io.StringIO()
        with patch.object(sys,'argv',['gate','--execute']), \
             patch.object(gate,'snapshot',side_effect=[{'input':'before'},{'input':'after'}]), redirect_stdout(output):
            self.assertEqual(gate.main(),1)
        self.assertIn('FAIL_SOURCE_DRIFT',output.getvalue())
        self.assertNotIn('PASS_SIX_HOST_CASES_NO_HARDWARE_OR_REGISTRY_MUTATION',output.getvalue())

    def test_oracle_rejects_ack_condition_clear_zero_null_and_faked_native_count(self):
        for field, bad in [('active_after_ack',False),('ack_time',None),('ack_time',False),
                           ('raised_fact_state',2),('checks',True),('checks',0)]:
            value = copy.deepcopy(self.observations['SUP-004']);value[field] = bad
            self.assertTrue(gate.observe('SUP-004',value)[0],field)

    def test_oracle_rejects_missing_engine_fields_identity_source_and_float_errors(self):
        for field,bad in [('id',2),('source','physical'),('rpm',1999),('temperature',float('nan')),
                          ('runtime',None),('alarm',True),('communication',3)]:
            value = copy.deepcopy(self.observations['SUP-005']);value['engines'][0][field] = bad
            self.assertTrue(gate.observe('SUP-005',value)[0],field)
        value = copy.deepcopy(self.observations['SUP-005']);value['engines'].pop()
        with self.assertRaises(ValueError):gate.observe('SUP-005',value)

    def test_oracle_rejects_navigation_refresh_rewind_no_fix_and_missing_properties(self):
        for field,bad in [('age_rewound',True),('ingest_behind_observed',True),('latitude',None),
                          ('nofix_position_present',True),('quality','valid-zero'),('offline_age',0),('fix',1)]:
            value=copy.deepcopy(self.observations['SUP-007']);value[field]=bad
            self.assertTrue(gate.observe('SUP-007',value)[0],field)

    def test_provider_oracle_rejects_missing_as_zero_stale_current_and_certification_label(self):
        for case in ('SUP-008','SUP-009','SUP-010'):
            for field,bad,index in [('present',True,4),('current',True,3),('source','physical',0),('sequence',0,0)]:
                value=copy.deepcopy(self.observations[case]);value['steps'][index][field]=bad
                self.assertTrue(gate.observe(case,value)[0],(case,field))
            value=copy.deepcopy(self.observations[case]);value['scope']='certified vessel equipment'
            self.assertTrue(gate.observe(case,value)[0])
            value=copy.deepcopy(self.observations[case]);value['steps'].pop()
            with self.assertRaises(ValueError):gate.observe(case,value)

    def test_duplicate_nonfinite_and_unknown_native_output_cannot_be_accepted(self):
        for raw in ['{"case":"SUP-004","case":"SUP-005"}','{"value":NaN}','{"value":Infinity}']:
            with self.assertRaises(ValueError):gate.strict_json(raw)
        with self.assertRaises(ValueError):gate.observe('SUP-999',{'case':'SUP-999','checks':20})

    def test_monotonic_navigation_rejects_every_older_observation_and_preserves_uint64_boundaries(self):
        sentence=json.dumps(gate.synthetic_rmc())
        compile_c(r'''
#include "navigation_nmea.h"
#include <assert.h>
int main(void){
const char *sentence=SENTENCE;
const uint64_t starts[]={0u,1u,UINT64_MAX-300u};
const vg_nav_age_thresholds_t thresholds={100u,300u};
for(size_t i=0u;i<3u;i++){
 vg_navigation_state_t state={0};uint64_t start=starts[i];
 assert(vg_nav_ingest_sentence(&state,sentence,start,VG_SOURCE_SIMULATION));
 assert(vg_nav_update_age(&state,start+300u,&thresholds));
 assert(state.age_state==VG_NAV_AGE_OFFLINE && state.data_age_ms==300u);
 vg_navigation_state_t saved=state;
 for(uint64_t offset=0u;offset<300u;offset++){
  assert(!vg_nav_update_age(&state,start+offset,&thresholds));assert(!memcmp(&state,&saved,sizeof(saved)));
  assert(!vg_nav_ingest_sentence(&state,sentence,start+offset,VG_SOURCE_SIMULATION));assert(!memcmp(&state,&saved,sizeof(saved)));
 }
 assert(vg_nav_update_age(&state,start+300u,&thresholds));
 assert(vg_nav_ingest_sentence(&state,sentence,start+300u,VG_SOURCE_SIMULATION));
 assert(state.last_valid_ms==start+300u && state.data_age_ms==0u && state.age_state==VG_NAV_AGE_VALID);
}
return 0;}
'''.replace('SENTENCE',sentence))


if __name__ == '__main__':
    unittest.main(verbosity=2)
