"""Bounded private-test native receipt verifier; never persist/output credentials."""
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def owned_root(folder):
    return (folder.resolve() == folder and not folder.is_symlink() and folder.is_dir()
            and folder.parent == Path(tempfile.gettempdir()).resolve()
            and folder.name.startswith('vg-live-http-'))


def build_verifier(folder, env):
    if not owned_root(folder):
        raise RuntimeError('RECEIPT_NATIVE_UNOWNED_ROOT')
    binary = folder/('receipt-verify.exe' if os.name == 'nt' else 'receipt-verify')
    if binary.exists() or binary.is_symlink():
        raise RuntimeError('RECEIPT_NATIVE_FRESH_PATH_REQUIRED')
    command = [env.get('VG_HOST_CC', 'gcc'), '-std=c99', '-Wall', '-Wextra', '-Werror', '-pedantic', '-Os',
               '-I', str(ROOT/'firmware/src'), '-I', str(ROOT/'scripts'),
               str(ROOT/'scripts/event_receipt_verify_fixture.c'), '-o', str(binary)]
    if os.name != 'nt':
        command.append('-lm')
    result = subprocess.run(command, env=env, cwd=ROOT, capture_output=True, timeout=60)
    if result.returncode or not binary.is_file() or binary.is_symlink():
        raise RuntimeError('RECEIPT_NATIVE_COMPILE_FAILED')
    return binary


def verify_receipt(binary, env, body, status, receipt):
    expected_name = 'receipt-verify.exe' if os.name == 'nt' else 'receipt-verify'
    if not owned_root(binary.parent) or binary.name != expected_name or not binary.is_file() or binary.is_symlink():
        raise ValueError('RECEIPT_NATIVE_OWNED_BINARY_REQUIRED')
    if not 0 < len(body) <= 4096 or len(receipt) > 512 or status not in (200, 201):
        raise ValueError('RECEIPT_NATIVE_BOUNDED_INPUT_REQUIRED')
    wire = struct.pack('<II', len(body), len(receipt))+body+receipt
    result = subprocess.run([str(binary), str(status)], env=env, input=wire,
                            capture_output=True, cwd=ROOT, timeout=15)
    if result.returncode == 0 and result.stdout.strip() == b'VERIFIED' and not result.stderr:
        return True
    if result.returncode == 3 and result.stdout.strip() == b'REFUSED' and not result.stderr:
        return False
    raise RuntimeError('RECEIPT_NATIVE_UNEXPECTED_RESULT_NO_SECRET_OUTPUT')


def build_retirement_fixture(folder, env):
    if not owned_root(folder):
        raise RuntimeError('RETIREMENT_NATIVE_UNOWNED_ROOT')
    binary = folder/('receipt-retire.exe' if os.name == 'nt' else 'receipt-retire')
    if binary.exists() or binary.is_symlink():
        raise RuntimeError('RETIREMENT_NATIVE_FRESH_PATH_REQUIRED')
    command = [env.get('VG_HOST_CC', 'gcc'), '-std=c99', '-D_POSIX_C_SOURCE=200809L',
               '-Wall', '-Wextra', '-Werror', '-pedantic', '-Os',
               '-I', str(ROOT/'firmware/src'), '-I', str(ROOT/'scripts'),
               str(ROOT/'scripts/event_retirement_file_fixture.c'), '-o', str(binary)]
    if os.name != 'nt':
        command.append('-lm')
    result = subprocess.run(command, env=env, cwd=ROOT, capture_output=True, timeout=60)
    if result.returncode or not binary.is_file() or binary.is_symlink():
        raise RuntimeError('RETIREMENT_NATIVE_COMPILE_FAILED')
    return binary


def run_retirement(binary, env, phase, identity, body=b'', status=201, receipt=b''):
    expected = 'receipt-retire.exe' if os.name == 'nt' else 'receipt-retire'
    if not owned_root(binary.parent) or binary.name != expected or not binary.is_file() or binary.is_symlink():
        raise ValueError('RETIREMENT_NATIVE_OWNED_BINARY_REQUIRED')
    if phase not in ('prepare', 'old', 'current', 'tamper', 'inspect') or not re.fullmatch('[a-f0-9]{32}', identity):
        raise ValueError('RETIREMENT_NATIVE_PHASE_ID_REQUIRED')
    if status not in (200, 201) or len(body) > 4096 or len(receipt) > 512:
        raise ValueError('RETIREMENT_NATIVE_BOUNDED_INPUT_REQUIRED')
    for slot in range(2):
        path = binary.parent/('receipt-slot'+str(slot)+'.bin')
        if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_size > 5184 or phase == 'prepare')):
            raise ValueError('RETIREMENT_NATIVE_PRIVATE_SLOT_REQUIRED')
    if phase in ('old', 'current', 'tamper') and (not body or len(receipt) != 134):
        raise ValueError('RETIREMENT_NATIVE_EXACT_RECEIPT_REQUIRED')
    wire = struct.pack('<II', len(body), len(receipt))+body+receipt
    result = subprocess.run([str(binary), phase, str(binary.parent), 'receipt-'+identity,
                             'receipt-next-'+identity, str(status)], env=env, input=wire,
                            capture_output=True, cwd=ROOT, timeout=30)
    if result.returncode or result.stderr or not 0 < len(result.stdout) <= 1024:
        raise RuntimeError('RETIREMENT_NATIVE_UNEXPECTED_RESULT_NO_SECRET_OUTPUT')
    output = result.stdout.strip()
    if phase in ('inspect', 'tamper') and output != (b'CHECKED' if phase == 'inspect' else b'REFUSED'):
        raise RuntimeError('RETIREMENT_NATIVE_EXACT_MARKER_REQUIRED')
    return output
