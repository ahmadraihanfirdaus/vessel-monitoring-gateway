#!/usr/bin/env python3
"""UI-002 view source/placeholder audit, not a rendering or API test."""
import unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
EXPECTED=('overview','safety','propulsion','navigation','power','alarms-events','device-health','test-evidence')
class DashboardViewsSourceTests(unittest.TestCase):
    def test_all_eight_views_exist(self):
        p=R/'backend/laravel/resources/views/monitoring/sections'
        self.assertEqual(set(p.glob('*.blade.php')),{p/(k+'.blade.php') for k in EXPECTED})
    def test_all_eight_includes(self):
        content=(R/'backend/laravel/resources/views/monitoring/index.blade.php').read_text()
        for k in EXPECTED:self.assertIn("@include('monitoring.sections."+k+"')",content)
    def test_no_false_live_data_or_network_fetch(self):
        for k in EXPECTED:
            s=(R/'backend/laravel/resources/views/monitoring/sections'/f'{k}.blade.php').read_text()
            self.assertIn('DATA NOT CONNECTED',s)
            for forbidden in ('fetch(', 'DB::','Device::all(','token=','Bearer '):self.assertNotIn(forbidden,s)
    def test_view_section_labels(self):
        labels=['Overview','Safety','Propulsion','Navigation','Power','Alarms / Events','Device Health','Test Evidence']
        for k,label in zip(EXPECTED,labels):
            self.assertIn('>'+label+'</h2>',(R/'backend/laravel/resources/views/monitoring/sections'/f'{k}.blade.php').read_text())
if __name__=='__main__':unittest.main()
