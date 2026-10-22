"""Deterministic host fixture: C99/PHP CLI only, no network/DB."""
import json,os,subprocess
from phase9_b5_testlib import ROOT,valid_raw,run_c
CLAIMS={'tls_verified':True,'external_secret':True,'device_authenticated':True,'device_id':'demo'}
PHP=(
"require 'backend/laravel/app/Support/Phase9B4IngestContract.php';"
"require 'backend/laravel/app/Support/Phase9B5StrictPayload.php';"
"require 'backend/laravel/app/Support/Phase9B5AuthClaims.php';"
"require 'backend/laravel/app/Support/Phase9B5DedupLedger.php';"
"require 'backend/laravel/app/Support/Phase9B6ChannelAudit.php';"
"require 'backend/laravel/app/Support/Phase9B6HostDecision.php';"
)
def php(raw,expression):
 p=subprocess.run([os.environ.get('VG_PHP_CLI','php'),'-r',PHP+expression],input=raw,text=True,capture_output=True,cwd=ROOT,timeout=35)
 if p.returncode:raise AssertionError('PHP_FAILED '+p.stdout+' '+p.stderr)
 return p.stdout.strip()
def ingest(rows,capacity=8):
 code=("$l=new App\\Support\\Phase9B5DedupLedger("+str(capacity)+");"
       "$items=json_decode(stream_get_contents(STDIN),true);"
       "foreach($items as $item){$r=App\\Support\\Phase9B6HostDecision::ingest($item['claims'],$item['raw'],$l);"
       "echo json_encode($r,JSON_THROW_ON_ERROR).PHP_EOL;}")
 out=php(json.dumps(rows),code)
 return [json.loads(line) for line in out.splitlines()]
def item(raw=None,claims=None):return {'raw':valid_raw() if raw is None else raw,'claims':CLAIMS if claims is None else claims}
