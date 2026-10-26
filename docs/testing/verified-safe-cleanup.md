# Verified Safe Cleanup - current user policy

Effective user update2026-10-26, adopted at safe postcommit checkpoint
develop0507fc90b63aea8aec3ee32a722a38e25c5d3147. This replaces only the former
read-only cleanup rule11. All LOCKED/security/testing/commit/NO PUSH rules remain.
Do not edit AGENTS.md to implement this user policy.

Cleanup supports substantive development and does not justify an administrative
batch. Audit candidates read-only first at an actual Git/index/worktree/WIP
checkpoint. Delete selectively only tracked files with positive proof of
replacement/obsolescence/no requirement, complete dependency/compatibility review
and relevant full tests. No forced file-count reduction or no-text-hit inference.

| Decision | Meaning | Action |
|---|---|---|
| SAFE_TO_DELETE | Positive replacement/nonnecessity proof plus complete testable dependency/compatibility evidence | May remove exact approved group, then all relevant gates; exact-scope local commit only PASS |
| DEFERRED | Incomplete proof, uncertainty or still required | Preserve |
| PROTECTED | Protected category or preexisting untracked/WIP/secret/history/audit artifact | Preserve; no cleanup deletion |

For each candidate inspect direct/indirect references, dynamic loading/autoload/
reflection/configuration/routes/providers/DI/scripts, firmware/SDK/PlatformIO/
build/linker/board, Laravel/migrations/seeders/fixtures/schema/API/dashboard,
Actions/CI/regression/security/evidence generation, legacy contracts/backward
compatibility/traceability/history. No absence-of-rg-hit proof alone is sufficient.

Deletion-protected categories: LOCKED requirements and baseline contracts, Git
history, historical evidence/audit trails, formal registries/traceability/
verification documents, used schema-history migrations, required regression/
golden/reference fixtures, legacy API/telemetry contracts, AGENTS/instructions,
all secrets/local sensitive configuration, the two protected firmware untracked
files, ALL preexisting untracked files, ALL active uncommitted changes, both
handoffs and continuity information. Never mainDB/app-data cleanup.

No gitclean/hardreset/destructive checkout/forcepush/mass deletion. One clear
dependency group at a time. Before any Windows removal verify the resolved
absolute exact target remains in the intended workspace and is the reviewed
tracked unchanged file. No recursive or broad deletion. Test before/after the
removal; on failure keep evidence/no commit and restore only owned cleanup edits
without overwriting other work. No deletion/staging of protected files.

Every actual removal records path/reason/positive evidence/dependencies/impact/
tests/security/PASS-FAIL-DEFERRED/parent and resulting commit. Changed/deleted
scope and staged bytes require exact review. Commit locally on expected develop
only all mandatory gates PASS. No push or remote/destructive Git operation.

Update BOTH docs/handoff/CODEX_RESUME.md and CHATGPT_CONTEXT.md automatically at
safe checkpoints and after each major committed batch with current HEAD/source/
38requirements/evidence/roadmap/blockers/WIP and this policy, without secrets.
Historical read-only inventories are preserved and are not deletion permission.

At adoption no repository file has been removed. The tracked Laravel welcome
template is still explicitly rendered by root route, so it is DEFERRED/required
at this checkpoint. A related project-entry/UI change must first implement and
verify its replacement and complete reference/compatibility review before any
SAFE_TO_DELETE decision. Preexisting ignored builds/vendor/caches remain protected.

Remaining main priorities: finish safe local software, bugs/integration/security/
consistency/verification. Hardware/hosted CI/deployedTLS and unavailable formal
gates retain explicit NOT_RUN/BLOCKED status. No production-readiness claim.
