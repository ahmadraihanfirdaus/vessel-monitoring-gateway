# SUP017 dedicated public reference audit protocol

Parent develop777d762be36f9e778b9dd259476a28d42393e39f. This is the seventh
related acceptance scope of the active fault/storage/software-verification batch,
reviewed BEFORE dedicated SUP017 execution. The six-scope fault/storage protocol
and historical pinned matrix stay unchanged. SUP017 remains a separate prescribed
READ_ONLY_TRACEABILITY_AUDIT case, not inferred from native/DB test successes.

Expected existing case: audit requirement, code, test and evidence references;
every requirement has valid implementation and verification links. Use the
existing living traceability checker and extend its public-path admission/hash
inventory, rather than replacing its LOCKED mapping/status derivation.

Dedicated observations: exactly38LOCKED IDs and original test mappings; all
implementation/evidence paths resolve to regular public files inside the repo;
all34unique planned SIM/SUP IDs resolve to the existing plan and canonical rows;
PASS case rows have valid evidence paths; NOT_RUN/PLANNED cases remain explicitly
unexecuted and link to their verification definitions. No inferred hardware or
semantic-completeness approval. Reject traversal, absolute/foreign paths,
symlinks/junction escapes, sensitive names, missing files, unstable file reads,
duplicate/missing mappings/status mismatch, and fabricated VERIFIED status.

Default invocation is read-only. Explicit --report may create a NEW named JSON
artifact only inside evidence/test-results; refuse existing/foreign/sensitive
output paths. Do not read/hash dotenv, keys, credentials, .git or private folders.
Record parent HEAD, script/protocol/registry hashes, per-requirement mapped links,
file hashes, source/evidence counts and test-definition references, without
copying source/evidence bodies or secrets. No PHP/DB/network bootstrap or writes.

One existing SEC002 source link is backend/laravel/.env.example. Treat ONLY this
exact tracked template as metadata-only presence/regular-file/in-repo/stat proof;
DO NOT open/hash its content or assume it lacks credentials. Report sha256:null
and explicit PROTECTED_TEMPLATE_METADATA_ONLY qualification. Any real dotenv,
secret/key/private-folder link is refused. This exception proves the existing
template link exists, not its values/security. No sensitive content is read.

Positive/negative/path/security tests must PASS, followed by actual dedicated
audit/report and manual requirement/code/test/evidence link review. Existing
LOCKED hashes and source/status checker rules stay authoritative. Only actual
case execution/review plus mandatory local batch gates may promote SUP017 and
derived TST001 formal status. No requirement VERIFIED; partial implementation and
unperformed hardware/hostedCI/deployedTLS remain explicit. Both handoffs update.
No cleanup scope, remote interaction, main DB operation or push.

PROTOCOL_CASE_REVIEW=PASS_SUP017_READ_ONLY_PUBLIC_REFERENCE_AUDIT
EXECUTION=NOT_RUN_AT_PROTOCOL_CREATION
