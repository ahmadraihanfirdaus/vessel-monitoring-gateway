# Docker inspect formatter and subprocess isolation

Published parent: `090ccccc8796c65659b0dc6af83f1061591c67d3` (148 commits).
Run [40555976413](https://github.com/ahmadraihanfirdaus/vessel-monitoring-gateway/actions/runs/40555976413)
proves DOCKER_INSPECT_FAILED before JSON parsing/UUID/PDO/migration/fixture access.
Runner exit3 is NOT the Docker child exit. The latter and actual Binds are unknown.
One forwarded64hex container ID matches cleanup;the workflow passes the official
`${{ job.services.mysql.id }}` through both guarded step environments.

## Exact contract and causality

Actual argv is a six-element Symfony Process array:
`["docker","--host=unix:///var/run/docker.sock","inspect","--format",TEMPLATE,ID]`.
TEMPLATE is the selected-fields string in HostedMySqlService.php,one argument;
ID must be64lowerhex. No caller shell composition or full inspect/environment dump.
The executable token is resolved by PATH;resolved private paths are not logged.
Symfony inherits process environment by default;this is not a claim that every
hosted variable was logged or verified. Explicit host stays the local Unix socket;
context rejects DOCKER_HOST/CONTEXT/TLS_VERIFY/CERT_PATH overrides. Workflow/job/
event/Linux/runner/service proof precede real database admission.

5s Process timeout,8192-byte stdout bound,successful child exit andtrim are retained.
Success must subsequently decode to one JSON object;the default unformatted inspect
array,empty/truncated/malformed output andincorrect properties fail closed. The
command may return empty stdout at child exit0;the following JSON gate rejects it.
Actual daemon executable/connection/proc_open failures cannot be inferred from
the old runner exit3 or the newly confirmed fixture bug.

Official [Docker CLI inspector source](https://github.com/docker/cli/blob/v28.0.4/cli/command/inspect/inspector.go)
tries typed template execution andcan fall back to JSON decoding with missingkey
errors. The published `.Id` selection triggers fallback for the synthetic typed
response;`len .HostConfig.Binds` then fails onnull. Official CLI28.0.4 was executed
locally against a fixed owned API,without Docker daemon or database. The exact
old template hash is pinned by the negative oracle. Null yields child1/template
len error;empty array yields child0/object/binds0. The null-safe conditional is
the only formatter change. It preserves counts for nonempty binds;the PHP bind
policy remainsstrict0. Missing property andmalformed scalar/object types reject.
This proves a local formatter defect,not that hosted Binds wasnull. Hosted root
cause remains UNKNOWN until a new approved verification provides matching proof.

## Subprocess diagnostic contract

Only failures of the actual inspect command emit one bounded JSON record prefixed
MYSQL_INSPECT_DIAGNOSTIC. Its class is one of EXECUTABLE_NOT_FOUND,
PROC_OPEN_UNAVAILABLE,PROCESS_START_EXCEPTION,PROCESS_RUNTIME_EXCEPTION,
DAEMON_UNREACHABLE,CONTAINER_NOT_FOUND,TEMPLATE_NIL_LENGTH,TEMPLATE_ERROR,TIMEOUT,
CHILD_NONZERO,OUTPUT_LIMIT. Raw child stderr may be classified in memory by fixed
signatures;unrecognized nonzero staysCHILD_NONZERO. These classifications never
authorize a target. Exceptions remain unchained andprimary DOCKER_INSPECT_FAILED
is retained. Safe metadata:fixed phase,numeric nullable child exit,elapsed capped
at10000ms,stdout observation capped8193,booleans and8192limit. Counts are not content.
No stderr,environment,credentials,URL,path,body,argv or memory is recorded.

## Verification and next step

13real CLI/PHP owned-API tests;112focused PHP cases;465actual isolated MariaDB
cases;303no-DB cases PASS/0FAIL/0SKIP. 234pure policy comparisons have0acceptance
differences. New real child tests cover exit7versusrunner3,missing executable,
disabled proc_open,stderr classifications,timeout andexact/over output bounds.
Start/runtime exception types are deterministically classified without forcing
resource exhaustion. Windows timeout fixture was reduced15to7seconds to remain
above real5s andfit unchanged10s outer supervisor;the policy timeout did not change.
Independent actual daemon/Linux process-launch behavior remains NOT_RUN locally.
Both YAML/actionlint PASS andthe new formatter test runs before hostedDB admission.
No production code,locked baseline,allowed target,UUID,ACK,lease/device ownership,
metadata,receipt orretry contract is weakened. No firmware/hardware changes.

Before publication:verify exact scoped manifest/security/Git evidence,clean branch
portfolio,current main equals parent andfast-forward. Only new user approval may
publish andrun hosted CI. If failure recurs,the bounded diagnostic distinguishes
the child boundary inone run. Do not infer causal SIGSEGV/disconnect orproduction
readiness. Physical ESP32,NVS/RTOS,deployedTLS andship trials remain NOT_RUN.
