#!/usr/bin/env python3
"""Validate a citation manifest, paper citation coverage, and optional online metadata."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.I)


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower()
    return re.sub(r"[\W_]+", "", value, flags=re.UNICODE)


def similarity(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, normalize(left), normalize(right)).ratio()


def validate_schema(payload: dict, schema_path: Path) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", "Citation manifest was not checked with JSON Schema.")]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [finding("Blocker", "SCHEMA_READ", str(exc), str(schema_path))]
    output = []
    for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        output.append(finding("Blocker", "MANIFEST_SCHEMA", f"{location}: {error.message}"))
    return output


def numeric_citations(text: str) -> set[str]:
    output: set[str] = set()
    for content in re.findall(r"\[([0-9\s,，、;\-–—]+)\]", text):
        for part in re.split(r"[,，、;]\s*", content):
            token = part.strip()
            if not token:
                continue
            range_match = re.fullmatch(r"(\d+)\s*[\-–—]\s*(\d+)", token)
            if range_match:
                start, end = map(int, range_match.groups())
                if 0 < start <= end and end - start <= 100:
                    output.update(str(value) for value in range(start, end + 1))
            elif token.isdigit():
                output.add(str(int(token)))
    return output


def paper_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        with zipfile.ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
        return "\n".join("".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p"))
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF citation checking requires pypdf") from exc
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def fetch_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "CUMCM-citation-validator/1.0 (metadata verification)"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def check_url(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "CUMCM-citation-validator/1.0"}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {"status": response.status, "final_url": response.geturl()}
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 405}:
            request = urllib.request.Request(url, headers={"User-Agent": "CUMCM-citation-validator/1.0"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return {"status": response.status, "final_url": response.geturl()}
        raise


def fetch_source_text(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "CUMCM-citation-validator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read(5 * 1024 * 1024 + 1)
        if len(data) > 5 * 1024 * 1024:
            raise ValueError("source exceeds 5 MiB inspection limit")
        content_type = response.headers.get_content_type()
        if content_type == "application/pdf" or data.startswith(b"%PDF"):
            with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
                handle.write(data)
                handle.flush()
                from pypdf import PdfReader

                text = "\n".join(page.extract_text() or "" for page in PdfReader(handle.name).pages[:8])
        else:
            decoded = data.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            text = re.sub(r"<script\b[\s\S]*?</script>|<style\b[\s\S]*?</style>", " ", decoded, flags=re.I)
            text = re.sub(r"<[^>]+>", " ", text)
        return {
            "status": response.status,
            "final_url": response.geturl(),
            "text": re.sub(r"\s+", " ", text).strip(),
        }


def crossref_metadata(doi: str, timeout: int) -> dict:
    encoded = urllib.parse.quote(doi, safe="")
    payload = fetch_json(f"https://api.crossref.org/works/{encoded}", timeout)
    return payload["message"]


def openalex_metadata(doi: str, timeout: int) -> dict:
    identifier = urllib.parse.quote(f"https://doi.org/{doi}", safe="")
    return fetch_json(f"https://api.openalex.org/works/{identifier}", timeout)


def author_tokens(value) -> set[str]:
    values = value if isinstance(value, list) else [value]
    output = set()
    for item in values:
        text = str(item or "")
        whole = normalize(text)
        if whole:
            output.add(whole)
        output.update(
            normalize(token)
            for token in re.split(r"[,;，、\s]+", text)
            if normalize(token)
        )
    return output


def external_refchecker(paper: Path, mode: str, timeout: int) -> dict:
    executable = shutil.which("academic-refchecker")
    if not executable:
        severity = "Critical" if mode == "required" else "Major"
        return {
            "available": False,
            "findings": [finding(severity, "REFCHECKER_UNAVAILABLE", "academic-refchecker is not installed.")],
        }
    if paper.suffix.lower() not in {".pdf", ".tex", ".bib", ".bbl", ".txt"}:
        severity = "Critical" if mode == "required" else "Major"
        return {
            "available": True,
            "findings": [
                finding(
                    severity,
                    "REFCHECKER_INPUT",
                    "The external CLI does not declare DOCX support; render the paper to PDF before running it.",
                    str(paper),
                )
            ],
        }
    with tempfile.TemporaryDirectory(prefix="cumcm-refchecker-") as temp:
        report_path = Path(temp) / "report.json"
        command = [
            executable,
            "--paper",
            str(paper),
            "--report-file",
            str(report_path),
            "--report-format",
            "json",
            "--no-llm",
            "--check-citation-order",
        ]
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=max(timeout, 60))
            report = None
            if report_path.is_file():
                try:
                    report = json.loads(report_path.read_text(encoding="utf-8"))
                except Exception:
                    report = report_path.read_text(encoding="utf-8", errors="replace")[-12000:]
            local = []
            if proc.returncode:
                local.append(
                    finding(
                        "Critical",
                        "REFCHECKER_FAILED",
                        "External multi-source reference verification reported errors or failed.",
                        {"returncode": proc.returncode, "stderr_tail": proc.stderr[-6000:]},
                    )
                )
            return {
                "available": True,
                "command": command,
                "returncode": proc.returncode,
                "report": report,
                "findings": local,
            }
        except Exception as exc:
            return {
                "available": True,
                "findings": [finding("Critical", "REFCHECKER_ERROR", str(exc))],
            }


def inspect(
    manifest_path: Path,
    paper: Path | None,
    online: bool,
    timeout: int,
    schema_path: Path | None = None,
    refchecker_mode: str = "off",
) -> dict:
    findings: list[dict] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"manifest": str(manifest_path), "findings": [finding("Blocker", "MANIFEST_JSON", str(exc))], "citations": []}
    if not isinstance(manifest, dict):
        return {"manifest": str(manifest_path), "findings": [finding("Blocker", "MANIFEST_SCHEMA", "Manifest root must be an object.")], "citations": []}
    if schema_path:
        findings.extend(validate_schema(manifest, schema_path))
    citations = manifest.get("citations")
    if manifest.get("version") != 1 or not isinstance(citations, list):
        return {
            "manifest": str(manifest_path),
            "findings": [finding("Blocker", "MANIFEST_SCHEMA", "Expected version 1 and a citations array.")],
            "citations": [],
        }
    competition_context = manifest.get("competition_context")
    if not isinstance(competition_context, dict):
        findings.append(
            finding(
                "Major",
                "CITATION_CONTEXT_REQUIRED",
                "Record whether this is a live competition or retrospective audit, plus the competition year and evidence cutoff date.",
            )
        )
        competition_context = {}
    context_mode = competition_context.get("mode")
    competition_year = competition_context.get("competition_year")
    evidence_cutoff = str(competition_context.get("evidence_cutoff_date", ""))
    invalid_items = [index for index, item in enumerate(citations) if not isinstance(item, dict)]
    if invalid_items:
        findings.append(finding("Blocker", "CITATION_ITEM_SCHEMA", "Every citation must be an object.", invalid_items))
    citations = [item for item in citations if isinstance(item, dict)]
    ids = [str(item.get("id", "")).strip() for item in citations]
    duplicates = sorted({item for item in ids if item and ids.count(item) > 1})
    if duplicates:
        findings.append(finding("Blocker", "DUPLICATE_CITATION_ID", "Citation IDs must be unique.", duplicates))

    text = None
    cited_ids: set[str] = set()
    if paper:
        try:
            text = paper_text(paper)
            cited_ids = numeric_citations(text)
        except Exception as exc:
            findings.append(finding("Blocker", "PAPER_READ", str(exc)))

    checked = []
    for item in citations:
        citation_id = str(item.get("id", "")).strip()
        local = []
        required = ["title", "authors", "year", "source_type", "verified_at", "verified_by", "verification_evidence", "claims"]
        missing = [field for field in required if not item.get(field)]
        if not citation_id:
            missing.append("id")
        if missing:
            local.append(finding("Critical", "CITATION_FIELDS", f"Citation {citation_id or '?'} is missing required fields.", missing))
        placeholder_blob = json.dumps(item, ensure_ascii=False)
        if re.search(
            r"replace|publisher\.example|人工检索后|作者甲|作者乙|来源名称|"
            r"队员姓名或角色|YYYY-MM-DD|实际支持的具体陈述",
            placeholder_blob,
            re.I,
        ):
            local.append(
                finding(
                    "Blocker",
                    "CITATION_PLACEHOLDER",
                    f"Citation {citation_id or '?'} still contains template or example metadata.",
                )
            )
        verifier = str(item.get("verified_by", ""))
        if re.search(r"ChatGPT|DeepSeek|Claude|Gemini|Codex|OpenAI|AI|模型|机器人", verifier, re.I):
            local.append(
                finding(
                    "Blocker",
                    "NON_HUMAN_CITATION_VERIFIER",
                    f"Citation {citation_id or '?'} claims verification by an AI system rather than a team member.",
                    verifier,
                )
            )
        evidence = item.get("verification_evidence", {})
        if isinstance(evidence, dict) and evidence.get("source_snapshot_sha256") == "0" * 64:
            local.append(
                finding(
                    "Blocker",
                    "CITATION_EVIDENCE_PLACEHOLDER",
                    f"Citation {citation_id or '?'} has no real source snapshot hash.",
                )
            )
        if item.get("source_type") not in {"primary", "official", "standard", "dataset", "secondary"}:
            local.append(finding("Major", "SOURCE_TYPE", f"Citation {citation_id}: source_type is not recognized."))
        if item.get("source_type") == "secondary":
            local.append(finding("Major", "SECONDARY_SOURCE", f"Citation {citation_id}: justify why a primary or official source is unavailable."))
        try:
            citation_year = int(item.get("year"))
        except (TypeError, ValueError):
            citation_year = None
        if (
            context_mode == "live_competition"
            and isinstance(competition_year, int)
            and citation_year is not None
            and citation_year > competition_year
        ):
            local.append(
                finding(
                    "Critical",
                    "POST_COMPETITION_CITATION",
                    f"Citation {citation_id}: publication year {citation_year} is later than competition year {competition_year}.",
                )
            )
        verified_at = str(item.get("verified_at", ""))
        if context_mode == "live_competition" and evidence_cutoff and verified_at and verified_at > evidence_cutoff:
            local.append(
                finding(
                    "Critical",
                    "POST_CUTOFF_VERIFICATION",
                    f"Citation {citation_id}: verification date is later than the declared evidence cutoff.",
                    {"verified_at": verified_at, "evidence_cutoff_date": evidence_cutoff},
                )
            )
        claims = item.get("claims", [])
        if not isinstance(claims, list) or not claims:
            local.append(finding("Critical", "CLAIM_MAPPING", f"Citation {citation_id}: no claim-support mapping was recorded."))
        else:
            for claim_index, claim in enumerate(claims):
                if not isinstance(claim, dict):
                    local.append(
                        finding(
                            "Critical",
                            "CLAIM_FIELDS",
                            f"Citation {citation_id}, claim {claim_index + 1}: claim record must be an object.",
                        )
                    )
                    continue
                missing_claim = [field for field in ("paper_location", "claim", "support_note") if not claim.get(field)]
                if missing_claim:
                    local.append(
                        finding(
                            "Major",
                            "CLAIM_FIELDS",
                            f"Citation {citation_id}, claim {claim_index + 1}: incomplete support record.",
                            missing_claim,
                        )
                    )

        doi = str(item.get("doi", "")).strip()
        url = str(item.get("url", "")).strip()
        if not doi and not url:
            local.append(finding("Critical", "NO_IDENTIFIER", f"Citation {citation_id}: provide a DOI or source URL."))
        if doi and not DOI_PATTERN.match(doi):
            local.append(finding("Critical", "DOI_FORMAT", f"Citation {citation_id}: invalid DOI syntax.", doi))
        if url and urllib.parse.urlparse(url).scheme not in {"http", "https"}:
            local.append(finding("Critical", "URL_FORMAT", f"Citation {citation_id}: URL must use HTTP(S).", url))

        online_evidence = {}
        definitive_not_found = set()
        if online:
            if doi and DOI_PATTERN.match(doi):
                try:
                    metadata = crossref_metadata(doi, timeout)
                    remote_title = (metadata.get("title") or [""])[0]
                    title_score = similarity(str(item.get("title", "")), remote_title)
                    remote_year = None
                    for field in ("published-print", "published-online", "issued"):
                        parts = ((metadata.get(field) or {}).get("date-parts") or [])
                        if parts and parts[0]:
                            remote_year = parts[0][0]
                            break
                    online_evidence["crossref"] = {
                        "title": remote_title,
                        "title_similarity": round(title_score, 3),
                        "year": remote_year,
                    }
                    remote_authors = [
                        f"{author.get('given', '')} {author.get('family', '')}"
                        for author in metadata.get("author", [])
                    ]
                    local_authors = author_tokens(item.get("authors"))
                    remote_author_tokens = author_tokens(remote_authors)
                    overlap = len(local_authors & remote_author_tokens) / max(1, len(local_authors))
                    online_evidence["crossref"]["author_token_overlap"] = round(overlap, 3)
                    if title_score < 0.72:
                        local.append(finding("Critical", "TITLE_METADATA", f"Citation {citation_id}: title disagrees with DOI metadata.", online_evidence["crossref"]))
                    if remote_year and str(item.get("year")) != str(remote_year):
                        local.append(finding("Major", "YEAR_METADATA", f"Citation {citation_id}: year differs from DOI metadata.", online_evidence["crossref"]))
                    if local_authors and remote_author_tokens and overlap < 0.5:
                        local.append(finding("Critical", "AUTHOR_METADATA", f"Citation {citation_id}: authors disagree with DOI metadata.", online_evidence["crossref"]))
                except Exception as exc:
                    if isinstance(exc, urllib.error.HTTPError) and exc.code == 404:
                        definitive_not_found.add("crossref")
                    local.append(finding("Major", "DOI_LOOKUP", f"Citation {citation_id}: DOI metadata lookup failed: {exc}"))
                try:
                    metadata = openalex_metadata(doi, timeout)
                    openalex_title = str(metadata.get("title", ""))
                    openalex_year = metadata.get("publication_year")
                    openalex_score = similarity(str(item.get("title", "")), openalex_title)
                    online_evidence["openalex"] = {
                        "id": metadata.get("id"),
                        "title": openalex_title,
                        "title_similarity": round(openalex_score, 3),
                        "year": openalex_year,
                        "is_retracted": metadata.get("is_retracted"),
                    }
                    if openalex_score < 0.72:
                        local.append(finding("Critical", "OPENALEX_TITLE", f"Citation {citation_id}: title disagrees with OpenAlex.", online_evidence["openalex"]))
                    if metadata.get("is_retracted"):
                        local.append(finding("Critical", "RETRACTED_SOURCE", f"Citation {citation_id}: OpenAlex marks this work as retracted.", online_evidence["openalex"]))
                except Exception as exc:
                    if isinstance(exc, urllib.error.HTTPError) and exc.code == 404:
                        definitive_not_found.add("openalex")
                    local.append(finding("Major", "OPENALEX_LOOKUP", f"Citation {citation_id}: OpenAlex lookup failed: {exc}"))
                try:
                    online_evidence["doi_resolver"] = check_url(f"https://doi.org/{doi}", timeout)
                except Exception as exc:
                    if isinstance(exc, urllib.error.HTTPError) and exc.code == 404:
                        definitive_not_found.add("resolver")
                    local.append(finding("Major", "DOI_RESOLVER", f"Citation {citation_id}: DOI resolver failed: {exc}"))
                if {"crossref", "openalex", "resolver"} <= definitive_not_found:
                    local.append(
                        finding(
                            "Blocker",
                            "CITATION_NOT_FOUND",
                            f"Citation {citation_id}: DOI is definitively absent from Crossref, OpenAlex, and the DOI resolver despite a completed-verification claim.",
                            doi,
                        )
                    )
            if url:
                try:
                    source = fetch_source_text(url, timeout)
                    source_text = source.pop("text")
                    title_present = normalize(str(item.get("title", ""))) in normalize(source_text)
                    source["title_present"] = title_present
                    online_evidence["url"] = source
                    if not title_present:
                        local.append(
                            finding(
                                "Critical",
                                "URL_TITLE_EVIDENCE",
                                f"Citation {citation_id}: the declared title was not found in the reachable source content.",
                                {"title": item.get("title"), "url": url},
                            )
                        )
                except Exception as exc:
                    severity = "Blocker" if isinstance(exc, urllib.error.HTTPError) and exc.code == 404 else "Major"
                    local.append(finding(severity, "URL_LOOKUP", f"Citation {citation_id}: source URL could not be verified: {exc}"))
            time.sleep(0.1)

        findings.extend(local)
        checked.append({"id": citation_id, "online": online_evidence, "findings": local})

    if text is not None:
        manifest_ids = {item for item in ids if item}
        missing_manifest = sorted(cited_ids - manifest_ids, key=lambda value: int(value))
        uncited_manifest = sorted(
            manifest_ids - cited_ids,
            key=lambda value: (0, int(value)) if value.isdigit() else (1, value),
        )
        if missing_manifest:
            findings.append(finding("Critical", "PAPER_CITATION_UNMAPPED", "Paper citations are absent from the manifest.", missing_manifest))
        if uncited_manifest:
            findings.append(finding("Major", "MANIFEST_NOT_CITED", "Manifest entries are not cited in the paper.", uncited_manifest))

    external = None
    if paper and refchecker_mode != "off":
        external = external_refchecker(paper, refchecker_mode, timeout)
        findings.extend(external.get("findings", []))
    return {
        "manifest": str(manifest_path),
        "paper": str(paper) if paper else None,
        "online": online,
        "citations": checked,
        "external_refchecker": external,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--paper", type=Path)
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--external-refchecker", choices=("off", "auto", "required"), default="off")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.manifest.is_file():
        print(json.dumps({"error": "citation manifest not found", "manifest": str(args.manifest)}, ensure_ascii=False))
        return 2
    if args.paper and not args.paper.is_file():
        print(json.dumps({"error": "paper not found", "paper": str(args.paper)}, ensure_ascii=False))
        return 2
    schema = args.schema
    if schema is None:
        schema = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "citation-manifest.schema.json"
    report = inspect(
        args.manifest.resolve(),
        args.paper.resolve() if args.paper else None,
        args.online,
        args.timeout,
        schema.resolve(),
        args.external_refchecker,
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
