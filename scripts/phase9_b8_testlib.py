"""Batch 8 deterministic C99 and PHP fixture; no DB or network."""
import os,json,subprocess
from phase9_b3_host_fixture import compile_and_run
from phase9_b5_testlib import ROOT, valid_raw
BASE=(
"require 'backend/laravel/app/Support/Phase9B4IngestContract.php';"
"require 'backend/laravel/app/Support/Phase9B5StrictPayload.php';"
"require 'backend/laravel/app/Support/Phase9B5AuthClaims.php';"
"require 'backend/laravel/app/Support/Phase9B5DedupLedger.php';"
"require 'backend/laravel/app/Support/Phase9B6ChannelAudit.php';"
"require 'backend/laravel/app/Support/Phase9B6HostDecision.php';"
"require 'backend/laravel/app/Support/Phase9B8ReplayWindow.php';"
"require 'backend/laravel/app/Support/Phase9B8AttestedDecision.php';")
CLAIMS={'tls_verified':True,'external_secret':True,'device_authenticated':True,'device_id':'demo',
        'scope':'telemetry:ingest','iat_ms':1000,'exp_ms':2000}
def decisions(items,capacity=16):
 body=(f"$l=new App\\Support\\Phase9B5DedupLedger({capacity});"
       f"$w=new App\\Support\\Phase9B8ReplayWindow({capacity});"
       "$items=json_decode(stream_get_contents(STDIN),true);"
       "foreach($items as $item){$r=App\\Support\\Phase9B8AttestedDecision::admit($item['claims'],$item['raw'],$item['now'],$l,$w);"
       "echo json_encode($r,JSON_THROW_ON_ERROR).PHP_EOL;}")
 p=subprocess.run([os.environ.get('VG_PHP_CLI','php'),'-r',BASE+body],
                  input=json.dumps(items),capture_output=True,text=True,cwd=ROOT,timeout=40)
 if p.returncode:raise AssertionError('PHP_EXEC_FAILED '+p.stdout+' '+p.stderr)
 return [json.loads(s) for s in p.stdout.splitlines()]
def item(seq=1,claims=None,now=1100,raw=None):
 return {'claims':CLAIMS.copy() if claims is None else claims,
         'now':now,'raw':valid_raw(sequence=seq) if raw is None else raw}
