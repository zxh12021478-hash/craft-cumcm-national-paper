---
name: craft-apmcm-paper
description: Prepare, solve rehearsal problems, and audit English APMCM mathematical modeling papers with source-bound contest rules, reproducible results, and submission checks. Use for 亚太杯/APMCM preparation, English abstracts, paper-code-figure consistency, and historical rehearsals; do not apply CUMCM submission rules.
---

# APMCM paper workflow

This is an independent APMCM mode. It does not load the parent CUMCM entrypoint, its compliance rules, scoring rubric, or submission packager. The existing CUMCM skill is unchanged.

## First decision

Read `references/rules-2026.md` and `assets/rules-2026.json` for current-season work. Read only the relevant workflow below next. Distinguish English November APMCM from the separate Chinese event; never infer rules from the word 亚太杯 alone.

Choose `training`, `historical-rehearsal`, or `live-contest`. Historical rehearsals may solve and draft a full paper when requested. For a live contest, establish the actual current AI policy and authorized scope before assisting; silence in a notice is neither permission nor prohibition. Unknown policy blocks a live assistance plan and final readiness, not ordinary pre-contest learning.

## Routes

- **Rules / preparation:** `references/rules-2026.md`. Verify year, event, official source, dates/timezone, English language, page structure, anonymity, naming, support-file policy, and AI use. Preserve source URLs and hashes. Historical examples cannot fill missing current rules.
- **Problem / rehearsal:** `references/rehearsal.md`. Freeze official inputs and requirement coverage before models; freeze strategy before opening same-case solutions. Select methods from the problem, not from a fixed preference for complex algorithms. Preserve code, baseline, independent checks, sensitivity, and limitations.
- **English drafting / audit:** `references/english-audit.md` and `assets/paper-template.md`. Work from frozen results. Verify every required answer and high-consequence number across summary, equations, text, tables, figure labels, and conclusions. A language edit must not change units, quantifiers, denominator, or uncertainty.
- **Final package:** `references/bundle-contract.md`. Use `scripts/audit_bundle.py`, then `scripts/package_bundle.py`. Rehearsal ZIPs are local evidence bundles, never official upload instructions. Unknown 2026 fields must fail `--final`; resolve them against actual notices instead of suppressing checks.

## Evidence standard

Separate measured data, published specifications, assumed parameters, simulated outputs, and forecasts. A reduced-order model is not CFD; a discrete best candidate is not a global optimum. Explain each mechanism, units, initial/boundary conditions, and what observations could disprove the assumptions. Report solver feasibility and independent residuals, not just success flags.

For each subproblem supply a direct answer, traceable calculation and one check with a different failure path. Compare against a transparent baseline, test the assumption that most affects the recommendation, and quantify whether the claimed improvement survives. Do not trade requirement coverage for ornate prose or many models.

State review status precisely: `verified`, `supported-not-reproduced`, `inference`, `unable-to-verify`. Automated hash/numeric checks establish limited consistency, not semantic correctness, rule authenticity, human approval, or prize quality. A small historical case is not broad validation. Never claim a prize guarantee or infer actual judging deductions without feedback.

For complex skill changes use independent AI assessment from frozen raw artifacts, keep it separate from the solver's self-assessment, and do not call it human review. Keep private past submissions outside public repositories. Extract general lessons only after checking the actual evidence.
