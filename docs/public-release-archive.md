# Clean Public Release Archive

Do not distribute a raw copy of the development workspace as the public source
archive. A workspace can contain ignored build products and local metadata such
as `.git`, `.pio`, editor files, generated SDK configuration and caches.

Use the existing helper from a clean tracked worktree and index. First inspect
the metadata-only plan (no blob contents read and no output created):

```bash
python -B scripts/create_public_archive.py "<absolute-existing-directory-outside-repository>/new-audit.zip"
```

After reviewing the source/security gates, explicitly create a NEW local ZIP:

```bash
python -B scripts/create_public_archive.py "<absolute-existing-directory-outside-repository>/new-audit.zip" --execute
# Bash compatibility entry; delegates to the same cross-platform policy:
bash scripts/create_public_archive.sh "<absolute-existing-directory-outside-repository>/new-audit.zip" --execute
```

The parent output directory must already exist, must not be linked, and must be
outside the source repository. Existing output and neighboring temporary files
are never overwritten, renamed or deleted. An interrupted or rejected own output
is retained and is not reported successful; choose a fresh path on the next run.
No workspace file is removed or changed by packaging.

Only the current committed HEAD is exported, with admitted regular-file metadata
and immutable Git blobs. Working changes, ignored files, untracked files and Git
history/metadata are not copied. Execution refuses tracked/index changes and
unexpected untracked files. The exact protected untracked AGENTS.md and two
firmware files may remain; they are never included. The plan alone is available
with WIP and explicitly does not claim to capture it.

Filtering happens BEFORE any excluded blob content or size is requested. All
dotenv names, including tracked `.env.example`, are deliberately excluded. This
is a filtered review snapshot, not an exact Git clone, workspace backup or a
deployable package. Configuration templates must be obtained through a separately
reviewed process when needed; this tool never opens them to infer that they lack
secrets. The committed `firmware/sdkconfig.defaults` source is retained; generated
`sdkconfig` and other generated variants are excluded. No TLS setting is changed.

The initial real-commit payload review also identified machine-profile paths in
seven historical blobs, including previous handoff versions. Exact path/blob-ID
pins omit only those versions from the public snapshot and report each omission
and reason. Historical evidence stays unchanged locally. Current handoffs replace
machine-profile prefixes with `<LOCAL_HOME>`; safe changed versions are included
normally. An unknown or changed blob receives the full ordinary scan and is not
covered by an old omission pin. No content detector is waived. This is deliberately
a filtered disclosure view; omitted originals remain available for authorized
local audit and are not represented as included.

The archive test requires:

- the ZIP file set and every blob hash/length to match the filtered committed
  snapshot, with exclusions reported separately;
- no `.git`, `.pio`, `.vscode`, `__pycache__`, `node_modules`, `vendor`,
  `.env*`, private configuration/key paths, generated `sdkconfig`, `.pyc` or `.pyo` entries;
- no Windows user-profile path leakage in text content;
- no detected private-key headers, GitHub token forms or AWS access-key forms.

It also refuses traversal/noncanonical/Windows-device paths, duplicate or case
collisions, links/special modes/encrypted entries, missing/extra files, changed
blobs and excessive entries/sizes. Directory payloads, comments, extra fields and ambiguous/NUL-truncated names are
refused as non-source metadata. Forbidden metadata for the entire ZIP is
rejected before any member body is opened. Limits are 8,192 files, 8,000,000 bytes
per file and 128,000,000 bytes total. Binary/NUL files and large entries are never
silently skipped. A source-HEAD or clean-state change prevents a success result.

The helper prints the source commit, file count, archive size and SHA-256.

`scripts/test_public_archive_safety.py` uses fresh isolated synthetic Git/ZIP
fixtures to test positive, negative, boundary, no-clobber, metadata-before-content
and race behavior. Existing scanner regressions remain. The PR workflow source
registers these checks; this does not establish actual hosted CI or SUP-018 PASS.

Earlier implementation required exact tracked parity while rejecting the tracked
dotenv template and `sdkconfig.defaults`, making that contract unsatisfiable. It
also used forced temporary-file removal/output replacement. The 2026-10-27
continuation repairs these tooling defects without reading dotenv values or
altering LOCKED requirements, firmware behavior, application code or test DB data.

This process is a source-archive hygiene control only. Passing it does not
authorize deployment, public release, hardware installation, certification or
production use. Manual semantic review and the repository's security policy
remain applicable.
