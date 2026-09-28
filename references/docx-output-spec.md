# DOCX and final-render specification

Use the current official CUMCM format as the controlling source. When a DOCX is created or edited:

1. Build or edit the structured DOCX directly with the document workflow; do not use a Markdown import or copy-paste path as the authoritative final artifact.
2. Preserve anonymity and distinguish the print package from the electronic paper: under the current 2026 rule the printed copy includes the commitment and numbering pages, while the electronic paper omits both and begins with the abstract.
3. Enforce consistent body, heading, caption, equation, table, and reference styles.
4. Use editable equations where practical, not raster screenshots or unrendered LaTeX text.
5. Keep figures at publication resolution with readable labels.
6. Keep tables within margins and repeat headers across pages when helpful.
7. Prevent orphan headings, split captions, clipped equations, and blank pages.
8. Render the complete document to page images or PDF.
9. Inspect every page visually, including the one-page abstract limit.
10. Run `scripts/validate_docx.py` and repair material findings.
11. Verify the electronic paper matches the intended final submission.

Intermediate section files may use a working convention such as `题号-问题序号-内容类型.docx`, but they are not the final submission. Consolidate them into the single required electronic paper and use the active submission platform’s filename rule.

For the currently posted 2026 format, also check A4 paper, margins of at least 2.5 cm, an abstract of at most one page, no table of contents, main text of at most 30 pages before appendices, a single DOCX or PDF paper file no larger than 20 MB, and a separate ZIP/RAR supporting-material archive no larger than 20 MB. Re-verify these values against the live official notice immediately before submission.

Report font and layout requirements as official-rule constraints only when the current rule explicitly specifies them; otherwise use a clean, consistent scholarly style.
