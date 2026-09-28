#!/usr/bin/env python3
"""Generate a deadline-anchored CUMCM schedule with stop-loss checkpoints."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

FULL_PHASES = (
    ("kickoff_selection", "启动、读题、选题与规则核对", 3, "未完成题意核对和选题风险表，不进入主建模。"),
    ("decomposition_data", "子问拆解、数据审计与论证主线", 8, "数据质量不明时先完成透明基线，禁止直接上复杂模型。"),
    ("baseline", "覆盖全部子问的基线", 10, "到点仍无完整链路时，冻结新算法搜索，先打通全题。"),
    ("primary_model", "主模型、求解与独立验证", 15, "核心公式未获团队批准或验证命令失败，不得写入论文。"),
    ("innovation_robustness", "问题特定创新、对照、稳健性与不确定性", 12, "创新无消融证据则降级为改进细节，不做主卖点。"),
    ("results_spine", "冻结结果、图表、论证台账与摘要覆盖矩阵", 8, "冻结后任何数值变更必须触发全文一致性复验。"),
    ("paper_assembly", "正文、摘要、结论、引用与双格式装配", 10, "不再新增主模型；只修复证据链、表达与排版。"),
    ("final_audit_reserve", "干净运行、页面渲染、合规、全员理解与上传预演", 6, "最后储备只处理阻断项；禁止无验证的大改。")
)

TAKEOVER_PHASES = (
    ("handoff_quarantine", "外部基线交接、隔离、双系统披露、规则与材料盘点", 4, "交接、策略差异、交互记录或任一AI系统披露缺失时，不得引用基线结论。"),
    ("clean_run_forensics", "静态审计、干净运行、数字与引用取证", 8, "代码不能复现或数字对不上时，先修复事实层，停止润色。"),
    ("model_correction", "模型纠错、完整基线与团队再批准", 12, "未通过变量、目标、约束和现实合理性复核，不进入创新。"),
    ("innovation_validation", "问题特定创新、对照、消融、稳健性与不确定性", 14, "无独立证据的创新降级；不因时间压力保留虚假亮点。"),
    ("result_freeze_figures", "结果冻结、图表、台账与直接答案", 10, "冻结后任何数据或参数变更都触发结果与全文复验。"),
    ("paper_rebuild", "按论证主线重构正文、摘要、结论与引用", 12, "不再新增主模型，只修复证据链和表达。"),
    ("adversarial_review", "评委视角红队、全员理解与定向返工", 7, "只修最高严重度瓶颈；禁止无回归验证的全文重写。"),
    ("final_audit_reserve", "页面渲染、合规、支撑材料与上传预演", 5, "最后储备只处理阻断项，保留可回滚版本。")
)


def parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamps must include a UTC offset, for example 2026-09-10T18:00:00+08:00")
    return parsed


def schedule(start: datetime, deadline: datetime, profile: str, findings: list[dict] | None = None) -> dict:
    seconds = (deadline - start).total_seconds()
    if seconds <= 0:
        raise ValueError("deadline must be later than start")
    phases = TAKEOVER_PHASES if profile == "takeover" else FULL_PHASES
    total_weight = sum(item[2] for item in phases)
    cursor = start
    rows = []
    for index, (phase_id, label, weight, stop_loss) in enumerate(phases):
        phase_seconds = seconds * weight / total_weight
        end = deadline if index == len(phases) - 1 else cursor + timedelta(seconds=phase_seconds)
        rows.append(
            {
                "id": phase_id,
                "label": label,
                "start": cursor.isoformat(timespec="minutes"),
                "hard_stop": end.isoformat(timespec="minutes"),
                "allocated_hours": round(phase_seconds / 3600, 2),
                "stop_loss": stop_loss,
            }
        )
        cursor = end
    freeze_index = {
        "full": {"model": 4, "result": 5, "content": 6},
        "takeover": {"model": 3, "result": 4, "content": 6},
    }[profile]
    severity_order = {"Blocker": 0, "Critical": 1, "Major": 2, "Minor": 3}
    worklist = sorted(
        [
            {
                "severity": item.get("severity"),
                "code": item.get("code"),
                "message": item.get("message"),
            }
            for item in (findings or [])
            if item.get("severity") in severity_order
        ],
        key=lambda item: (severity_order[item["severity"]], str(item.get("code"))),
    )
    if worklist:
        rows[0]["must_resolve_before_phase_exit"] = [
            item for item in worklist if item["severity"] in {"Blocker", "Critical"}
        ]
    return {
        "version": 1,
        "classification": "quality practice; not an official competition rule",
        "start": start.isoformat(timespec="minutes"),
        "deadline": deadline.isoformat(timespec="minutes"),
        "available_hours": round(seconds / 3600, 2),
        "profile": profile,
        "phases": rows,
        "finding_worklist": worklist,
        "global_freezes": {
            "no_new_primary_model_after": rows[freeze_index["model"]]["hard_stop"],
            "result_freeze": rows[freeze_index["result"]]["hard_stop"],
            "content_freeze": rows[freeze_index["content"]]["hard_stop"],
            "upload_dry_run_by": (deadline - timedelta(hours=min(3, seconds / 3600 * 0.04))).isoformat(timespec="minutes"),
        },
    }


def markdown(report: dict) -> str:
    lines = [
        "# CUMCM 竞赛执行时钟",
        "",
        f"- 开始：{report['start']}",
        f"- 截止：{report['deadline']}",
        f"- 可用时长：{report['available_hours']} 小时",
        "- 性质：质量实践，不是官方规则。",
        "",
        "| 阶段 | 开始 | 硬截止 | 小时 | 止损规则 |",
        "|---|---|---|---:|---|",
    ]
    for row in report["phases"]:
        lines.append(f"| {row['label']} | {row['start']} | {row['hard_stop']} | {row['allocated_hours']} | {row['stop_loss']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--deadline", required=True)
    parser.add_argument("--profile", choices=("full", "takeover"), default="full")
    parser.add_argument("--findings", type=Path, help="validate_submission JSON report; Blockers/Criticals are front-loaded")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    try:
        flattened = []
        if args.findings:
            source = json.loads(args.findings.read_text(encoding="utf-8"))
            if isinstance(source.get("checks"), dict):
                flattened = [
                    item
                    for check in source["checks"].values()
                    if isinstance(check, dict)
                    for item in check.get("findings", [])
                    if isinstance(item, dict)
                ]
            else:
                flattened = [item for item in source.get("findings", []) if isinstance(item, dict)]
        report = schedule(parse(args.start), parse(args.deadline), args.profile, flattened)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report), encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
