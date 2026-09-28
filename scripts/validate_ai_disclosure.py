#!/usr/bin/env python3
"""Check an AI-use disclosure for required CUMCM information."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
            return "\n".join("".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p"))
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF checking requires pypdf; provide DOCX/Markdown/text or install pypdf") from exc
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def inspect(path: Path) -> dict:
    text = extract_text(path)
    official_checks = {
        "tool_name": r"工具(名称)?|tool",
        "model_version": r"版本|型号|model|version",
        "purpose": r"使用目的|用途|环节|purpose",
        "prompting_process": r"主要提示方式|提示方式|使用过程|提示词|prompt|典型交互",
        "adoption": r"采纳|未采纳|采用情况|adopt",
        "human_modification": r"人工修改|修改情况|human modification",
        "human_verification": r"人工核验|人工审查|核验结论|验证|verification",
    }
    traceability_checks = {
        "provider": r"开发机构|公司|提供方|provider",
        "date_or_time": r"使用日期|时间|timestamp|20\d{2}[-/.年]",
        "affected_location": r"对应位置|论文位置|代码位置|章节|affected",
    }
    missing = [name for name, pattern in official_checks.items() if not re.search(pattern, text, re.I)]
    missing_traceability = [
        name for name, pattern in traceability_checks.items() if not re.search(pattern, text, re.I)
    ]
    findings = []
    if missing:
        findings.append({"severity": "Blocker", "code": "AI_DISCLOSURE_OFFICIAL_FIELDS", "message": "Required 2026 official disclosure concepts are missing.", "evidence": missing})
    if missing_traceability:
        findings.append({"severity": "Major", "code": "AI_DISCLOSURE_TRACEABILITY_FIELDS", "message": "Team-policy traceability fields are missing; these are not labeled as official requirements.", "evidence": missing_traceability})
    if len(text.strip()) < 200:
        findings.append({"severity": "Major", "code": "AI_DISCLOSURE_TOO_SHORT", "message": "Disclosure is unusually short; verify that material interactions are recorded."})
    if re.search(r"未使用任何\s*AI", text, re.I) and re.search(r"ChatGPT|DeepSeek|Claude|Gemini|Codex|通义|文心", text, re.I):
        findings.append({"severity": "Blocker", "code": "AI_DISCLOSURE_CONTRADICTION", "message": "The document claims no AI use but names an AI tool."})
    return {
        "file": str(path),
        "characters": len(text),
        "missing_fields": missing,
        "missing_traceability_fields": missing_traceability,
        "findings": findings,
    }


def inspect_manifest(path: Path, disclosure_text: str, expected_tools: list[str]) -> dict:
    findings = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"file": str(path), "tools": [], "findings": [{"severity": "Blocker", "code": "AI_MANIFEST_JSON", "message": str(exc)}]}
    if not isinstance(payload, dict):
        return {"file": str(path), "tools": [], "findings": [{"severity": "Blocker", "code": "AI_MANIFEST_SCHEMA", "message": "Manifest root must be an object."}]}
    schema_path = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "ai-use-manifest.schema.json"
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        findings.append({"severity": "Major", "code": "JSONSCHEMA_UNAVAILABLE", "message": "AI manifest schema was not fully validated."})
    else:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload), key=lambda item: list(item.absolute_path)):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            findings.append({"severity": "Blocker", "code": "AI_MANIFEST_SCHEMA", "message": f"{location}: {error.message}"})
    tools = payload.get("tools", [])
    if not isinstance(tools, list):
        tools = []
    valid_tools = [tool for tool in tools if isinstance(tool, dict)]
    names = {str(tool.get("name", "")).strip() for tool in valid_tools if str(tool.get("name", "")).strip()}
    missing_expected = sorted(set(expected_tools) - names)
    if missing_expected:
        findings.append(
            {
                "severity": "Blocker",
                "code": "EXPECTED_AI_TOOL_MISSING",
                "message": "The internal AI-use manifest omits a known generating system.",
                "evidence": missing_expected,
            }
        )
    placeholder_blob = json.dumps(payload, ensure_ascii=False)
    if re.search(r"替换为|说明本次|保存关键|队员A|论文3\.2节", placeholder_blob):
        findings.append({"severity": "Blocker", "code": "AI_MANIFEST_PLACEHOLDER", "message": "AI-use manifest still contains template values."})
    for tool in valid_tools:
        name = str(tool.get("name", "")).strip()
        version = str(tool.get("model_version", "")).strip()
        if name and name not in disclosure_text:
            findings.append({"severity": "Blocker", "code": "AI_TOOL_NOT_IN_PDF", "message": f"AI tool is absent from the PDF disclosure: {name}"})
        if version and version not in disclosure_text:
            findings.append({"severity": "Critical", "code": "AI_VERSION_NOT_IN_PDF", "message": f"AI model version is absent from the PDF disclosure: {version}"})
        for use_index, use in enumerate(tool.get("uses", []) if isinstance(tool.get("uses"), list) else []):
            if not isinstance(use, dict):
                continue
            try:
                stamp = datetime.fromisoformat(str(use.get("timestamp", "")).replace("Z", "+00:00"))
                if stamp.tzinfo is None or stamp.utcoffset() is None:
                    raise ValueError("timezone offset is required")
            except Exception as exc:
                findings.append({"severity": "Blocker", "code": "AI_USE_TIMESTAMP", "message": f"{name} use {use_index + 1}: {exc}"})
    signoff = payload.get("team_signoff", {})
    if isinstance(signoff, dict):
        reviewers = [str(value) for value in signoff.get("verified_by", [])]
        if any(re.search(r"ChatGPT|DeepSeek|Claude|Gemini|Codex|OpenAI|AI", value, re.I) for value in reviewers):
            findings.append({"severity": "Blocker", "code": "AI_SIGNOFF_NON_HUMAN", "message": "AI-use manifest must be signed by team members."})
    return {"file": str(path), "tools": sorted(names), "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expected-tool", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Enforce final-submission filename and PDF format")
    args = parser.parse_args()
    if not args.file.exists():
        print(json.dumps({"error": "file not found", "file": str(args.file)}, ensure_ascii=False))
        return 2
    try:
        report = inspect(args.file)
        text = extract_text(args.file)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "file": str(args.file)}, ensure_ascii=False))
        return 2
    if args.strict:
        if args.file.stem != "AI工具使用详情":
            report["findings"].append({"severity": "Critical", "code": "AI_DISCLOSURE_NAME", "message": "Final disclosure filename must be AI工具使用详情."})
        if args.file.suffix.lower() != ".pdf":
            report["findings"].append({"severity": "Critical", "code": "AI_DISCLOSURE_FORMAT", "message": "Final disclosure must be supplied as PDF."})
        if args.manifest is None:
            report["findings"].append({"severity": "Blocker", "code": "NO_AI_USE_MANIFEST", "message": "Strict AI-use validation requires the internal machine-readable manifest."})
    if args.manifest:
        manifest_report = inspect_manifest(args.manifest.resolve(), text, args.expected_tool)
        report["manifest"] = manifest_report
        report["findings"].extend(manifest_report["findings"])
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
