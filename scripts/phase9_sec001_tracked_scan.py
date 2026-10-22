#!/usr/bin/env python3
"""SEC-001 tracked source hygiene audit, no network or repository mutations."""
import subprocess,sys
from pathlib import Path
from phase9_sec001_source_patterns import classify
TEXT_EXT={'.c','.h','.cpp','.py','.php','.md','.txt','.yml','.yaml','.json','.xml','.ini','.env','.sh','.csv','.blade.php'}
def scan(repo):
 names=(subprocess.check_output(['git','ls-files','-z'],cwd=repo).split(b'\0') + subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=repo).split(b'\0'))
 findings=[];count=0
 for raw in names:
  if not raw:continue
  path=raw.decode('utf-8',errors='strict');p=Path(path)
  if path in ('firmware/.gitignore','firmware/.vscode/extensions.json'):continue
  if p.suffix.lower() not in TEXT_EXT and not path.endswith('.blade.php'):continue
  f=repo/p
  if f.is_symlink() or not f.is_file():continue
  data=f.read_bytes();count+=1
  if len(data)>2_000_000:continue
  for reason in classify(data):findings.append((path,reason))
 return count,findings
if __name__=='__main__':
 repo=Path.cwd().resolve()
 count,findings=scan(repo)
 for path,reason in findings:print('FINDING='+reason+' PATH='+path)
 print('SEC001_TRACKED_SCANNED='+str(count))
 print('SEC001_CREDENTIAL_PATTERN_FINDINGS='+str(len(findings)))
 sys.exit(0 if not findings else 2)
