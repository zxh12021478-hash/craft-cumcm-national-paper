#!/usr/bin/env python3
"""Unified, low-friction orchestration for the CUMCM two-system workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
PROFILE_FILE = SKILL_ROOT / "assets" / "workflows" / "workflow-profiles.json"
CONFIG_RELATIVE = Path(".cumcm") / "workflow.json"
NON_HUMAN_REVIEWER = re.compile(r"(?i)(?:\bai\b|\bgpt\b|\bcodex\b|assistant|模型|机器人)")
GATE_ORDER = (
    "problem_reconciliation",
    "model_selection",
    "baseline_deviation",
    "result_acceptance",
    "final_submission",
)
TEMPLATE_MAP = {
    "problem_reconciliation": "题面核对签字模板.json",
    "strategy_contract": "求解策略合同模板.json",
    "external_handoff": "外部基线交接清单模板.json",
    "execution_manifest": "干净运行清单模板.json",
    "result_ledger": "核心结果台账模板.json",
    "truth_checks": "独立真值检查模板.json",
    "innovation_tournament": "结构洞察淘汰赛模板.json",
    "innovation_calibration": "创新盲测校准台账模板.json",
    "citation_manifest": "参考文献核验清单模板.json",
    "ai_use_manifest": "AI工具使用详情内部清单模板.json",
    "team_audit": "全员理解审计模板.json",
    "visual_qa": "页面人工复核记录模板.json",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def finding(severity: str, code: str, message: str, evidence: Any = None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_digest(path: Path) -> str:
    if path.is_file():
        return sha256(path)
    if path.is_dir():
        digest = hashlib.sha256()
        for item in sorted(path.rglob("*")):
            if not item.is_file() or ".git" in item.parts or ".cumcm" in item.parts:
                continue
            digest.update(str(item.relative_to(path)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(sha256(item).encode("ascii"))
            digest.update(b"\0")
        return digest.hexdigest()
    raise FileNotFoundError(path)


def load_profiles() -> dict:
    payload = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    return payload["profiles"]


def config_path(root: Path) -> Path:
    return root.resolve() / CONFIG_RELATIVE


def load_config(root: Path) -> dict:
    path = config_path(root)
    if not path.is_file():
        raise FileNotFoundError(f"workflow not initialized: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(root: Path, payload: dict) -> None:
    payload["updated_at"] = now()
    atomic_write(config_path(root), payload)


def project_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def relative_or_absolute(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def init_project(root: Path, problem: str, deadline: str | None, profile: str) -> dict:
    profiles = load_profiles()
    if profile not in profiles:
        raise ValueError(f"unknown profile: {profile}")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = config_path(root)
    if path.exists():
        raise FileExistsError(f"workflow already initialized: {path}")
    for directory in (
        ".cumcm/contracts",
        ".cumcm/reports",
        "strategy",
        "handoff",
        "baseline",
        "results",
        "figures",
        "verifications",
        "submission",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    template_root = SKILL_ROOT / "assets" / "templates"
    contracts = {}
    for key, filename in TEMPLATE_MAP.items():
        source = template_root / filename
        target = root / ".cumcm" / "contracts" / filename
        shutil.copy2(source, target)
        contracts[key] = relative_or_absolute(root, target)
    payload = {
        "version": 1,
        "problem": problem,
        "deadline": deadline,
        "profile": profile,
        "created_at": now(),
        "updated_at": now(),
        "gates": {
            gate: {
                "status": "pending",
                "approved_at": None,
                "approved_by": None,
                "rationale": None,
                "evidence": [],
            }
            for gate in GATE_ORDER
        },
        "contracts": contracts,
        "artifacts": {},
        "declarations": {
            "ai_used": "unknown",
            "external_baseline_used": "unknown",
        },
        "events": [{"at": now(), "action": "init", "profile": profile}],
    }
    save_config(root, payload)
    return payload


def required_artifact_gaps(config: dict) -> list[str]:
    profiles = load_profiles()
    profile = profiles[config["profile"]]
    required = list(profile.get("required_artifacts", []))
    if config.get("declarations", {}).get("external_baseline_used") == "no":
        required = [name for name in required if name not in {"baseline_inventory", "external_handoff"}]
    gaps = []
    for name in required:
        record = config.get("artifacts", {}).get(name)
        if not record or record.get("passed") is False:
            gaps.append(name)
    return gaps


def artifact_integrity_gaps(root: Path, config: dict, names: list[str]) -> list[str]:
    gaps = []
    for name in names:
        record = config.get("artifacts", {}).get(name)
        if not record or not record.get("path"):
            continue
        path = project_path(root, record["path"])
        if not path.exists():
            gaps.append(f"{name}:missing")
            continue
        expected = record.get("sha256")
        if expected and path_digest(path) != expected:
            gaps.append(f"{name}:changed")
    return gaps


def status_report(root: Path) -> dict:
    config = load_config(root)
    profiles = load_profiles()
    profile = profiles[config["profile"]]
    pending_gates = [gate for gate in profile["human_gates"] if config["gates"][gate]["status"] != "approved"]
    return {
        "root": str(root.resolve()),
        "problem": config["problem"],
        "profile": config["profile"],
        "profile_purpose": profile["purpose"],
        "pending_human_gates": pending_gates,
        "missing_strict_artifacts": required_artifact_gaps(config),
        "artifacts": config.get("artifacts", {}),
        "declarations": config.get("declarations", {}),
    }


def approve_gate(root: Path, gate: str, reviewer: str, rationale: str, evidence: list[str]) -> dict:
    config = load_config(root)
    if gate not in config["gates"]:
        raise ValueError(f"unknown human gate: {gate}")
    if NON_HUMAN_REVIEWER.search(reviewer):
        raise ValueError("human gate cannot be approved by an AI identity")
    if not reviewer.strip() or not rationale.strip():
        raise ValueError("approval requires a real reviewer and rationale")
    evidence_paths = []
    for item in evidence:
        path = project_path(root, item)
        if not path.exists():
            raise FileNotFoundError(f"approval evidence missing: {path}")
        evidence_paths.append(relative_or_absolute(root, path))
    if not evidence_paths:
        raise ValueError("approval requires at least one existing evidence artifact")
    artifacts = config.get("artifacts", {})
    if gate == "model_selection":
        innovation = artifacts.get("innovation_report")
        tournament = artifacts.get("innovation_tournament")
        if not innovation or not innovation.get("passed") or innovation.get("phase") != "freeze":
            raise ValueError("model_selection requires a passing freeze-phase innovation tournament")
        if not tournament:
            raise ValueError("model_selection requires the audited innovation tournament")
        integrity_gaps = artifact_integrity_gaps(
            root,
            config,
            ["innovation_tournament", "innovation_report"],
        )
        if integrity_gaps:
            raise ValueError(f"model_selection found changed innovation evidence: {', '.join(integrity_gaps)}")
        report_path = project_path(root, innovation["path"])
        report_payload = json.loads(report_path.read_text(encoding="utf-8"))
        if (
            report_payload.get("phase") != "freeze"
            or report_payload.get("summary", {}).get("passed") is not True
            or report_payload.get("tournament_sha256") != tournament.get("sha256")
        ):
            raise ValueError("model_selection innovation report is not bound to the frozen tournament")
    if gate == "baseline_deviation":
        baseline_used = config.get("declarations", {}).get("external_baseline_used")
        if baseline_used == "unknown":
            raise ValueError("declare whether an external baseline was used before baseline_deviation")
        if baseline_used == "yes" and "baseline_inventory" not in artifacts:
            raise ValueError("baseline_deviation requires a baseline inventory when an external baseline was used")
    if gate == "result_acceptance":
        required_reports = [artifacts.get("reproduction_report"), artifacts.get("truth_report")]
        if not all(report and report.get("passed") for report in required_reports):
            raise ValueError("result_acceptance requires passing reproduction and truth reports")
    if gate == "final_submission":
        final_report = artifacts.get("final_report")
        if not final_report or not final_report.get("passed"):
            raise ValueError("final_submission requires a passing final report")
    config["gates"][gate] = {
        "status": "approved",
        "approved_at": now(),
        "approved_by": reviewer,
        "rationale": rationale,
        "evidence": evidence_paths,
    }
    config["events"].append({"at": now(), "action": "approve", "gate": gate, "by": reviewer})
    save_config(root, config)
    return config["gates"][gate]


def freeze_strategy(root: Path, artifacts: list[str]) -> dict:
    config = load_config(root)
    profile = load_profiles()[config["profile"]]
    missing_gates = [
        gate
        for gate in profile["required_before_strategy_freeze"]
        if config["gates"][gate]["status"] != "approved"
    ]
    if missing_gates:
        raise ValueError(f"strategy freeze blocked by human gates: {', '.join(missing_gates)}")
    required_machine = list(profile.get("required_machine_artifacts_before_strategy_freeze", []))
    missing_machine = [
        name
        for name in required_machine
        if not config.get("artifacts", {}).get(name)
        or config["artifacts"][name].get("passed") is False
    ]
    if missing_machine:
        raise ValueError(f"strategy freeze blocked by machine evidence: {', '.join(missing_machine)}")
    changed_machine = artifact_integrity_gaps(root, config, required_machine)
    if changed_machine:
        raise ValueError(f"strategy freeze found changed innovation evidence: {', '.join(changed_machine)}")
    records = []
    for item in artifacts:
        path = project_path(root, item)
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append(
            {
                "path": relative_or_absolute(root, path),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    if not records:
        raise ValueError("freeze requires at least one strategy artifact")
    payload = {
        "version": 1,
        "problem": config["problem"],
        "frozen_at": now(),
        "artifacts": records,
        "human_approvals": {
            gate: config["gates"][gate] for gate in profile["required_before_strategy_freeze"]
        },
    }
    target = root / ".cumcm" / "strategy-freeze.json"
    atomic_write(target, payload)
    config["artifacts"]["strategy_freeze"] = {
        "path": relative_or_absolute(root, target),
        "sha256": sha256(target),
    }
    config["events"].append({"at": now(), "action": "freeze_strategy"})
    save_config(root, config)
    return payload


def inventory_files(source: Path) -> list[dict]:
    records = []
    for path in sorted(source.rglob("*")):
        if not path.is_file() or ".git" in path.parts or ".cumcm" in path.parts:
            continue
        records.append(
            {
                "path": str(path.relative_to(source)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return records


def ingest_baseline(
    root: Path,
    source: str,
    tool_name: str,
    tool_version: str,
    interaction_log: str | None,
) -> dict:
    config = load_config(root)
    if "strategy_freeze" not in config["artifacts"]:
        raise ValueError("baseline ingest requires a frozen strategy")
    source_path = project_path(root, source)
    if not source_path.is_dir():
        raise NotADirectoryError(source_path)
    log_record = None
    if interaction_log:
        log_path = project_path(root, interaction_log)
        if not log_path.is_file():
            raise FileNotFoundError(log_path)
        log_record = {
            "path": relative_or_absolute(root, log_path),
            "sha256": sha256(log_path),
        }
    payload = {
        "version": 1,
        "ingested_at": now(),
        "source_root": relative_or_absolute(root, source_path),
        "generating_system": {"tool": tool_name, "version": tool_version},
        "strategy_freeze": config["artifacts"]["strategy_freeze"],
        "interaction_log": log_record,
        "files": inventory_files(source_path),
    }
    target = root / ".cumcm" / "baseline-inventory.json"
    atomic_write(target, payload)
    config["artifacts"]["baseline_inventory"] = {
        "path": relative_or_absolute(root, target),
        "sha256": sha256(target),
        "file_count": len(payload["files"]),
        "interaction_log_present": bool(log_record),
    }
    config["declarations"]["external_baseline_used"] = "yes"
    config["events"].append({"at": now(), "action": "ingest_baseline", "tool": tool_name})
    save_config(root, config)
    return payload


def register_artifact(root: Path, kind: str, path_value: str) -> dict:
    config = load_config(root)
    path = project_path(root, path_value)
    if not path.exists():
        raise FileNotFoundError(path)
    record = {
        "path": relative_or_absolute(root, path),
        "sha256": path_digest(path),
        "kind": "file" if path.is_file() else "directory",
    }
    if path.is_file():
        record["size_bytes"] = path.stat().st_size
    config["artifacts"][kind] = record
    config["events"].append({"at": now(), "action": "register", "kind": kind})
    save_config(root, config)
    return record


def set_declarations(root: Path, ai_used: str | None, external_baseline_used: str | None) -> dict:
    config = load_config(root)
    if ai_used:
        config["declarations"]["ai_used"] = ai_used
    if external_baseline_used:
        config["declarations"]["external_baseline_used"] = external_baseline_used
    config["events"].append({"at": now(), "action": "set_declarations"})
    save_config(root, config)
    return config["declarations"]


def set_profile(root: Path, profile: str) -> dict:
    config = load_config(root)
    if profile not in load_profiles():
        raise ValueError(f"unknown profile: {profile}")
    old = config["profile"]
    config["profile"] = profile
    config["events"].append({"at": now(), "action": "set_profile", "from": old, "to": profile})
    save_config(root, config)
    return {"profile": profile, "missing_strict_artifacts": required_artifact_gaps(config)}


def run_child(command: list[str], output: Path) -> tuple[int, dict]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if output.is_file():
        try:
            report = json.loads(output.read_text(encoding="utf-8"))
        except Exception:
            report = {"stdout": completed.stdout, "stderr": completed.stderr}
    else:
        report = {"stdout": completed.stdout, "stderr": completed.stderr}
    return completed.returncode, report


def reproduce(root: Path, code_root: str, manifest: str) -> tuple[int, dict]:
    config = load_config(root)
    code_path = project_path(root, code_root)
    manifest_path = project_path(root, manifest)
    target = root / ".cumcm" / "reports" / "reproduction.json"
    command = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "execute_submission.py"),
        str(code_path),
        "--manifest",
        str(manifest_path),
        "--output",
        str(target),
        "--json",
    ]
    returncode, report = run_child(command, target)
    reproduction_record = {
        "path": relative_or_absolute(root, target),
        "passed": returncode == 0,
    }
    if target.is_file():
        reproduction_record["sha256"] = sha256(target)
    config["artifacts"]["reproduction_report"] = reproduction_record
    config["events"].append({"at": now(), "action": "reproduce", "returncode": returncode})
    save_config(root, config)
    return returncode, report


def run_truth_checks(root: Path, manifest: str) -> tuple[int, dict]:
    config = load_config(root)
    manifest_path = project_path(root, manifest)
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    target = root / ".cumcm" / "reports" / "truth-checks.json"
    command = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "truth_harness.py"),
        str(manifest_path),
        "--root",
        str(root.resolve()),
        "--output",
        str(target),
        "--json",
    ]
    returncode, report = run_child(command, target)
    truth_record = {
        "path": relative_or_absolute(root, target),
        "passed": returncode == 0,
    }
    if target.is_file():
        truth_record["sha256"] = sha256(target)
    config["artifacts"]["truth_report"] = truth_record
    config["events"].append({"at": now(), "action": "truth_check", "returncode": returncode})
    save_config(root, config)
    return returncode, report


def run_innovation_audit(
    root: Path,
    manifest: str,
    phase: str,
    weights: str | None,
) -> tuple[int, dict]:
    config = load_config(root)
    manifest_path = project_path(root, manifest)
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    target = root / ".cumcm" / "reports" / f"innovation-{phase}.json"
    command = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "innovation_tournament.py"),
        str(manifest_path),
        "--root",
        str(root.resolve()),
        "--phase",
        phase,
        "--output",
        str(target),
        "--json",
    ]
    weights_path = None
    if weights:
        weights_path = project_path(root, weights)
        if not weights_path.is_file():
            raise FileNotFoundError(weights_path)
        command.extend(["--weights", str(weights_path)])
    returncode, report = run_child(command, target)
    config["artifacts"]["innovation_tournament"] = {
        "path": relative_or_absolute(root, manifest_path),
        "sha256": sha256(manifest_path),
        "kind": "file",
    }
    report_record = {
        "path": relative_or_absolute(root, target),
        "passed": returncode == 0,
        "phase": phase,
    }
    if target.is_file():
        report_record["sha256"] = sha256(target)
    config["artifacts"]["innovation_report"] = report_record
    if weights_path:
        config["artifacts"]["innovation_weights"] = {
            "path": relative_or_absolute(root, weights_path),
            "sha256": sha256(weights_path),
            "kind": "file",
        }
    config["events"].append(
        {"at": now(), "action": "innovation_audit", "phase": phase, "returncode": returncode}
    )
    save_config(root, config)
    return returncode, report


def run_innovation_calibration(
    root: Path,
    ledger: str,
    output_weights: str | None,
) -> tuple[int, dict]:
    config = load_config(root)
    ledger_path = project_path(root, ledger)
    if not ledger_path.is_file():
        raise FileNotFoundError(ledger_path)
    target = root / ".cumcm" / "reports" / "innovation-calibration.json"
    weights_target = project_path(root, output_weights) if output_weights else None
    command = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "calibrate_innovation_selector.py"),
        str(ledger_path),
        "--root",
        str(root.resolve()),
        "--output",
        str(target),
        "--json",
    ]
    if weights_target:
        command.extend(["--output-weights", str(weights_target)])
    returncode, report = run_child(command, target)
    config["artifacts"]["innovation_calibration_ledger"] = {
        "path": relative_or_absolute(root, ledger_path),
        "sha256": sha256(ledger_path),
        "kind": "file",
    }
    calibration_record = {
        "path": relative_or_absolute(root, target),
        "passed": returncode == 0,
        "status": report.get("status"),
    }
    if target.is_file():
        calibration_record["sha256"] = sha256(target)
    config["artifacts"]["innovation_calibration_report"] = calibration_record
    if weights_target and weights_target.is_file():
        config["artifacts"]["innovation_weights_proposal"] = {
            "path": relative_or_absolute(root, weights_target),
            "sha256": sha256(weights_target),
            "kind": "file",
            "requires_team_approval_before_activation": True,
        }
    config["events"].append(
        {"at": now(), "action": "innovation_calibration", "returncode": returncode}
    )
    save_config(root, config)
    return returncode, report


VALIDATOR_ARTIFACT_ARGS = {
    "paper": "--paper",
    "code": "--code",
    "ai_disclosure": "--ai-disclosure",
    "ai_use_manifest": "--ai-use-manifest",
    "result_ledger": "--result-ledger",
    "citation_manifest": "--citation-manifest",
    "execution_manifest": "--execution-manifest",
    "team_audit": "--team-audit",
    "external_handoff": "--handoff-manifest",
    "visual_qa": "--visual-qa",
}


def validation_command(root: Path, strict: bool) -> tuple[list[str], Path]:
    config = load_config(root)
    submission = config["artifacts"].get("submission")
    if not submission:
        raise ValueError("register the submission directory before audit")
    target_name = "final-validation.json" if strict else "working-audit.json"
    target = root / ".cumcm" / "reports" / target_name
    command = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "validate_submission.py"),
        str(project_path(root, submission["path"])),
        "--ai-used",
        config["declarations"]["ai_used"],
        "--external-baseline-used",
        config["declarations"]["external_baseline_used"],
        "--workflow-record",
        str(config_path(root)),
        "--output",
        str(target),
        "--json",
    ]
    for kind, flag in VALIDATOR_ARTIFACT_ARGS.items():
        record = config["artifacts"].get(kind)
        if record:
            command.extend([flag, str(project_path(root, record["path"]))])
    if strict:
        render_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        render_dir = root / ".cumcm" / "reports" / f"final-render-{render_stamp}"
        command.extend(
            [
                "--strict",
                "--run-clean",
                "--online",
                "--external-refchecker",
                "auto",
                "--render-dir",
                str(render_dir),
            ]
        )
    return command, target


def audit_submission(root: Path, strict: bool) -> tuple[int, dict]:
    config = load_config(root)
    if strict:
        if config["profile"] != "final-strict":
            raise ValueError("switch to final-strict before final-check")
        profile = load_profiles()[config["profile"]]
        missing_gates = [
            gate
            for gate in profile["required_before_final_check"]
            if config["gates"][gate]["status"] != "approved"
        ]
        if missing_gates:
            raise ValueError(f"final-check blocked by human gates: {', '.join(missing_gates)}")
        missing_artifacts = required_artifact_gaps(config)
        if missing_artifacts:
            raise ValueError(f"final-check missing artifacts: {', '.join(missing_artifacts)}")
        required_names = list(profile.get("required_artifacts", []))
        if config.get("declarations", {}).get("external_baseline_used") == "no":
            required_names = [name for name in required_names if name not in {"baseline_inventory", "external_handoff"}]
        integrity_gaps = artifact_integrity_gaps(root, config, required_names)
        if integrity_gaps:
            raise ValueError(f"final-check found missing or changed registered artifacts: {', '.join(integrity_gaps)}")
    command, target = validation_command(root, strict)
    returncode, report = run_child(command, target)
    config = load_config(root)
    artifact_name = "final_report" if strict else "working_audit"
    config["artifacts"][artifact_name] = {
        "path": relative_or_absolute(root, target),
        "passed": returncode == 0,
    }
    config["events"].append({"at": now(), "action": artifact_name, "returncode": returncode})
    save_config(root, config)
    return returncode, report


def emit(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    initialize = sub.add_parser("init")
    initialize.add_argument("--problem", required=True)
    initialize.add_argument("--deadline")
    initialize.add_argument("--profile", choices=sorted(load_profiles()), default="competition-lite")

    sub.add_parser("status")

    profile = sub.add_parser("set-profile")
    profile.add_argument("profile", choices=sorted(load_profiles()))

    approve = sub.add_parser("approve")
    approve.add_argument("gate", choices=GATE_ORDER)
    approve.add_argument("--by", required=True)
    approve.add_argument("--rationale", required=True)
    approve.add_argument("--evidence", action="append", default=[])

    freeze = sub.add_parser("freeze-strategy")
    freeze.add_argument("--artifact", action="append", required=True)

    ingest = sub.add_parser("ingest-baseline")
    ingest.add_argument("--source", required=True)
    ingest.add_argument("--tool", required=True)
    ingest.add_argument("--version", required=True)
    ingest.add_argument("--interaction-log")

    register = sub.add_parser("register")
    register.add_argument(
        "kind",
        choices=[
            "submission",
            "paper",
            "code",
            "ai_disclosure",
            "ai_use_manifest",
            "result_ledger",
            "citation_manifest",
            "execution_manifest",
            "team_audit",
            "external_handoff",
            "visual_qa",
        ],
    )
    register.add_argument("path")

    declarations = sub.add_parser("set-declarations")
    declarations.add_argument("--ai-used", choices=["yes", "no", "unknown"])
    declarations.add_argument("--external-baseline-used", choices=["yes", "no", "unknown"])

    reproduce_parser = sub.add_parser("reproduce")
    reproduce_parser.add_argument("--code-root", required=True)
    reproduce_parser.add_argument("--manifest", required=True)

    truth = sub.add_parser("truth-check")
    truth.add_argument("--manifest", required=True)

    innovation = sub.add_parser("innovation-audit")
    innovation.add_argument("--manifest", required=True)
    innovation.add_argument("--phase", choices=["discovery", "freeze"], default="discovery")
    innovation.add_argument("--weights")

    calibration = sub.add_parser("calibrate-innovation")
    calibration.add_argument("--ledger", required=True)
    calibration.add_argument("--output-weights")

    sub.add_parser("audit")
    sub.add_parser("final-check")

    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "init":
            result = init_project(root, args.problem, args.deadline, args.profile)
            returncode = 0
        elif args.command == "status":
            result, returncode = status_report(root), 0
        elif args.command == "set-profile":
            result, returncode = set_profile(root, args.profile), 0
        elif args.command == "approve":
            result = approve_gate(root, args.gate, args.by, args.rationale, args.evidence)
            returncode = 0
        elif args.command == "freeze-strategy":
            result, returncode = freeze_strategy(root, args.artifact), 0
        elif args.command == "ingest-baseline":
            result = ingest_baseline(root, args.source, args.tool, args.version, args.interaction_log)
            returncode = 0
        elif args.command == "register":
            result, returncode = register_artifact(root, args.kind, args.path), 0
        elif args.command == "set-declarations":
            result = set_declarations(root, args.ai_used, args.external_baseline_used)
            returncode = 0
        elif args.command == "reproduce":
            returncode, result = reproduce(root, args.code_root, args.manifest)
        elif args.command == "truth-check":
            returncode, result = run_truth_checks(root, args.manifest)
        elif args.command == "innovation-audit":
            returncode, result = run_innovation_audit(root, args.manifest, args.phase, args.weights)
        elif args.command == "calibrate-innovation":
            returncode, result = run_innovation_calibration(root, args.ledger, args.output_weights)
        elif args.command == "audit":
            returncode, result = audit_submission(root, False)
        elif args.command == "final-check":
            returncode, result = audit_submission(root, True)
        else:
            raise ValueError(args.command)
        emit(result)
        return returncode
    except Exception as exc:
        emit({"error": str(exc), "root": str(root), "command": args.command})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
