#!/usr/bin/env python3
"""Replace or verify only the abstract body in a Markdown paper."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ABSTRACT_HEADING = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\*\*|__)?\s*摘\s*要\s*(?:\*\*|__)?\s*[:：]?\s*$"
)
KEYWORD_MARKER = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\*\*|__)?\s*关\s*键\s*[词字]\s*(?:\*\*|__)?\s*(?:[:：].*)?$"
)


class BoundaryError(ValueError):
    """Raised when the Markdown abstract boundaries are not unambiguous."""


@dataclass(frozen=True)
class Boundaries:
    body_start: int
    body_end: int
    heading_line: int
    keyword_line: int


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_utf8(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BoundaryError(f"{path} is not valid UTF-8 Markdown") from exc


def line_payload(line: str) -> str:
    return line.rstrip("\r\n").lstrip("\ufeff")


def locate(text: str) -> Boundaries:
    lines = text.splitlines(keepends=True)
    offsets: list[int] = []
    cursor = 0
    for line in lines:
        offsets.append(cursor)
        cursor += len(line)

    headings = [index for index, line in enumerate(lines) if ABSTRACT_HEADING.fullmatch(line_payload(line))]
    if len(headings) != 1:
        raise BoundaryError(f"expected exactly one abstract heading, found {len(headings)}")
    heading_index = headings[0]

    keywords = [
        index
        for index, line in enumerate(lines)
        if index > heading_index and KEYWORD_MARKER.fullmatch(line_payload(line))
    ]
    if len(keywords) != 1:
        raise BoundaryError(
            f"expected exactly one keyword marker after the abstract heading, found {len(keywords)}"
        )
    keyword_index = keywords[0]
    return Boundaries(
        body_start=offsets[heading_index] + len(lines[heading_index]),
        body_end=offsets[keyword_index],
        heading_line=heading_index + 1,
        keyword_line=keyword_index + 1,
    )


def newline_style(text: str) -> str:
    first_lf = text.find("\n")
    if first_lf > 0 and text[first_lf - 1] == "\r":
        return "\r\n"
    return "\n"


def normalize_abstract(value: str, newline: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        raise BoundaryError("replacement abstract is empty")
    return newline + normalized.replace("\n", newline) + newline * 2


def preservation_report(original: str, revised: str, operation: str) -> dict:
    original_bounds = locate(original)
    revised_bounds = locate(revised)
    original_prefix = original[: original_bounds.body_start]
    revised_prefix = revised[: revised_bounds.body_start]
    original_suffix = original[original_bounds.body_end :]
    revised_suffix = revised[revised_bounds.body_end :]
    original_abstract = original[original_bounds.body_start : original_bounds.body_end]
    revised_abstract = revised[revised_bounds.body_start : revised_bounds.body_end]

    prefix_unchanged = original_prefix == revised_prefix
    suffix_unchanged = original_suffix == revised_suffix
    return {
        "operation": operation,
        "status": "pass" if prefix_unchanged and suffix_unchanged else "blocked",
        "outside_abstract_unchanged": prefix_unchanged and suffix_unchanged,
        "abstract_changed": original_abstract != revised_abstract,
        "abstract_heading_unchanged": prefix_unchanged,
        "keywords_and_remainder_unchanged": suffix_unchanged,
        "original_sha256": digest_text(original),
        "revised_sha256": digest_text(revised),
        "original_abstract_sha256": digest_text(original_abstract),
        "revised_abstract_sha256": digest_text(revised_abstract),
        "preserved_prefix_sha256": digest_text(original_prefix),
        "preserved_suffix_sha256": digest_text(original_suffix),
        "original_heading_line": original_bounds.heading_line,
        "original_keyword_line": original_bounds.keyword_line,
        "revised_heading_line": revised_bounds.heading_line,
        "revised_keyword_line": revised_bounds.keyword_line,
    }


def write_report(path: Path | None, report: dict) -> None:
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def replace(args: argparse.Namespace) -> int:
    source = read_utf8(args.source)
    replacement = read_utf8(args.abstract)
    bounds = locate(source)
    revised = (
        source[: bounds.body_start]
        + normalize_abstract(replacement, newline_style(source))
        + source[bounds.body_end :]
    )
    report = preservation_report(source, revised, "replace")
    if report["status"] != "pass":
        raise BoundaryError("replacement altered content outside the abstract body")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(revised.encode("utf-8"))
    write_report(args.report, report)
    return 0


def verify(args: argparse.Namespace) -> int:
    original = read_utf8(args.original)
    revised = read_utf8(args.revised)
    report = preservation_report(original, revised, "verify")
    write_report(args.report, report)
    return 0 if report["status"] == "pass" else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)

    replace_parser = subparsers.add_parser("replace", help="replace only the Markdown abstract body")
    replace_parser.add_argument("--source", required=True, type=Path)
    replace_parser.add_argument("--abstract", required=True, type=Path)
    replace_parser.add_argument("--output", required=True, type=Path)
    replace_parser.add_argument("--report", type=Path)
    replace_parser.set_defaults(handler=replace)

    verify_parser = subparsers.add_parser("verify", help="verify that only the abstract body changed")
    verify_parser.add_argument("--original", required=True, type=Path)
    verify_parser.add_argument("--revised", required=True, type=Path)
    verify_parser.add_argument("--report", type=Path)
    verify_parser.set_defaults(handler=verify)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (BoundaryError, OSError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
