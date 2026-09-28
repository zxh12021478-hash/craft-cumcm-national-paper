#!/usr/bin/env python3
"""Maintain a human-led CUMCM stage state with explicit approval gates."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

STAGES = (
    "intake",
    "problem_decomposition",
    "data_audit",
    "baseline",
    "candidate_selection",
    "core_approval",
    "external_baseline_handoff",
    "implementation",
    "validation",
    "result_freeze",
    "paper",
    "final_audit",
)
TEAM_GATES = {
    "problem_decomposition",
    "core_approval",
    "external_baseline_handoff",
    "result_freeze",
    "final_audit",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["updated_at"] = now()
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def ensure_stage(state: dict, stage: str) -> dict:
    if stage not in STAGES or stage not in state.get("stages", {}):
        raise ValueError(f"unknown stage: {stage}")
    return state["stages"][stage]


def previous_ready(state: dict, stage: str) -> bool:
    index = STAGES.index(stage)
    if index == 0:
        return True
    previous = state["stages"][STAGES[index - 1]]["status"]
    return previous in {"completed", "approved"}


def advance_pointer(state: dict, stage: str) -> None:
    index = STAGES.index(stage)
    state["current_stage"] = STAGES[index + 1] if index + 1 < len(STAGES) else "complete"


def init_state(template: Path, output: Path, problem: str | None, deadline: str | None) -> dict:
    if output.exists():
        raise FileExistsError(f"state file already exists: {output}")
    state = load(template)
    state["problem"] = problem
    state["deadline"] = deadline
    atomic_write(output, state)
    return state


def mutate(state: dict, command: str, stage: str, args: argparse.Namespace) -> None:
    entry = ensure_stage(state, stage)
    status = entry["status"]
    if command == "start":
        if status not in {"not_started", "rework", "blocked"}:
            raise ValueError(f"cannot start {stage} from {status}")
        if not previous_ready(state, stage):
            raise ValueError(f"previous stage has not passed: {stage}")
        entry.update(status="in_progress", started_at=entry["started_at"] or now(), blocking_reason=None)
        state["current_stage"] = stage
    elif command == "complete":
        if status != "in_progress":
            raise ValueError(f"cannot complete {stage} from {status}")
        entry["completed_at"] = now()
        entry["evidence"].extend(args.evidence or [])
        if stage in TEAM_GATES:
            entry["status"] = "awaiting_team"
            state["current_stage"] = stage
        else:
            entry["status"] = "completed"
            advance_pointer(state, stage)
    elif command == "request-approval":
        if status not in {"in_progress", "completed"}:
            raise ValueError(f"cannot request approval for {stage} from {status}")
        entry["status"] = "awaiting_team"
        entry["completed_at"] = entry["completed_at"] or now()
        entry["evidence"].extend(args.evidence or [])
        state["current_stage"] = stage
    elif command == "approve":
        if status != "awaiting_team":
            raise ValueError(f"cannot approve {stage} from {status}")
        if not args.by or not args.rationale:
            raise ValueError("approval requires --by and --rationale")
        entry.update(status="approved", approved_at=now(), approved_by=args.by, blocking_reason=None)
        entry["evidence"].append(f"team rationale: {args.rationale}")
        advance_pointer(state, stage)
    elif command == "rework":
        if status not in {"awaiting_team", "completed", "approved", "blocked"}:
            raise ValueError(f"cannot return {stage} to rework from {status}")
        if not args.reason:
            raise ValueError("rework requires --reason")
        entry.update(status="rework", blocking_reason=args.reason, approved_at=None, approved_by=None)
        state["current_stage"] = stage
    elif command == "block":
        if not args.reason:
            raise ValueError("block requires --reason")
        entry.update(status="blocked", blocking_reason=args.reason)
        state["current_stage"] = stage
    else:
        raise ValueError(command)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--template", type=Path, required=True)
    init.add_argument("--problem")
    init.add_argument("--deadline")
    sub.add_parser("status")
    for name in ("start", "complete", "request-approval", "approve", "rework", "block"):
        command = sub.add_parser(name)
        command.add_argument("stage", choices=STAGES)
        command.add_argument("--evidence", action="append")
        command.add_argument("--by")
        command.add_argument("--rationale")
        command.add_argument("--reason")
    args = parser.parse_args()
    path = args.state.resolve()
    try:
        if args.command == "init":
            state = init_state(args.template.resolve(), path, args.problem, args.deadline)
        else:
            if not path.is_file():
                raise FileNotFoundError(path)
            state = load(path)
            if args.command != "status":
                mutate(state, args.command, args.stage, args)
                atomic_write(path, state)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "state": str(path)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
