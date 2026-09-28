#!/usr/bin/env python3
"""Measure routed instruction size and fail when a declared word budget is exceeded."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "assets" / "workflows" / "efficiency-profiles.json"


def resolve_set(name: str, sets: dict, stack: tuple[str, ...] = ()) -> tuple[list[str], int | None]:
    if name in stack:
        raise ValueError(f"instruction set cycle: {' -> '.join(stack + (name,))}")
    item = sets[name]
    files: list[str] = []
    parent = item.get("extends")
    if parent:
        inherited, _ = resolve_set(parent, sets, stack + (name,))
        files.extend(inherited)
    files.extend(item.get("files", []))
    return list(dict.fromkeys(files)), item.get("max_words")


def measure(paths: list[str]) -> dict:
    totals = {"files": len(paths), "lines": 0, "words": 0, "characters": 0, "bytes": 0}
    details = []
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        text = path.read_text(encoding="utf-8")
        row = {
            "file": relative,
            "lines": len(text.splitlines()),
            "words": len(re.findall(r"\S+", text)),
            "characters": len(text),
            "bytes": len(text.encode("utf-8")),
        }
        details.append(row)
        for key in ("lines", "words", "characters", "bytes"):
            totals[key] += row[key]
    return {"totals": totals, "details": details}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--set", dest="set_names", action="append", help="Measure only this instruction set.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    sets = config["instruction_sets"]
    names = args.set_names or list(sets)
    reports = {}
    failures = []
    for name in names:
        files, max_words = resolve_set(name, sets)
        report = measure(files)
        report["max_words"] = max_words
        report["within_budget"] = max_words is None or report["totals"]["words"] <= max_words
        if not report["within_budget"]:
            failures.append({"set": name, "words": report["totals"]["words"], "max_words": max_words})
        reports[name] = report
    payload = {"version": 1, "status": "pass" if not failures else "fail", "sets": reports, "failures": failures}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
