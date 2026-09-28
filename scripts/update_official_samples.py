#!/usr/bin/env python3
"""Build a best-effort catalog of official CUMCM displayed-paper pages."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import re
import urllib.parse
import urllib.request
from pathlib import Path

ARCHIVE = "https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/qkt_sxjm_lw_lwzs.shtml"
LANDING = "https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/{year}qgdxssxjmjslwzs/"
DOWNLOAD_NOTICE_2012 = "https://www.mcm.edu.cn/html_cn/node/8c3e830dda1bb96e37585116432e5747.html"
MANUAL_OFFICIAL_PAPERS = {
    2023: [
        {
            "code": "A0175",
            "title": "2023高教社杯全国大学生数学建模竞赛A题论文展示（A0175）",
            "url": "https://dxs.moe.gov.cn/zx/a/hd_sxjm_sxjmlw_2023qgdxssxjmjslwzs_2023atlw/231104/1865114.shtml",
        }
    ]
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CUMCM-sample-index/1.0"})
    with urllib.request.urlopen(request, timeout=8) as response:
        return response.read().decode("utf-8", errors="ignore")


def strip_tags(raw: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def extract_papers(page: str, base: str, year: int) -> list[dict]:
    papers = []
    for match in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>([\s\S]*?)</a>", page, re.I):
        href, body = match.groups()
        title = strip_tags(body)
        if str(year) not in title or "数学建模竞赛" not in title or "论文展示" not in title:
            continue
        code_match = re.search(r"[（(]\s*([A-E]\s*\d+)\s*[）)]", title, re.I)
        if not code_match:
            continue
        code = re.sub(r"\s+", "", code_match.group(1).upper())
        papers.append({"code": code, "title": title, "url": urllib.parse.urljoin(base, href)})
    unique = {}
    for paper in papers:
        unique[(paper["code"], paper["url"])] = paper
    return sorted(unique.values(), key=lambda x: (x["code"][0], int(re.sub(r"\D", "", x["code"]) or 0)))


def extract_index_pages(page: str, base: str, year: int) -> list[str]:
    """Find official nested year-index pages hidden behind a directory landing page."""
    pages = set()
    for match in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"']", page, re.I):
        url = urllib.parse.urljoin(base, html.unescape(match.group(1)))
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname != "dxs.moe.gov.cn":
            continue
        path = parsed.path.casefold()
        if (
            str(year) in path
            and path.endswith(".shtml")
            and "/zx/hd/sxjm/sxjmlw/" in path
            and url != base
        ):
            pages.add(url)
    return sorted(pages)


def merge_papers(groups: list[list[dict]]) -> list[dict]:
    unique = {}
    for papers in groups:
        for paper in papers:
            unique[(paper["code"], paper["url"])] = paper
    return sorted(unique.values(), key=lambda x: (x["code"][0], int(re.sub(r"\D", "", x["code"]) or 0)))


def quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(catalog: dict) -> str:
    lines = [
        "version: 1",
        f"generated_at: {quote(catalog['generated_at'])}",
        f"official_archive: {quote(ARCHIVE)}",
        f"official_download_notice_2012: {quote(DOWNLOAD_NOTICE_2012)}",
        "scope: \"Catalog every official year page in range and every individual display link discoverable from those pages.\"",
        "award_label_policy: \"Display status is not itself proof of a particular prize grade. Record national-first or national-second only when an official source states it.\"",
        "usage: \"Open only the relevant official pages. Learn structure and reasoning; do not copy text, equations, figures, or code.\"",
        "years:",
    ]
    for year in catalog["years"]:
        lines.extend([
            f"  - year: {year['year']}",
            f"    landing_url: {quote(year['landing_url'])}",
            f"    fetch_status: {quote(year['fetch_status'])}",
            "    papers:",
        ])
        if not year["papers"]:
            lines.append("      []")
        else:
            for paper in year["papers"]:
                lines.extend([
                    f"      - code: {quote(paper['code'])}",
                    f"        title: {quote(paper['title'])}",
                    f"        url: {quote(paper['url'])}",
                ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mirror-output", type=Path, action="append", default=[])
    parser.add_argument("--start-year", type=int, default=2012)
    parser.add_argument("--end-year", type=int, default=dt.datetime.now().year)
    args = parser.parse_args()
    requested_years = list(range(args.end_year, args.start_year - 1, -1))

    def process_year(year: int) -> dict:
        url = LANDING.format(year=year)
        try:
            page = fetch(url)
            groups = [extract_papers(page, url, year)]
            index_pages = set(extract_index_pages(page, url, year))
            index_pages.add(urllib.parse.urljoin(url, f"{year}gjsbqgdxssxjmjslwzs.shtml"))
            for index_url in sorted(index_pages):
                try:
                    nested = fetch(index_url)
                except Exception:
                    continue
                groups.append(extract_papers(nested, index_url, year))
            groups.append(MANUAL_OFFICIAL_PAPERS.get(year, []))
            papers = merge_papers(groups)
            status = "ok" if papers else "landing-only"
        except Exception as exc:
            papers = []
            status = f"unavailable: {type(exc).__name__}"
        return {"year": year, "landing_url": url, "fetch_status": status, "papers": papers}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        years = list(pool.map(process_year, requested_years))
    catalog = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "years": years}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = render(catalog)
    args.output.write_text(rendered, encoding="utf-8")
    for mirror in args.mirror_output:
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} with {sum(len(y['papers']) for y in years)} individual paper links and {len(years)} year landing pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
