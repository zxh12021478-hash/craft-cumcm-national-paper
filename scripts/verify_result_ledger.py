#!/usr/bin/env python3
"""Verify canonical results against machine outputs and declared artifact occurrences."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def numeric(value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"not a scalar number: {value!r}")
    number = float(str(value).replace(",", "").strip())
    if not math.isfinite(number):
        raise ValueError(f"non-finite number: {value!r}")
    return number


def validate_schema(payload: dict, schema_path: Path) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", "Result ledger was not checked with JSON Schema.")]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [finding("Blocker", "SCHEMA_READ", str(exc), str(schema_path))]
    output = []
    for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        output.append(finding("Blocker", "LEDGER_SCHEMA", f"{location}: {error.message}"))
    return output


def json_key(payload, key: str):
    current = payload
    for part in key.split(".") if key else []:
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise KeyError(part)
    return current


def source_value(root: Path, source: dict) -> float:
    path = (root / source["file"]).resolve()
    path.relative_to(root.resolve())
    if not path.is_file():
        raise FileNotFoundError(source["file"])
    fmt = source.get("format", path.suffix.lower().lstrip("."))
    if fmt == "json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        value = json_key(payload, source.get("key", ""))
    elif fmt == "csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        if "where" in source:
            where = {str(k): str(v) for k, v in source["where"].items()}
            matches = [row for row in rows if all(str(row.get(k)) == v for k, v in where.items())]
            if len(matches) != 1:
                raise ValueError(f"CSV selector matched {len(matches)} rows")
            row = matches[0]
        else:
            row = rows[int(source.get("row", 0))]
        value = row[source["column"]]
    elif fmt in {"txt", "text", "md", "log"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(source["regex"], text, re.I | re.M)
        if not match:
            raise ValueError("source regex did not match")
        value = match.group(int(source.get("group", 1)))
    else:
        raise ValueError(f"unsupported source format: {fmt}")
    return numeric(value) * numeric(source.get("scale", 1.0))


def artifact_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        with zipfile.ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
        return "\n".join("".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p"))
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF extraction requires pypdf") from exc
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    if suffix == ".json":
        return json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False)
    return path.read_text(encoding="utf-8", errors="ignore")


def within_tolerance(actual: float, expected: float, absolute: float, relative: float) -> bool:
    allowed = max(absolute, relative * max(abs(expected), abs(actual)))
    return abs(actual - expected) <= allowed


def inspect(ledger_path: Path, root: Path, schema_path: Path | None = None, final: bool = False) -> dict:
    findings: list[dict] = []
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"ledger": str(ledger_path), "findings": [finding("Blocker", "LEDGER_JSON", str(exc))], "results": []}
    if not isinstance(ledger, dict):
        return {"ledger": str(ledger_path), "findings": [finding("Blocker", "LEDGER_SCHEMA", "Ledger root must be an object.")], "results": []}
    if schema_path:
        findings.extend(validate_schema(ledger, schema_path))
    results = ledger.get("results")
    if ledger.get("version") != 1 or not isinstance(results, list):
        return {
            "ledger": str(ledger_path),
            "findings": [finding("Blocker", "LEDGER_SCHEMA", "Expected version 1 and a results array.")],
            "results": [],
        }
    if final and not ledger.get("approved_by_team"):
        findings.append(
            finding(
                "Blocker",
                "RESULTS_NOT_APPROVED",
                "Final validation requires approved_by_team=true after the team accepts the headline results.",
            )
        )
    if final and not ledger.get("frozen_at"):
        findings.append(finding("Critical", "RESULTS_NOT_FROZEN", "Final validation requires a result-freeze timestamp."))
    elif final:
        try:
            stamp = datetime.fromisoformat(str(ledger.get("frozen_at")).replace("Z", "+00:00"))
            if stamp.tzinfo is None or stamp.utcoffset() is None:
                raise ValueError("timezone offset is required")
        except Exception as exc:
            findings.append(
                finding(
                    "Blocker",
                    "INVALID_FREEZE_TIMESTAMP",
                    f"frozen_at must be an ISO timestamp with timezone: {exc}",
                    ledger.get("frozen_at"),
                )
            )

    invalid_items = [index for index, item in enumerate(results) if not isinstance(item, dict)]
    if invalid_items:
        findings.append(finding("Blocker", "RESULT_ITEM_SCHEMA", "Every result must be an object.", invalid_items))
    results = [item for item in results if isinstance(item, dict)]
    ids = [str(item.get("id", "")) for item in results]
    duplicates = sorted({item for item in ids if item and ids.count(item) > 1})
    if duplicates:
        findings.append(finding("Blocker", "DUPLICATE_RESULT_ID", "Result IDs must be unique.", duplicates))
    checked = []
    text_cache: dict[Path, str] = {}
    for index, item in enumerate(results):
        result_id = str(item.get("id", "")).strip()
        local_findings = []
        if not result_id:
            local_findings.append(finding("Blocker", "RESULT_ID", f"Result at index {index} has no ID."))
            findings.extend(local_findings)
            continue
        try:
            expected = numeric(item["value"])
        except Exception as exc:
            local_findings.append(finding("Blocker", "CANONICAL_VALUE", f"{result_id}: {exc}"))
            findings.extend(local_findings)
            checked.append({"id": result_id, "findings": local_findings})
            continue
        absolute = numeric(item.get("absolute_tolerance", 0.0))
        relative = numeric(item.get("relative_tolerance", 0.0))
        if absolute < 0 or relative < 0:
            local_findings.append(finding("Blocker", "TOLERANCE", f"{result_id}: tolerances cannot be negative."))

        source = item.get("source")
        source_actual = None
        if not isinstance(source, dict):
            local_findings.append(finding("Major", "NO_MACHINE_SOURCE", f"{result_id}: no machine-readable source was declared."))
        else:
            try:
                source_actual = source_value(root, source)
                if not within_tolerance(source_actual, expected, absolute, relative):
                    local_findings.append(
                        finding(
                            "Blocker" if item.get("decision_critical", True) else "Critical",
                            "SOURCE_MISMATCH",
                            f"{result_id}: machine source does not match the canonical value.",
                            {"canonical": expected, "source": source_actual, "unit": item.get("unit", "")},
                        )
                    )
            except Exception as exc:
                local_findings.append(finding("Critical", "SOURCE_READ", f"{result_id}: {exc}", source))

        occurrences = item.get("occurrences", [])
        if not occurrences:
            local_findings.append(finding("Major", "NO_OCCURRENCES", f"{result_id}: no paper/table/figure-text occurrence was declared."))
        occurrence_results = []
        for occurrence in occurrences:
            try:
                artifact = (root / occurrence["file"]).resolve()
                artifact.relative_to(root.resolve())
                if not artifact.is_file():
                    raise FileNotFoundError(occurrence["file"])
                if artifact not in text_cache:
                    text_cache[artifact] = artifact_text(artifact)
                matches = list(re.finditer(occurrence["regex"], text_cache[artifact], re.I | re.M))
                minimum = int(occurrence.get("expected_min", 1))
                maximum = occurrence.get("expected_max")
                if len(matches) < minimum or (maximum is not None and len(matches) > int(maximum)):
                    raise ValueError(f"regex matched {len(matches)} times; expected {minimum}..{maximum or '∞'}")
                values = []
                for match in matches:
                    actual = numeric(match.group(int(occurrence.get("group", 1)))) * numeric(occurrence.get("scale", 1.0))
                    values.append(actual)
                    if not within_tolerance(actual, expected, absolute, relative):
                        local_findings.append(
                            finding(
                                "Blocker" if item.get("decision_critical", True) else "Critical",
                                "ARTIFACT_MISMATCH",
                                f"{result_id}: declared artifact occurrence differs from the canonical value.",
                                {"file": occurrence["file"], "canonical": expected, "actual": actual},
                            )
                        )
                unit_regex = occurrence.get("unit_regex")
                if unit_regex and not re.search(unit_regex, "\n".join(match.group(0) for match in matches), re.I):
                    local_findings.append(finding("Major", "UNIT_MISSING", f"{result_id}: expected unit not found in occurrence.", unit_regex))
                occurrence_results.append({"file": occurrence["file"], "matches": len(matches), "values": values})
            except Exception as exc:
                local_findings.append(finding("Critical", "OCCURRENCE_READ", f"{result_id}: {exc}", occurrence))

        findings.extend(local_findings)
        checked.append(
            {
                "id": result_id,
                "canonical": expected,
                "unit": item.get("unit", ""),
                "source_value": source_actual,
                "occurrences": occurrence_results,
                "findings": local_findings,
            }
        )
    return {"ledger": str(ledger_path), "root": str(root), "results": checked, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--root", type=Path, help="Artifact root; defaults to the ledger directory")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--final", action="store_true", help="Require team approval and a frozen timestamp")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.ledger.is_file():
        print(json.dumps({"error": "ledger not found", "ledger": str(args.ledger)}, ensure_ascii=False))
        return 2
    root = (args.root or args.ledger.parent).resolve()
    schema = args.schema
    if schema is None:
        schema = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "result-ledger.schema.json"
    report = inspect(args.ledger.resolve(), root, schema.resolve(), args.final)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
