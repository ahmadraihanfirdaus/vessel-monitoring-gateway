"""Independent native/functional contract oracles. No database or network access."""
import hashlib
from html.parser import HTMLParser
import json
import math
import re

SECTIONS = ('Overview', 'Safety', 'Propulsion', 'Navigation', 'Power',
            'Alarms and Events', 'Device Health', 'Test Evidence')
IDENTITY = ('schema_version', 'device_id', 'firmware_version', 'boot_id',
            'sequence', 'uptime_ms', 'source_mode', 'channels')
SECTION_MARKERS = {
    'Overview': ('Schema 1.1', 'sequence 24', 'engine_4_rpm'),
    'Safety': ('bilge_state', 'vapor_surrogate', 'Quality'),
    'Propulsion': ('engine_1_rpm', 'engine_4_rpm', 'RUNNING'),
    'Navigation': ('nav_', 'Quality'), 'Power': ('power_', 'Quality'),
    'Alarms and Events': ('ACK bukan CLEAR', 'alarm_ack', 'alarm_cleared'),
    'Device Health': ('Last server receipt', 'High-water boot / sequence', 'simulation'),
    'Test Evidence': ('PARTIAL', 'NOT_APPROVED', 'NOT_RUN'),
}
PROVENANCE_MARKERS = ('runtime:demo', 'SIMULATION', 'LIVE', 'read-only',
    'Waktu penerimaan server bukan waktu global pengukuran',
    'unitless surrogate; not ppm or %LEL', 'low-power prototype')


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('DUPLICATE_FIELD')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE')))


def native_contract(raw):
    """Check actual native wire BEFORE any test database fixture is prepared."""
    if not isinstance(raw, bytes) or not raw or len(raw) > 128 * 1024:
        raise ValueError('BOUNDED_NATIVE_WIRE_REQUIRED')
    lines = raw.splitlines()
    if not 1 <= len(lines) <= 64:
        raise ValueError('NATIVE_FRAME_COUNT')
    observations = {'frames': len(lines), 'valid_zero': 0, 'unavailable': 0,
                    'stale': 0, 'channels': 0, 'wire_sha256': hashlib.sha256(raw).hexdigest()}
    previous = {}
    for line in lines:
        if not 0 < len(line) <= 4096:
            raise ValueError('WIRE_BOUND')
        packet = strict_json(line)
        if not isinstance(packet, dict) or set(packet) != set(IDENTITY):
            raise ValueError('REQUIRED_NATIVE_FIELDS')
        if packet['schema_version'] not in ('1.0', '1.1') or packet['source_mode'] != 'simulation':
            raise ValueError('NATIVE_SCHEMA_OR_PROVENANCE')
        for name in ('device_id', 'boot_id', 'firmware_version'):
            if not isinstance(packet[name], str) or not re.fullmatch(r'[A-Za-z0-9._:-]{1,48}', packet[name]):
                raise ValueError('IDENTITY_BOUND')
        for name in ('sequence', 'uptime_ms'):
            value = packet[name]
            if type(value) is not int or not 0 <= value <= 2**64 - 1 or (name == 'sequence' and value == 0):
                raise ValueError('UINT64_REQUIRED')
        identity = (packet['device_id'], packet['boot_id'])
        if identity in previous and packet['sequence'] <= previous[identity]:
            raise ValueError('NATIVE_SEQUENCE_NOT_INCREASING')
        previous[identity] = packet['sequence']
        channels = packet['channels']
        limit = 16 if packet['schema_version'] == '1.0' else 72
        if not isinstance(channels, dict) or not 1 <= len(channels) <= limit:
            raise ValueError('CHANNEL_COUNT')
        for name, channel in channels.items():
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,31}', name) or not isinstance(channel, dict):
                raise ValueError('CHANNEL_IDENTITY')
            if set(channel) != {'value', 'quality'}:
                raise ValueError('QUALITY_VALUE_REQUIRED')
            quality, value = channel['quality'], channel['value']
            try:
                finite = type(value) in (float, int) and math.isfinite(value)
            except OverflowError:
                finite = False
            if quality == 'valid':
                if not finite:
                    raise ValueError('VALID_VALUE_REQUIRED')
                observations['valid_zero'] += value == 0
            elif quality in ('invalid', 'missing', 'unknown'):
                if value is not None:
                    raise ValueError('UNAVAILABLE_MUST_BE_NULL')
                observations['unavailable'] += 1
            elif quality == 'stale':
                if value is not None and not finite:
                    raise ValueError('STALE_VALUE_BOUND')
                observations['stale'] += 1
            else:
                raise ValueError('QUALITY_UNKNOWN_LABEL')
            observations['channels'] += 1
    return observations


class Sections(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.counts = {name: 0 for name in SECTIONS}
        self.stack = []
        self.text = {name: [] for name in SECTIONS}

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            labels = [value for key, value in attrs if key == 'aria-label']
            if len(labels) > 1:
                raise ValueError('DUPLICATE_SECTION_LABEL')
            label = labels[0] if labels else None
            self.stack.append(label)
            if label in self.counts:
                self.counts[label] += 1

    def handle_endtag(self, tag):
        if tag == 'section':
            if not self.stack:
                raise ValueError('UNBALANCED_SECTION')
            self.stack.pop()

    def handle_data(self, text):
        for label in self.stack:
            if label in self.text:
                self.text[label].append(text)


def functional_observation(status, body):
    if status != 200 or not isinstance(body, bytes) or not 0 < len(body) <= 1024 * 1024:
        raise ValueError('FUNCTIONAL_RESPONSE_REQUIRED')
    parser = Sections()
    parser.feed(body.decode('utf-8', errors='strict'))
    parser.close()
    if parser.stack or any(count != 1 for count in parser.counts.values()):
        raise ValueError('EXACT_EIGHT_SECTIONS_REQUIRED')
    # Dedicated native continuous profile, not an arbitrary page containing labels.
    text = {name: ' '.join(' '.join(parts).split()) for name, parts in parser.text.items()}
    markers = {name: {marker: marker in text[name] for marker in values}
               for name, values in SECTION_MARKERS.items()}
    if not all(all(values.values()) for values in markers.values()):
        raise ValueError('SECTION_DATA_NOT_CONNECTED')
    global_markers = {marker: marker.encode() in body for marker in PROVENANCE_MARKERS}
    if not all(global_markers.values()):
        raise ValueError('PROVENANCE_OR_FRESHNESS_MISSING')
    # No raw HTML, cookies, CSRF inputs, location or measurement values retained.
    return {'status': status, 'body_sha256': hashlib.sha256(body).hexdigest(),
            'section_counts': parser.counts, 'section_markers': markers,
            'provenance_markers': global_markers}
