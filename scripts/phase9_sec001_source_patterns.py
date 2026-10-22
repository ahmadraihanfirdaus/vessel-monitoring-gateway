#!/usr/bin/env python3
"""SEC-001 narrowly scoped credential scanner; DOES NOT certify the repo secret-free."""
from __future__ import annotations
import re
PATTERNS={
 'PRIVATE_KEY_BEGIN':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 'AWS_ACCESS_KEY':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
 'GITHUB_CLASSIC_TOKEN':re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{24,}\b'),
 'GITHUB_FINEGRAINED_TOKEN':re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{40,}\b'),
 'SLACK_LEGACY_TOKEN':re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{15,}\b'),
}
def classify(data:bytes):
 return sorted(k for k,pattern in PATTERNS.items() if pattern.search(data))
