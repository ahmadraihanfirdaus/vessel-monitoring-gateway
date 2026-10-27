"""Private harness telemetry: drain pipes, retain static categories, never raw logs."""
from threading import Lock, Thread
from time import monotonic
import json
import os
import sys
import re
from php_native_causality import native_state

STAGES = ('AUTOLOAD_DONE', 'PROFILE_ADMITTED', 'APPLICATION_ADMITTED', 'ROWS_ADMITTED', 'REQUEST_DONE')
SHUTDOWNS = ('NO_FATAL_REPORTED', 'FATAL_ERROR', 'PARSE_ERROR', 'CORE_ERROR', 'COMPILE_ERROR',
             'USER_ERROR', 'RECOVERABLE_ERROR', 'MEMORY_LIMIT')
CONNECTIONS = ('NONE', 'UPSTREAM_CONNECTION_ERROR', 'UPSTREAM_TIMEOUT', 'UPSTREAM_DISCONNECTED',
               'UPSTREAM_PROTOCOL_ERROR', 'UPSTREAM_INCOMPLETE_RESPONSE', 'UPSTREAM_IO_ERROR',
               'UPSTREAM_RESPONSE_TOO_LARGE', 'UPSTREAM_HTTP_502', 'RELAY_IO_ERROR', 'DOWNSTREAM_IO_ERROR')


def valid_runtime(data):
    keys = {'php_version','sapi','debug_build','zts','int_bytes','extensions','opcache_enable_cli',
            'opcache_jit','opcache_jit_buffer_size','memory_limit','segv_handler','term_handler'}
    if not isinstance(data, dict) or set(data) != keys:
        return False
    extensions = {'PDO','pdo_mysql','mysqlnd','openssl','mbstring','intl','FFI','Zend OPcache','xdebug','pcov'}
    if not isinstance(data['extensions'], dict) or set(data['extensions']) != extensions:
        return False
    version = lambda v: isinstance(v,str) and (v in ('NOT_LOADED','OTHER') or re.fullmatch(r'[0-9]{1,6}(?:\.[0-9]{1,6}){0,3}',v) is not None)
    return (data['php_version'] in ('8.2.35','OTHER') and data['sapi'] in ('CLI','CLI_SERVER','OTHER')
        and type(data['debug_build']) is bool and type(data['zts']) is bool
        and type(data['int_bytes']) is int and data['int_bytes'] in (4,8)
        and all(version(v) for v in data['extensions'].values())
        and all(isinstance(data[k],str) and len(data[k]) <= 20 and
                (data[k]=='OTHER' or re.fullmatch(r'(?:-1|[0-9]+[KMG]?|off|on|tracing|function)?',data[k],re.I) is not None)
                for k in ('opcache_enable_cli','opcache_jit','opcache_jit_buffer_size','memory_limit'))
        and data['segv_handler'] in ('DEFAULT','IGNORED','CUSTOM','UNAVAILABLE')
        and data['term_handler'] in ('DEFAULT','IGNORED','CUSTOM','UNAVAILABLE'))


class ServerLogCapture:
    """Continuously drain without a disk log or an unbounded queue/line buffer."""
    LINE_LIMIT = 4096
    COUNT_LIMIT = 16777216

    def __init__(self):
        self.lock = Lock()
        self.pending = bytearray()
        self.discarding = False
        self.bytes_seen = 0
        self.count_capped = self.line_truncated = False
        self.stages, self.errors, self.caught = set(), set(), set()
        self.last_stage = 'NONE_OBSERVED'
        self.shutdown = 'NONE_OBSERVED'
        self.state = 'NOT_STARTED'
        self.thread = self.stream = None
        self.runtime = None

    def _line(self, line):
        if b'VG_PHP_RUNTIME=' in line:
            try:
                data = json.loads(line.split(b'VG_PHP_RUNTIME=',1)[1])
                if valid_runtime(data):
                    self.runtime = data
            except (ValueError, TypeError, KeyError):
                pass
        # Only complete, bounded lines are classified. No arbitrary values kept.
        for stage in STAGES:
            if b'VG_LIVE_STAGE='+stage.encode() in line:
                self.stages.add(stage)
                self.last_stage = stage
        for category in SHUTDOWNS:
            if b'VG_LIVE_SHUTDOWN='+category.encode() in line:
                self.shutdown = category
                if category != 'NO_FATAL_REPORTED':
                    self.errors.add(category)
        for category in ('RUNTIME', 'LOGIC', 'OTHER'):
            if b'VG_LIVE_CAUGHT='+category.encode() in line:
                self.caught.add(category)
        lower = line.lower()
        for marker, category in ((b'fatal error:', 'FATAL_ERROR'), (b'parse error:', 'PARSE_ERROR'),
                                 (b'uncaught ', 'UNCAUGHT_REPORTED'),
                                 (b'allowed memory size of', 'MEMORY_LIMIT')):
            if marker in lower:
                self.errors.add(category)

    def feed(self, chunk):
        if not isinstance(chunk, bytes) or len(chunk) > self.LINE_LIMIT:
            raise ValueError('invalid bounded log chunk')
        with self.lock:
            self.count_capped |= self.bytes_seen+len(chunk) > self.COUNT_LIMIT
            self.bytes_seen = min(self.COUNT_LIMIT, self.bytes_seen+len(chunk))
            for part in chunk.splitlines(keepends=True):
                end = part.endswith(b'\n') or part.endswith(b'\r')
                if not self.discarding:
                    if len(self.pending)+len(part) > self.LINE_LIMIT:
                        self.pending.clear()
                        self.line_truncated = self.discarding = True
                    else:
                        self.pending.extend(part)
                if end:
                    if not self.discarding:
                        self._line(bytes(self.pending))
                    self.pending.clear()
                    self.discarding = False

    def _drain(self):
        try:
            read = getattr(self.stream, 'read1', self.stream.read)
            while True:
                chunk = read(self.LINE_LIMIT)
                if not chunk:
                    break
                self.feed(chunk)
            with self.lock:
                if self.pending and not self.discarding:
                    self._line(bytes(self.pending))
                self.pending.clear()
                self.state = 'EOF'
        except (OSError, ValueError):
            with self.lock:
                self.pending.clear()
                self.state = 'READ_ERROR'
        finally:
            try:
                self.stream.close()
            except (OSError, ValueError):
                with self.lock:
                    self.state = 'READ_ERROR'

    def start(self, stream):
        self.stream, self.state = stream, 'ACTIVE'
        self.thread = Thread(target=self._drain, daemon=True)
        self.thread.start()

    def finish(self):
        if self.thread is None:
            return True
        self.thread.join(timeout=2)
        return not self.thread.is_alive() and self.state == 'EOF'

    def snapshot(self):
        with self.lock:
            return {'capture_status': self.state, 'log_bytes_observed': self.bytes_seen,
                    'log_count_capped': self.count_capped, 'log_line_truncated': self.line_truncated,
                    'last_stage': self.last_stage, 'observed_stages': sorted(self.stages),
                    'error_categories': sorted(self.errors), 'caught_categories': sorted(self.caught),
                    'request_shutdown': self.shutdown,
                    'runtime': self.runtime, 'capture_scope': 'PROCESS_CUMULATIVE_ASYNCHRONOUS_BEST_EFFORT'}


class PhpLifecycle:
    EVENTS = ('SERVER_STARTING', 'SERVER_STARTED', 'READINESS_PASSED', 'READINESS_FAILED',
              'REQUESTS_BEGIN', 'PROXY_FAILURE', 'GATE_FAILED', 'BEFORE_CLEANUP',
              'CLEANUP_TERMINATE', 'CLEANUP_KILL', 'CLEANUP_COMPLETE',
              'PASSIVE_OBSERVATION_BEGIN', 'PASSIVE_WINDOW_EXPIRED', 'PRE_TERMINATE', 'EXIT_BEFORE_TERMINATE')

    def __init__(self, capture, clock=monotonic):
        self.capture, self.clock = capture, clock
        self.started, self.sequence = clock(), 0
        self.proxy_events = self.proxy_events_suppressed = 0
        self.process = None
        self.phase = 'STARTUP'
        self.shutdown = 'NONE_REQUESTED'
        self.native_outcome = 'NOT_ASSESSED'
        self.request_disconnect = False
        self.lock = Lock()

    def observe(self, event, connection='NONE'):
        if event not in self.EVENTS or connection not in CONNECTIONS:
            raise ValueError('invalid lifecycle category')
        with self.lock:
            if connection == 'UPSTREAM_DISCONNECTED' and self.phase == 'REQUEST':
                self.request_disconnect = True
            # Reserve32 records for lifecycle/failure/cleanup even during startup retry floods.
            if event == 'PROXY_FAILURE':
                if self.proxy_events >= 96:
                    self.proxy_events_suppressed = min(65535, self.proxy_events_suppressed+1)
                    return
                self.proxy_events += 1
            if self.sequence >= 128:
                return
            self.sequence += 1
            code = self.process.poll() if self.process is not None else None
            state = ('NOT_STARTED' if self.process is None else 'ALIVE' if code is None
                     else 'EXITED' if type(code) is int else 'UNKNOWN')
            code = code if type(code) is int and -2147483648 <= code <= 4294967295 else None
            elapsed = max(0, int((self.clock()-self.started)*1000))
            record = {'event': event, 'sequence': self.sequence, 'phase': self.phase,
                      'elapsed_ms': min(elapsed, 3600000), 'elapsed_capped': elapsed > 3600000,
                      'process_state': state, 'exit_code': code,
                      'exit_category': 'UNAVAILABLE' if code is None else 'ZERO' if code == 0
                                       else 'SIGNAL' if os.name == 'posix' and code < 0 else 'NONZERO',
                      'connection': connection, 'shutdown': self.shutdown,
                      'native_state': native_state(self.process) if self.process is not None else None,
                      'native_outcome': self.native_outcome,
                      'event_limit_reached': self.sequence == 128 or self.proxy_events == 96,
                      'proxy_events_suppressed': self.proxy_events_suppressed, **self.capture.snapshot()}
            sys.stdout.write('LIVE_HTTP_PHP_LIFECYCLE='+json.dumps(record, sort_keys=True)+'\n')
            sys.stdout.flush()
