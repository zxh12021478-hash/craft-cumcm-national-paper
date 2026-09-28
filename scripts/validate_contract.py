#!/usr/bin/env python3
"""Validate a JSON instance against a bundled or user-supplied JSON Schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def result(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def validate(instance_path: Path, schema_path: Path) -> dict:
    findings: list[dict] = []
    try:
        instance = json.loads(instance_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "instance": str(instance_path),
            "schema": str(schema_path),
            "findings": [result("Blocker", "INSTANCE_JSON", str(exc))],
        }
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "instance": str(instance_path),
            "schema": str(schema_path),
            "findings": [result("Blocker", "SCHEMA_JSON", str(exc))],
        }
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        findings.append(
            result(
                "Major",
                "JSONSCHEMA_UNAVAILABLE",
                "The jsonschema package is unavailable; only basic JSON parsing was completed.",
            )
        )
    else:
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            findings.append(
                result(
                    "Critical",
                    "SCHEMA_VIOLATION",
                    f"{location}: {error.message}",
                    {"validator": error.validator, "validator_value": error.validator_value},
                )
            )
    return {
        "instance": str(instance_path),
        "schema": str(schema_path),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instance", type=Path)
    parser.add_argument("schema", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.instance.is_file() or not args.schema.is_file():
        print(json.dumps({"error": "instance and schema must exist"}, ensure_ascii=False))
        return 2
    report = validate(args.instance.resolve(), args.schema.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
