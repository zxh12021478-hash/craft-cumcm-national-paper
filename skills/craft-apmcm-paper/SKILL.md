---
name: craft-apmcm-paper
description: Quickly develop evidence-based APMCM solution strategies and hand them to Modex for drafting, then audit modeling results and English papers. Use for 亚太杯/APMCM思路、Modex交接、结果验证、英文审查与提交检查; preserve CUMCM rules separately.
---

# APMCM strategy → Modex → audit

Independent APMCM mode: do not load the CUMCM entrypoint, rubric, rules or packager. Preserve the user's CUMCM workflow and files.

## Two skill phases

1. **New problem:** load `references/quick-strategy.md` and the official question/necessary attachment facts. Give one implementable main route, core equations, a testable improvement mechanism, a baseline, validation plan and fallback. Use `assets/strategy-handoff.md`; read `references/modex-handoff.md` for the return contract. Run a small probe only when it changes route selection. Deliver the Modex handoff and wait. Do not require a complete solve, frozen results or a validation campaign before handing off.
2. **Returned draft:** load `references/english-audit.md` and inspect the actual question, complete first manuscript, code and outputs. Audit substantive errors before language; repair affected artifacts and repeated claims. Use `assets/modex-return.md` to locate missing outputs. Do not replace Modex's initial authoring role or rewrite a sound model merely because a more elaborate one exists. Reconstruct the abstract only from the complete paper and verified results.

Modex implements, calculates and writes the initial paper. Doubao is for authorized skill development/testing only; never invoke it as a contest participant, dependency or handoff recipient. Explicitly requested historical rehearsals can include full solving/drafting.

**Abstract priority:** the English Summary is a key deliverable. Use `references/abstract-priority.md`: before Modex drafting specify the evidence needed for each answer; after the complete draft and substantive repairs reconstruct an answer-led summary with the operative contribution, decisive comparisons and material limits. No invented gains, fixed word quotas or mandatory multiple versions.

## Strategy and cost discipline

Select methods from problem structure and observable data, not a model catalogue. Check feasibility and identifiability before optimizing or fitting. Read only the relevant section of `references/task-families.md` for forecasting, ranking, optimization or engineering risks. If ambiguity or route choice remains consequential, use `references/route-challenge.md` for one decisive refutation, not a mandatory model tournament. A cheap falsification or analytic bound can be more valuable than a large simulation. Keep useful innovation as a hypothesis until evidence supports it.

Use one concise handoff plus necessary attachments. Do not repeat the same advice across reports or read every reference. Reuse code and verified results; scripts return compact metrics and paths. `scripts/context_cache.py` binds a brief to evidence hashes: changed dependencies invalidate it; unchanged hashes establish freshness, not truth. The complete first draft needs review; later revisions need changed/affected claims and unresolved issues, not another complete solve. Stop when the requested handoff or necessary repairs are complete. Do not claim usage savings without measured usage.

## Conditional routes

- **Rules:** choose `training`, `historical-rehearsal` or `live-contest`. Distinguish November English APMCM from separate Chinese/LLM events. Read `references/rules-2026.md` and `assets/rules-2026.json`, verify actual current official notices when rules matter. Unknown AI permission blocks live assistance, not preparation. Historical templates cannot fill missing current requirements.
- **Full rehearsal / material model failure:** `references/rehearsal.md`. Freeze strategy before reading same-case solutions. Preserve baseline and failed evidence. For physical claims, also use `references/physical-validation.md`; numerical verification alone is not empirical validation.
- **English / visuals:** `references/english-audit.md`; `assets/paper-template.md` is an authoring aid, not an official template. Check formulas, quantities, axes/captions and English scope together; render and inspect every paper page.
- **Packaging when requested:** `references/bundle-contract.md`, `scripts/audit_bundle.py`, then `scripts/package_bundle.py`. Bind the original-question requirement matrix so omitted tasks cannot disappear from the audit. Rehearsal archives are not official upload instructions. Unresolved current rules must fail `--final`.

## Evidence boundaries

Distinguish given/measured/calibrated/assumed inputs and simulated/forecast outputs. Before handoff, specify required answers and checks; after the draft, require actual answers, reproducible calculations and independent failure paths. Trace units, constraints, baselines and uncertainty. An infeasibility certificate or preference-dependent answer may be correct; do not invent a unique winner or a feasible plan.

Use precise statuses: `verified`, `supported-not-reproduced`, `inference`, `unable-to-verify`. Hash/numeric passes, a second AI opinion and small synthetic tests do not establish semantic correctness, empirical validity, broad performance or prize quality. Never guarantee awards. Keep private submissions outside public repositories. For substantial skill changes, independently forward-test frozen raw artifacts; do not give the evaluator expected answers or call AI assessment human review.
