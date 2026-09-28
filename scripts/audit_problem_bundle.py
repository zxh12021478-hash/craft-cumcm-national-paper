#!/usr/bin/env python3
"""Inventory official problem artifacts and flag content plain extraction can miss."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_digest(value) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def inspect_docx(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        document = ET.fromstring(zf.read("word/document.xml"))
        text = "".join(node.text or "" for node in document.iter(W + "t"))
        return {
            "characters": len(text),
            "equations": len(list(document.iter(M + "oMath"))),
            "drawings": len(list(document.iter(W + "drawing"))),
            "embedded_objects": [name for name in names if name.startswith("word/embeddings/")],
            "media": [name for name in names if name.startswith("word/media/")],
            "charts": [name for name in names if name.startswith("word/charts/")],
        }


def inspect_xlsx(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        sheets = [
            {"name": node.attrib.get("name"), "state": node.attrib.get("state", "visible")}
            for node in workbook.iter(S + "sheet")
        ]
        formulas = sum(
            zf.read(name).count(b"<f")
            for name in names
            if name.startswith("xl/worksheets/") and name.endswith(".xml")
        )
        return {
            "sheets": sheets,
            "formulas": formulas,
            "external_links": [name for name in names if name.startswith("xl/externalLinks/")],
            "drawings": [name for name in names if name.startswith("xl/drawings/")],
            "media": [name for name in names if name.startswith("xl/media/")],
            "embeddings": [name for name in names if name.startswith("xl/embeddings/")],
        }


def inspect_pdf(path: Path) -> dict:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    characters = [len(re.sub(r"\s+", "", page.extract_text() or "")) for page in reader.pages]
    return {"pages": len(reader.pages), "characters_per_page": characters}


def inspect(root: Path, excluded: set[Path] | None = None) -> dict:
    findings = []
    risks = []
    artifacts = []
    excluded = {path.resolve() for path in (excluded or set())}
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not path.name.startswith(".") and path.resolve() not in excluded
    )
    if not files:
        findings.append(finding("Blocker", "NO_PROBLEM_ARTIFACTS", "No problem files were found."))
    for path in files:
        record = {
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "type": path.suffix.lower(),
        }
        try:
            if path.suffix.lower() == ".docx":
                record["inspection"] = inspect_docx(path)
                if any(record["inspection"][key] for key in ("equations", "drawings", "embedded_objects", "media", "charts")):
                    risks.append({"file": record["path"], "risk": "Render all pages and inspect equations, drawings, media, charts, and embedded objects."})
            elif path.suffix.lower() in {".xlsx", ".xlsm"}:
                record["inspection"] = inspect_xlsx(path)
                risks.append({"file": record["path"], "risk": "Reconcile sheets, hidden state, formulas, drawings, units, merged headers, and requested output ranges."})
            elif path.suffix.lower() == ".xls":
                risks.append(
                    {
                        "file": record["path"],
                        "risk": "Open the legacy workbook in a spreadsheet application; reconcile every visible/hidden sheet, merged header, formula, unit, and requested input/output range.",
                    }
                )
            elif path.suffix.lower() == ".pdf":
                record["inspection"] = inspect_pdf(path)
                low_text = [index + 1 for index, count in enumerate(record["inspection"]["characters_per_page"]) if count < 30]
                if low_text:
                    risks.append({"file": record["path"], "risk": "Render/OCR and reconcile image-based or low-text pages.", "pages": low_text})
        except Exception as exc:
            findings.append(finding("Critical", "PROBLEM_ARTIFACT_READ", f"{record['path']}: {exc}"))
        artifacts.append(record)
    for index, risk in enumerate(risks, start=1):
        risk["risk_id"] = f"R{index:03d}"
    bundle_sha256 = stable_digest(
        [{"path": item["path"], "bytes": item["bytes"], "sha256": item["sha256"]} for item in artifacts]
    )
    return {
        "root": str(root),
        "bundle_sha256": bundle_sha256,
        "artifacts": artifacts,
        "risks_requiring_team_reconciliation": risks,
        "required_gate": "Team confirms rendered prompt, equations, maps, workbook structure, units, output ranges, and hashes before strategy approval.",
        "findings": findings,
    }


def validate_reconciliation(report: dict, reconciliation_path: Path | None) -> list[dict]:
    findings = []
    if reconciliation_path is None:
        return [
            finding(
                "Major",
                "PROBLEM_RECONCILIATION_REQUIRED",
                "Strict problem-bundle approval requires a human reconciliation record bound to this bundle.",
                report.get("bundle_sha256"),
            )
        ]
    try:
        payload = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [finding("Blocker", "PROBLEM_RECONCILIATION_JSON", str(exc))]
    if not isinstance(payload, dict):
        return [finding("Blocker", "PROBLEM_RECONCILIATION_SCHEMA", "Reconciliation root must be an object.")]
    schema_path = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "problem-reconciliation.schema.json"
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        findings.append(
            finding(
                "Major",
                "JSONSCHEMA_UNAVAILABLE",
                "Problem reconciliation schema was not fully validated.",
            )
        )
    else:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for error in sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
            key=lambda item: list(item.absolute_path),
        ):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            findings.append(finding("Blocker", "PROBLEM_RECONCILIATION_SCHEMA", f"{location}: {error.message}"))

    if payload.get("bundle_sha256") != report.get("bundle_sha256"):
        findings.append(
            finding(
                "Blocker",
                "PROBLEM_BUNDLE_HASH_MISMATCH",
                "Reconciliation record is not bound to the current official problem bundle.",
                {
                    "expected": report.get("bundle_sha256"),
                    "actual": payload.get("bundle_sha256"),
                },
            )
        )

    expected_artifacts = {item["path"]: item["sha256"] for item in report.get("artifacts", [])}
    recorded_artifacts = {}
    for item in payload.get("artifacts", []) if isinstance(payload.get("artifacts"), list) else []:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if path in recorded_artifacts:
            findings.append(finding("Blocker", "PROBLEM_ARTIFACT_DUPLICATE", f"Duplicate artifact attestation: {path}"))
        recorded_artifacts[path] = item.get("sha256")
    for path, expected_hash in expected_artifacts.items():
        if path not in recorded_artifacts:
            findings.append(finding("Blocker", "PROBLEM_ARTIFACT_UNREVIEWED", f"Artifact not attested: {path}"))
        elif recorded_artifacts[path] != expected_hash:
            findings.append(
                finding(
                    "Blocker",
                    "PROBLEM_ARTIFACT_HASH_MISMATCH",
                    f"Artifact hash mismatch: {path}",
                    {"expected": expected_hash, "actual": recorded_artifacts[path]},
                )
            )
    extras = sorted(set(recorded_artifacts) - set(expected_artifacts))
    if extras:
        findings.append(finding("Critical", "PROBLEM_ARTIFACT_UNKNOWN", "Attestation names files outside the audited bundle.", extras))

    expected_risks = {item["risk_id"] for item in report.get("risks_requiring_team_reconciliation", [])}
    closed_risks = {}
    for item in payload.get("risk_closures", []) if isinstance(payload.get("risk_closures"), list) else []:
        if not isinstance(item, dict):
            continue
        risk_id = item.get("risk_id")
        if risk_id in closed_risks:
            findings.append(finding("Blocker", "PROBLEM_RISK_DUPLICATE", f"Duplicate risk closure: {risk_id}"))
        closed_risks[risk_id] = item.get("status")
    missing_risks = sorted(expected_risks - {risk_id for risk_id, status in closed_risks.items() if status == "closed"})
    if missing_risks:
        findings.append(finding("Blocker", "PROBLEM_RISKS_OPEN", "Problem-artifact risks remain unreconciled.", missing_risks))
    extra_risks = sorted(set(closed_risks) - expected_risks)
    if extra_risks:
        findings.append(finding("Major", "PROBLEM_RISK_UNKNOWN", "Reconciliation cites unknown risk IDs.", extra_risks))

    subproblems = payload.get("subproblems", [])
    ids = [item.get("id") for item in subproblems if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        findings.append(finding("Blocker", "PROBLEM_SUBPROBLEM_DUPLICATE", "Subproblem IDs in the reconciliation record must be unique.", ids))
    if payload.get("unresolved_ambiguities"):
        findings.append(
            finding(
                "Blocker",
                "PROBLEM_AMBIGUITY_OPEN",
                "The official prompt cannot be marked reconciled while task-defining ambiguities remain open.",
                payload.get("unresolved_ambiguities"),
            )
        )
    audited_workbooks = {
        item.get("path")
        for item in report.get("artifacts", [])
        if isinstance(item, dict) and item.get("type") in {".xlsx", ".xlsm", ".xls"}
    }
    workbook_ranges = payload.get("workbook_ranges", [])
    if not isinstance(workbook_ranges, list):
        workbook_ranges = []
    mapped_workbooks = {
        item.get("file")
        for item in workbook_ranges
        if isinstance(item, dict) and item.get("file")
    }
    missing_workbooks = sorted(audited_workbooks - mapped_workbooks)
    if missing_workbooks:
        findings.append(
            finding(
                "Blocker",
                "PROBLEM_WORKBOOK_RANGES_MISSING",
                "Every audited workbook requires a human-verified range inventory.",
                missing_workbooks,
            )
        )
    unknown_workbooks = sorted(mapped_workbooks - audited_workbooks)
    if unknown_workbooks:
        findings.append(
            finding(
                "Critical",
                "PROBLEM_WORKBOOK_UNKNOWN",
                "Range attestations cite workbooks outside the audited bundle.",
                unknown_workbooks,
            )
        )
    range_keys = []
    for item in workbook_ranges:
        if not isinstance(item, dict):
            continue
        range_keys.append((item.get("file"), item.get("sheet"), item.get("range"), item.get("role")))
        invalid_users = sorted(set(item.get("used_by_subproblems", [])) - set(ids))
        if invalid_users:
            findings.append(
                finding(
                    "Blocker",
                    "PROBLEM_WORKBOOK_SUBPROBLEM",
                    "Workbook range attestation cites unknown subproblem IDs.",
                    invalid_users,
                )
            )
    if len(range_keys) != len(set(range_keys)):
        findings.append(
            finding(
                "Blocker",
                "PROBLEM_WORKBOOK_RANGE_DUPLICATE",
                "Workbook range attestations must be unique by file, sheet, range, and role.",
                range_keys,
            )
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--reconciliation", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.root.is_dir():
        print(json.dumps({"error": "problem bundle directory not found"}, ensure_ascii=False))
        return 2
    excluded = {path for path in (args.output, args.reconciliation) if path is not None}
    report = inspect(args.root.resolve(), excluded)
    report["reconciliation"] = str(args.reconciliation.resolve()) if args.reconciliation else None
    report["reconciliation_sha256"] = (
        sha256(args.reconciliation.resolve()) if args.reconciliation and args.reconciliation.is_file() else None
    )
    report["findings"].extend(
        validate_reconciliation(report, args.reconciliation.resolve() if args.reconciliation else None)
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
