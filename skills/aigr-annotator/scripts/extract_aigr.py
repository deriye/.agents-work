#!/usr/bin/env python3
"""AIGR block extractor.

Scans source files for ``<<<AIGR ... AIGR>>>`` blocks, extracts review
metadata into ``.aigr`` JSON sidecar files, and strips the markers from
the source.  Code inside the markers is preserved.

Label format: ``[category:LEVEL]`` — e.g. ``[severity:CRITICAL]``,
``[confidence:HIGH]``, ``[priority:URGENT]``.

Exit codes:
    0 — success (or no blocks found)
    1 — validation errors in one or more blocks
    2 — fatal error (file not found, permission denied, etc.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import Sequence

START_MARKER = "<<<AIGR"
END_MARKER = "AIGR>>>"

HEADER_RE = re.compile(
    r"^\s*(?P<id>\S+)\s+\[(?P<category>\w+):(?P<level>\w+)]\s+(?P<note>.+)$"
)
SEPARATOR_RE = re.compile(r"^[=\-~*#]{3,}$")

COMMENT_PREFIXES_WITH_SPACE = ("# ", "// ", "-- ", ";; ", "% ", "* ", "/* ", "/// ")
BARE_COMMENT_PREFIXES = ("#", "//", "--", ";;", "%", "*")

SUPPORTED_EXTENSIONS: set[str] = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".cpp", ".c", ".h", ".hpp",
    ".rs", ".go", ".txt", ".md",
    ".java", ".kt", ".cs",
    ".rb", ".sh", ".bash",
    ".yaml", ".yml", ".toml",
}


@dataclass
class ReviewItem:
    """A single extracted review item."""
    id: str
    category: str
    level: str
    note: str
    description: str
    anchor: str
    startLine: int
    endLine: int


@dataclass
class Header:
    """Parsed header fields from the ``<<<AIGR`` line."""
    id: str
    category: str
    level: str
    note: str


@dataclass
class ValidationError:
    """A problem found during block validation."""
    file: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"ERROR {self.file}:{self.line}: {self.message}"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def normalize_line(line: str) -> str:
    """Collapse whitespace and strip for anchor computation."""
    return re.sub(r"\s+", " ", line.replace("\t", " ")).strip()


def compute_anchor(line: str) -> str:
    """Return the first 8 hex chars of the SHA-1 of *line* (normalized)."""
    return hashlib.sha1(normalize_line(line).encode()).hexdigest()[:8]


def strip_comment_prefix(line: str) -> str:
    """Remove the leading comment prefix from *line*."""
    stripped = line.strip()
    for prefix in COMMENT_PREFIXES_WITH_SPACE:
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    for prefix in BARE_COMMENT_PREFIXES:
        if stripped == prefix:
            return ""
        if (stripped.startswith(prefix)
                and len(stripped) > len(prefix)
                and not stripped[len(prefix)].isalnum()):
            return stripped[len(prefix):].lstrip()
    return stripped


def is_comment_line(line: str) -> bool:
    """Return ``True`` if *line* begins with a recognised comment prefix."""
    stripped = line.strip()
    if not stripped:
        return False
    return any(stripped.startswith(p) for p in (*BARE_COMMENT_PREFIXES, "/*", "///"))


def _find_start_marker(line: str) -> str | None:
    cleaned = strip_comment_prefix(line)
    if START_MARKER in cleaned:
        idx = cleaned.index(START_MARKER)
        return cleaned[idx + len(START_MARKER):].strip()
    return None


def _has_end_marker(line: str) -> bool:
    return END_MARKER in strip_comment_prefix(line)


def _parse_header(text: str) -> Header | None:
    text = text.strip()
    if not text:
        return None
    m = HEADER_RE.match(text)
    if m:
        return Header(
            id=m["id"], category=m["category"],
            level=m["level"], note=m["note"].strip(),
        )
    return None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_blocks(filepath: str, lines: list[str]) -> list[ValidationError]:
    """Check all AIGR blocks for structural problems.

    Returns a list of errors.  Empty list means all blocks are valid.
    """
    errors: list[ValidationError] = []
    filename = os.path.basename(filepath)
    i = 0

    while i < len(lines):
        remainder = _find_start_marker(lines[i])
        if remainder is None:
            i += 1
            continue

        open_line = i + 1  # 1-indexed for display
        i += 1

        # Check header
        header = _parse_header(remainder)
        if header is None:
            # Try next line
            if i < len(lines) and not _has_end_marker(lines[i]):
                content = strip_comment_prefix(lines[i])
                header = _parse_header(content)
                if header is not None:
                    i += 1

        if header is None:
            errors.append(ValidationError(
                filename, open_line,
                f"Malformed header. Expected: <<<AIGR <ID> [category:LEVEL] <note>. "
                f"Got: <<<AIGR {remainder!r}"
            ))
            # Skip to end marker or EOF
            while i < len(lines):
                if _has_end_marker(lines[i]):
                    i += 1
                    break
                i += 1
            else:
                errors.append(ValidationError(
                    filename, open_line,
                    "Unclosed block: no AIGR>>> found before end of file."
                ))
            continue

        # Consume description + code, check for closing marker
        has_code = False
        found_close = False
        while i < len(lines):
            if _has_end_marker(lines[i]):
                found_close = True
                i += 1
                break
            if not is_comment_line(lines[i]) and lines[i].strip():
                has_code = True
            i += 1

        if not found_close:
            errors.append(ValidationError(
                filename, open_line,
                f"Unclosed block '{header.id}': no AIGR>>> found before end of file."
            ))
        elif not has_code:
            errors.append(ValidationError(
                filename, open_line,
                f"Block '{header.id}' contains no code lines between markers."
            ))

    return errors


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_blocks(lines: list[str]) -> tuple[list[str], list[ReviewItem]]:
    """Parse *lines*, remove AIGR markers, return cleaned lines and items."""
    cleaned: list[str] = []
    items: list[ReviewItem] = []
    i = 0

    while i < len(lines):
        remainder = _find_start_marker(lines[i])
        if remainder is None:
            cleaned.append(lines[i])
            i += 1
            continue

        i += 1
        header = _parse_header(remainder)
        description_parts: list[str] = []

        if header is None:
            while i < len(lines) and not _has_end_marker(lines[i]):
                content = strip_comment_prefix(lines[i])
                if content and not SEPARATOR_RE.match(content):
                    header = _parse_header(content)
                    if header is not None:
                        i += 1
                break

        if header is None:
            while i < len(lines):
                if _has_end_marker(lines[i]):
                    i += 1
                    break
                cleaned.append(lines[i])
                i += 1
            continue

        description_done = False
        code_lines: list[str] = []

        while i < len(lines):
            if _has_end_marker(lines[i]):
                i += 1
                break
            if not description_done and is_comment_line(lines[i]):
                content = strip_comment_prefix(lines[i])
                if content and not SEPARATOR_RE.match(content):
                    description_parts.append(content)
                i += 1
                continue
            description_done = True
            code_lines.append(lines[i])
            i += 1

        if not code_lines:
            continue

        start_line = len(cleaned) + 1
        cleaned.extend(code_lines)
        end_line = len(cleaned)

        anchor = "00000000"
        for cl in code_lines:
            if normalize_line(cl):
                anchor = compute_anchor(cl)
                break

        items.append(ReviewItem(
            id=header.id, category=header.category, level=header.level,
            note=header.note, description="\n".join(description_parts),
            anchor=anchor, startLine=start_line, endLine=end_line,
        ))

    return cleaned, items


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------

def process_file(
    filepath: str, *, dry_run: bool = False, validate_only: bool = False
) -> tuple[dict | None, list[ValidationError]]:
    """Extract AIGR blocks from a single file.

    Returns:
        (aigr_data, errors) — aigr_data is None if no blocks found or
        validation failed.
    """
    filepath = os.path.abspath(filepath)

    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as exc:
        return None, [ValidationError(filepath, 0, f"Cannot read file: {exc}")]

    if START_MARKER not in content:
        return None, []

    raw_lines = content.split("\n")
    trailing_newline = content.endswith("\n") and raw_lines[-1] == ""
    if trailing_newline:
        raw_lines = raw_lines[:-1]

    # Always validate first
    errors = validate_blocks(filepath, raw_lines)
    if errors:
        for e in errors:
            print(str(e), file=sys.stderr)
        return None, errors

    if validate_only:
        print(f"  OK: {filepath}")
        return None, []

    cleaned_lines, items = extract_blocks(raw_lines)

    if not items:
        return None, []

    filename = os.path.basename(filepath)
    aigr_data = {"file": filename, "items": [asdict(it) for it in items]}

    # Check for duplicate IDs
    seen_ids: dict[str, int] = {}
    for it in items:
        if it.id in seen_ids:
            errors.append(ValidationError(
                filename, 0,
                f"Duplicate ID '{it.id}' (first at line {seen_ids[it.id]}, "
                f"also at line {it.startLine}). Each block must have a unique ID."
            ))
        seen_ids[it.id] = it.startLine

    if errors:
        for e in errors:
            print(str(e), file=sys.stderr)
        return None, errors

    if dry_run:
        print(f"  [DRY RUN] Would extract {len(items)} item(s) from {filepath}")
        for it in items:
            print(f"    - {it.id} [{it.category}:{it.level}] {it.note} "
                  f"(lines {it.startLine}-{it.endLine})")
        return aigr_data, []

    try:
        cleaned_content = "\n".join(cleaned_lines)
        if trailing_newline:
            cleaned_content += "\n"
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(cleaned_content)

        aigr_path = filepath + ".aigr"
        with open(aigr_path, "w", encoding="utf-8", newline="") as f:
            json.dump(aigr_data, f, indent=2)
            f.write("\n")

        print(f"  Extracted {len(items)} item(s) from {filename}")
        print(f"  Written: {aigr_path}")
    except OSError as exc:
        return None, [ValidationError(filepath, 0, f"Cannot write: {exc}")]

    return aigr_data, []


def collect_files(paths: Sequence[str]) -> list[str]:
    """Recursively collect supported source files from *paths*."""
    result: list[str] = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            result.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fname in sorted(files):
                    if os.path.splitext(fname)[1].lower() in SUPPORTED_EXTENSIONS:
                        result.append(os.path.join(root, fname))
        else:
            print(f"Warning: '{p}' not found, skipping.", file=sys.stderr)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Extract AIGR review blocks from source files.",
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to process")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without modifying files")
    parser.add_argument("--validate", action="store_true",
                        help="Validate blocks only, do not extract")
    parser.add_argument("--ext", action="append",
                        help="Extra file extension (e.g. --ext .vue)")
    args = parser.parse_args()

    if args.ext:
        for ext in args.ext:
            SUPPORTED_EXTENSIONS.add(ext if ext.startswith(".") else f".{ext}")

    files = collect_files(args.paths)
    if not files:
        print("No supported files found.", file=sys.stderr)
        sys.exit(2)

    total_items = 0
    total_files = 0
    total_errors = 0

    for fp in files:
        result, errors = process_file(
            fp, dry_run=args.dry_run, validate_only=args.validate
        )
        total_errors += len(errors)
        if result:
            total_items += len(result["items"])
            total_files += 1

    print()
    if total_errors > 0:
        print(f"FAILED: {total_errors} error(s). Fix the issues above and retry.",
              file=sys.stderr)
        sys.exit(1)
    elif total_files == 0 and not args.validate:
        print("No AIGR blocks found.")
    elif args.validate:
        print("All blocks valid.")
    else:
        verb = "Would extract" if args.dry_run else "Extracted"
        print(f"{verb} {total_items} review item(s) from {total_files} file(s).")


if __name__ == "__main__":
    main()
