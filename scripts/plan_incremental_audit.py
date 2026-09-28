#!/usr/bin/env python3
"""Plan a conservative delta audit between two CUMCM artifact directories."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


IGNORED_PARTS = {".git", "__pycache__", ".DS_Store", ".pytest_cache", ".mypy_cache"}
CODE_SUFFIXES = {".py", ".m", ".r", ".jl", ".c", ".cc", ".cpp", ".java", ".ipynb"}
DATA_SUFFIXES = {".csv", ".tsv", ".xls", ".xlsx", ".parquet", ".feather", ".mat", ".db"}
PAPER_SUFFIXES = {".docx", ".tex", ".pdf", ".md"}
FIGURE_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg", ".eps", ".tif", ".tiff"}
CONFIG_NAMES = {
    "requirements.txt", "pyproject.toml", "poetry.lock", "environment.yml", "environment.yaml",
    "package-lock.json", "pnpm-lock.yaml", "renv.lock", "manifest.toml",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def category(relative: str) -> str:
    path = Path(relative)
    lower = relative.lower()
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in CODE_SUFFIXES or name in CONFIG_NAMES:
        return "code_or_environment"
    if suffix in DATA_SUFFIXES or any(token in lower for token in ("/data/", "原始数据", "input")):
        return "data"
    if any(token in lower for token in ("citation", "reference", "参考文献")) or suffix == ".bib":
        return "citation"
    if any(token in lower for token in ("ai-use", "ai_use", "ai工具", "disclosure", "披露")):
        return "ai_disclosure"
    if suffix in FIGURE_SUFFIXES or any(token in lower for token in ("/fig", "/plot", "图表")):
        return "figure"
    if any(token in lower for token in ("/result", "/output", "结果", "ledger")):
        return "result"
    if suffix in PAPER_SUFFIXES or any(token in lower for token in ("paper", "论文", "abstract", "摘要")):
        return "paper"
    if suffix in {".json", ".yaml", ".yml", ".toml"}:
        return "configuration"
    return "support"


DEPENDENCIES = {
    "code_or_environment": {"code", "results", "figures", "paper", "validation", "disclosure"},
    "data": {"data", "code", "results", "figures", "paper", "validation", "disclosure"},
    "configuration": {"code", "results", "validation", "paper"},
    "result": {"results", "figures", "paper", "validation"},
    "figure": {"figures", "paper", "visual_qa"},
    "paper": {"paper", "cross_artifact_consistency", "visual_qa"},
    "citation": {"citations", "paper", "compliance"},
    "ai_disclosure": {"disclosure", "compliance"},
    "support": {"supporting_materials"},
}


def build_report(baseline: Path, current: Path) -> dict:
    old = inventory(baseline)
    new = inventory(current)
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    modified = sorted(path for path in set(old) & set(new) if old[path] != new[path])
    changed = sorted(set(added + removed + modified))
    categories = sorted({category(path) for path in changed})
    scope: set[str] = set()
    for item in categories:
        scope.update(DEPENDENCIES[item])

    full_triggers = {"code_or_environment", "data", "configuration"}
    if not changed:
        mode = "none"
        reason = "No artifact hash changed; reuse the prior verified state."
    elif removed or full_triggers.intersection(categories):
        mode = "full"
        reason = "Core dependency or removal changed; downstream results and claims require full revalidation."
    else:
        mode = "targeted"
        reason = "Only downstream artifacts changed; review the dependency closure shown below."

    return {
        "version": 1,
        "baseline": str(baseline.resolve()),
        "current": str(current.resolve()),
        "baseline_file_count": len(old),
        "current_file_count": len(new),
        "added": added,
        "removed": removed,
        "modified": modified,
        "changed_categories": categories,
        "audit_mode": mode,
        "reason": reason,
        "review_scope": sorted(scope),
        "changed_hashes": {path: {"before": old.get(path), "after": new.get(path)} for path in changed},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true", help="Return 2 when a full audit is required.")
    args = parser.parse_args()
    if not args.baseline.is_dir() or not args.current.is_dir():
        parser.error("baseline and current must be directories")
    report = build_report(args.baseline, args.current)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 2 if args.strict and report["audit_mode"] == "full" else 0


if __name__ == "__main__":
    raise SystemExit(main())
