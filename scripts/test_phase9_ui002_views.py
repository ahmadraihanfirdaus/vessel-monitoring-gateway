#!/usr/bin/env python3
"""UI-002 connected-view source guards; actual rendering is tested in Laravel."""
import unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
EXPECTED=('overview','safety','propulsion','navigation','power','alarms-events','device-health','test-evidence')
class DashboardViewsSourceTests(unittest.TestCase):
    def test_all_eight_views_exist(self):
        p=R/'backend/laravel/resources/views/monitoring/sections'
        self.assertEqual(set(p.glob('*.blade.php')),{p/(k+'.blade.php') for k in EXPECTED})
    def test_all_eight_includes(self):
        content=(R/'backend/laravel/resources/views/monitoring/index.blade.php').read_text(encoding='utf-8')
        for k in EXPECTED:self.assertIn("@include('monitoring.sections."+k+"')",content)
    def test_no_false_live_data_or_network_fetch(self):
        entry=(R/'backend/laravel/resources/views/monitoring/index.blade.php').read_text(encoding='utf-8')
        self.assertIn("@if($state === null)",entry)
        self.assertIn('DATA NOT CONNECTED',entry)
        self.assertIn("'freshness' => $sampleFreshness",entry)
        freshness=(R/'backend/laravel/resources/views/monitoring/freshness.blade.php').read_text(encoding='utf-8')
        self.assertIn("SNAPSHOT: {{ $freshness['label'] }}",freshness)
        self.assertIn('class="badge SNAPSHOT"',freshness)
        script=(R/'backend/laravel/public/assets/monitoring-freshness.js').read_text(encoding='utf-8')
        for forbidden in ('fetch(', 'XMLHttpRequest', 'WebSocket', 'sendBeacon', 'innerHTML', 'eval('):
            self.assertNotIn(forbidden,script)
        table=(R/'backend/laravel/resources/views/monitoring/channel-table.blade.php').read_text(encoding='utf-8')
        self.assertIn("@if($channels === [])",table)
        self.assertIn("$channel['value'] !== null",table)
        for k in EXPECTED:
            s=(R/'backend/laravel/resources/views/monitoring/sections'/f'{k}.blade.php').read_text(encoding='utf-8')
            for forbidden in ('fetch(', 'DB::','Device::all(','token=','Bearer '):self.assertNotIn(forbidden,s)
        bindings={'overview':"$state['channels'] ?? []",'safety':"$sectionChannels['safety']",
                  'propulsion':"$sectionChannels['propulsion']",'navigation':"$sectionChannels['navigation']",
                  'power':"$sectionChannels['power']",'alarms-events':'$events',
                  'device-health':'$health','test-evidence':"$evidence['available']"}
        for k,binding in bindings.items():
            self.assertIn(binding,(R/'backend/laravel/resources/views/monitoring/sections'/f'{k}.blade.php').read_text(encoding='utf-8'))
        runtime=(R/'backend/laravel/tests/Feature/MonitoringRenderingTest.php').read_text(encoding='utf-8')
        self.assertIn('test_no_sample_is_explicit_without_zero_or_safe_defaults',runtime)
        self.assertIn('test_all_eight_sections_render_actual_data_and_configured_assignments',runtime)
    def test_view_section_labels(self):
        labels=['Overview','Safety','Propulsion','Navigation','Power','Alarms and Events','Device Health','Test Evidence']
        for k,label in zip(EXPECTED,labels):
            self.assertIn('>'+label+'</h2>',(R/'backend/laravel/resources/views/monitoring/sections'/f'{k}.blade.php').read_text(encoding='utf-8'))
if __name__=='__main__':unittest.main()
