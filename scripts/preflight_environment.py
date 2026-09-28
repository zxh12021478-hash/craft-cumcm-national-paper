#!/usr/bin/env python3
"""Check the local environment before a CUMCM strategy, takeover, or final audit."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import shutil
import sys
from pathlib import Path

PACKAGE_IMPORTS = {
    "jsonschema": "jsonschema",
    "pypdf": "pypdf",
    "python-docx": "docx",
    "Pillow": "PIL",
    "PyYAML": "yaml",
}
PROFILE_REQUIREMENTS = {
    "strategy": {"packages": set(), "binaries": set()},
    "takeover": {"packages": {"jsonschema", "PyYAML"}, "binaries": set()},
    "final": {
        "packages": {"jsonschema", "pypdf", "python-docx", "Pillow", "PyYAML"},
        "binaries": {"soffice", "pdftoppm"},
    },
}
OPTIONAL_BINARIES = ("uv", "academic-refchecker", "matlab", "octave", "Rscript", "julia")


def pinned_versions() -> dict[str, str]:
    requirements = Path(__file__).resolve().parent / "requirements-validator.txt"
    pins = {}
    for raw in requirements.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, version = line.split("==", 1)
        pins[name.strip().lower()] = version.strip()
    return pins


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def inspect(profile: str) -> dict:
    required = PROFILE_REQUIREMENTS[profile]
    pins = pinned_versions()
    packages = {}
    binaries = {}
    findings = []
    for distribution, import_name in PACKAGE_IMPORTS.items():
        available = importlib.util.find_spec(import_name) is not None
        version = None
        if available:
            try:
                version = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError:
                pass
        packages[distribution] = {"available": available, "version": version}
        if distribution in required["packages"] and not available:
            findings.append(
                finding(
                    "Critical",
                    "MISSING_PACKAGE",
                    f"{distribution} is required for the {profile} profile.",
                    {"import": import_name},
                )
            )
        expected = pins.get(distribution.lower())
        if distribution in required["packages"] and available and expected and version != expected:
            findings.append(
                finding(
                    "Critical",
                    "PACKAGE_VERSION_MISMATCH",
                    f"{distribution} {version!r} is installed; pinned version is {expected!r}.",
                    {"distribution": distribution, "installed": version, "expected": expected},
                )
            )
    for binary in sorted(required["binaries"] | set(OPTIONAL_BINARIES)):
        path = shutil.which(binary)
        binaries[binary] = path
        if binary in required["binaries"] and path is None:
            findings.append(
                finding("Critical", "MISSING_BINARY", f"{binary} is required for the {profile} profile.")
            )
    return {
        "profile": profile,
        "python": sys.executable,
        "python_version": sys.version.split()[0],
        "packages": packages,
        "pinned_versions": pins,
        "binaries": binaries,
        "requirements_file": str(Path(__file__).resolve().parent / "requirements-validator.txt"),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=tuple(PROFILE_REQUIREMENTS), default="takeover")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = inspect(args.profile)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
