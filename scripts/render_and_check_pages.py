#!/usr/bin/env python3
"""Render a CUMCM DOCX/PDF and verify page-level submission constraints."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def convert_docx(docx: Path, destination: Path) -> Path:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("DOCX rendering requires soffice or libreoffice")
    command = [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(destination), str(docx)]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=180)
    expected = destination / f"{docx.stem}.pdf"
    if proc.returncode or not expected.is_file():
        raise RuntimeError(f"DOCX-to-PDF conversion failed: {proc.stderr or proc.stdout}")
    return expected


def pdf_pages(pdf: Path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Page checking requires pypdf") from exc
    reader = PdfReader(str(pdf))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        box = page.mediabox
        width = float(box.width)
        height = float(box.height)
        pages.append({"index": index, "text": page.extract_text() or "", "width_points": width, "height_points": height})
    return pages


def docx_hard_pages(docx: Path) -> list[dict]:
    """Recover text by explicit Word page breaks when PDF CJK maps are unusable."""
    with zipfile.ZipFile(docx) as zf:
        document = ET.fromstring(zf.read("word/document.xml"))
    output = []
    current: list[str] = []
    page_index = 1
    for paragraph in document.iter(W + "p"):
        pieces: list[str] = []
        for node in paragraph.iter():
            if node.tag == W + "t":
                pieces.append(node.text or "")
            elif node.tag == W + "tab":
                pieces.append("\t")
            elif node.tag == W + "br" and node.attrib.get(W + "type") == "page":
                current.append("".join(pieces))
                output.append({"index": page_index, "text": "\n".join(current)})
                page_index += 1
                current = []
                pieces = []
        current.append("".join(pieces))
    output.append({"index": page_index, "text": "\n".join(current)})
    return output


def first_matching_page(pages: list[dict], pattern: str, start: int = 0) -> int | None:
    regex = re.compile(pattern, re.I | re.M)
    for page in pages[start:]:
        if regex.search(page["text"]):
            return page["index"]
    return None


TOC_LEADER = re.compile(r"(?:\.\s*){3,}|…{2,}|⋯{2,}|·{3,}")


def is_toc_line(line: str) -> bool:
    """Return True for a table-of-contents entry rather than a real heading."""
    compact = line.strip()
    if not compact:
        return False
    return bool(
        TOC_LEADER.search(compact)
        or re.search(r"\s{3,}\d+\s*$", compact)
        or re.search(r"(?:问题重述|问题分析|附\s*录).{0,80}\d+\s*$", compact)
    )


def first_heading_page(pages: list[dict], pattern: str, start: int = 0) -> int | None:
    """Locate a section heading while ignoring matching entries in a TOC."""
    regex = re.compile(pattern, re.I)
    for page in pages[start:]:
        for line in page["text"].splitlines():
            if regex.search(line) and not is_toc_line(line):
                return page["index"]
    return None


def toc_pages(pages: list[dict], search_limit: int = 8) -> list[int]:
    detected = []
    for page in pages[:search_limit]:
        text = page["text"]
        explicit_heading = any(re.fullmatch(r"\s*目\s*录\s*", line) for line in text.splitlines())
        leader_count = sum(bool(TOC_LEADER.search(line)) for line in text.splitlines())
        numbered_entries = sum(
            bool(re.search(r"(?:问题重述|问题分析|模型|附\s*录).{0,100}\d+\s*$", line))
            for line in text.splitlines()
        )
        continuation = bool(detected and detected[-1] == page["index"] - 1 and leader_count >= 1)
        if explicit_heading or leader_count >= 3 or numbered_entries >= 4 or continuation:
            detected.append(page["index"])
    return detected


def render_pdf(pdf: Path, output: Path, dpi: int) -> list[str]:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("Page-image rendering requires pdftoppm")
    prefix = output / "page"
    command = [pdftoppm, "-png", "-r", str(dpi), str(pdf), str(prefix)]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=600)
    if proc.returncode:
        raise RuntimeError(f"pdftoppm failed: {proc.stderr or proc.stdout}")
    images = sorted(output.glob("page-*.png"))
    if not images:
        raise RuntimeError("pdftoppm produced no page images")
    return [str(path) for path in images]


def image_ink_coverage(paths: list[str]) -> list[dict]:
    try:
        from PIL import Image
    except ImportError:
        return []
    output = []
    for index, raw in enumerate(paths, start=1):
        with Image.open(raw) as image:
            gray = image.convert("L")
            histogram = gray.histogram()
            total = max(1, sum(histogram))
            ink = sum(histogram[:245])
            output.append({"page": index, "ink_fraction": round(ink / total, 6)})
    return output


def inspect(
    source: Path,
    output_root: Path,
    dpi: int,
    abstract_max_pages: int,
    body_max_pages: int,
    body_start_pattern: str,
    appendix_pattern: str,
) -> dict:
    findings: list[dict] = []
    render_dir = output_root / f"{source.stem}-render"
    if render_dir.exists():
        return {
            "source": str(source),
            "findings": [finding("Blocker", "OUTPUT_EXISTS", f"Render directory already exists: {render_dir}")],
            "metrics": {},
        }
    render_dir.mkdir(parents=True)
    try:
        with tempfile.TemporaryDirectory(prefix="cumcm-render-") as temp:
            temp_dir = Path(temp)
            pdf = source if source.suffix.lower() == ".pdf" else convert_docx(source, temp_dir)
            copied_pdf = render_dir / "rendered-paper.pdf"
            shutil.copy2(pdf, copied_pdf)
            pages = pdf_pages(copied_pdf)
            if not pages:
                raise RuntimeError("PDF has no pages")
            page_count = len(pages)
            logical_pages = docx_hard_pages(source) if source.suffix.lower() == ".docx" else pages
            if source.suffix.lower() == ".docx":
                source_cjk = set(re.findall(r"[\u3400-\u9fff]", "\n".join(page["text"] for page in logical_pages)))
                rendered_cjk = set(re.findall(r"[\u3400-\u9fff]", "\n".join(page["text"] for page in pages)))
                if len(source_cjk) >= 20 and len(rendered_cjk) < max(5, int(len(source_cjk) * 0.3)):
                    findings.append(
                        finding(
                            "Major",
                            "CJK_RENDER_MAPPING",
                            "Rendered PDF exposes far less Chinese text diversity than the DOCX; inspect for missing glyphs or font substitution.",
                            {"docx_unique_cjk": len(source_cjk), "pdf_unique_cjk": len(rendered_cjk)},
                        )
                    )
            body_start = first_heading_page(logical_pages, body_start_pattern, start=1)
            appendix_start = first_heading_page(logical_pages, appendix_pattern, start=1)
            detected_toc_pages = toc_pages(logical_pages)
            keyword_page = first_matching_page(logical_pages, r"关\s*键\s*[词字]")
            abstract_pages = keyword_page
            front_matter_pages = body_start - 1 if body_start else None
            body_end = (appendix_start - 1) if appendix_start else page_count
            body_pages = body_end - body_start + 1 if body_start else None

            first_text = logical_pages[0]["text"]
            if source.stat().st_size > 20 * 1024 * 1024:
                findings.append(
                    finding(
                        "Critical",
                        "PAPER_FILE_SIZE",
                        "The electronic paper exceeds 20 MiB.",
                        {"bytes": source.stat().st_size},
                    )
                )
            if not re.search(r"摘\s*要", first_text):
                findings.append(finding("Critical", "ABSTRACT_FIRST", "The first rendered page does not contain a recognized abstract heading."))
            if not re.search(r"关\s*键\s*[词字]", first_text):
                findings.append(finding("Major", "KEYWORDS_FIRST", "The first rendered page does not contain recognized keywords."))
            if detected_toc_pages:
                findings.append(
                    finding(
                        "Critical",
                        "FORBIDDEN_TOC",
                        "A table of contents was detected; the current CUMCM paper format forbids one.",
                        detected_toc_pages,
                    )
                )
            if abstract_pages is None:
                findings.append(finding("Major", "BODY_START", "Could not identify the first body page.", body_start_pattern))
            elif abstract_pages > abstract_max_pages:
                findings.append(
                    finding(
                        "Critical",
                        "ABSTRACT_PAGES",
                        f"The abstract and keywords extend through rendered page {abstract_pages}; limit is {abstract_max_pages} page(s).",
                    )
                )
            if body_pages is None:
                findings.append(finding("Major", "BODY_PAGE_COUNT", "Could not calculate rendered body-page count."))
            elif body_pages > body_max_pages:
                findings.append(finding("Critical", "BODY_PAGES", f"Rendered body occupies {body_pages} pages; limit is {body_max_pages}."))

            non_a4 = []
            for page in pages:
                measured = sorted((page["width_points"], page["height_points"]))
                expected = sorted((595.28, 841.89))
                if any(abs(a - b) > 12 for a, b in zip(measured, expected)):
                    non_a4.append({"page": page["index"], "width": round(page["width_points"], 2), "height": round(page["height_points"], 2)})
            if non_a4:
                findings.append(finding("Critical", "PAGE_SIZE", "Rendered pages not recognized as A4.", non_a4[:20]))

            blank_pages = [
                page["index"]
                for page in pages
                if len(re.sub(r"\s+", "", page["text"])) < 12
            ]
            if blank_pages:
                findings.append(
                    finding(
                        "Major",
                        "NEAR_BLANK_PAGES",
                        "Near-blank rendered pages require manual confirmation.",
                        blank_pages,
                    )
                )
            identity_pattern = re.compile(
                r"参赛队员|队员姓名|参赛学校|所属学校|指导教师|学号\s*[:：]|"
                r"电子邮箱\s*[:：]|联系电话\s*[:：]|(?:/Users/|[A-Za-z]:\\\\Users\\\\)",
                re.I,
            )
            identity_hits = [
                page["index"]
                for page in logical_pages
                if identity_pattern.search(page["text"])
            ]
            if identity_hits:
                findings.append(
                    finding(
                        "Critical",
                        "POSSIBLE_IDENTITY",
                        "Possible team identity or machine-specific path appears in the rendered paper.",
                        identity_hits,
                    )
                )

            images = render_pdf(copied_pdf, render_dir, dpi)
            coverage = image_ink_coverage(images)
            near_empty_images = [item for item in coverage if item["ink_fraction"] < 0.0005]
            if near_empty_images:
                findings.append(
                    finding(
                        "Major",
                        "VISUALLY_NEAR_EMPTY",
                        "Rendered page images appear nearly empty; inspect font rendering and page breaks.",
                        near_empty_images,
                    )
                )
            metrics = {
                "source_sha256": sha256(source),
                "source_bytes": source.stat().st_size,
                "page_count": page_count,
                "hard_break_page_count": len(logical_pages) if source.suffix.lower() == ".docx" else None,
                "abstract_pages": abstract_pages,
                "front_matter_pages": front_matter_pages,
                "body_start_page": body_start,
                "body_pages": body_pages,
                "appendix_start_page": appendix_start,
                "toc_pages": detected_toc_pages,
                "render_dpi": dpi,
                "render_dir": str(render_dir),
                "rendered_pdf": str(copied_pdf),
                "page_images": images,
                "page_ink_coverage": coverage,
                "manual_inspection": {
                    "required": True,
                    "checks": [
                        "clipping",
                        "overlap",
                        "equations",
                        "tables",
                        "figures",
                        "captions",
                        "page_breaks",
                        "anonymity",
                    ],
                },
            }
            return {"source": str(source), "metrics": metrics, "findings": findings}
    except Exception as exc:
        findings.append(finding("Blocker", "RENDER", str(exc)))
        return {"source": str(source), "metrics": {"render_dir": str(render_dir)}, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paper", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=140)
    parser.add_argument("--abstract-max-pages", type=int, default=1)
    parser.add_argument("--body-max-pages", type=int, default=30)
    parser.add_argument("--body-start-pattern", default=r"问题重述|问题分析|一[、.．]\s*问题")
    parser.add_argument("--appendix-pattern", default=r"(^|\n)\s*附\s*录")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    paper = args.paper.resolve()
    if not paper.is_file() or paper.suffix.lower() not in {".docx", ".pdf"}:
        print(json.dumps({"error": "paper must be an existing DOCX or PDF", "paper": str(paper)}, ensure_ascii=False))
        return 2
    if args.dpi < 72 or args.dpi > 300:
        parser.error("--dpi must be between 72 and 300")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = inspect(
        paper,
        args.output_dir.resolve(),
        args.dpi,
        args.abstract_max_pages,
        args.body_max_pages,
        args.body_start_pattern,
        args.appendix_pattern,
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
