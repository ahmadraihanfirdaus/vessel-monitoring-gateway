"""Build the fixed ESP32 candidate image locally; never uploads or erases hardware."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import struct
import sys

from audit_precommit_security import TOKEN_PATTERN, EMBEDDED_URL_PASSWORD_PATTERN

ROOT = Path(__file__).resolve().parents[1]
APP_LIMIT = 1048576


def security_config_valid(config):
    enabled = set(re.findall(r'^CONFIG_([A-Z0-9_]+)=y$', config, re.M))
    required = {'MBEDTLS_CERTIFICATE_BUNDLE', 'MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL',
                'COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'MBEDTLS_HAVE_TIME_DATE',
                'MBEDTLS_HAVE_TIME', 'ESP_HTTP_CLIENT_ENABLE_HTTPS'}
    return required <= enabled and not enabled.intersection(
        {'ESP_TLS_INSECURE', 'ESP_TLS_SKIP_SERVER_CERT_VERIFY'})


def source_snapshot():
    paths = [ROOT/'firmware/platformio.ini', ROOT/'firmware/CMakeLists.txt', ROOT/'firmware/sdkconfig.defaults', ROOT/'scripts/build_esp32_port.py']
    paths += [p for p in (ROOT/'firmware/src').rglob('*')
              if p.is_file() and (p.suffix in {'.c', '.h', '.cpp', '.hpp'} or p.name == 'CMakeLists.txt')]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def sanitize(text):
    home = str(Path.home())
    for value in (home, home.replace('\\', '/'), home.replace('\\', '\\\\')):
        text = text.replace(value, '<LOCAL_HOME>')
    text = TOKEN_PATTERN.sub('[REDACTED_TOKEN]', text)
    text = EMBEDDED_URL_PASSWORD_PATTERN.sub('[REDACTED_URL_AUTH]', text)
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pio-cli', default=os.getenv('VG_PLATFORMIO_CLI', 'platformio'))
    parser.add_argument('--evidence-name', required=True)
    args = parser.parse_args()
    if re.fullmatch(r'esp32-transport-sdk-build-[a-z0-9-]+\.txt', args.evidence_name) is None:
        parser.error('expected a fixed ESP32 transport evidence filename')
    target = ROOT/'evidence/test-results'/args.evidence_name
    if target.exists():
        parser.error('evidence already exists; select a new run name')
    env = os.environ.copy()
    env['PLATFORMIO_SETTING_ENABLE_TELEMETRY'] = 'no'
    env['PLATFORMIO_SETTING_CHECK_PLATFORMIO_INTERVAL'] = '0'
    inputs = source_snapshot()
    try:
        completed = subprocess.run([args.pio_cli, 'run', '-d', 'firmware', '-e', 'esp32dev_espidf'],
            cwd=ROOT, env=env, capture_output=True, text=True, errors='replace', timeout=300)
        output = sanitize(completed.stdout+completed.stderr).rstrip()+'\n'
        target.write_bytes(output.encode('utf-8'))
        if inputs != source_snapshot():
            with target.open('ab') as log: log.write(b'ESP32_SOURCE_STABILITY=FAIL_CHANGED_DURING_BUILD\n')
            print('ESP32_SOURCE_STABILITY=FAIL_CHANGED_DURING_BUILD')
            return 1
        for line in output.splitlines():
            if any(word in line for word in ('error:', 'Error:', 'RAM:', 'Flash:', '[SUCCESS]', '[FAILED]')):
                print(line)
        if completed.returncode:
            return 1
        image = ROOT/'firmware/.pio/build/esp32dev_espidf/firmware.bin'
        if not image.is_file() or image.stat().st_size > APP_LIMIT:
            print('ESP32_IMAGE=FAIL_MISSING_OR_OVER_ONE_MIB')
            return 1
        build = image.parent
        partition = build/'partitions.bin'
        factory = []
        raw = partition.read_bytes()
        for offset in range(0, len(raw)-31, 32):
            magic, kind, subtype, start, size, label, flags = struct.unpack('<HBBII16sI', raw[offset:offset+32])
            if magic == 0x50AA and kind == 0 and subtype == 0:
                factory.append((start, size))
        if factory != [(0x10000, APP_LIMIT)]:
            print('ESP32_PARTITION=FAIL_EXPECTED_ONE_MIB_FACTORY')
            return 1
        config = (ROOT/'firmware/sdkconfig.esp32dev_espidf').read_text(encoding='utf-8')
        if not security_config_valid(config):
            print('ESP32_SECURITY_CONFIG=FAIL_TLS_VALIDATION_OR_ASSERTIONS')
            return 1
        flash = re.search(r'^CONFIG_ESPTOOLPY_FLASHSIZE="(2MB|4MB|8MB|16MB)"$', config, re.M)
        if flash is None:
            print('ESP32_SIM_LAYOUT=BLOCKED_UNRECOGNIZED_SDK_CONFIG')
            return 3
        core = Path(env.get('PLATFORMIO_CORE_DIR', str(Path.home()/'.platformio')))
        esptool = core/'packages/tool-esptoolpy/esptool.py'
        sdk_python = Path(args.pio_cli).with_name('python.exe') if args.pio_cli.endswith('.exe') else Path(sys.executable)
        merged = build/'firmware.merged.bin'
        merge = subprocess.run([str(sdk_python), str(esptool), '--chip', 'esp32', 'merge_bin',
            '--output', str(merged), '--flash_mode', 'dio', '--flash_freq', '40m',
            '--flash_size', flash.group(1), '--fill-flash-size', flash.group(1),
            '0x1000', str(build/'bootloader.bin'), '0x8000', str(partition), '0x10000', str(image)],
            cwd=ROOT, env=env, capture_output=True, text=True, errors='replace', timeout=60)
        with target.open('ab') as log:
            log.write(sanitize(merge.stdout+merge.stderr).encode('utf-8'))
        if merge.returncode or not merged.is_file():
            print('ESP32_SIM_MERGE=FAIL')
            return 1
        combined = merged.read_bytes()
        app = image.read_bytes()
        if combined[0x10000:0x10000+len(app)] != app or any(byte != 255 for byte in combined[0x9000:0xF000]):
            print('ESP32_SIM_MERGE=FAIL_APP_OR_BLANK_NVS')
            return 1
        record = 'ESP32_SIM_MERGE=PASS_SHA256_'+hashlib.sha256(combined).hexdigest()+'\n'
        source_digest = hashlib.sha256(repr(sorted(inputs.items())).encode('utf-8')).hexdigest()
        record += 'ESP32_SOURCE_STABILITY=PASS_SHA256_'+source_digest+'\n'
        record += 'ESP32_SIM_LAYOUT='+flash.group(1)+'_SDK_CONFIG_ONLY_PHYSICAL_FLASH_UNVERIFIED\n'
        stack = []
        for report in build.rglob('*.su'):
            for line in report.read_text(encoding='utf-8').splitlines():
                parts = line.split('\t')
                if len(parts)>1 and parts[1].isdigit():
                    stack.append((int(parts[1]), parts[0].split(':')[-1]))
        if not stack or max(row[0] for row in stack) > 2048:
            print('ESP32_OWN_STACK_FRAMES=FAIL_MISSING_OR_OVER_TWO_KIB')
            return 1
        record += 'ESP32_OWN_LARGEST_STACK_FRAME='+str(max(row[0] for row in stack))+'\n'
        record += 'ESP32_FULL_CALL_STACK_AND_HEAP=NOT_RUN_HARDWARE_WATERMARK_REQUIRED\n'
        with target.open('ab') as log: log.write(record.encode('utf-8'))
        print(record, end='')
        print('ESP32_IMAGE=PASS_BYTES_'+str(image.stat().st_size)+'_LIMIT_'+str(APP_LIMIT))
        print('ESP32_HARDWARE_UPLOAD=NOT_RUN')
        return 0
    except (OSError, subprocess.TimeoutExpired):
        with target.open('ab') as log: log.write(b'ESP32_BUILD=BLOCKED_TOOL_PERMISSION_OR_TIMEOUT\n')
        print('ESP32_BUILD=BLOCKED_TOOL_PERMISSION_OR_TIMEOUT')
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
