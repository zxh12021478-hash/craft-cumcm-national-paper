# Open-source integration policy

Read this file when choosing execution, citation, document, rule-monitoring, or workflow infrastructure.

## Default rule

Keep the skill runnable with the bundled scripts and the standard library. Detect optional tools; never install them silently during a competition. If a tool is selected, pin a released version or commit before the contest and record its version in the reproducibility report.

## Adopted integration points

| Capability | Upstream | License | Use |
|---|---|---|---|
| State and stage gates | `handsomeZR-netizen/mathmodel-skill` | MIT | Adopt the ideas of persistent state, explicit exit gates, local repair, deterministic scoring, and regression tests. Do not import its empirical award-paper statistics without independently verifying provenance and sampling. |
| Independent solver verification | `RealSeaberry/AutoMCM-Pro` | MIT | Require solver code plus a separate verification command with machine-readable PASS/FAIL. Reject its Autopilot authorship model and broad automatic Git staging. |
| Reference verification | `markrussinovich/refchecker` / `academic-refchecker` | MIT | When installed and explicitly enabled, run deterministic/no-LLM PDF or bibliography checks and retain the JSON report. The team must still inspect primary sources. |
| Python environments | `astral-sh/uv` | MIT or Apache-2.0 | Prefer `uv sync --frozen` when a valid `uv.lock` exists; otherwise use a disposable `venv`. |
| Machine-readable contracts | `python-jsonschema/jsonschema` | MIT | Validate result, citation, execution, and state manifests. The scripts still perform basic checks without it, but strict final validation fails closed; install and pin it before the contest. |
| Data-frame contracts | `unionai-oss/pandera` | MIT | Optional for problem-specific table schemas and statistical checks; do not make it a universal dependency. |
| Rule-page monitoring | `thp/urlwatch` | BSD-3-Clause | Optional long-running change monitor. The bundled rule checker remains the submission gate because it also checks required language and snapshots. |
| Link checking | `lycheeverse/lychee` | MIT or Apache-2.0 | Optional bulk URL check for Markdown/HTML support material. It does not verify that a cited source supports a claim. |
| PDF/DOCX handling | `py-pdf/pypdf` and `python-openxml/python-docx` | BSD-3-Clause / MIT | Use for structural inspection; use LibreOffice and Poppler for rendered-page QA. |

## Optional, not default

- Snakemake, DVC, and showyourwork are strong reproducibility systems, but their installation and learning cost is usually too high inside a 72-hour contest. Use them only when the team already works fluently with them.
- Manubot and Quarto are useful for scholarly publishing, but do not replace native CUMCM DOCX/PDF layout verification.

## Rejected sources

- Do not copy or vendor a repository that lacks a clear license.
- Do not treat a large archive of winning papers, books, or proprietary templates as reusable merely because it is public on GitHub.
- Do not use the `latexstudio/CUMCMThesis` source as the current compliance authority: the repository states that it is adapted through 2023, and its repository does not expose a clear reuse license. Current official rules prevail.
