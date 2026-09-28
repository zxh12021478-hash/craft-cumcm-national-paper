#!/usr/bin/env python3
"""Check official CUMCM rule pages for availability, required language, and snapshot changes."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def normalized_text(raw: str) -> str:
    raw = re.sub(r"<script\b[\s\S]*?</script>|<style\b[\s\S]*?</style>", " ", raw, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", text).strip()


def fetch(url: str, timeout: int) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "CUMCM-official-rule-monitor/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
        return normalized_text(raw), response.geturl()


def inspect(manifest_path: Path, snapshot_path: Path | None, timeout: int) -> dict:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "manifest": str(manifest_path),
            "snapshot": str(snapshot_path) if snapshot_path else None,
            "documents": {},
            "findings": [finding("Blocker", "RULE_MANIFEST_JSON", str(exc))],
        }
    snapshot = {}
    if snapshot_path and snapshot_path.is_file():
        try:
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8")).get("documents", {})
        except Exception as exc:
            return {
                "manifest": str(manifest_path),
                "snapshot": str(snapshot_path),
                "documents": {},
                "findings": [finding("Blocker", "RULE_SNAPSHOT_JSON", str(exc))],
            }
    findings: list[dict] = []
    if manifest.get("version") != 1 or not isinstance(manifest.get("documents"), list):
        findings.append(finding("Blocker", "RULE_MANIFEST_SCHEMA", "Expected version 1 and a documents array."))
    try:
        last_reviewed = date.fromisoformat(str(manifest.get("last_reviewed")))
        age_days = (date.today() - last_reviewed).days
        if age_days > 30:
            findings.append(
                finding(
                    "Major",
                    "RULE_REVIEW_STALE",
                    "The bundled official-rule review is older than 30 days; refresh it before final compliance advice.",
                    {"last_reviewed": str(last_reviewed), "age_days": age_days},
                )
            )
    except Exception:
        findings.append(finding("Critical", "RULE_REVIEW_DATE", "last_reviewed must be an ISO date."))
    documents = {}
    for document in manifest.get("documents", []):
        if not isinstance(document, dict) or not document.get("id") or not document.get("url"):
            findings.append(finding("Blocker", "RULE_DOCUMENT_SCHEMA", "Each rule document requires id and url.", document))
            continue
        doc_id = document["id"]
        local = []
        parsed = urlparse(document["url"])
        if parsed.scheme != "https" or parsed.hostname not in {"mcm.edu.cn", "www.mcm.edu.cn"}:
            local.append(
                finding(
                    "Blocker",
                    "NON_OFFICIAL_RULE_SOURCE",
                    f"{doc_id}: rule source must be an official HTTPS mcm.edu.cn page.",
                    document["url"],
                )
            )
            documents[doc_id] = {"url": document["url"], "findings": local}
            findings.extend(local)
            continue
        try:
            text, final_url = fetch(document["url"], timeout)
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            missing = [phrase for phrase in document.get("required_phrases", []) if phrase not in text]
            if missing:
                local.append(finding("Critical", "REQUIRED_LANGUAGE", f"{doc_id}: required official language was not found.", missing))
            previous = snapshot.get(doc_id, {})
            changed = bool(previous.get("normalized_sha256") and previous["normalized_sha256"] != digest)
            if changed:
                local.append(
                    finding(
                        "Major",
                        "OFFICIAL_PAGE_CHANGED",
                        f"{doc_id}: official page content changed since the stored snapshot; re-review before relying on remembered rules.",
                        {"previous": previous["normalized_sha256"], "current": digest},
                    )
                )
            documents[doc_id] = {
                "url": document["url"],
                "final_url": final_url,
                "normalized_sha256": digest,
                "characters": len(text),
                "changed": changed,
                "findings": local,
            }
        except Exception as exc:
            local.append(finding("Critical", "OFFICIAL_FETCH", f"{doc_id}: {exc}"))
            documents[doc_id] = {"url": document["url"], "findings": local}
        findings.extend(local)
    return {"manifest": str(manifest_path), "snapshot": str(snapshot_path) if snapshot_path else None, "documents": documents, "findings": findings}


def write_snapshot(report: dict, output: Path) -> None:
    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "documents": {
            key: {
                "url": value.get("url"),
                "final_url": value.get("final_url"),
                "normalized_sha256": value.get("normalized_sha256"),
                "characters": value.get("characters"),
            }
            for key, value in report["documents"].items()
            if value.get("normalized_sha256")
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--write-snapshot", type=Path)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.manifest.is_file():
        print(json.dumps({"error": "rule manifest not found", "manifest": str(args.manifest)}, ensure_ascii=False))
        return 2
    report = inspect(args.manifest.resolve(), args.snapshot.resolve() if args.snapshot else None, args.timeout)
    if args.write_snapshot:
        write_snapshot(report, args.write_snapshot.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in report["findings"]}
    return int(bool({"Blocker", "Critical"} & severities or (args.strict and "Major" in severities)))


if __name__ == "__main__":
    raise SystemExit(main())
