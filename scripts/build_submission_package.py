#!/usr/bin/env python3
"""Prepare, approve, and deterministically build a hash-bound CUMCM upload package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_LIMIT = 20 * 1024 * 1024
SOURCE_SUFFIXES = {".py", ".m", ".mlx", ".r", ".jl", ".ipynb", ".c", ".cc", ".cpp", ".java"}
SKIP_NAMES = {".DS_Store", "Thumbs.db"}
SKIP_PARTS = {"__pycache__", ".git", ".svn", ".idea", ".vscode", ".cumcm", "node_modules", ".pytest_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".tmp", ".temp", ".swp"}
SECRET_NAMES = {".env", ".env.local", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest root must be an object")
    return payload


def inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def skipped(path: Path) -> bool:
    return path.name in SKIP_NAMES or any(part in SKIP_PARTS for part in path.parts) or path.suffix.lower() in SKIP_SUFFIXES


def safe_relative(raw: str) -> bool:
    path = Path(raw)
    return bool(raw) and not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def collect_support(root: Path, inputs: Iterable[Path], paper: Path) -> list[Path]:
    files: set[Path] = set()
    for supplied in inputs:
        path = supplied.expanduser().resolve()
        if not inside(root, path):
            raise ValueError(f"support input must stay inside project root: {path}")
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in the upload manifest: {path}")
        if path.is_file():
            candidates = [path]
        elif path.is_dir():
            candidates = [item for item in path.rglob("*") if item.is_file()]
        else:
            raise FileNotFoundError(path)
        for item in candidates:
            resolved = item.resolve()
            if resolved == paper or skipped(resolved.relative_to(root)):
                continue
            if item.is_symlink():
                raise ValueError(f"symlinks are not allowed in the upload manifest: {item}")
            lowered = resolved.name.lower()
            if lowered in SECRET_NAMES or lowered.startswith(".env."):
                raise ValueError(f"credential-like file is forbidden from support material: {resolved}")
            files.add(resolved)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def prepare(args: argparse.Namespace) -> int:
    root = args.root.expanduser().resolve()
    paper = args.paper.expanduser().resolve()
    if not root.is_dir() or not paper.is_file() or not inside(root, paper):
        raise ValueError("project root must exist and paper must be a file inside it")
    if paper.suffix.lower() not in {".pdf", ".docx"}:
        raise ValueError("electronic paper must be a PDF or DOCX")
    support = collect_support(root, args.support, paper)
    if not support:
        raise ValueError("support allowlist is empty")
    records = [
        {
            "path": item.relative_to(root).as_posix(),
            "sha256": sha256(item),
            "bytes": item.stat().st_size,
        }
        for item in support
    ]
    payload = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project_root": str(root),
        "paper": {
            "path": paper.relative_to(root).as_posix(),
            "upload_name": args.paper_upload_name or paper.name,
            "sha256": sha256(paper),
            "bytes": paper.stat().st_size,
        },
        "support_archive": {
            "upload_name": args.support_upload_name,
            "files": records,
        },
        "ai_used": args.ai_used,
        "limits": {"paper_max_bytes": args.paper_max_bytes, "support_max_bytes": args.support_max_bytes},
        "approved_by_team": False,
        "approval": None,
    }
    manifest = args.manifest.expanduser().resolve()
    if manifest.exists() and not args.replace_unapproved:
        raise FileExistsError(f"manifest exists; use a new path or --replace-unapproved: {manifest}")
    if manifest.exists():
        previous = load_json(manifest)
        if previous.get("approved_by_team"):
            raise ValueError("an approved manifest is immutable; write a new manifest")
    atomic_json(manifest, payload)
    print(json.dumps({"status": "prepared", "manifest": str(manifest), "paper": payload["paper"], "support_files": len(records), "approved_by_team": False}, ensure_ascii=False, indent=2))
    return 0


def approve(args: argparse.Namespace) -> int:
    manifest = args.manifest.expanduser().resolve()
    payload = load_json(manifest)
    if payload.get("approved_by_team"):
        raise ValueError("manifest is already approved and immutable")
    if not args.approved_by.strip():
        raise ValueError("approved-by must identify the real team approver")
    payload["approved_by_team"] = True
    payload["approval"] = {
        "approved_by": args.approved_by,
        "approved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "statement": "团队确认此清单列出的精确文件用于最终打包。",
    }
    atomic_json(manifest, payload)
    print(json.dumps({"status": "approved", "manifest": str(manifest), "approval": payload["approval"]}, ensure_ascii=False, indent=2))
    return 0


def validate_manifest(payload: dict[str, Any], root_override: Path | None, strict: bool) -> tuple[Path, Path, list[tuple[Path, str]], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    if payload.get("version") != 1:
        findings.append({"severity": "Blocker", "code": "MANIFEST_VERSION", "message": "unsupported manifest version"})
    root = (root_override or Path(str(payload.get("project_root", "")))).expanduser().resolve()
    paper_record = payload.get("paper") or {}
    paper = (root / str(paper_record.get("path", ""))).resolve()
    if not inside(root, paper) or not paper.is_file():
        findings.append({"severity": "Blocker", "code": "PAPER_MISSING", "message": "paper is absent or outside project root"})
    elif sha256(paper) != paper_record.get("sha256"):
        findings.append({"severity": "Blocker", "code": "PAPER_CHANGED", "message": "paper changed after manifest preparation"})
    support: list[tuple[Path, str]] = []
    seen = set()
    for record in (payload.get("support_archive") or {}).get("files") or []:
        relative = str(record.get("path", ""))
        if not safe_relative(relative):
            findings.append({"severity": "Blocker", "code": "UNSAFE_ARCHIVE_PATH", "message": relative})
            continue
        path = (root / relative).resolve()
        arcname = Path(relative).as_posix()
        if arcname in seen:
            findings.append({"severity": "Blocker", "code": "DUPLICATE_ARCHIVE_PATH", "message": arcname})
            continue
        seen.add(arcname)
        if not inside(root, path) or not path.is_file() or path.is_symlink():
            findings.append({"severity": "Blocker", "code": "SUPPORT_MISSING", "message": relative})
        elif sha256(path) != record.get("sha256"):
            findings.append({"severity": "Blocker", "code": "SUPPORT_CHANGED", "message": relative})
        elif skipped(Path(relative)) or path.name.lower() in SECRET_NAMES or path.name.lower().startswith(".env."):
            findings.append({"severity": "Blocker", "code": "FORBIDDEN_SUPPORT_FILE", "message": relative})
        else:
            support.append((path, arcname))
    if not support:
        findings.append({"severity": "Blocker", "code": "EMPTY_SUPPORT", "message": "support archive has no files"})
    if not any(path.suffix.lower() in SOURCE_SUFFIXES for path, _ in support):
        findings.append({"severity": "Blocker", "code": "NO_SOURCE_CODE", "message": "support archive contains no recognized source-code file"})
    ai_used = payload.get("ai_used")
    if ai_used not in {"yes", "no"}:
        findings.append({"severity": "Blocker" if strict else "Major", "code": "AI_USE_UNKNOWN", "message": "ai_used must be yes or no before final build"})
    if ai_used == "yes" and not any(Path(arcname).name == "AI工具使用详情.pdf" for _, arcname in support):
        findings.append({"severity": "Blocker", "code": "AI_DETAIL_MISSING", "message": "AI工具使用详情.pdf is required in the support allowlist when ai_used=yes"})
    if strict and not payload.get("approved_by_team"):
        findings.append({"severity": "Blocker", "code": "TEAM_APPROVAL_MISSING", "message": "team approval is required for strict final build"})
    return root, paper, support, findings


def deterministic_zip(path: Path, support: list[tuple[Path, str]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=False) as archive:
        for source, arcname in sorted(support, key=lambda item: item[1]):
            info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with source.open("rb") as handle, archive.open(info, "w", force_zip64=True) as target:
                shutil.copyfileobj(handle, target, length=1024 * 1024)


def build(args: argparse.Namespace) -> int:
    manifest = args.manifest.expanduser().resolve()
    payload = load_json(manifest)
    root_override = args.root.expanduser().resolve() if args.root else None
    root, paper, support, findings = validate_manifest(payload, root_override, args.strict)
    limits = payload.get("limits") or {}
    paper_limit = int(limits.get("paper_max_bytes", DEFAULT_LIMIT))
    support_limit = int(limits.get("support_max_bytes", DEFAULT_LIMIT))
    if paper.is_file() and paper.stat().st_size > paper_limit:
        findings.append({"severity": "Blocker", "code": "PAPER_TOO_LARGE", "message": f"{paper.stat().st_size} > {paper_limit}"})
    if findings:
        print(json.dumps({"status": "blocked", "manifest": str(manifest), "findings": findings}, ensure_ascii=False, indent=2))
        return 2
    output = args.output_dir.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"output directory must not exist: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cumcm-package-", dir=output.parent) as temporary:
        staging = Path(temporary)
        upload = staging / "upload"
        evidence = staging / "evidence"
        upload.mkdir()
        evidence.mkdir()
        paper_name = Path(str(payload["paper"]["upload_name"])).name
        support_name = Path(str(payload["support_archive"]["upload_name"])).name
        if paper_name != payload["paper"]["upload_name"] or support_name != payload["support_archive"]["upload_name"]:
            raise ValueError("upload names must be plain filenames")
        if Path(paper_name).suffix.lower() not in {".pdf", ".docx"}:
            raise ValueError("paper upload name must end in .pdf or .docx")
        if Path(support_name).suffix.lower() != ".zip":
            raise ValueError("support upload name must end in .zip")
        paper_out = upload / paper_name
        support_out = upload / support_name
        shutil.copyfile(paper, paper_out)
        deterministic_zip(support_out, support)
        if support_out.stat().st_size > support_limit:
            print(json.dumps({"status": "blocked", "findings": [{"severity": "Blocker", "code": "SUPPORT_TOO_LARGE", "message": f"{support_out.stat().st_size} > {support_limit}"}]}, ensure_ascii=False, indent=2))
            return 2
        with zipfile.ZipFile(support_out) as archive:
            bad = archive.testzip()
            if bad:
                print(json.dumps({"status": "blocked", "findings": [{"severity": "Blocker", "code": "ZIP_CORRUPT", "message": bad}]}, ensure_ascii=False, indent=2))
                return 2
            archived = archive.namelist()
        hashes = {paper_out.name: sha256(paper_out), support_out.name: sha256(support_out)}
        report = {
            "version": 1,
            "status": "pass",
            "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "manifest": str(manifest),
            "manifest_sha256": sha256(manifest),
            "project_root": str(root),
            "upload_files": [
                {"name": paper_out.name, "bytes": paper_out.stat().st_size, "sha256": hashes[paper_out.name]},
                {"name": support_out.name, "bytes": support_out.stat().st_size, "sha256": hashes[support_out.name]},
            ],
            "support_entries": archived,
            "source_manifest_hashes_verified": True,
            "deterministic_zip": True,
            "approved_by_team": bool(payload.get("approved_by_team")),
            "findings": [],
        }
        (evidence / "SHA256SUMS.txt").write_text("".join(f"{hashes[name]}  {name}\n" for name in sorted(hashes)), encoding="utf-8")
        (evidence / "提交包校验报告.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        shutil.copytree(staging, output)
    print(json.dumps({"status": "pass", "output_dir": str(output), "upload_dir": str(output / "upload"), "evidence_dir": str(output / "evidence"), "upload_hashes": hashes}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic, hash-bound CUMCM submission package.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--root", type=Path, required=True)
    prepare_parser.add_argument("--paper", type=Path, required=True)
    prepare_parser.add_argument("--support", type=Path, action="append", required=True)
    prepare_parser.add_argument("--manifest", type=Path, required=True)
    prepare_parser.add_argument("--paper-upload-name")
    prepare_parser.add_argument("--support-upload-name", default="支撑材料.zip")
    prepare_parser.add_argument("--ai-used", choices=("yes", "no", "unknown"), default="unknown")
    prepare_parser.add_argument("--paper-max-bytes", type=int, default=DEFAULT_LIMIT)
    prepare_parser.add_argument("--support-max-bytes", type=int, default=DEFAULT_LIMIT)
    prepare_parser.add_argument("--replace-unapproved", action="store_true")
    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("--manifest", type=Path, required=True)
    approve_parser.add_argument("--approved-by", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--manifest", type=Path, required=True)
    build_parser.add_argument("--root", type=Path)
    build_parser.add_argument("--output-dir", type=Path, required=True)
    build_parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            return prepare(args)
        if args.command == "approve":
            return approve(args)
        return build(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
