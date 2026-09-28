#!/usr/bin/env python3
"""Create and verify one pinned Python environment for all final CUMCM validators."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import venv
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = SKILL_ROOT / "scripts" / "requirements-validator.txt"


def env_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path(".cumcm/validator-venv"),
        help="New environment directory; an existing destination is never overwritten.",
    )
    parser.add_argument("--wheelhouse", type=Path, help="Optional pre-downloaded wheel directory for offline setup.")
    parser.add_argument("--plan", action="store_true", help="Print the commands without creating or installing anything.")
    args = parser.parse_args()
    destination = args.destination.resolve()
    python = env_python(destination)
    install = [
        str(python),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
    ]
    if args.wheelhouse:
        wheelhouse = args.wheelhouse.resolve()
        install.extend(["--no-index", "--find-links", str(wheelhouse)])
    install.extend(["-r", str(REQUIREMENTS)])
    preflight = [
        str(python),
        str(SKILL_ROOT / "scripts" / "preflight_environment.py"),
        "--profile",
        "final",
        "--json",
    ]
    plan = {
        "destination": str(destination),
        "requirements": str(REQUIREMENTS),
        "create": [sys.executable, "-m", "venv", str(destination)],
        "install": install,
        "verify": preflight,
    }
    if args.plan:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    if destination.exists():
        print(
            json.dumps(
                {
                    "error": "destination already exists; choose a new path instead of overwriting it",
                    "destination": str(destination),
                },
                ensure_ascii=False,
            )
        )
        return 2
    if args.wheelhouse and not args.wheelhouse.resolve().is_dir():
        print(json.dumps({"error": "wheelhouse not found", "wheelhouse": str(args.wheelhouse.resolve())}, ensure_ascii=False))
        return 2
    destination.parent.mkdir(parents=True, exist_ok=True)
    venv.EnvBuilder(with_pip=True, clear=False).create(destination)
    installed = subprocess.run(install, text=True)
    if installed.returncode:
        return installed.returncode
    verified = subprocess.run(preflight, text=True)
    return verified.returncode


if __name__ == "__main__":
    raise SystemExit(main())
