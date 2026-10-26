"""Owned browser component bridge; no personal profile or certificate bypass."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT/'scripts/browser_monitoring_probe.js'


def owned_root(folder):
    return (folder.resolve() == folder and folder.is_dir() and not folder.is_symlink()
            and folder.parent == Path(tempfile.gettempdir()).resolve()
            and folder.name.startswith('vg-live-http-'))


def environment(env, browser):
    if any(env.get(name) for name in ('NODE_OPTIONS', 'NODE_TLS_REJECT_UNAUTHORIZED')):
        raise RuntimeError('BROWSER_UNREVIEWED_NODE_OVERRIDE')
    allowed = {'PATH', 'PATHEXT', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'TEMP', 'TMP',
               'USERPROFILE', 'LOCALAPPDATA', 'APPDATA'}
    result = {key:value for key,value in env.items() if key.upper() in allowed}
    result['VG_BROWSER_BINARY'] = str(browser)
    return result


def preflight(node, browser, env):
    result = subprocess.run([node, str(DRIVER), '--check'], cwd=ROOT,
                            env=environment(env, browser), capture_output=True, timeout=15)
    if result.returncode or result.stderr or result.stdout.strip() != b'BROWSER_PREREQUISITE=PASS_NO_LAUNCH':
        raise RuntimeError('BROWSER_PREREQUISITE_UNAVAILABLE')


def execute(node, browser, env, folder, profile, wire, base):
    if not owned_root(folder) or not base.startswith('https://127.0.0.1:'):
        raise RuntimeError('BROWSER_UNOWNED_ROOT_OR_UPSTREAM')
    seed = folder/'browser-native-seed.jsonl'
    if seed.exists() or seed.is_symlink():
        raise RuntimeError('BROWSER_FRESH_SEED_PATH_REQUIRED')
    seed.write_bytes(wire)
    child = environment(env, browser)
    child.update(VG_BROWSER_ROOT=str(folder), VG_BROWSER_UPSTREAM=base,
                 VG_BROWSER_AGENT=profile['agent'], VG_BROWSER_COOKIE=profile['cookie'],
                 VG_BROWSER_EMAIL=profile['email'], VG_BROWSER_LOGIN=env['VG_LIVE_LOGIN_SECRET'],
                 VG_BROWSER_DEVICE_TOKEN=env['VG_LIVE_DEVICE_TOKEN'])
    result = subprocess.run([node, str(DRIVER), '--execute'], cwd=ROOT, env=child,
                            capture_output=True, timeout=80)
    # No stderr/exception/HTML/credentials are copied into public evidence.
    if result.stderr or len(result.stdout) > 32768:
        raise RuntimeError('BROWSER_UNEXPECTED_DIAGNOSTIC')
    lines = result.stdout.decode('utf-8', errors='strict').splitlines()
    records = [line for line in lines if line.startswith('BROWSER_MONITORING_RECORD=')]
    if len(records) != 1 or len(lines) != 2:
        raise RuntimeError('BROWSER_STRUCTURED_RECORD_REQUIRED')
    record = json.loads(records[0].split('=', 1)[1])
    expected = {'browser', 'upstream_tls_verified', 'cookie_attributes', 'initial', 'middle',
                'expired', 'refreshed', 'no_data_polling', 'failure', 'profile_closed', 'observations', 'fallbacks'}
    if not isinstance(record, dict) or set(record) != expected:
        raise RuntimeError('BROWSER_UNEXPECTED_RECORD_SCHEMA')
    for line in lines:
        print(line, flush=True)
    if result.returncode not in (0, 1, 3):
        raise RuntimeError('BROWSER_UNEXPECTED_EXIT')
    return result.returncode
