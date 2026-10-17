# Clean Public Release Archive

Do not distribute a raw copy of the development workspace as the public source
archive. A workspace can contain ignored build products and local metadata such
as `.git`, `.pio`, editor files, generated SDK configuration and caches.

Use the repository helper from a clean tracked worktree:

```bash
bash scripts/create_public_archive.sh "/c/Users/<user>/Downloads/vessel-monitoring-gateway-public.zip"
```

The helper uses `git archive` on the current commit and then runs
`scripts/test_public_archive.py` before keeping the ZIP.

The archive test requires:

- the ZIP file set to match `git ls-files` exactly;
- no `.git`, `.pio`, `.vscode`, `__pycache__`, `node_modules`, `vendor`,
  `.env`, generated `sdkconfig`, `.pyc` or `.pyo` entries;
- no Windows user-profile path leakage in text content;
- no detected private-key headers, GitHub token forms or AWS access-key forms.

The helper prints the source commit, file count, archive size and SHA-256.

This process is a source-archive hygiene control only. Passing it does not
authorize deployment, public release, hardware installation, certification or
production use. Manual semantic review and the repository's security policy
remain applicable.
