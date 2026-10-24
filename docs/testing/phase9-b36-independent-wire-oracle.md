# Phase 9 B36 — independent Python/C99 canonical receipt interoperability

Context: NET-002, TEL-003, SYS-003, SEC-001, TST-001 and TST-002.

B35 uses one C99 encoder and decoder, which could share an undetected
layout/endian assumption. B36 adds a **separate fixed-offset C99 reference**
encoder/decoder and Python's independently implemented `struct`/`zlib.crc32`
oracle for the 72-byte `VG35` format. Independent processes stage checkpoint,
encode wire bytes, decode/check CRC, and compare B34 trusted envelope fields.
26 cross-process cases include one accepted record and 25 denied records,
including rebuilt-CRC data mutations, altered identity/ACK/generation,
wrong endianness, truncated and trailing data, and zero-valued controls.
Denied outcomes must not overwrite caller output or trusted fixture bytes.

This is a **host interop/test-only** batch. CRC32 is noncryptographic; a malicious
party with control of the trusted comparator can forge it. No server ACK,
cryptographic authentication, persistent trusted CAS, concurrent writers,
ESP32/NVS, power-loss durability or formal production closure is demonstrated.
