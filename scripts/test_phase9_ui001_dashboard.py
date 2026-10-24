#!/usr/bin/env python3
"""UI-001 narrow source contract check. Does not assert live UI rendering."""
import os,re,subprocess,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class DashboardEntrySourceTests(unittest.TestCase):
    def test_web_route_protected(self):
        s=(R/'backend/laravel/routes/web.php').read_text()
        self.assertIn("Route::middleware('auth')->get('/monitoring'",s)
        self.assertIn("view('monitoring.index')",s)
    def test_label_names_and_unknown(self):
        s=(R/'backend/laravel/app/Support/DashboardSignalLabel.php').read_text()
        for v in ('LIVE','STALE','OFFLINE','SIMULATION','UNKNOWN'):
            self.assertIn(v,s)
        if os.environ.get('NET001_UI_SKIP_PHP') != '1':
            p=R/'backend/laravel/app/Support/DashboardSignalLabel.php'
            code=("require "+repr(str(p).replace('\\','/'))+"; "
                  "$r=\\App\\Support\\DashboardSignalLabel::labels('stale','simulation'); "
                  "if ($r['freshness']!=='STALE' || $r['source_mode']!=='SIMULATION') exit(3); "
                  "$u=\\App\\Support\\DashboardSignalLabel::labels('bogus','bogus'); "
                  "if ($u['freshness']!=='UNKNOWN' || $u['source_mode']!=='UNKNOWN') exit(4);")
            subprocess.run([os.environ.get('VG_PHP_CLI','php'),'-r',code],check=True,capture_output=True,text=True)
    def test_view_is_explicitly_unconnected(self):
        s=(R/'backend/laravel/resources/views/monitoring/index.blade.php').read_text()
        self.assertIn('belum tersambung',s.lower())
        self.assertNotIn('DB::',s)
    def test_no_guest_monitoring_route(self):
        s=(R/'backend/laravel/routes/web.php').read_text()
        self.assertNotIn("Route::get('/monitoring'",s)
if __name__=='__main__':unittest.main()
