"""Deterministic private proxy faults. No database, credentials or external hosts."""
from contextlib import redirect_stdout
from email.message import Message
import http.client
import io
import json
import socket
import socketserver
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import run_live_http_integration as gate


class ProxyDiagnosticsTest(unittest.TestCase):
    def handler(self):
        h = object.__new__(gate.ProxyHandler)
        h.connection = MagicMock()
        h.headers = Message()
        h.headers['Host'] = '127.0.0.1:12345'
        h.command = 'GET'
        h.path = '/monitoring/owned-fixture'
        h.rfile = io.BytesIO(b'')
        h.wfile = MagicMock()
        h.server = SimpleNamespace(server_port=12345, backend_port=23456,
            readonly_api_unavailable=lambda *args: False,
            consume_commit_reply_drop=lambda *args: False, relay_error_categories=set())
        for name in ['send_error', 'send_response', 'send_header', 'end_headers']:
            setattr(h, name, MagicMock())
        response = MagicMock(status=200)
        response.read.return_value = b'ok'
        response.getheaders.return_value = []
        upstream = MagicMock()
        upstream.getresponse.return_value = response
        return h, upstream, response

    def invoke(self, h, upstream):
        output = io.StringIO()
        with patch.object(gate.http.client, 'HTTPConnection', return_value=upstream) as connect, redirect_stdout(output):
            h.relay()
        connect.assert_called_once_with('127.0.0.1', 23456, timeout=15)
        h.connection.settimeout.assert_called_once_with(10)
        upstream.close.assert_called_once()
        records = [json.loads(line.split('=', 1)[1]) for line in output.getvalue().splitlines()
                   if line.startswith('LIVE_HTTP_PROXY_DIAGNOSTIC=')]
        return records, output.getvalue()

    def test_each_upstream_exception_has_static_reason_phase_and_closed_connection(self):
        cases = [
            ('request', ConnectionRefusedError('synthetic-private'), 'UPSTREAM_CONNECTION_ERROR', 'UPSTREAM_REQUEST'),
            ('request', TimeoutError('synthetic-private'), 'UPSTREAM_TIMEOUT', 'UPSTREAM_REQUEST'),
            ('headers', TimeoutError('synthetic-private'), 'UPSTREAM_TIMEOUT', 'UPSTREAM_HEADERS'),
            ('headers', http.client.RemoteDisconnected('synthetic-private'), 'UPSTREAM_DISCONNECTED', 'UPSTREAM_HEADERS'),
            ('headers', http.client.BadStatusLine('synthetic-private'), 'UPSTREAM_PROTOCOL_ERROR', 'UPSTREAM_HEADERS'),
            ('headers', http.client.LineTooLong('synthetic-private'), 'UPSTREAM_PROTOCOL_ERROR', 'UPSTREAM_HEADERS'),
            ('body', http.client.IncompleteRead(b'synthetic-private', 1), 'UPSTREAM_INCOMPLETE_RESPONSE', 'UPSTREAM_BODY'),
            ('body', TimeoutError('synthetic-private'), 'UPSTREAM_TIMEOUT', 'UPSTREAM_BODY'),
            ('body', OSError('synthetic-private'), 'UPSTREAM_IO_ERROR', 'UPSTREAM_BODY'),
        ]
        for at, error, reason, phase in cases:
            with self.subTest(reason=reason, phase=phase):
                h, upstream, response = self.handler()
                {'request': upstream.request, 'headers': upstream.getresponse, 'body': response.read}[at].side_effect = error
                records, output = self.invoke(h, upstream)
                h.send_error.assert_called_once_with(502)
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]['reason'], reason)
                self.assertEqual(records[0]['phase'], phase)
                self.assertNotIn('synthetic-private', output)

    def test_exact_response_limit_passes_and_one_extra_byte_remains_502(self):
        for size in [gate.MAX_REPLY, gate.MAX_REPLY+1]:
            with self.subTest(size=size):
                h, upstream, response = self.handler()
                response.read.return_value = b'x'*size
                records, _ = self.invoke(h, upstream)
                response.read.assert_called_once_with(gate.MAX_REPLY+1)
                if size == gate.MAX_REPLY:
                    self.assertEqual(records, [])
                    h.send_error.assert_not_called()
                    h.send_response.assert_called_once_with(200)
                else:
                    h.send_error.assert_called_once_with(502)
                    self.assertEqual(records[0]['reason'], 'UPSTREAM_RESPONSE_TOO_LARGE')
                    self.assertEqual(records[0]['response_bytes_observed'], gate.MAX_REPLY+1)

    def test_upstream_502_is_identified_and_forwarded_without_fabricating_a_new_body(self):
        h, upstream, response = self.handler()
        response.status = 502
        records, _ = self.invoke(h, upstream)
        h.send_error.assert_not_called()
        h.send_response.assert_called_once_with(502)
        h.wfile.write.assert_called_once_with(b'ok')
        self.assertEqual(records[0]['reason'], 'UPSTREAM_HTTP_502')

    def test_downstream_write_failure_never_attempts_a_second_http_status(self):
        h, upstream, _ = self.handler()
        h.wfile.write.side_effect = BrokenPipeError('synthetic-private')
        records, output = self.invoke(h, upstream)
        h.send_response.assert_called_once_with(200)
        h.send_error.assert_not_called()
        self.assertTrue(h.close_connection)
        self.assertEqual(records[0]['reason'], 'DOWNSTREAM_IO_ERROR')
        self.assertEqual(records[0]['phase'], 'DOWNSTREAM_RESPONSE')
        self.assertNotIn('synthetic-private', output)

    def test_error_response_delivery_failure_still_closes_upstream_without_second_attempt(self):
        h, upstream, _ = self.handler()
        upstream.request.side_effect = ConnectionRefusedError('synthetic-private')
        h.send_error.side_effect = BrokenPipeError('synthetic-private')
        records, output = self.invoke(h, upstream)
        h.send_error.assert_called_once_with(502)
        self.assertTrue(h.close_connection)
        self.assertEqual([r['reason'] for r in records], ['UPSTREAM_CONNECTION_ERROR', 'DOWNSTREAM_IO_ERROR'])
        self.assertEqual(records[-1]['phase'], 'ERROR_RESPONSE')
        self.assertNotIn('synthetic-private', output)

    def test_relay_policy_oserror_has_its_own_phase_and_no_exception_text(self):
        h, upstream, _ = self.handler()
        h.server.consume_commit_reply_drop = MagicMock(side_effect=OSError('synthetic-private'))
        records, output = self.invoke(h, upstream)
        h.send_error.assert_called_once_with(502)
        self.assertEqual(records[0]['reason'], 'RELAY_IO_ERROR')
        self.assertEqual(records[0]['phase'], 'FAULT_POLICY')
        self.assertNotIn('synthetic-private', output)

    def test_metadata_is_bounded_static_and_never_exposes_arbitrary_values(self):
        output = io.StringIO()
        with patch.object(gate.time, 'monotonic', return_value=1000), redirect_stdout(output):
            gate.proxy_diagnostic('UPSTREAM_IO_ERROR', 'UPSTREAM_BODY', 0, 'synthetic-private', gate.MAX_REPLY+100)
        r = json.loads(output.getvalue().split('=', 1)[1])
        self.assertEqual(set(r), {'reason', 'phase', 'upstream_status_category', 'duration_ms',
                                 'duration_capped', 'response_bytes_observed', 'response_limit_bytes'})
        self.assertEqual(r['upstream_status_category'], 'OTHER')
        self.assertEqual(r['duration_ms'], 60000)
        self.assertTrue(r['duration_capped'])
        self.assertEqual(r['response_bytes_observed'], gate.MAX_REPLY+1)
        self.assertEqual(r['response_limit_bytes'], gate.MAX_REPLY)
        self.assertNotIn('synthetic-private', output.getvalue())
        for reason, phase in [('synthetic-private', 'UPSTREAM_BODY'), ('UPSTREAM_IO_ERROR', 'synthetic-private')]:
            output = io.StringIO()
            with redirect_stdout(output), self.assertRaises(ValueError):
                gate.proxy_diagnostic(reason, phase, 0)
            self.assertEqual(output.getvalue(), '')


class RawUpstream(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(2)
        self.request.recv(8192)
        if self.server.wire:
            self.request.sendall(self.server.wire)


class OwnedWireServer(socketserver.ThreadingTCPServer):
    daemon_threads = True

    def handle_error(self, request, address):
        pass


class LoopbackProxyDiagnosticsTest(unittest.TestCase):
    def execute(self, backend_port):
        # Real loopback TCP; no TLS claim here. Real TLS is a separate gate.
        proxy = gate.LoopbackTLSProxy(('127.0.0.1', 0), gate.ProxyHandler)
        proxy.backend_port = backend_port
        proxy.relay_error_categories = set()
        thread = threading.Thread(target=proxy.serve_forever, kwargs={'poll_interval': 0.01})
        thread.start()
        client = http.client.HTTPConnection('127.0.0.1', proxy.server_port, timeout=3)
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                client.request('GET', '/owned-fixture?opaque=synthetic-private')
                response = client.getresponse()
                body = response.read(gate.MAX_REPLY+1)
        finally:
            client.close()
            proxy.shutdown()
            proxy.server_close()
            thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        records = [json.loads(l.split('=', 1)[1]) for l in output.getvalue().splitlines()
                   if l.startswith('LIVE_HTTP_PROXY_DIAGNOSTIC=')]
        self.assertNotIn('synthetic-private', output.getvalue())
        return response.status, body, records

    def wire(self, wire):
        backend = OwnedWireServer(('127.0.0.1', 0), RawUpstream)
        backend.wire = wire
        thread = threading.Thread(target=backend.serve_forever, kwargs={'poll_interval': 0.01})
        thread.start()
        try:
            return self.execute(backend.server_address[1])
        finally:
            backend.shutdown()
            backend.server_close()
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive())

    def test_actual_loopback_connection_refused_malformed_disconnect_and_incomplete_chunk(self):
        # Keep the target port reserved but not listening: deterministic refusal.
        with socket.socket() as reserved:
            reserved.bind(('127.0.0.1', 0))
            status, _, records = self.execute(reserved.getsockname()[1])
        self.assertEqual(status, 502)
        self.assertEqual(records[0]['reason'], 'UPSTREAM_CONNECTION_ERROR')
        for wire, reason in [
            (b'not-http synthetic-private\r\n\r\n', 'UPSTREAM_PROTOCOL_ERROR'),
            (b'', 'UPSTREAM_DISCONNECTED'),
            (b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n10\r\nshort', 'UPSTREAM_INCOMPLETE_RESPONSE'),
        ]:
            with self.subTest(reason=reason):
                status, _, records = self.wire(wire)
                self.assertEqual(status, 502)
                self.assertEqual(records[0]['reason'], reason)

    def test_actual_loopback_oversize_and_upstream_502_preserve_response_bound_and_forwarding(self):
        status, body, records = self.wire(b'HTTP/1.1 200 OK\r\nContent-Length: '+str(gate.MAX_REPLY+1).encode()
                                         +b'\r\n\r\n'+b'x'*(gate.MAX_REPLY+1))
        self.assertEqual(status, 502)
        self.assertLess(len(body), gate.MAX_REPLY)
        self.assertEqual(records[0]['reason'], 'UPSTREAM_RESPONSE_TOO_LARGE')
        status, body, records = self.wire(b'HTTP/1.1 502 Bad Gateway\r\nContent-Length: 2\r\n\r\nok')
        self.assertEqual((status, body), (502, b'ok'))
        self.assertEqual(records[0]['reason'], 'UPSTREAM_HTTP_502')

    def test_truncated_content_length_response_must_not_be_rewritten_as_success(self):
        status, _, records = self.wire(b'HTTP/1.1 200 OK\r\nContent-Length: 30\r\n\r\nshort')
        self.assertEqual(status, 502)
        self.assertEqual(records[0]['reason'], 'UPSTREAM_INCOMPLETE_RESPONSE')
        self.assertEqual(records[0]['response_bytes_observed'], 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
