#!/usr/bin/env python3
"""Real production middleware under PHP CLI stand-ins; no DB, vendor or network."""
import json, os, pathlib, subprocess, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class B9HttpProbe(unittest.TestCase):
 def test_real_middleware_media_and_size_boundaries(self):
  cases=[
   dict(body='{}',type='text/plain',length=None),
   dict(body='{}',type='application/json',length=None),
   dict(body='{}',type='application/json; charset=utf-8',length='2'),
   dict(body='{}',type='application/vnd.gateway+json',length='2'),
   dict(body='x'*4097,type='text/plain',length='4097'),
   dict(body='x'*4097,type='application/json',length='1'),
   dict(body='{}',type='',length=None),
   dict(body='{}',type='application/json',length='4097'),
  ]
  cmd=[os.environ.get('VG_PHP_CLI','php'),str(ROOT/'scripts/phase9_b9_middleware_probe.php')]
  p=subprocess.run(cmd,input=json.dumps(cases),text=True,capture_output=True,cwd=ROOT,timeout=40)
  self.assertEqual(p.returncode,0,p.stderr)
  actual=[json.loads(s) for s in p.stdout.splitlines()]
  self.assertEqual([x['status'] for x in actual],[415,200,200,200,413,413,415,413])
  self.assertEqual(actual[0]['data'],{'error':'unsupported_telemetry_media_type'})
  self.assertEqual(actual[4]['data']['max_bytes'],4096)
if __name__=='__main__':unittest.main(verbosity=2)
