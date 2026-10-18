---
name: craft-apmcm-paper
description: Quickly develop evidence-based APMCM solution strategies and hand them to Modex for drafting, then audit modeling results and English papers. Use for 亚太杯/APMCM思路、Modex交接、结果验证、英文审查与提交检查; preserve CUMCM rules separately.
---

# APMCM paper workflow

This is an independent APMCM mode. It does not load the parent CUMCM entrypoint, its compliance rules, scoring rubric, or submission packager. The existing CUMCM skill is unchanged.

## Default: quick strategy, low context cost

For a new problem, load only `references/quick-strategy.md` and the official problem/necessary attachment facts. Return one recommended route with core equations, a defensible innovation mechanism, one decisive low-cost validation plan (run a small probe only if necessary to choose the route), known gaps, and a fallback trigger. Use `assets/strategy-handoff.md` for Modex. Do not default to a full solution, full manuscript, broad literature review, exhaustive optimization, or multiple agents. Stronger strategy comes from problem structure and evidence, not a model catalogue.

Reuse verified inputs and results. `scripts/context_cache.py` can bind a short local brief to input hashes; check it before rereading large files. A changed dependency invalidates the brief. The cache proves freshness only, not truth. Inspect failed or consequential new evidence rather than repeating unchanged audits. Use local scripts for deterministic checks and return compact summaries. Do not claim a percentage saving without measured usage.

## Mode and rule boundary

Choose `training`, `historical-rehearsal`, or `live-contest`. Distinguish November English APMCM from the separate Chinese event. Read `references/rules-2026.md` and `assets/rules-2026.json` when current rules matter, then only the route needed for this phase. Historical rehearsals can include a full solve/draft when explicitly requested. For live work, establish actual current AI permission and scope first; unknown policy blocks live assistance and final readiness, not pre-contest learning.

## Modex handoff

The default contest workflow has two skill phases: (1) generate the Modex strategy handoff, then stop and wait for its draft; (2) audit the returned manuscript, code and results, and make justified targeted repairs. Modex implements the proposed solution, runs the calculations and writes the full initial manuscript. Use `references/modex-handoff.md`; do not require a complete solve, frozen numerical results or a full validation campaign before the first handoff. Mark planned work and untested claims explicitly. Doubao is used only during skill development/testing when authorized; it is not a contest participant, runtime dependency or handoff recipient. Do not invoke or delegate to it in the contest workflow. Do not replace Modex's initial-draft role or rewrite a reasonable model because another method looks more elaborate. Full-body drafting remains available when the user explicitly requests it, as in a historical rehearsal. Reconstruct a final abstract only from the complete paper and frozen results.

## Routes

- **Rules / preparation:** `references/rules-2026.md`. Verify year, event, official source, dates/timezone, English language, page structure, anonymity, naming, support-file policy, and AI use. Preserve source URLs and hashes. Historical examples cannot fill missing current rules.
- **Deep problem / rehearsal (requested or material failure):** `references/rehearsal.md`. Freeze official inputs and requirement coverage before models; freeze strategy before opening same-case solutions. Select methods from the problem, not from a fixed preference for complex algorithms. Preserve code, baseline, independent checks, sensitivity, and limitations. For engineering claims requiring physical validation, also read `references/physical-validation.md`.
- **English drafting / audit:** `references/english-audit.md` and `assets/paper-template.md`. Work from frozen results. Verify every required answer and high-consequence number across summary, equations, text, tables, figure labels, and conclusions. A language edit must not change units, quantifiers, denominator, or uncertainty.
- **Final package:** `references/bundle-contract.md`. Use `scripts/audit_bundle.py`, then `scripts/package_bundle.py`. Rehearsal ZIPs are local evidence bundles, never official upload instructions. Unknown 2026 fields must fail `--final`; resolve them against actual notices instead of suppressing checks.

## Evidence standard

Separate measured data, published specifications, assumed parameters, simulated outputs, and forecasts. A reduced-order model is not CFD; a discrete best candidate is not a global optimum. Explain each mechanism, units, initial/boundary conditions, and what observations could disprove the assumptions. Report solver feasibility and independent residuals, not just success flags.

At the strategy handoff, specify each subproblem's required answer, proposed calculation, baseline and validation plan; distinguish executed checks from work assigned to Modex. After the draft returns, require direct answers, traceable calculations and checks with a different failure path. Verify the baseline comparison and the assumption most affecting the recommendation, and quantify whether claimed improvements survive. Do not trade requirement coverage for ornate prose or many models.

State review status precisely: `verified`, `supported-not-reproduced`, `inference`, `unable-to-verify`. Automated hash/numeric checks establish limited consistency, not semantic correctness, rule authenticity, human approval, or prize quality. A small historical case is not broad validation. Never claim a prize guarantee or infer actual judging deductions without feedback.

For complex skill changes use independent AI assessment from frozen raw artifacts, keep it separate from the solver's self-assessment, and do not call it human review. Keep private past submissions outside public repositories. Extract general lessons only after checking the actual evidence.
