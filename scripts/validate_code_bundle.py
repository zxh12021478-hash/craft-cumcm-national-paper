#!/usr/bin/env python3
"""Static reproducibility audit for a mathematical-modeling code bundle."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

CODE_SUFFIXES = {".py", ".m", ".r", ".ipynb", ".jl", ".cpp", ".c", ".java"}
ENTRY_NAMES = {"run_all.py", "main.py", "main.m", "run_all.m", "main.r", "main.ipynb"}
DEPENDENCY_NAMES = {"requirements.txt", "environment.yml", "environment.yaml", "pyproject.toml", "Pipfile", "renv.lock", "Manifest.toml"}
LOCK_NAMES = {"uv.lock", "poetry.lock", "Pipfile.lock", "conda-lock.yml", "renv.lock", "Manifest.toml"}
MACHINE_RESULT_SUFFIXES = {".json", ".csv", ".tsv", ".xlsx", ".mat"}
SECRET_PATTERNS = (
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "OpenAI-style key"),
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "Anthropic-style key"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"AKIA[A-Z0-9]{16}"), "AWS access key"),
    (re.compile(r"(?i)(?:api[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*[\"'][^\"']{8,}[\"']"), "credential literal"),
)


def item(severity, code, message, evidence=None):
    out = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        out["evidence"] = evidence
    return out


def inspect(root: Path) -> dict:
    findings = []
    files = [p for p in root.rglob("*") if p.is_file() and not any(part.startswith(".") for part in p.relative_to(root).parts)]
    code_files = [p for p in files if p.suffix.lower() in CODE_SUFFIXES]
    entries = [p for p in code_files if p.name.lower() in ENTRY_NAMES]
    dependencies = [p for p in files if p.name in DEPENDENCY_NAMES]
    locks = [p for p in files if p.name in LOCK_NAMES]
    verification_files = [
        p
        for p in code_files
        if "verification" in {part.lower() for part in p.relative_to(root).parts}
        or p.stem.lower().startswith(("verify_", "test_"))
    ]
    machine_results = [
        p
        for p in files
        if p.suffix.lower() in MACHINE_RESULT_SUFFIXES
        and any(part.lower() in {"result", "results", "output", "outputs"} for part in p.relative_to(root).parts)
    ]
    if not code_files:
        findings.append(item("Blocker", "NO_CODE", "No supported source-code files were found."))
    if not entries:
        findings.append(item("Major", "NO_ENTRYPOINT", "No conventional reproducible entry point was found."))
    if not dependencies:
        findings.append(item("Major", "NO_DEPENDENCIES", "No dependency/environment specification was found."))
    if dependencies and not locks:
        findings.append(item("Major", "NO_DEPENDENCY_LOCK", "Dependencies are declared but no lock file was found; record exact versions before final submission."))
    if code_files and not verification_files:
        findings.append(
            item(
                "Critical",
                "NO_INDEPENDENT_VERIFICATION",
                "No separate verification/test script was found. Solver output must be checked independently before it enters the paper.",
            )
        )
    if code_files and not machine_results:
        findings.append(item("Major", "NO_MACHINE_RESULTS", "No machine-readable result artifact was found under a results/output directory."))

    abs_paths = []
    placeholders = []
    syntax_errors = []
    random_users = []
    seed_users = []
    silent_exceptions = []
    external_urls = []
    secret_hits = []
    for path in code_files:
        rel = str(path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            findings.append(item("Critical", "READ_ERROR", f"Cannot read {rel}: {exc}"))
            continue
        for match in re.findall(r"(?:[A-Za-z]:\\\\[^\"'\n]+|/(?:Users|home|tmp|var|opt)/[^\"'\n]+)", text):
            abs_paths.append({"file": rel, "path": match[:160]})
        if re.search(r"TODO|TBD|FIXME|待补充|此处修改|YOUR_PATH", text, re.I):
            placeholders.append(rel)
        if re.search(r"numpy\.random|np\.random|random\.|rand\(|randn\(|rng\(", text):
            random_users.append(rel)
        if re.search(r"random\.seed|np\.random\.seed|default_rng\s*\(|rng\s*\(\s*\d+|seed\s*=", text):
            seed_users.append(rel)
        if re.search(r"except\s*:\s*(?:\n\s*)?pass|catch\s*\n?\s*$", text, re.M):
            silent_exceptions.append(rel)
        external_urls.extend({"file": rel, "url": u} for u in re.findall(r"https?://[^\s\"')]+", text))
        for pattern, label in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                secret_hits.append({"file": rel, "line": text[:match.start()].count("\n") + 1, "type": label})
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=rel)
            except SyntaxError as exc:
                syntax_errors.append({"file": rel, "line": exc.lineno, "message": exc.msg})

    if syntax_errors:
        findings.append(item("Critical", "SYNTAX", "Python syntax errors were detected.", syntax_errors))
    if abs_paths:
        findings.append(item("Critical", "ABSOLUTE_PATHS", "Machine-specific absolute paths were detected.", abs_paths[:30]))
    if placeholders:
        findings.append(item("Critical", "PLACEHOLDERS", "Unresolved code placeholders were detected.", sorted(set(placeholders))))
    if random_users and not seed_users:
        findings.append(item("Major", "RANDOM_SEED", "Stochastic code was detected without an obvious fixed-seed protocol.", sorted(set(random_users))))
    if silent_exceptions:
        findings.append(item("Major", "SILENT_ERRORS", "Silent exception handling may hide failed computations.", sorted(set(silent_exceptions))))
    if secret_hits:
        findings.append(item("Blocker", "POSSIBLE_SECRET", "Possible credential literals were detected; remove them before sharing or packaging.", secret_hits[:30]))

    unpinned = []
    for dependency in dependencies:
        if dependency.name != "requirements.txt":
            continue
        for line_number, raw in enumerate(dependency.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith(("#", "-", "git+", "http://", "https://")):
                continue
            if not re.search(r"(?:==|===|~=)", line):
                unpinned.append({"file": str(dependency.relative_to(root)), "line": line_number, "requirement": line})
    if unpinned:
        findings.append(item("Major", "UNPINNED_DEPENDENCIES", "Some Python requirements are not pinned or compatibly constrained.", unpinned[:40]))

    support_docs = [p for p in files if p.name.lower() in {"readme.md", "readme.txt", "说明.txt", "数据说明.md"}]
    if not support_docs:
        findings.append(item("Minor", "NO_BUNDLE_GUIDE", "No concise run/data guide was found in the code bundle."))

    metrics = {
        "total_files": len(files),
        "code_files": len(code_files),
        "entrypoints": [str(p.relative_to(root)) for p in entries],
        "dependency_files": [str(p.relative_to(root)) for p in dependencies],
        "lock_files": [str(p.relative_to(root)) for p in locks],
        "verification_files": [str(p.relative_to(root)) for p in verification_files],
        "machine_result_files": [str(p.relative_to(root)) for p in machine_results],
        "external_url_count": len(external_urls),
    }
    return {"root": str(root), "metrics": metrics, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.root.is_dir():
        print(json.dumps({"error": "directory not found", "root": str(args.root)}, ensure_ascii=False))
        return 2
    report = inspect(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
        for finding in report["findings"]:
            print(f"[{finding['severity']}] {finding['code']}: {finding['message']}")
    severities = {x["severity"] for x in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
