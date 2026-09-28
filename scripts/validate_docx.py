#!/usr/bin/env python3
"""Static structural QA for a CUMCM DOCX without executing macros."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def load_xml(zf: zipfile.ZipFile, name: str):
    try:
        return ET.fromstring(zf.read(name))
    except KeyError:
        return None


def paragraph_text(p) -> str:
    return "".join((node.text or "") for node in p.iter(W + "t")).strip()


def inspect_docx(path: Path) -> dict:
    findings = []
    try:
        with zipfile.ZipFile(path) as zf:
            document = load_xml(zf, "word/document.xml")
            styles = load_xml(zf, "word/styles.xml")
            if document is None:
                return {"file": str(path), "findings": [finding("Blocker", "DOCX_XML", "word/document.xml is missing")], "metrics": {}}

            paragraphs = [paragraph_text(p) for p in document.iter(W + "p")]
            paragraphs = [p for p in paragraphs if p]
            text = "\n".join(paragraphs)
            tables = len(list(document.iter(W + "tbl")))
            equations = len(list(document.iter(M + "oMath")))
            drawings = len(list(document.iter(W + "drawing")))
            images = len([n for n in zf.namelist() if n.startswith("word/media/")])
            page_breaks = len([br for br in document.iter(W + "br") if br.attrib.get(W + "type") == "page"])
            file_size_mb = path.stat().st_size / (1024 * 1024)

            if file_size_mb > 20:
                findings.append(finding("Critical", "FILE_SIZE", "The paper exceeds the current 20 MB electronic-file limit.", round(file_size_mb, 2)))
            if paragraphs and not re.search(r"摘\s*要", paragraphs[0]):
                findings.append(finding("Critical", "FIRST_PAGE", "The electronic paper should begin with the abstract page; the first nonempty paragraph is not recognized as 摘要.", paragraphs[0][:120]))
            if re.search(r"承诺书|编号专用页", "\n".join(paragraphs[:8])):
                findings.append(finding("Critical", "FORBIDDEN_FRONT_MATTER", "The electronic paper appears to contain a commitment or numbering page, which should not be included."))

            required_sections = {
                "摘要": r"摘\s*要",
                "关键词": r"关\s*键\s*词",
                "问题重述或分析": r"问题(重述|分析)",
                "模型假设": r"模型假设|假设条件",
                "符号说明": r"符号说明|符号约定",
                "模型建立": r"模型(建立|构建)",
                "模型求解": r"模型求解|求解算法|算法设计",
                "模型检验": r"模型检验|模型验证|结果验证",
                "敏感性或稳健性": r"敏感性分析|灵敏度分析|稳健性分析|鲁棒性分析",
                "模型评价": r"模型评价|优缺点|模型改进|局限性",
                "参考文献": r"参考文献",
            }
            for label, pattern in required_sections.items():
                if not re.search(pattern, text, re.I):
                    severity = "Major" if label in {"模型检验", "模型建立", "模型求解", "摘要"} else "Minor"
                    findings.append(finding(severity, "MISSING_SECTION", f"Missing or unrecognized section: {label}"))

            if re.search(r"(^|\n)\s*目\s*录\s*($|\n)", text):
                findings.append(finding("Critical", "FORBIDDEN_TOC", "A table of contents was detected; current CUMCM format rules should be checked."))
            if re.search(r"学校[:：]|学院[:：]|姓名[:：]|学号[:：]", text):
                findings.append(finding("Blocker", "ANONYMITY", "Possible school or participant identity appears in the paper body."))
            if re.search(r"TODO|TBD|待补充|XXX|此处插入|placeholder", text, re.I):
                findings.append(finding("Critical", "PLACEHOLDER", "Unresolved placeholder text was detected."))

            figure_captions = re.findall(r"(?:^|\n)\s*图\s*\d+[\-—.]?\d*\s*[^\n]*", text)
            table_captions = re.findall(r"(?:^|\n)\s*表\s*\d+[\-—.]?\d*\s*[^\n]*", text)
            figure_mentions = len(re.findall(r"图\s*\d+", text))
            table_mentions = len(re.findall(r"表\s*\d+", text))
            if images and not figure_captions:
                findings.append(finding("Major", "FIGURE_CAPTIONS", "Images exist but no numbered Chinese figure captions were detected.", images))
            if tables and not table_captions:
                findings.append(finding("Major", "TABLE_CAPTIONS", "Word tables exist but no numbered Chinese table captions were detected.", tables))
            if images and figure_mentions < images:
                findings.append(finding("Minor", "FIGURE_REFERENCES", "Some images may not be numbered or referenced in text.", {"images": images, "mentions": figure_mentions}))
            if tables and table_mentions < tables:
                findings.append(finding("Minor", "TABLE_REFERENCES", "Some tables may not be numbered or referenced in text.", {"tables": tables, "mentions": table_mentions}))
            if equations == 0 and re.search(r"模型|方程|目标函数|约束", text):
                findings.append(finding("Major", "NO_EDITABLE_EQUATIONS", "Modeling language is present but no Office Math equations were detected; equations may be images or missing."))

            citation_ids = {int(x) for x in re.findall(r"\[(\d+)\]", text)}
            if "参考文献" in text and not citation_ids:
                findings.append(finding("Major", "CITATIONS", "Reference section detected but no bracketed in-text citations were found."))

            fonts = Counter()
            font_sizes = Counter()
            for rpr in document.iter(W + "rPr"):
                rf = rpr.find(W + "rFonts")
                if rf is not None:
                    for key in (W + "ascii", W + "eastAsia", W + "hAnsi"):
                        if rf.attrib.get(key):
                            fonts[rf.attrib[key]] += 1
                sz = rpr.find(W + "sz")
                if sz is not None and sz.attrib.get(W + "val"):
                    font_sizes[sz.attrib[W + "val"]] += 1
            if len(fonts) > 8:
                findings.append(finding("Minor", "FONT_VARIETY", "Many explicit fonts were detected; inspect style consistency.", dict(fonts.most_common(12))))
            if len(font_sizes) > 10:
                findings.append(finding("Minor", "SIZE_VARIETY", "Many explicit font sizes were detected; inspect style consistency.", dict(font_sizes.most_common(12))))

            if styles is None:
                findings.append(finding("Minor", "STYLES", "styles.xml is missing; formatting consistency may be fragile."))

            section_metrics = []
            for index, section in enumerate(document.iter(W + "sectPr"), start=1):
                margin = section.find(W + "pgMar")
                size = section.find(W + "pgSz")
                margins = {}
                if margin is not None:
                    for side in ("top", "right", "bottom", "left"):
                        raw = margin.attrib.get(W + side)
                        if raw is not None:
                            margins[side] = int(raw)
                    too_small = {k: v for k, v in margins.items() if v < 1417}
                    if too_small:
                        findings.append(finding("Critical", "PAGE_MARGINS", f"Section {index} has margins below 2.5 cm.", too_small))
                page_size = {}
                if size is not None:
                    for key in ("w", "h"):
                        raw = size.attrib.get(W + key)
                        if raw is not None:
                            page_size[key] = int(raw)
                    if len(page_size) == 2:
                        measured = sorted((page_size["w"], page_size["h"]))
                        a4 = sorted((11906, 16838))
                        if any(abs(x - y) > 300 for x, y in zip(measured, a4)):
                            findings.append(finding("Critical", "PAGE_SIZE", f"Section {index} is not recognized as A4.", page_size))
                section_metrics.append({"index": index, "margins_twips": margins, "page_size_twips": page_size})

            metrics = {
                "paragraphs": len(paragraphs),
                "characters": len(text),
                "tables": tables,
                "drawings": drawings,
                "embedded_images": images,
                "equation_nodes": equations,
                "manual_page_breaks": page_breaks,
                "figure_captions": len(figure_captions),
                "table_captions": len(table_captions),
                "citation_ids": len(citation_ids),
                "file_size_mb": round(file_size_mb, 3),
                "sections": section_metrics,
                "top_fonts": dict(fonts.most_common(8)),
                "top_font_sizes_half_points": dict(font_sizes.most_common(8)),
            }
            return {"file": str(path), "metrics": metrics, "findings": findings}
    except zipfile.BadZipFile:
        return {"file": str(path), "metrics": {}, "findings": [finding("Blocker", "BAD_DOCX", "File is not a valid DOCX ZIP package.")]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Return nonzero for Major findings as well as Critical/Blocker")
    args = parser.parse_args()
    if not args.docx.exists():
        print(json.dumps({"error": "file not found", "file": str(args.docx)}, ensure_ascii=False))
        return 2
    report = inspect_docx(args.docx)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"DOCX: {report['file']}")
        print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
        for item in report["findings"]:
            print(f"[{item['severity']}] {item['code']}: {item['message']}")
    severities = {x["severity"] for x in report["findings"]}
    if {"Blocker", "Critical"} & severities or (args.strict and "Major" in severities):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
