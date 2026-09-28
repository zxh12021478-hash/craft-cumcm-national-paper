#!/usr/bin/env python3
"""Run one deterministic readiness check for the CUMCM skill and validator runtime."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = SKILL_ROOT / "assets" / "workflows" / "validator-runtime.json"
RULE_MANIFEST = SKILL_ROOT / "assets" / "rules" / "cumcm-current-rules.json"
RULE_SNAPSHOT = SKILL_ROOT / "assets" / "rules" / "cumcm-current-rules.snapshot.json"


def finding(severity: str, code: str, message: str, evidence: Any = None) -> dict[str, Any]:
    row: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        row["evidence"] = evidence
    return row


def run(command: list[str], timeout: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-6000:],
            "stderr_tail": completed.stderr[-3000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "stdout_tail": (exc.stdout or "")[-6000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-3000:] if isinstance(exc.stderr, str) else "",
            "timed_out": True,
        }


def check_write_access(directory: Path) -> bool:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        descriptor, raw = tempfile.mkstemp(prefix=".cumcm-write-test-", dir=directory)
        os.close(descriptor)
        Path(raw).unlink()
        return True
    except OSError:
        return False


def load_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1:
        raise ValueError("validator runtime config must have version 1")
    return payload


def requirement_names() -> list[str]:
    requirements = SKILL_ROOT / "scripts" / "requirements-validator.txt"
    return [
        line.split("==", 1)[0].strip().lower().replace("-", "_")
        for line in requirements.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "==" in line
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the pinned CUMCM runtime and skill before competition use.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--validator-python", type=Path)
    parser.add_argument("--wheelhouse", type=Path)
    parser.add_argument("--online", action="store_true", help="Also compare current official pages to the frozen snapshot.")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--skip-instruction-budget", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    config_path = args.config.expanduser().resolve()
    project_root = args.project_root.expanduser().resolve()
    findings: list[dict[str, Any]] = []
    checks: dict[str, Any] = {}
    try:
        config = load_config(config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {"status": "fail", "findings": [finding("Blocker", "RUNTIME_CONFIG", str(exc))]}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    validator = (args.validator_python or (Path.home() / config["home_relative_python"])).expanduser().absolute()
    requested_wheelhouse = args.wheelhouse or (Path.home() / config["home_relative_wheelhouse"])
    wheelhouse = requested_wheelhouse.expanduser().resolve()
    bundled_wheelhouse = SKILL_ROOT / str(config.get("skill_relative_wheelhouse", ""))
    if not args.wheelhouse and (not wheelhouse.is_dir() or not any(wheelhouse.glob("*.whl"))) and bundled_wheelhouse.is_dir():
        wheelhouse = bundled_wheelhouse.resolve()
    checks["validator_python"] = str(validator)
    checks["wheelhouse"] = str(wheelhouse)
    if not validator.is_file() or not os.access(validator, os.X_OK):
        findings.append(
            finding(
                "Blocker",
                "PINNED_RUNTIME_MISSING",
                "固定校验环境不存在或不可执行。",
                {
                    "expected": str(validator),
                    "repair": [
                        sys.executable,
                        str(SKILL_ROOT / "scripts" / "bootstrap_validator_env.py"),
                        "--destination",
                        str(validator.parent.parent),
                        "--wheelhouse",
                        str(wheelhouse),
                    ],
                },
            )
        )
    wheel_files = list(wheelhouse.glob("*.whl")) if wheelhouse.is_dir() else []
    if not wheel_files:
        findings.append(finding("Critical", "OFFLINE_WHEELHOUSE_MISSING", "离线依赖仓不存在或为空。", str(wheelhouse)))
    else:
        normalized_wheels = [path.name.lower().replace("-", "_") for path in wheel_files]
        missing_direct = [name for name in requirement_names() if not any(wheel.startswith(name + "_") for wheel in normalized_wheels)]
        checks["offline_direct_requirements"] = {"required": requirement_names(), "missing": missing_direct}
        if missing_direct:
            findings.append(finding("Critical", "OFFLINE_WHEEL_INCOMPLETE", "离线依赖仓缺少直接依赖。", missing_direct))

    current_platform = {"system": platform.system(), "machine": platform.machine()}
    checks["platform"] = current_platform
    if current_platform != {"system": config.get("platform_system"), "machine": config.get("platform_machine")}:
        findings.append(finding("Critical", "RUNTIME_PLATFORM_MISMATCH", "当前平台与固定离线运行环境不一致。", {"current": current_platform, "expected": {"system": config.get("platform_system"), "machine": config.get("platform_machine")}}))

    if not project_root.is_dir():
        findings.append(finding("Blocker", "PROJECT_ROOT_MISSING", "项目目录不存在。", str(project_root)))
    else:
        usage = shutil.disk_usage(project_root)
        checks["disk"] = {"free_bytes": usage.free, "minimum_free_bytes": int(config["minimum_free_bytes"])}
        if usage.free < int(config["minimum_free_bytes"]):
            findings.append(finding("Critical", "LOW_DISK_SPACE", "可用磁盘空间低于赛时安全下限。", checks["disk"]))
        write_target = project_root / ".cumcm"
        checks["project_write_access"] = check_write_access(write_target)
        if not checks["project_write_access"]:
            findings.append(finding("Blocker", "PROJECT_NOT_WRITABLE", "无法写入项目的 .cumcm 状态目录。", str(write_target)))

    if validator.is_file() and os.access(validator, os.X_OK):
        preflight = run(
            [str(validator), str(SKILL_ROOT / "scripts" / "preflight_environment.py"), "--profile", "final", "--json", "--strict"],
            args.timeout,
        )
        checks["final_preflight"] = preflight
        if preflight["returncode"] != 0:
            findings.append(finding("Blocker", "FINAL_PREFLIGHT_FAILED", "固定环境未通过 final 严格预检。", preflight))
        else:
            try:
                actual_python = json.loads(preflight["stdout_tail"])["python_version"]
            except (KeyError, TypeError, json.JSONDecodeError):
                actual_python = None
            checks["python_version"] = {"actual": actual_python, "expected": config.get("python_version")}
            if actual_python != config.get("python_version"):
                findings.append(finding("Critical", "PYTHON_VERSION_MISMATCH", "固定环境的 Python 版本与锁定值不一致。", checks["python_version"]))
        if not args.skip_tests:
            tests = run([str(validator), "-m", "unittest", "discover", "-s", str(SKILL_ROOT / "tests"), "-p", "test_*.py"], args.timeout)
            checks["regression_tests"] = tests
            if tests["returncode"] != 0:
                findings.append(finding("Blocker", "REGRESSION_FAILED", "Skill 回归测试未全部通过。", tests))

    if not args.skip_instruction_budget:
        budget_python = str(validator) if validator.is_file() else sys.executable
        budget = run([budget_python, str(SKILL_ROOT / "scripts" / "measure_instruction_budget.py"), "--strict"], args.timeout)
        checks["instruction_budget"] = budget
        if budget["returncode"] != 0:
            findings.append(finding("Critical", "INSTRUCTION_BUDGET_FAILED", "路由指令预算超限或检查失败。", budget))

    if args.online:
        rule_python = str(validator) if validator.is_file() else sys.executable
        rules = run(
            [
                rule_python,
                str(SKILL_ROOT / "scripts" / "check_official_rules.py"),
                "--manifest",
                str(RULE_MANIFEST),
                "--snapshot",
                str(RULE_SNAPSHOT),
                "--strict",
            ],
            args.timeout,
        )
        checks["official_rules"] = rules
        if rules["returncode"] != 0:
            findings.append(finding("Critical", "OFFICIAL_RULE_CHECK_FAILED", "官方规则页检查失败、已变化或需人工复核。", rules))

    severe = {item["severity"] for item in findings}
    status = "pass" if not ({"Blocker", "Critical"} & severe) else "fail"
    if not args.strict and status == "pass" and "Major" in severe:
        status = "warn"
    report = {
        "version": 1,
        "runtime_id": config["runtime_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "config": str(config_path),
        "skill_root": str(SKILL_ROOT),
        "project_root": str(project_root),
        "checks": checks,
        "findings": findings,
        "recommended_validator_python": str(validator),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if status == "pass" or (status == "warn" and not args.strict) else 2


if __name__ == "__main__":
    raise SystemExit(main())
