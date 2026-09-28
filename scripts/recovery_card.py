#!/usr/bin/env python3
"""Build and verify a compact, hash-bound CUMCM contest recovery card."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HIGH_SEVERITIES = {"Blocker": 0, "Critical": 1, "Major": 2}


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
            if not item.is_file() or item.is_symlink() or ".git" in item.parts or ".cumcm" in item.parts:
                continue
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(sha256(item).encode("ascii"))
            digest.update(b"\0")
        return digest.hexdigest()
    raise FileNotFoundError(path)


def canonical_hash(payload: dict[str, Any]) -> str:
    clean = {key: value for key, value in payload.items() if key != "payload_sha256"}
    encoded = json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def resolve_project_path(root: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def current_hours(deadline: str | None) -> float | None:
    if not deadline:
        return None
    try:
        target = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        return round((target - datetime.now(timezone.utc)).total_seconds() / 3600, 2)
    except ValueError:
        return None


def collect_findings(payload: Any, output: list[dict[str, str]]) -> None:
    if isinstance(payload, dict):
        severity = payload.get("severity")
        message = payload.get("message") or payload.get("title")
        if severity in HIGH_SEVERITIES and isinstance(message, str):
            output.append(
                {
                    "severity": severity,
                    "code": str(payload.get("code") or payload.get("id") or "UNSPECIFIED"),
                    "message": message,
                }
            )
        for value in payload.values():
            collect_findings(value, output)
    elif isinstance(payload, list):
        for value in payload:
            collect_findings(value, output)


def artifact_rows(root: Path, workflow: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for name, record in sorted((workflow.get("artifacts") or {}).items()):
        if not isinstance(record, dict):
            rows.append({"name": name, "status": "invalid_record"})
            continue
        path = resolve_project_path(root, record.get("path"))
        recorded = record.get("sha256")
        current = path_digest(path) if path and path.exists() else None
        if path is None:
            status = "path_missing"
        elif not path.exists():
            status = "file_missing"
        elif recorded and recorded != current:
            status = "hash_mismatch"
        else:
            status = "current"
        rows.append(
            {
                "name": name,
                "path": str(path) if path else None,
                "kind": "directory" if path and path.is_dir() else "file",
                "recorded_sha256": recorded,
                "current_sha256": current,
                "status": status,
            }
        )
    return rows


def headline_rows(root: Path, workflow: dict[str, Any]) -> dict[str, Any]:
    record = (workflow.get("artifacts") or {}).get("result_ledger")
    if not isinstance(record, dict):
        return {"status": "not_registered", "frozen_at": None, "approved_by_team": False, "results": []}
    path = resolve_project_path(root, record.get("path"))
    if not path or not path.is_file():
        return {"status": "missing", "path": str(path) if path else None, "results": []}
    try:
        ledger = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "invalid", "path": str(path), "error": str(exc), "results": []}
    rows = []
    for result in ledger.get("results") or []:
        if not isinstance(result, dict) or not result.get("decision_critical", False):
            continue
        rows.append(
            {
                "id": result.get("id"),
                "question": result.get("question"),
                "label": result.get("label"),
                "value": result.get("value"),
                "unit": result.get("unit"),
            }
        )
    return {
        "status": "current",
        "path": str(path),
        "sha256": sha256(path),
        "frozen_at": ledger.get("frozen_at"),
        "approved_by_team": bool(ledger.get("approved_by_team")),
        "results": rows,
    }


def next_action(workflow: dict[str, Any], artifacts: list[dict[str, Any]], findings: list[dict[str, str]]) -> str:
    stale = [row["name"] for row in artifacts if row.get("status") != "current"]
    if stale:
        return "先处理失效或缺失文件并重建恢复卡：" + "、".join(stale[:5])
    if findings:
        first = findings[0]
        return f"先关闭 {first['severity']} {first['code']}：{first['message']}"
    for gate, record in (workflow.get("gates") or {}).items():
        if isinstance(record, dict) and record.get("status") != "approved":
            return f"推进并由团队确认下一道门：{gate}"
    return "所有已登记门均关闭；若结果已冻结，进入 final 严格终审与确定性打包。"


def build_card(root: Path, workflow_path: Path, findings_path: Path | None) -> dict[str, Any]:
    workflow = load_json(workflow_path)
    findings: list[dict[str, str]] = []
    if findings_path:
        collect_findings(load_json(findings_path), findings)
        unique = {(item["severity"], item["code"], item["message"]): item for item in findings}
        findings = sorted(unique.values(), key=lambda item: (HIGH_SEVERITIES[item["severity"]], item["code"]))[:5]
    artifacts = artifact_rows(root, workflow)
    problem_id = workflow.get("problem")
    problem_record = next(
        (
            record
            for name in ("problem_bundle", "official_problem", "problem_file", "problem")
            if isinstance((record := (workflow.get("artifacts") or {}).get(name)), dict)
        ),
        None,
    )
    problem = resolve_project_path(root, problem_record.get("path")) if problem_record else None
    card: dict[str, Any] = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project_root": str(root),
        "source_workflow": str(workflow_path),
        "source_workflow_sha256": sha256(workflow_path),
        "problem": {
            "id": problem_id,
            "path": str(problem) if problem else None,
            "sha256": path_digest(problem) if problem and problem.exists() else None,
            "status": "current" if problem and problem.exists() else "not_registered",
        },
        "profile": workflow.get("profile"),
        "deadline": workflow.get("deadline"),
        "remaining_hours_at_build": current_hours(workflow.get("deadline")),
        "gates": workflow.get("gates") or {},
        "declarations": workflow.get("declarations") or {},
        "artifacts": artifacts,
        "headline_results": headline_rows(root, workflow),
        "active_findings": findings,
    }
    card["next_action"] = next_action(workflow, artifacts, findings)
    card["payload_sha256"] = canonical_hash(card)
    return card


def render_markdown(card: dict[str, Any]) -> str:
    lines = [
        "# CUMCM 赛时恢复卡",
        "",
        f"- 生成时间：{card['generated_at']}",
        f"- 赛题：{card['problem'].get('id') or '未登记'}",
        f"- 赛题原件：{card['problem'].get('path') or '未登记'}",
        f"- 工作模式：{card.get('profile') or '未登记'}",
        f"- 截止时间：{card.get('deadline') or '未登记'}",
        f"- 生成时剩余小时：{card.get('remaining_hours_at_build')}",
        f"- 恢复卡校验哈希：`{card['payload_sha256']}`",
        "",
        "## 下一步唯一动作",
        "",
        card["next_action"],
        "",
        "## 人工决策门",
        "",
    ]
    for name, record in card.get("gates", {}).items():
        status = record.get("status") if isinstance(record, dict) else "invalid"
        lines.append(f"- {name}: {status}")
    lines.extend(["", "## 已登记文件", ""])
    if card["artifacts"]:
        for row in card["artifacts"]:
            lines.append(f"- {row['name']}: {row.get('status')} | {row.get('path') or '无路径'}")
    else:
        lines.append("- 尚无已登记文件。")
    lines.extend(["", "## 已冻结核心结果", ""])
    result_block = card["headline_results"]
    if result_block.get("results"):
        for row in result_block["results"]:
            lines.append(f"- {row.get('id')}: {row.get('value')} {row.get('unit') or ''} | {row.get('label') or ''}")
    else:
        lines.append(f"- 状态：{result_block.get('status')}；没有可安全恢复的已登记核心结果。")
    lines.extend(["", "## 当前高风险问题", ""])
    if card["active_findings"]:
        for item in card["active_findings"]:
            lines.append(f"- [{item['severity']}] {item['code']}: {item['message']}")
    else:
        lines.append("- 未从提供的审查报告中提取到 Blocker/Critical/Major。")
    lines.extend(
        [
            "",
            "## 恢复规则",
            "",
            "先运行恢复卡 verify。若工作流、赛题或已登记文件哈希不一致，本卡失效，必须重建；不要凭旧卡继续修改。",
            "",
        ]
    )
    return "\n".join(lines)


def verify_card(root: Path, card_path: Path, markdown_path: Path | None) -> dict[str, Any]:
    card = load_json(card_path)
    findings = []
    expected = card.get("payload_sha256")
    actual = canonical_hash(card)
    if expected != actual:
        findings.append({"severity": "Blocker", "code": "CARD_HASH", "message": "恢复卡自身哈希不匹配。"})
    workflow = resolve_project_path(root, card.get("source_workflow"))
    if not workflow or not workflow.is_file():
        findings.append({"severity": "Blocker", "code": "WORKFLOW_MISSING", "message": "源工作流文件不存在。"})
    elif sha256(workflow) != card.get("source_workflow_sha256"):
        findings.append({"severity": "Critical", "code": "WORKFLOW_CHANGED", "message": "工作流已变化，恢复卡必须重建。"})
    problem_record = card.get("problem") or {}
    problem = resolve_project_path(root, problem_record.get("path"))
    if problem_record.get("sha256") and (not problem or not problem.exists() or path_digest(problem) != problem_record.get("sha256")):
        findings.append({"severity": "Critical", "code": "PROBLEM_CHANGED", "message": "赛题原件缺失或哈希变化。"})
    for row in card.get("artifacts") or []:
        path = resolve_project_path(root, row.get("path"))
        recorded = row.get("current_sha256")
        if not path or not path.exists() or (recorded and path_digest(path) != recorded):
            findings.append(
                {
                    "severity": "Critical",
                    "code": "ARTIFACT_CHANGED",
                    "message": f"已登记文件变化或缺失：{row.get('name')}",
                }
            )
    if markdown_path:
        if not markdown_path.is_file() or str(expected) not in markdown_path.read_text(encoding="utf-8"):
            findings.append({"severity": "Major", "code": "MARKDOWN_MISMATCH", "message": "Markdown 恢复卡缺失或未绑定同一哈希。"})
    return {"status": "pass" if not findings else "fail", "card": str(card_path), "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify a hash-bound CUMCM contest recovery card.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--root", type=Path, required=True)
    build.add_argument("--workflow", type=Path)
    build.add_argument("--findings", type=Path)
    build.add_argument("--output-json", type=Path)
    build.add_argument("--output-markdown", type=Path)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("--card", type=Path, required=True)
    verify.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if args.command == "build":
        workflow = (args.workflow or (root / ".cumcm" / "workflow.json")).expanduser().resolve()
        if not workflow.is_file():
            print(json.dumps({"error": "workflow not found", "workflow": str(workflow)}, ensure_ascii=False))
            return 2
        findings = args.findings.expanduser().resolve() if args.findings else None
        card = build_card(root, workflow, findings)
        output_json = (args.output_json or (root / ".cumcm" / "recovery" / "赛时恢复卡.json")).expanduser().resolve()
        output_markdown = (args.output_markdown or (root / ".cumcm" / "recovery" / "赛时恢复卡.md")).expanduser().resolve()
        atomic_text(output_json, json.dumps(card, ensure_ascii=False, indent=2) + "\n")
        atomic_text(output_markdown, render_markdown(card))
        print(json.dumps({"status": "built", "json": str(output_json), "markdown": str(output_markdown), "payload_sha256": card["payload_sha256"], "next_action": card["next_action"]}, ensure_ascii=False, indent=2))
        return 0

    report = verify_card(root, args.card.expanduser().resolve(), args.markdown.expanduser().resolve() if args.markdown else None)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
