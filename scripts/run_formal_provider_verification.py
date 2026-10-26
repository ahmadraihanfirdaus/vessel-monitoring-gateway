"""Dedicated host cases; read-only default. No automatic formal registry mutation."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = ('SUP-004', 'SUP-005', 'SUP-007', 'SUP-008', 'SUP-009', 'SUP-010')
PROTOCOL = ROOT/'docs/testing/formal-provider-cases-20261026.md'


def snapshot():
    paths = list((ROOT/'firmware/src').glob('*.h'))
    paths += [PROTOCOL, Path(__file__), ROOT/'scripts/formal_provider_fixture.c',
              ROOT/'scripts/test_formal_provider_verification.py', ROOT/'scripts/continuous_simulation_fixture.c']
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def synthetic_rmc(payload=None):
    # Public mathematical fixture, no observed location, route or operational data.
    if payload is None:
        payload = 'GPRMC,000000.00,A,0030.0000,N,00130.0000,E,5.0,90.0,010100,,,A'
    checksum = 0
    for value in payload.encode('ascii'):
        checksum ^= value
    return '$'+payload+'*'+format(checksum, '02X')


def synthetic_navigation_inputs():
    good = synthetic_rmc()
    fields = good[1:good.index('*')].split(',')
    result = [good]
    for index, value in [(3,'0060.0000'), (7,'NaN'), (8,'360.0'), (2,'V')]:
        changed = fields.copy(); changed[index] = value
        result.append(synthetic_rmc(','.join(changed)))
    return result


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('DUPLICATE_NATIVE_FIELD')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE_NATIVE_OUTPUT')))


def observe(case, value):
    """Independent protocol oracle, returns field-level expected/actual failures."""
    failures = []
    comparisons = []
    def check(field, actual, expected):
        # bool is not an acceptable JSON integer and vice versa.
        same = type(actual) is type(expected) and actual == expected
        if isinstance(expected, float) and isinstance(actual, (int, float)) and not isinstance(actual, bool):
            same = math.isfinite(actual) and math.isclose(actual, expected, abs_tol=1e-6, rel_tol=0)
        comparisons.append({'field': field, 'expected': expected, 'actual': actual, 'pass': same})
        if not same:
            failures.append(field)
    if not isinstance(value, dict):
        raise ValueError('NATIVE_OBJECT_REQUIRED')
    check('case', value.get('case'), case)
    count = value.get('checks')
    check('native_assertions_present', isinstance(count, int) and not isinstance(count, bool) and count >= 14, True)
    if case == 'SUP-004':
        expected = dict(active_after_ack=True, acknowledged=True, ack_state=2, raised=0,
                        ack_time_present=True, ack_time=0, cleared_time_present_after_ack=False,
                        raised_fact_state=1, condition_after_explicit_clear=False, next_alarm_id=3, next_event_id=4)
        for key, wanted in expected.items():
            check(key, value.get(key), wanted)
    elif case == 'SUP-005':
        engines = value.get('engines')
        if not isinstance(engines, list) or len(engines) != 4:
            raise ValueError('EXACT_FOUR_ENGINE_OBSERVATIONS_REQUIRED')
        for index, engine in enumerate(engines):
            if not isinstance(engine, dict):
                raise ValueError('ENGINE_OBJECT_REQUIRED')
            expected = dict(id=index+1, source='simulation', state=2,
                            rpm=float((2000, 2020, 2010, 1990)[index]),
                            temperature=float((82, 83, 84, 82.5)[index]),
                            runtime=3600+index*60, alarm=False, communication=1)
            for key, wanted in expected.items():
                check('engine'+str(index+1)+'.'+key, engine.get(key), wanted)
        for key, wanted in dict(lost_state=0, lost_rpm=0.0, lost_alarm=False).items():
            check(key, value.get(key), wanted)
    elif case == 'SUP-007':
        expected = dict(synthetic_only=True, latitude=0.5, longitude=1.5, sog=5.0, cog=90.0,
                        fix=True, source='simulation', quality='valid', initial_age=0,
                        before_age_state=1, stale_state=2, offline_state=3, offline_age=300,
                        ingest_rewound=False, ingest_unchanged=True, ingest_behind_observed=False,
                        observed_unchanged=True, age_rewound=False, age_unchanged=True,
                        nofix_position_quality='invalid', nofix_position_present=False)
        for key, wanted in expected.items():
            check(key, value.get(key), wanted)
    elif case in ('SUP-008', 'SUP-009', 'SUP-010'):
        labels = {'SUP-008': ('attitude/motion prototype', 'not vessel stability certification'),
                  'SUP-009': ('vibration/acceleration prototype', 'not machinery condition certification'),
                  'SUP-010': ('low-power electrical bench prototype', 'safe low-power bench reference only')}
        check('label', value.get('label'), labels[case][0])
        check('scope', value.get('scope'), labels[case][1])
        if case == 'SUP-010':
            check('hazard', value.get('hazard'), 'not vessel electrical safety certification')
            check('zero_present', value.get('zero_present'), True)
        values = {'SUP-008': [[0.,0.],[12.5,-4.],[-8.,6.],[-8.,6.],[0.,0.],[0.,0.],[0.,0.],[1.,-1.]],
                  'SUP-009': [[0.,0.,1.,.02],[.12,-.08,1.03,.35],[-.25,.20,.92,.80],[-.25,.20,.92,.80],
                              [0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[.01,0.,1.,.05]],
                  'SUP-010': [[5.,.1,.5],[12.,.25,3.],[12.,-.05,-.6],[12.,-.05,-.6],
                              [0.,0.,0.],[0.,0.,0.],[0.,0.,0.],[5.,.05,.25]]}
        qualities = ('valid','valid','valid','stale','missing','invalid','unknown','valid')
        steps = value.get('steps')
        if not isinstance(steps, list) or len(steps) != 8:
            raise ValueError('EXACT_EIGHT_PROVIDER_OBSERVATIONS_REQUIRED')
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError('STEP_OBJECT_REQUIRED')
            q = qualities[index]
            for key, wanted in dict(quality=q, source='simulation', present=q in ('valid','stale'),
                                    current=q=='valid', time=index*100, sequence=index+1).items():
                check(str(index)+'.'+key, step.get(key), wanted)
            numbers = step.get('values')
            if not isinstance(numbers, list) or len(numbers) != len(values[case][index]):
                raise ValueError('EXACT_PROVIDER_FIELD_COUNT_REQUIRED')
            for field, wanted in enumerate(values[case][index]):
                check(str(index)+'.values.'+str(field), numbers[field], wanted)
    else:
        raise ValueError('UNREGISTERED_CASE')
    return failures, comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    try:
        protocol = PROTOCOL.read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        print('FORMAL_PROVIDER_GATE=BLOCKED_PROTOCOL_UNAVAILABLE')
        return 3
    if 'PROTOCOL_CASE_BY_CASE_REVIEW=PASS_FOR_THE_SIX_SPECIFIED_HOST_EXECUTION_CLASSES' not in protocol:
        print('FORMAL_PROVIDER_GATE=BLOCKED_PROTOCOL_REVIEW_REQUIRED')
        return 3
    if not args.execute:
        print('FORMAL_PROVIDER_CASES='+','.join(CASES))
        print('FORMAL_PROVIDER_GATE=NOT_RUN_READ_ONLY')
        return 0
    inputs = snapshot()
    try:
        head = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        branch = subprocess.run(['git','branch','--show-current'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        print('SOURCE_COMMIT='+head+' BRANCH='+branch, flush=True)
        print('SOURCE_INPUTS='+json.dumps(inputs,sort_keys=True), flush=True)
        compiler = os.environ.get('VG_HOST_CC', 'gcc')
        version = subprocess.run([compiler,'--version'],capture_output=True,text=True,timeout=15,check=True).stdout.splitlines()[0]
        print('HOST_COMPILER='+version, flush=True)
        failures = 0
        with tempfile.TemporaryDirectory(prefix='vg-formal-providers-') as raw:
            folder = Path(raw).resolve()
            if folder.parent != Path(tempfile.gettempdir()).resolve() or not folder.name.startswith('vg-formal-providers-') or folder.is_symlink():
                raise ValueError('OWNED_TEMP_REQUIRED')
            binary = folder/('provider-cases.exe' if os.name == 'nt' else 'provider-cases')
            command = [compiler,'-std=c99','-Wall','-Wextra','-Werror','-pedantic','-Os',
                       '-I',str(ROOT/'firmware/src'),str(ROOT/'scripts/formal_provider_fixture.c'),'-o',str(binary)]
            if os.name != 'nt':
                command.append('-lm')
            result = subprocess.run(command,capture_output=True,timeout=60,cwd=ROOT)
            if result.returncode or not binary.is_file():
                print('FORMAL_PROVIDER_GATE=FAIL_NATIVE_COMPILE_NO_UNREDACTED_DIAGNOSTICS')
                return 1
            print('NATIVE_BINARY_SHA256='+hashlib.sha256(binary.read_bytes()).hexdigest(), flush=True)
            for case in CASES:
                arguments = [str(binary),case]+(synthetic_navigation_inputs() if case == 'SUP-007' else [])
                result = subprocess.run(arguments,capture_output=True,timeout=15,cwd=ROOT)
                if result.returncode or result.stderr or not 0 < len(result.stdout) <= 8192:
                    print('FORMAL_CASE='+case+'=FAIL_NATIVE_PROCESS',flush=True); failures += 1
                    continue
                value = strict_json(result.stdout)
                errors, comparisons = observe(case,value)
                print('NATIVE_OBSERVATION='+json.dumps(value,sort_keys=True,allow_nan=False),flush=True)
                print('EXPECTED_ACTUAL='+json.dumps(comparisons,sort_keys=True,allow_nan=False),flush=True)
                print('FORMAL_CASE='+case+('=FAIL_FIELDS_'+','.join(errors) if errors else '=PASS_HOST_ONLY'),flush=True)
                failures += bool(errors)
        if snapshot() != inputs:
            print('FORMAL_PROVIDER_GATE=FAIL_SOURCE_DRIFT'); return 1
        digest = hashlib.sha256(repr(sorted(inputs.items())).encode()).hexdigest()
        print('FORMAL_PROVIDER_SOURCE_STABILITY=PASS_SHA256_'+digest,flush=True)
        print('FORMAL_PROVIDER_GATE='+('FAIL' if failures else 'PASS_SIX_HOST_CASES_NO_HARDWARE_OR_REGISTRY_MUTATION'),flush=True)
        return 1 if failures else 0
    except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, KeyError, TypeError) as error:
        print('FORMAL_PROVIDER_GATE=BLOCKED_'+type(error).__name__+'_NO_UNREDACTED_DIAGNOSTICS',flush=True)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
