"""Owned child observations only. No ptrace, memory, core, environment or raw status output."""
from pathlib import Path
import subprocess
import sys
from time import monotonic


def native_state(process, platform=sys.platform, reader=None):
    result = {'availability': 'NOT_SUPPORTED', 'kernel_state': 'UNKNOWN', 'core_dumping': None,
              'segv_pending': None, 'term_pending': None, 'segv_caught': None, 'term_caught': None,
              'segv_ignored': None, 'term_ignored': None}
    if not platform.startswith('linux'):
        return result
    result['availability'] = 'UNAVAILABLE'
    if type(process.pid) is not int or process.pid <= 0:
        return result
    try:
        if reader is None:
            with (Path('/proc')/str(process.pid)/'status').open('rb') as stream:
                raw = stream.read(8193)
        else:
            raw = reader(process.pid)
        if not isinstance(raw, bytes) or len(raw) > 8192:
            return result
        values = {}
        for line in raw.splitlines():
            key, sep, value = line.partition(b':')
            if sep and key in (b'State', b'CoreDumping', b'SigPnd', b'ShdPnd', b'SigCgt', b'SigIgn'):
                values[key] = value.strip()
        states = {b'R':'RUNNING', b'S':'SLEEPING', b'D':'DISK_WAIT', b'T':'STOPPED',
                  b't':'TRACING_STOP', b'Z':'ZOMBIE', b'X':'DEAD', b'I':'IDLE'}
        result['kernel_state'] = states.get(values.get(b'State', b'')[:1], 'UNKNOWN')
        core = values.get(b'CoreDumping')
        result['core_dumping'] = core == b'1' if core in (b'0', b'1') else None
        def mask(key):
            value = values.get(key)
            if value is None or not 1 <= len(value) <= 32 or any(c not in b'0123456789abcdefABCDEF' for c in value):
                return None
            return int(value, 16)
        pending, shared = mask(b'SigPnd'), mask(b'ShdPnd')
        masks = {'pending': pending | shared if pending is not None and shared is not None else None,
                 'caught': mask(b'SigCgt'), 'ignored': mask(b'SigIgn')}
        for kind, value in masks.items():
            for name, number in (('segv', 11), ('term', 15)):
                result[name+'_'+kind] = bool(value & (1 << (number-1))) if value is not None else None
        result['availability'] = 'OBSERVED'
    except OSError:
        pass
    return result


def finish_failed_upstream(process, lifecycle, clock=monotonic):
    """Use half of the EXISTING10s cleanup budget passively; do not extend it.

    No requests are retried. Only a failed request disconnect enters this path.
    A post-terminate signal is deliberately kept causally unresolved.
    """
    deadline = clock()+10
    lifecycle.observe('PASSIVE_OBSERVATION_BEGIN')
    if process.poll() is None:
        try:
            process.wait(timeout=min(5, max(0, deadline-clock())))
        except subprocess.TimeoutExpired:
            lifecycle.observe('PASSIVE_WINDOW_EXPIRED')
    code = process.poll()
    if code is not None:
        lifecycle.native_outcome = ('SIGNAL_EXIT_BEFORE_TERMINATE' if type(code) is int and code < 0
                                    else 'EXIT_BEFORE_TERMINATE')
        lifecycle.shutdown = 'ALREADY_EXITED'
        lifecycle.observe('EXIT_BEFORE_TERMINATE')
        return
    lifecycle.observe('PRE_TERMINATE')
    lifecycle.shutdown = 'TERMINATE_REQUESTED'
    lifecycle.observe('CLEANUP_TERMINATE')
    process.terminate()
    try:
        process.wait(timeout=max(0, deadline-clock()))
        lifecycle.native_outcome = ('SIGNAL_AFTER_TERMINATE_CAUSE_UNRESOLVED'
                                    if process.poll() == -11 else 'EXIT_AFTER_PASSIVE_WINDOW_AND_TERMINATE')
    except subprocess.TimeoutExpired:
        lifecycle.shutdown = 'KILL_REQUESTED'
        lifecycle.observe('CLEANUP_KILL')
        process.kill()
        process.wait(timeout=5)  # Existing fallback deadline, unchanged.
        lifecycle.native_outcome = 'KILLED_AFTER_EXISTING_CLEANUP_BUDGET'
