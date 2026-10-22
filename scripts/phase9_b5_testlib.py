"""Host fixture helpers. No network or DB access."""
import json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VALID={'schema_version':'1.0','device_id':'demo','firmware_version':'demo-5','boot_id':'synthetic','sequence':1,'uptime_ms':0,'source_mode':'simulation','channels':{'rpm':{'value':0,'quality':'valid'},'temp':{'value':None,'quality':'missing'}}}
def valid_raw(**changes):
 v=json.loads(json.dumps(VALID));v.update(changes);return json.dumps(v,separators=(',',':'))
def php_eval(raw,body):
 includes=['Phase9B4IngestContract','Phase9B5StrictPayload','Phase9B5DedupLedger','Phase9B5AuthClaims']
 code=''.join("require 'backend/laravel/app/Support/"+n+".php';" for n in includes)+body
 p=subprocess.run([os.environ.get('VG_PHP_CLI','php'),'-r',code],input=raw,text=True,capture_output=True,cwd=ROOT,timeout=40)
 if p.returncode:raise AssertionError('PHP_CLI_ERROR '+p.stdout+p.stderr)
 return p.stdout.strip()
def run_c(source):
 with tempfile.TemporaryDirectory(prefix='vg-b5-') as td:
  root=Path(td);name=root/'test.c';exe=root/('test.exe' if os.name=='nt' else 'test')
  name.write_text('#include <assert.h>\n'+source)
  p=subprocess.run([os.environ.get('VG_HOST_CC','gcc'),'-std=c99','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'firmware/src'),str(name),'-o',str(exe)],capture_output=True,text=True,timeout=40)
  if p.returncode:raise AssertionError(p.stdout+p.stderr)
  p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
  if p.returncode:raise AssertionError(p.stdout+p.stderr)
  return p.stdout
