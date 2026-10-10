
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, BadZipFile, LargeZipFile
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

DOCUMENT_TYPES = {
    ".md", ".txt", ".csv", ".rst",
    ".json", ".yaml", ".yml", ".docx",
}

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
MAX_DOCX_EXTRACTED_BYTES = 50 * 1024 * 1024
MAX_DOCX_MEMBERS = 2000

# These rules identify material requiring manual review.
# A match is not automatically proof of sensitive disclosure.
RULES = {
    "VESSEL_OR_LAW_ENFORCEMENT_CONTEXT": (
        r"\b(?:patrol|patroli|police|kepolisian|"
        r"policing)\b"
    ),
    "POSSIBLE_COMPANY_IDENTITY": (
        r"\b(?:PT\.?|CV\.?)\s+"
        r"(?:[A-Z][A-Za-z.-]*\s*){2,7}"
    ),
    "POSSIBLE_VESSEL_IDENTIFIER": (
        r"\b(?:KP|KRI|KPL)[ -]+"
        r"[A-Z]{1,8}[- ]?\d{3,5}\b"
    ),
    "REAL_WORLD_ASSERTION": (
        r"\b(?:onboard|installed|observed|"
        r"field[- ]verified|actual vessel|"
        r"real vessel|provided photo|"
        r"project owner|terpasang|"
        r"kapal nyata)\b"
    ),
    "CERTIFICATION_LANGUAGE": (
        r"\b(?:certified|certification|"
        r"type[- ]approved|type approval|"
        r"compliant|compliance|"
        r"marine[- ]qualified)\b"
    ),
    "PERSON_OR_AFFILIATION_FIELD": (
        r"\b(?:prepared by|author|creator|"
        r"narasumber|penyusun|pembimbing|"
        r"contact person)\s*[:=]"
    ),
    "NUMERIC_COORDINATE": (
        r"\b(?:latitude|longitude|lat|lon|lng)"
        r"\s*[:=]\s*-?\d{1,3}\.\d{4,}"
    ),
}

PATTERNS = {
    name: re.compile(pattern, re.IGNORECASE)
    for name, pattern in RULES.items()
}


def git_output(arguments):
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Git inventory or blob retrieval failed"
        )

    return result.stdout


def decode_git_path(raw):
    value = raw.decode("utf-8", errors="strict")

    if (
        value.startswith("/")
        or ".." in value.split("/")
        or not value
    ):
        raise ValueError("Unsafe Git path")

    return value


def git_candidates():
    index = {}

    entries = git_output([
        "ls-files", "--stage", "-z"
    ])

    for item in entries.split(b"\0"):
        if not item:
            continue

        metadata, separator, raw_path = item.partition(b"\t")

        if not separator:
            raise ValueError("Malformed Git index entry")

        fields = metadata.split()

        if len(fields) != 3:
            raise ValueError("Malformed Git index metadata")

        mode, object_id, stage = fields
        relative = decode_git_path(raw_path)

        if stage != b"0":
            raise ValueError(
                "Unresolved Git merge entry detected"
            )

        if relative in index:
            raise ValueError(
                "Duplicate Git index entry detected"
            )

        index[relative] = {
            "mode": mode.decode("ascii"),
            "object_id": object_id.decode("ascii"),
        }

    other_entries = git_output([
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
    ])

    untracked = set()

    for item in other_entries.split(b"\0"):
        if item:
            relative = decode_git_path(item)

            if relative in index:
                raise ValueError(
                    "Duplicate tracked/untracked path"
                )

            untracked.add(relative)

    return index, untracked


def read_working_file(relative):
    path = ROOT / relative

    if path.is_symlink():
        raise ValueError(
            "Symbolic link requires separate review"
        )

    if not path.is_file():
        raise ValueError(
            "Candidate file missing or not regular"
        )

    data = path.read_bytes()

    if len(data) > MAX_DOCUMENT_BYTES:
        raise ValueError(
            "Document exceeds audit size limit"
        )

    return data


def docx_segments(data):
    segments = []

    with ZipFile(BytesIO(data)) as archive:
        members = archive.infolist()

        if len(members) > MAX_DOCX_MEMBERS:
            raise ValueError(
                "DOCX has too many package members"
            )

        total_uncompressed = sum(
            item.file_size for item in members
        )

        if total_uncompressed > MAX_DOCX_EXTRACTED_BYTES:
            raise ValueError(
                "DOCX exceeds extraction size limit"
            )

        if archive.testzip() is not None:
            raise ValueError(
                "DOCX package integrity error"
            )

        for name in archive.namelist():
            if not name.endswith(".xml"):
                continue

            if not (
                name.startswith("word/")
                or name.startswith("docProps/")
                or name.startswith("customXml/")
            ):
                continue

            root = ET.fromstring(
                archive.read(name)
            )

            if (
                name.startswith("docProps/")
                or name.startswith("customXml/")
            ):
                values = []

                for element in root.iter():
                    if element.text and element.text.strip():
                        values.append(element.text)

                    values.extend(
                        str(value)
                        for value in element.attrib.values()
                        if str(value).strip()
                    )

                if values:
                    segments.append(
                        (name, " ".join(values))
                    )

                continue

            paragraph_index = 0

            for paragraph in root.iter():
                if not paragraph.tag.endswith("}p"):
                    continue

                text = "".join(
                    node.text or ""
                    for node in paragraph.iter()
                    if node.tag.endswith("}t")
                )

                if text.strip():
                    paragraph_index += 1
                    segments.append((
                        f"{name}:paragraph-{paragraph_index}",
                        text,
                    ))

    return segments


def scan_document(relative, data):
    if len(data) > MAX_DOCUMENT_BYTES:
        raise ValueError(
            "Document exceeds audit size limit"
        )

    if Path(relative).suffix.lower() == ".docx":
        segments = docx_segments(data)

    else:
        if b"\0" in data:
            raise ValueError(
                "Binary content in text document"
            )

        lines = data.decode(
            "utf-8-sig"
        ).splitlines()

        segments = [
            (f"line-{number}", line)
            for number, line in enumerate(lines, start=1)
        ]

    results = defaultdict(list)

    for location, content in segments:
        for category, pattern in PATTERNS.items():
            if pattern.search(content):
                results[category].append(location)

    return results


def document_sources(relative, index):
    working_data = read_working_file(relative)

    if relative not in index:
        return [
            ("untracked", working_data)
        ]

    entry = index[relative]

    if entry["mode"] not in {"100644", "100755"}:
        raise ValueError(
            "Unsupported Git index file mode"
        )

    staged_data = git_output([
        "cat-file",
        "blob",
        entry["object_id"],
    ])

    if staged_data == working_data:
        return [
            ("index+working", staged_data)
        ]

    # Git can store LF while the working copy uses CRLF on Windows.
    # Normalizing only the line endings avoids double-counting the
    # same visible text, without ignoring actual content changes.
    # Do not normalize DOCX packages or other non-text data.
    if (
        Path(relative).suffix.lower() != ".docx"
        and b"\0" not in staged_data
        and b"\0" not in working_data
        and staged_data.replace(b"\r\n", b"\n")
        == working_data.replace(b"\r\n", b"\n")
    ):
        return [
            ("index+working", staged_data)
        ]

    return [
        ("index", staged_data),
        ("working", working_data),
    ]


def main():
    print(
        "=== PHASE 2.7B.5K.7 - "
        "PUBLIC DOCUMENTATION AUDIT ==="
    )
    print()

    try:
        index, untracked = git_candidates()
    except (
        OSError,
        UnicodeError,
        ValueError,
        RuntimeError,
    ) as error:
        print("FAIL: Unable to inventory Git candidates")
        print("Reason:", type(error).__name__)
        return 1

    candidates = sorted(
        set(index) | untracked
    )

    documents = [
        relative
        for relative in candidates
        if Path(relative).suffix.lower() in DOCUMENT_TYPES
    ]

    flagged_files = 0
    flagged_locations = 0
    scanned_versions = 0
    errors = 0

    for relative in documents:
        try:
            sources = document_sources(
                relative, index
            )

            file_findings = []

            for source, data in sources:
                findings = scan_document(
                    relative, data
                )

                scanned_versions += 1

                for category, locations in sorted(
                    findings.items()
                ):
                    file_findings.append((
                        source,
                        category,
                        locations,
                    ))

        except (
            OSError,
            UnicodeError,
            ValueError,
            RuntimeError,
            BadZipFile,
            LargeZipFile,
            ET.ParseError,
        ) as error:
            errors += 1

            print("ERROR:", relative)
            print("Reason:", type(error).__name__)
            print()

            continue

        if not file_findings:
            continue

        flagged_files += 1

        print("FILE:", relative)

        for source, category, locations in file_findings:
            flagged_locations += len(locations)

            preview = ", ".join(
                locations[:5]
            )

            if len(locations) > 5:
                preview += ", ..."

            print(
                f"  REVIEW {category} [{source}]: "
                f"{len(locations)} location(s)"
            )
            print("  Locations:", preview)

        print()

    print("Git index entries:", len(index))
    print("Untracked candidates:", len(untracked))
    print("Total Git candidate files:", len(candidates))
    print("Documentation candidates:", len(documents))
    print("Document versions scanned:", scanned_versions)
    print("Files requiring review:", flagged_files)
    print("Flagged locations:", flagged_locations)
    print("Read errors:", errors)
    print()

    if errors:
        print(
            "RESULT: AUDIT INCOMPLETE - "
            "REVIEW ERRORS"
        )
        return 1

    if not documents:
        print(
            "RESULT: AUDIT INCOMPLETE - "
            "NO DOCUMENTS"
        )
        return 1

    print("PASS: Documentation inventory scan completed")
    print("PASS: All candidate documents were readable")
    print()
    print(
        "NOTE: Findings are manual review indicators"
    )
    print(
        "NOTE: A zero-finding result is not a "
        "confidentiality guarantee"
    )
    print(
        "NOTE: Document content and matched text "
        "were not printed"
    )
    print(
        "NOTE: DOCX images and embedded media "
        "were not inspected"
    )
    print(
        "NOTE: Personal names can escape "
        "pattern detection"
    )
    print(
        "NOTE: Manual semantic review is mandatory"
    )
    print(
        "NOTE: No files were modified"
    )
    print(
        "NOTE: Passing does not authorize publication"
    )

    if not index:
        print(
            "NOTE: No staged/index files yet; "
            "index-content review remains untested"
        )

    print(
        "RESULT: PUBLIC DOCUMENTATION "
        "REVIEW INVENTORY READY"
    )
    print(
        "=== PHASE 2.7B.5K.7 COMPLETE ==="
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
