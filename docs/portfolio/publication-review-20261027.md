# GitHub portfolio publication review - 2026-10-27

Decision: **SANITIZED_HISTORY_READY_FOR_APPROVAL**, conditional on the final
isolated build receipt and independent review described below. This is local
preparation only. **No publication, push, force push, remote merge, default-branch
change or replacement of an existing public history is authorized or performed.**

## Authoritative source and scope

The audited implementation checkpoint is `develop` at
`cf2044a69a9f7a71410f91236758de19c78c1537`, following software audit `be6bad7`.
The original repository has 137 reachable commits at that checkpoint, 1,599
historical paths and 2,071 admitted unique blobs (2,091 path/blob versions).
Every reachable commit/tree and commit message/identity was inspected. Deleted
content is included by walking every complete tree, not only current files.
The only historical prohibited filename is `backend/laravel/.env.example`;
its contents were deliberately not read, hashed or copied. An excluded object
is not treated as security-verified. No actual local dotenv file is accessed.

Current `main` and cached `origin/main` have two commits locally. Remote
visibility/default/fork/account settings were initially not queried by the local
inventory. A later read-only official public web observation displays
Public/main/2 commits; it does not inspect account email association or API
administrative/fork settings. Cached refs alone do not establish GitHub state.
The original `origin` configuration is left unchanged. Only the selected source
tip and all its ancestors belong to the candidate; no incidental Codex refs,
other branch refs, reflogs, notes, credentials or original object database are
cloned into it.

The genuine portfolio preparation commit follows that 137-commit checkpoint.
Its owner hash is obtained with Git instead of embedding its own self-hash in
the files it commits. The final isolated candidate must include this commit,
not merely the initial 137-commit candidate.

## Security findings and dispositions

| Finding | Evidence / severity | Disposition |
|---|---|---|
| 26 historical blob versions contain concrete local profile prefixes | Moderate privacy risk; 8 paths across historical handoffs, five execution logs and an early scanner fixture | Redact prefixes only in candidate document/log copies; replace early scanner input with runtime-joined synthetic profile components. Original blobs/evidence untouched. |
| 82 historical assignment matches in 45 workflow versions | Low / false positives after contextual review: current exact-pinned ephemeral database fixture lines and a deterministic repeated-byte testing key | Retain as synthetic CI-only configuration; exact path/blob/file/line hash reviews recorded. No values copied into this report. Never deploy these test fixtures. |
| One environment-template path in historical trees | Publication-policy exclusion; contents intentionally UNKNOWN | Omit from every candidate tree. This is not proof that a real secret existed in the file. |
| Commit identity/message screening | No unresolved content findings; one GitHub noreply identity across all 137 original commits | Retain raw author and committer identities, timestamps, timezone offsets and message bytes. Account association remains independently unverified. |
| High-confidence token/private-key/URL-credential screening | No unresolved matches in admitted historical content under the documented detectors | No claim of exhaustive confidentiality; independent semantic review remains required before publication. |

The initial audit report predates the added escaped-backslash coverage and
historical non-secret reviews; it is retained as an initial observation, not the
final result. The reviewed history audit includes raw/escaped Windows profiles
and POSIX home profiles. Existing token/key/assignment/bearer/coordinate/email
checks and exact non-secret dependency metadata reviews are reused. Private
keys/tokens/profile paths cannot be waived by the CI assignment registry.

Review records apply only to exact historical workflow content. A changed blob
or line invalidates the review. Arbitrary secret matches are not labelled
synthetic merely because they occur in a test directory. Unknown binary,
encoding, size, shallow history, replacement/grafted history, special entries,
unreviewed code privacy and shared forbidden blob cases fail closed.

## Objective comparison

| Option | Security | Git integrity and portfolio readability | Contribution potential |
|---|---|---|---|
| A - PRESERVE_AUTHENTIC_HISTORY | **Not ready**: original history retains profile paths and the prohibited template | All original hashes/signatures/content remain, but public disclosure is not justified | Original 137 commits / 14 author dates, conditional on GitHub eligibility; security prevents this option now |
| B - SANITIZED_HISTORY_CANDIDATE | Recommended: independent clean bare repository built only from inspected admitted bytes; all candidate history re-audited | All 137 original commits kept one-for-one; first 43 hashes unchanged, later 94 rewritten at baseline. Exact identities/dates/messages/topology retained. Old-to-new mapping makes redactions explicit. A real preparation commit is also preserved in the final candidate. | Historical dates retained; up to 137 baseline commit contributions over 14 dates if all eligibility conditions hold, plus genuine preparation work. No artificial activity |
| C - CLEAN_PUBLIC_SNAPSHOT | Available fallback using the existing filtered archive tooling; newest source still requires its own review | Simple current code view but loses actual Git progression. Existing archive of `be6bad7` is not the newest prepared portfolio. A new snapshot would need an honest chronology and actual new publication commit | One genuine initial snapshot commit, not the 137 historical commits; no historical graph reconstruction |

No snapshot was selected just for convenience. The sanitized candidate preserves
the authentic development sequence while disclosing that changed trees and
descendants necessarily receive new hashes. It is not byte-identical original
Git history and is not tamper-proof independent proof of historical activity.
Original evidence references retain original local commit identifiers; use the
mapping for public candidate identifiers. Redacted log copies cannot be checked
against original file hashes as if unchanged. Original hashes remain source
provenance, and the mapping records candidate hashes separately. No author or
date was invented, normalized, backdated or replaced. Existing one-commit
author/committer timestamp difference is preserved. No signed/extended commit
headers were silently discarded; unsupported signed metadata blocks the builder.

## Initial candidate and actual demonstration

The initial isolated candidate tip is
`431621325f58277b69681db066ee98d13bbe1ca0`, from source `cf2044a`, with all 137
commits retained. Its full candidate history audit PASS is stored with the
old/new mapping. It contains no remote and no copied original object database.

An initial materialized candidate run passed native core 226/226 repeated twice
and the 24-frame wire fixture, then failed traceability because SEC-002 still
referenced the omitted template. This **FAIL is preserved**. The correction
updates only the editable implementation-path reference to the actual external
key-loading source `backend/laravel/config/app.php`, and aligns both handoff
38-row tables. No LOCKED text/mapping, assessment, formal status or validator
rule is changed. The corrected candidate projection and final actual candidate
must pass the unchanged traceability validator before approval readiness.

The focused reference test initially also failed its stale expectation of one
metadata-only template in the current inventory. Its oracle now requires all
current references to have public content hashes and SEC-002 to include the
actual key loader, excluding the template. The dedicated template metadata-only
and all negative reference tests remain. All 12 reference tests then PASS; the
initial failed run is preserved alongside the correction, not overwritten.

The final prepared English README explains the real architecture, problem,
technology, native demo, evidence, historical bug fixes, limitations and
AI-assisted development. No invented screenshot, vessel installation, hardware
experience, employer affiliation or certification is added. The no-hardware
quick start executes real C99 fixtures, not a mock screenshot or supplied
application account. See [the demo guide](local-demo.md).

## GitHub contributions: conditional, not promised

At source `cf2044a`: **137 commits, 14 distinct original author dates** from
2026-10-10 through 2026-10-27, no merges and no empty commits. There is one public
GitHub noreply identity; evidence records its hash rather than reproducing the
address. One pre-existing author/committer timestamp difference remains intact.

The conditional upper bound is 137 eligible commit contributions over 14 author
dates, not 137 green cells and not necessarily 14 new cells. The real preparation
commit adds actual work on its real date; it does not manufacture another day.
**Existing visible green cells, existing contribution overlap, actual eligible
count and incremental new cells are NOT_VERIFIED.** Publishing a non-default
branch alone does not establish eligibility. No zero or guaranteed graph total
is substituted for unknown account state.

The [official public profile](https://github.com/ahmadraihanfirdaus) returned an
error while loading contribution content, and the date-filtered page could not
be fetched. Therefore an existing green-cell count is unavailable, not zero.
The [public repository root](https://github.com/ahmadraihanfirdaus/vessel-monitoring-gateway)
displays Public/main/2 commits, consistent with the cached local main branch.
No authenticated settings, Git network operation or GitHub mutation was used.

GitHub requires associated commit email, a standalone/non-fork repository,
default-branch or qualifying gh-pages reachability, and an eligible relationship
to the repository. The profile uses the original author date/timezone, which is
why the candidate preserves those fields. These are current documented rules,
not verified account settings. [GitHub contribution criteria and dates](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference).

A future **new standalone repository**, reviewed and explicitly approved by the
owner, avoids replacing existing public history. Another possibility is a new
review branch in the existing repository; contribution reachability and default
branch policy would need a separate owner decision. Neither destination is
created/configured by this task. Never force-push or silently change the existing
default branch to obtain contributions.

## Evidence and gates

- [Original history inventory](../../evidence/test-results/portfolio-original-history-audit-20261027.json): initial scan, findings intentionally retained.
- [Reviewed full original history](../../evidence/test-results/portfolio-reviewed-history-audit-20261027.json): 137 commits, complete-tree scan, escaped profiles, exact historical non-secret dispositions.
- [Initial sanitized candidate, mapping and full audit](../../evidence/test-results/portfolio-sanitized-baseline-20261027.json).
- [Contribution inventory and unverified conditions](../../evidence/test-results/portfolio-contributions-20261027.json).
- [Later official public GitHub observation](../../evidence/test-results/portfolio-github-public-observation-20261027.json): Public/main/2 commits; contribution graph unavailable, account association unverified.
- [Initial demo failure retained](../../evidence/test-results/portfolio-candidate-demo-20261027.json).
- [Corrected projection demo](../../evidence/test-results/portfolio-candidate-demo-corrected-20261027.json).
- [Focused tooling/security dependency tests](../../evidence/test-results/portfolio-tooling-gates-20261027.json).
- [Reference test correction](../../evidence/test-results/portfolio-tooling-correction-20261027.json): 12 PASS after the initial stale-oracle failure; the other focused suites retain 11/23/18/6 PASS.
- [Final history boundary tests](../../evidence/test-results/portfolio-history-boundaries-20261027.json): 12 history methods PASS, adding explicit commit/blob/aggregate size limits to the prior 11-method run.
- [Current source reference inventory](../../evidence/test-results/portfolio-reference-final-20261027.json).
- [Unchanged runtime and protected-source bindings](../../evidence/test-results/portfolio-source-bindings-20261027.json).
- [Working-content security screen](../../evidence/test-results/portfolio-working-security-20261027.txt): zero findings/warnings at that point; the exact final staged content requires its own final screen before commit.
- [Preparation scope and gate review](../../evidence/test-results/portfolio-preparation-review-20261027.json): both 38-row handoffs, unchanged source bindings/protected files and retained ZIP hash.
- [Exact source preparation file manifest](../../evidence/test-results/portfolio-preparation-files-20261027.csv).

The final build is performed from the actual committed preparation HEAD after
all mandatory local preparation gates pass. Its full receipt is deliberately
kept outside the public source, at
`private/portfolio-history-final-receipt-20261027.json`, beside the isolated bare
repository `private/portfolio-history-final-20261027/`. Inspect that receipt for
the final source/candidate hashes, complete mapping, actual final history scan,
identity/date/message/topology and strict object integrity gates. It is not
enough that the earlier 137-commit candidate passed. A missing or failed final
receipt means **PUBLICATION_BLOCKED**, regardless of the planned status above.

PHP/Laravel/MariaDB/TLS/browser/SDK evidence is retained with its source binding;
these suites are not rerun for documentation-only, reference-only and isolated
publication tooling changes. No firmware/backend runtime, dependency lock,
schema, migrations or physical behavior is changed. Current workflow source
does not prove hosted CI execution. Hardware/RTOS/NVS/power-loss/deployed TLS,
hosted CI, additional static/sanitizer coverage and final acceptance remain
NOT_RUN/BLOCKED within their documented scopes. System PARTIAL / NOT_APPROVED.

## Independent ChatGPT audit prompt

> Review this local publication preparation before any upload. Treat actual Git
> HEAD, the exact file manifest, reviewed original history report and final
> isolated receipt as authoritative. Compare every mapped commit's raw author,
> committer, timestamps, timezone, message and parents; compare candidate trees
> against the declared dotenv omission/profile-only transformations. Confirm
> all candidate reachable content and object integrity were checked, with no
> original unsafe refs, logs or object database copied. Verify the corrected
> traceability/native demo, preserved failed attempt, exact historical CI
> reviews, current README claims and all remaining NOT_RUN qualifications.
> Distinguish 137 baseline commits/14 dates from final preparation work and
> unknown existing GitHub green cells. Do not assume email association, remote
> visibility/default branch or eligibility. Do not expose secret values, change
> LOCKED requirements, change original history, delete evidence, run a normal
> database, fabricate activity, push, publish or change the default branch.
> Return READY_FOR_APPROVAL only if the final actual receipt and all mandatory
> gates support it; otherwise return PUBLICATION_BLOCKED with concrete reasons.
