"""Independent VGS2 envelope inspection and bounded owned host-file execution."""
import binascii
import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from data_ui_contracts import native_contract, strict_json

ROOT = Path(__file__).resolve().parents[1]


def inspect_slot(raw):
    if not isinstance(raw, bytes) or not 40 <= len(raw) <= 5184:
        raise ValueError('BOUNDED_SLOT_REQUIRED')
    if raw[:5] != b'VGS2\x02' or binascii.crc32(raw[:-4]) & 0xffffffff != struct.unpack('<I', raw[-4:])[0]:
        raise ValueError('SLOT_HEADER_OR_CRC')
    position = 5
    def take(count):
        nonlocal position
        if count < 0 or position + count > len(raw)-4:
            raise ValueError('TRUNCATED_SLOT')
        result = raw[position:position+count]; position += count
        return result
    def integer(format):
        return struct.unpack(format, take(struct.calcsize(format)))[0]
    def token():
        count = integer('<B')
        if not 1 <= count <= 48:
            raise ValueError('SLOT_IDENTITY_BOUND')
        value = take(count).decode('ascii')
        if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-' for c in value):
            raise ValueError('SLOT_IDENTITY')
        return value
    generation, sequence, rejected = integer('<Q'), integer('<Q'), integer('<Q')
    length, count = integer('<H'), integer('<B')
    if not 1 <= length <= 4096 or not 0 <= count <= 8:
        raise ValueError('SLOT_PAYLOAD_BOUND')
    device, boot = token(), token()
    latest = take(length)
    native_contract(latest+b'\n')
    packet = strict_json(latest)
    if packet['device_id'] != device or packet['boot_id'] != boot or packet['sequence'] != sequence:
        raise ValueError('SLOT_LATEST_IDENTITY')
    records = []
    for _ in range(count):
        event_boot = token()
        fields = take(30)  # event ID, alarm ID, source, mode, kind, occurred ms.
        event_id = struct.unpack('<Q', fields[:8])[0]
        source_id = struct.unpack('<I', fields[16:20])[0]
        if not 0 < event_id < 2**64-1 or source_id == 0 or fields[20] not in (1, 2) or not 1 <= fields[21] <= 5:
            raise ValueError('SLOT_EVENT_FIELDS')
        has_alarm = integer('<B')
        if has_alarm not in (0, 1):
            raise ValueError('SLOT_METADATA_FLAG')
        metadata = take(34) if has_alarm else b''
        if metadata and metadata[-1] > 3:
            raise ValueError('SLOT_METADATA_RESERVED_FLAGS')
        records.append((event_boot, event_id, hashlib.sha256(fields+metadata).hexdigest(), bool(has_alarm)))
    if position != len(raw)-4 or len({(r[0], r[1]) for r in records}) != count:
        raise ValueError('SLOT_TRAILING_OR_DUPLICATE_EVENTS')
    return dict(generation=generation, sequence=sequence, rejected=rejected, device=device,
                boot=boot, latest=packet, records=records, byte_count=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def owned_root(folder):
    return (folder.resolve() == folder and folder.is_dir() and not folder.is_symlink()
            and folder.parent == Path(tempfile.gettempdir()).resolve()
            and folder.name.startswith('vg-formal-offline-'))


def observe(facts, slots):
    expected = dict(generation=72, latest_sequence=8, retained=8, confirmed_floor=0,
                    original_first_id=1, original_last_id=8,
                    older_corruption_preserved_latest=True, healthy_reopen=True)
    if set(facts) != set(expected) | {'ram_rejected', 'disk_rejected'}:
        raise ValueError('EXACT_NATIVE_STATE_REQUIRED')
    for key, value in expected.items():
        if type(facts[key]) is not type(value) or facts[key] != value:
            raise ValueError('NATIVE_STATE_MISMATCH')
    if any(type(facts[k]) is not int or not 0 < facts[k] < 2**64 for k in ('ram_rejected', 'disk_rejected')):
        raise ValueError('SATURATION_NOT_OBSERVED')
    if len(slots) != 2 or sorted(s['generation'] for s in slots) != [71, 72]:
        raise ValueError('TWO_ORIGINAL_GENERATIONS_REQUIRED')
    for slot in slots:
        if (slot['device'] != 'runtime:demo' or slot['boot'] != 'bounded-boot-b'
                or slot['sequence'] != slot['generation']-64 or slot['rejected'] <= 0
                or len(slot['records']) != 8 or slot['byte_count'] > 5184
                or [(r[0], r[1], r[3]) for r in slot['records']] != [('bounded-boot-a', i, True) for i in range(1, 9)]):
            raise ValueError('RETAINED_PREFIX_OR_LATEST_MISMATCH')
        packet = slot['latest']
        if packet['schema_version'] != '1.1' or len(packet['channels']) != 48 or packet['uptime_ms'] != slot['sequence']*200:
            raise ValueError('ACTUAL_LATEST_NOT_AVAILABLE')
    if slots[0]['records'] != slots[1]['records']:
        raise ValueError('ORIGINAL_CRITICAL_METADATA_CHANGED')
    newest = max(slots, key=lambda s:s['generation'])
    if newest['rejected'] != facts['disk_rejected']:
        raise ValueError('COUNTER_NOT_PERSISTED')
    return dict(generation=72, latest_sequence=8, retained=8, current_confirmed_floor=0,
                original_boot='bounded-boot-a', latest_boot='bounded-boot-b',
                ram_rejected=facts['ram_rejected'], disk_rejected=facts['disk_rejected'],
                slot_bytes=[s['byte_count'] for s in slots], slot_sha256=[s['sha256'] for s in slots],
                original_metadata_unchanged=True, older_corruption_preserved_latest=True,
                database_access=False, physical_durability=False)


def execute():
    folder = Path(tempfile.mkdtemp(prefix='vg-formal-offline-')).resolve()
    if not owned_root(folder):
        raise RuntimeError('UNOWNED_TEMP_ROOT')
    try:
        binary = folder/('offline-bounded.exe' if os.name == 'nt' else 'offline-bounded')
        command = [os.environ.get('VG_HOST_CC', 'gcc'), '-std=c99', '-D_POSIX_C_SOURCE=200809L',
                   '-Wall', '-Wextra', '-Werror', '-pedantic', '-Os', '-I'+str(ROOT/'firmware/src'),
                   '-I'+str(ROOT/'scripts'), str(ROOT/'scripts/offline_bounded_file_fixture.c'), '-o', str(binary)]
        if os.name != 'nt':
            command.append('-lm')
        compiled = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60)
        if compiled.returncode or not binary.is_file() or binary.is_symlink():
            raise RuntimeError('NATIVE_FILE_COMPILE_FAILED')
        native = subprocess.run([str(binary), str(folder)], cwd=ROOT, capture_output=True, timeout=60)
        if native.returncode or native.stderr or len(native.stdout) > 8192:
            raise ValueError('NATIVE_FILE_EXECUTION_FAILED')
        lines = native.stdout.splitlines()
        if len(lines) != 2:
            raise ValueError('EXACT_NATIVE_FILE_OUTPUT_REQUIRED')
        paths = [folder/('offline-slot'+str(i)+'.bin') for i in (0, 1)]
        if any(not p.is_file() or p.is_symlink() for p in paths) or set(folder.iterdir()) != {binary, *paths}:
            raise ValueError('EXACT_OWNED_TWO_SLOT_OUTPUT_REQUIRED')
        slots = [inspect_slot(p.read_bytes()) for p in paths]
        # Native emitted latest wire is independently equal to the selected file.
        newest = max(slots, key=lambda s:s['generation'])
        if strict_json(lines[1]) != newest['latest']:
            raise ValueError('REOPEN_LATEST_OUTPUT_MISMATCH')
        return observe(strict_json(lines[0]), slots)
    finally:
        # Exact generated temporary root only; never repository cleanup.
        if not owned_root(folder):
            raise RuntimeError('REFUSE_FOREIGN_TEMP_CLEANUP')
        shutil.rmtree(folder)
