from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

MAX_TEXT_BYTES = 5 * 1024 * 1024

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".csv", ".json",
    ".jsonl", ".yaml", ".yml", ".toml",
    ".ini", ".php", ".js", ".ts", ".html",
    ".css", ".xml", ".svg", ".sh", ".c", ".h",
}

TEXT_FILENAMES = {
    ".gitignore",
    ".gitattributes",
    ".gitkeep",
    "LICENSE",
    "CHANGELOG",
    "README",
}

SENSITIVE_NAMES = {
    ".env",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
    "secrets.json",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "known_hosts.private",
}

SENSITIVE_EXTENSIONS = {
    ".pem", ".key", ".p12", ".pfx",
    ".sqlite", ".sqlite3", ".db", ".sql",
}

ALLOWED_ENV_TEMPLATES = {
    ".env.example",
    ".env.testing.example",
}

# Exact internal or historical artifacts are prohibited
# even when Git's ignore rules are bypassed.
BLOCKED_PATHS = {
    # Internal FIX blueprint
    "docs/architecture/engineering-blueprint-v1.0.docx",
    "docs/architecture/engineering-blueprint-v1.0.md",

    # Temporary public candidates and historical matrices
    "requirements/system-requirements.public-candidate.md",
    "requirements/traceability-matrix.public-candidate.csv",
    "requirements/traceability-matrix.proposed.csv",
    "requirements/traceability-matrix.v1-snapshot.csv",
    "requirements/traceability-matrix.v2-candidate.csv",

    # Internal requirements and traceability workflow
    "scripts/archive_private_requirements.py",
    "scripts/audit_combined_coverage.py",
    "scripts/audit_public_traceability_candidate.py",
    "scripts/audit_traceability.py",
    "scripts/audit_traceability_candidate.py",
    "scripts/build_public_requirements_candidate.py",
    "scripts/build_public_traceability_candidate.py",
    "scripts/build_traceability_candidate.py",
    "scripts/generate_traceability.py",
    "scripts/map_traceability_tests.py",
    "scripts/plan_supplemental_tests.py",
    "scripts/promote_traceability.py",

    # Internal blueprint and DOCX inspection utilities
    "scripts/isolate_internal_blueprint.py",
    "scripts/audit_docx_package.py",
    "scripts/audit_docx_privacy.py",
}

BLOCKED_DIRECTORIES = (
    "docs/internal/",
    "requirements/internal/",
    "evidence/private/",
    "secrets/",
    "credentials/",
    ".ssh/",
    ".aws/",
)

# Signature screening is intentionally conservative. It is not a
# replacement for a dedicated secret scanner or manual review.
TOKEN_PATTERN = re.compile(
    r"(?:"
    r"gh[oprsu]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"(?:AKIA|ASIA)[A-Z0-9]{16}|"
    r"AIza[0-9A-Za-z_-]{30,}|"
    r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}|"
    r"xox[baprs]-[A-Za-z0-9-]{16,}"
    r")"
)

PRIVATE_KEY_PATTERN = re.compile(
    r"-{5}BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-{5}"
)

# Accept common names such as DB_PASSWORD, AWS_SECRET_ACCESS_KEY,
# API_KEY, JWT_SECRET, as well as quoted JSON keys.
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    (?<![\w.-])
    [\"']?
    (?P<key>(?:[a-z][a-z0-9]*[_-])*
      (?:api[_-]?key|access[_-]?token|auth[_-]?token|
         client[_-]?secret|secret[_-]?access[_-]?key|
         secret[_-]?key|password|passwd|pwd|jwt[_-]?secret|
         private[_-]?key|github[_-]?token|app[_-]?key))
    [\"']?
    \s*[:=]\s*
    (?P<value>
      \"(?:\\.|[^\"\\\r\n])*\"|
      '(?:\\.|[^'\\\r\n])*'|
      [^\s#;,]+
    )
    """
)

BEARER_PATTERN = re.compile(
    r"(?i)\bauthorization\s*[:=]\s*[\"']?bearer\s+"
    r"(?P<value>[A-Za-z0-9._~+/=-]{12,})"
)

EMBEDDED_URL_PASSWORD_PATTERN = re.compile(
    r"(?i)\b(?:mysql|postgres(?:ql)?|mongodb(?:\+srv)?|redis|amqp)s?"
    r"://[^\s@/:]+:[^\s@]+@"
)

COORDINATE_PATTERN = re.compile(
    r"(?i)\b(?:latitude|longitude|lat|lon|lng)"
    r"\s*[:=]\s*-?\d{1,3}\.\d{4,}"
)

EMAIL_PATTERN = re.compile(
    r"(?i)\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PLACEHOLDERS = {
    "changeme", "change_me", "replace_me", "placeholder",
    "your_api_key", "your_password", "example_only",
    "none", "null", "true", "false", "not_set",
    "todo", "tbd", "redacted", "dummy", "example",
}

REFERENCE_PREFIXES = (
    "${", "{{", "<", "os.getenv(", "os.environ[",
    "getenv(", "process.env.", "env(", "config(",
    "settings.", "$", "***",
)


def is_placeholder_or_reference(value):
    value = value.strip().strip("\"'").strip().lower()
    if not value:
        return True
    if value in PLACEHOLDERS:
        return True
    if any(value.startswith(prefix) for prefix in REFERENCE_PREFIXES):
        return True
    return any(
        value.startswith(prefix)
        for prefix in ("your_", "example_", "sample_", "dummy_", "replace_")
    )


def is_public_example_email(address):
    domain = address.rsplit("@", 1)[-1].lower()
    return (
        domain in {"example.com", "example.net", "example.org"}
        or domain == "users.noreply.github.com"
    )

findings = []
warnings = []


def run_git(arguments):
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Git command failed: " + " ".join(arguments[:2])
        )

    return result.stdout


def decode_path(raw):
    return raw.decode("utf-8", errors="strict")


def get_index_entries():
    output = run_git(["ls-files", "--stage", "-z"])
    entries = {}

    for record in output.split(b"\0"):
        if not record:
            continue

        metadata, separator, raw_path = record.partition(b"\t")

        if not separator:
            raise RuntimeError("Malformed Git index entry")

        parts = metadata.split()

        if len(parts) != 3:
            raise RuntimeError("Invalid Git index metadata")

        mode, object_id, stage = parts
        relative = decode_path(raw_path)

        if stage != b"0":
            raise RuntimeError(
                "Unresolved Git merge entry: " + relative
            )

        if relative in entries:
            raise RuntimeError(
                "Duplicate Git index entry: " + relative
            )

        entries[relative] = {
            "mode": mode.decode("ascii"),
            "object_id": object_id.decode("ascii"),
        }

    return entries


def get_untracked_files():
    output = run_git([
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
    ])

    return {
        decode_path(record)
        for record in output.split(b"\0")
        if record
    }


def add_finding(relative, layer, line, reason):
    findings.append(
        (relative, layer, line, reason)
    )


def add_warning(relative, layer, line, reason):
    warnings.append(
        (relative, layer, line, reason)
    )


def check_filename(relative):
    path = Path(relative)
    name = path.name.lower()
    suffix = path.suffix.lower()

    normalized = relative.replace("\\", "/").lower()
    if normalized in BLOCKED_PATHS:
        add_finding(
            relative,
            "path",
            0,
            "Internal or historical artifact prohibited",
        )

    if any(
        normalized.startswith(prefix)
        for prefix in BLOCKED_DIRECTORIES
    ):
        add_finding(
            relative,
            "path",
            0,
            "Private directory prohibited",
        )

    if name in SENSITIVE_NAMES:
        add_finding(
            relative,
            "path",
            0,
            "Sensitive filename",
        )

    if name.startswith(".env.") and name not in ALLOWED_ENV_TEMPLATES:
        add_finding(
            relative,
            "path",
            0,
            "Environment configuration not approved",
        )

    if suffix in SENSITIVE_EXTENSIONS:
        add_finding(
            relative,
            "path",
            0,
            "Sensitive file extension",
        )

    return (
        suffix in TEXT_EXTENSIONS
        or path.name in TEXT_FILENAMES
        or name in ALLOWED_ENV_TEMPLATES
    )


def scan_text(relative, layer, data):
    if len(data) > MAX_TEXT_BYTES:
        add_finding(
            relative,
            layer,
            0,
            "Text file exceeds audit size limit",
        )
        return

    if b"\0" in data:
        add_finding(
            relative,
            layer,
            0,
            "Binary content in text candidate",
        )
        return

    try:
        content = data.decode("utf-8-sig")
    except UnicodeError:
        add_finding(
            relative,
            layer,
            0,
            "Text content is not valid UTF-8",
        )
        return

    for number, line in enumerate(
        content.splitlines(), start=1
    ):
        if TOKEN_PATTERN.search(line):
            add_finding(
                relative,
                layer,
                number,
                "Possible credential token",
            )

        if PRIVATE_KEY_PATTERN.search(line):
            add_finding(
                relative,
                layer,
                number,
                "Private key header",
            )

        for match in SECRET_ASSIGNMENT_PATTERN.finditer(line):
            if not is_placeholder_or_reference(match.group("value")):
                add_finding(
                    relative,
                    layer,
                    number,
                    "Possible hardcoded secret",
                )

        bearer = BEARER_PATTERN.search(line)
        if bearer and not is_placeholder_or_reference(bearer.group("value")):
            add_finding(
                relative,
                layer,
                number,
                "Possible bearer credential",
            )

        if EMBEDDED_URL_PASSWORD_PATTERN.search(line):
            add_finding(
                relative,
                layer,
                number,
                "Possible credential embedded in URL",
            )

        if COORDINATE_PATTERN.search(line):
            add_warning(
                relative,
                layer,
                number,
                "Numeric coordinate requires manual review",
            )

        for match in EMAIL_PATTERN.finditer(line):
            if not is_public_example_email(match.group()):
                add_warning(
                    relative,
                    layer,
                    number,
                    "Email address requires privacy review",
                )


def inspect_candidate(relative, index_entry):
    local = ROOT / relative

    if local.is_symlink():
        add_finding(
            relative,
            "working",
            0,
            "Symlink requires separate review",
        )
        return

    if not local.is_file():
        add_finding(
            relative,
            "working",
            0,
            "Missing or non-regular working file",
        )
        return

    is_text = check_filename(relative)

    if not is_text:
        add_finding(
            relative,
            "path",
            0,
            "Unsupported format; manual approval required",
        )
        return

    try:
        working_data = local.read_bytes()
    except OSError:
        add_finding(
            relative,
            "working",
            0,
            "Cannot read working file",
        )
        return

    if index_entry is None:
        scan_text(
            relative,
            "untracked",
            working_data,
        )
        return

    mode = index_entry["mode"]

    if mode not in {"100644", "100755"}:
        add_finding(
            relative,
            "index",
            0,
            "Unsupported Git index mode",
        )
        return

    try:
        index_data = run_git([
            "cat-file",
            "blob",
            index_entry["object_id"],
        ])
    except RuntimeError:
        add_finding(
            relative,
            "index",
            0,
            "Cannot read staged Git object",
        )
        return

    # The index is the source of the next commit.
    scan_text(
        relative,
        "index",
        index_data,
    )

    # Also inspect changes that may be staged later.
    if working_data != index_data:
        scan_text(
            relative,
            "working",
            working_data,
        )


def print_results():
    print("Potential security findings:", len(findings))
    print("Manual review warnings:", len(warnings))
    print()

    for relative, layer, line, reason in findings:
        print(
            f"REVIEW REQUIRED: "
            f"{relative}:{line} [{layer}] - {reason}"
        )

    for relative, layer, line, reason in warnings:
        print(
            f"WARNING: "
            f"{relative}:{line} [{layer}] - {reason}"
        )

    print()

    # Warnings also require manual sign-off before a publishable commit.
    # Fail closed rather than reporting success for potentially private data.
    if findings or warnings:
        print("RESULT: SECURITY REVIEW REQUIRED")
        return 1

    print("PASS: No prohibited files detected")
    print("PASS: No obvious secrets detected")
    print("PASS: Git index and working content checked")
    print("RESULT: AUTOMATED SECURITY SCREEN PASSED")
    return 0


def main():
    print("=== PHASE 2.7B.5K.5 - PUBLIC SECURITY AUDIT ===")

    try:
        index = get_index_entries()
        untracked = get_untracked_files()
    except (
        RuntimeError,
        UnicodeError,
        OSError,
    ) as error:
        print("FAIL:", error)
        return 1

    candidates = sorted(
        set(index) | untracked
    )

    if not candidates:
        print("FAIL: No Git candidate files found")
        return 1

    print("Git index entries:", len(index))
    print("Untracked candidates:", len(untracked))
    print("Total candidates:", len(candidates))
    print()

    for relative in candidates:
        inspect_candidate(
            relative,
            index.get(relative),
        )

    result = print_results()

    print()
    print("NOTE: This scan is not a confidentiality guarantee")
    print("NOTE: Unsupported binary files are blocked")
    print("NOTE: Manual semantic review is still mandatory")
    print("NOTE: No files were modified")
    print("NOTE: Passing does not authorize publication")
    print("=== PHASE 2.7B.5K.5 COMPLETE ===")

    return result


if __name__ == "__main__":
    sys.exit(main())
