# ESP32 transport software integration

This continuation starts at local `develop` commit
`bd34639940fff98461cf0e12cbf7e2e76c6664ce`. It connects existing contracts to
ESP-IDF APIs and the finite simulation runtime. It does not change the LOCKED
requirements, authorize hardware installation or establish formal verification.

## Configuration and security

The SDK adapter reads the external NVS namespace `vgw_net` in read-only mode.
Required keys are strings `ssid`, `wifi_pass`, `origin`, `bearer`, `device` and
unsigned 32-bit `timeout_ms`, `backoff_ms`, `attempts`. There is no embedded
credential, provisioning writer, automatic NVS erase or assumed operational
timeout. An absent profile leaves the local simulation running without network.
Partial, oversized or invalid configuration fails closed. Never put a provisioned
NVS image or its contents in Git or evidence.
The candidate build does not enable flash encryption; confidential NVS
provisioning/key storage on physical hardware is still an open security gate.
The generated simulator image contains blank NVS and no provisioned secrets.

The supported Wi-Fi profile uses WPA2 or stronger with an 8–63-byte passphrase;
raw 64-character PSKs and open networks are unsupported. The client requires
exclusive ownership of an uninitialized Wi-Fi driver and uses RAM Wi-Fi storage.
The HTTPS origin admits an authority and optional final slash only. Userinfo,
paths, queries, fragments and control characters are rejected. Endpoint paths
are fixed to the existing telemetry/event APIs. Credentials are not logged.

TLS uses the SDK certificate bundle and hostname verification, with redirects
and automatic authentication retries disabled. `sdkconfig.defaults` enables
certificate validity-date checks, which ESP-IDF otherwise disables by default.
The adapter and build gate reject insecure/skip-verification configurations.
An existing generated SDK configuration must also enable these settings; defaults
do not override an already generated configuration. The local ignored SDK
configuration was corrected accordingly. No certificate dates or system times
are fabricated: a trustworthy wall clock is an external prerequisite. There is
no clock-provisioning protocol in this slice. Real TLS handshakes remain NOT_RUN.

## Scheduling, bounds and failure behavior

One dedicated FreeRTOS worker owns actual asynchronous HTTPS calls and the
existing reconnect state machine. Submission uses a zero-wait mutex and a
zero-wait one-item queue; completion retrieval is also nonblocking. Queue pressure
returns failure to the caller. Only the worker waits for a completion consumer.
Payload storage is heap-owned, not a 4 KiB acquisition-stack object.

Limits are 4,096 body bytes, 512 reply bytes, 32–256 bearer characters,
1–48 device characters, policy intervals no greater than 60,000 ms and no more
than 16 attempts. These are resource limits, not vessel performance thresholds.
The worker checks elapsed monotonic time between SDK asynchronous polls.
Individual SDK/DNS call latency and a hard end-to-end deadline are unverified.
408/429/5xx and incomplete exchanges may retry within the configured attempt
bound and backoff; redirects, authentication/schema/conflict errors, response
overflow or exhaustion halt further submissions until explicit local reset.
Server Retry-After interpretation is not implemented.

HTTP 200/201 completion is only a transport fact. No application receipt is
acknowledged and no journal entry or retained state is deleted. The finite demo
keeps only the latest serialized frame in volatile RAM; its existing critical
journal also remains volatile. This does not satisfy durable NET-002 storage.
The source is explicitly SIMULATION and carries no physical control output.

## Integration and resource evidence

The finite six-step core runtime uses the shared serializer helper. Its actual
C99 bytes cross the real Laravel kernel and approved isolated MariaDB database,
then appear through a granted browser view. A colon-containing device ID exposed
a web-route mismatch with the existing wire contract; the route now accepts the
same character set. Missing/invalid samples remain null and a valid zero remains
zero. This kernel/HTML test is not a TCP browser or deployed TLS test.

The build uses the existing 1 MiB factory partition. Optimization of the new
networking dependency code retains assertions and the full root bundle. Early
oversize images are retained as failures in evidence. Large test-only automatic
fixtures moved to reset static scratch; two executions of the same boot entry
now pass the same 226 core cases each. These are not 452 distinct cases.
Compiler stack frames are checked separately from full-call-chain/device stack
watermarks and heap behavior, which remain NOT_RUN.

The build helper refuses overwriting evidence and rejects source mutation during
build. It checks the actual factory partition, application size and TLS settings,
then merges actual bootloader/partition/application outputs offline. It checks
the application slice and blank NVS region. The SDK-configured simulator flash
size does not establish physical flash capacity. It never uploads or erases.

Use `scripts/test_esp32_network_port.py` and `scripts/test_esp32_build_gate.py`
for local admission/security/build-evidence tests. Use
`scripts/build_esp32_port.py --evidence-name esp32-transport-sdk-build-<run>.txt`
with the installed PlatformIO CLI for an SDK build. The real backend gate remains
`scripts/run_mysql_integration.py` with explicit PHP 8.2.35 and the approved test
profile. See the dated execution summary for commands and actual outcomes.

Hosted CI, Wokwi execution of this image, physical ESP32 Wi-Fi/TLS, trusted-clock
integration, NVS provisioning/confidentiality, power-loss durability, full stack
and heap measurements, SIM-010..015 and remaining SUP protocols remain NOT_RUN.
Overall system status remains PARTIAL and final approval remains NOT_APPROVED.
