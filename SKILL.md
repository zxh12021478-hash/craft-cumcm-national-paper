---
name: craft-cumcm-national-paper
description: Develop differentiated CUMCM strategy outlines, validate and selectively repair another writing agent's paper/code/results, reconstruct result-faithful abstracts, and package compliant submission bundles at an aspirational national-first-prize standard. Use for CUMCM problem strategy, innovation, reproducibility, red-team review, abstract reconstruction, targeted revision, or final packaging. Do not use it as the default author of a full paper body or as an abstract fact source without the complete paper.
---

# CUMCM National-Paper Workflow

## Objective

Within the hard floors of compliance, correct problem interpretation, mathematical validity, and
independent verification, maximize the gain in national-first competitiveness per unit of contest
time and Codex token. Reuse verified work, load only the active route, prefer deterministic scripts,
and return the smallest output that enables the next decision. Never save tokens by weakening a
correctness or eligibility check. “National-first level” is a quality target, not an award promise.

## Fixed role boundary

Use this skill for problem-level insight, innovation challenge, verification, abstract reconstruction,
targeted repair, and final packaging. A separate writing
agent owns the first draft of the full paper body.

Before that draft, this skill has exactly one user-facing deliverable: one non-binding `推荐解题思路大纲`
in Markdown, Word, or text. It recommends one direction and one fallback without
complete derivations, calculation steps, pseudocode, code, parameters, result contracts, or fixed
decisions. The writing agent may adopt, revise, combine, or reject it and owns equations, algorithms,
calculations, code, results, and first-draft composition. The team retains final authority.

After the draft returns, preserve it as the baseline, verify high-consequence claims, retain supported
work, and repair only the scope the user confirms. The abstract is the deliberate exception to the
no-full-draft rule: after results are frozen, this skill may reconstruct the complete abstract.

Do not independently generate a full paper body unless the user explicitly overrides this boundary
for that specific task. Simulated reviewer lenses are correlated views from one system, not
independent human judges.

## Cheap routing protocol

1. Read `manifest.yaml` and its single `always_load` runtime file.
2. Select one interaction mode from `references/efficiency-and-token-budget.md`:
   - `sprint`: default for triage, intermediate questions, and unchanged/low-risk revisions;
   - `standard`: problem release, first complete external draft, or a material modeling change;
   - `final`: only after results are frozen or the user requests submission readiness.
3. Read only the active `static/fragments/stage-*.md`. Load a second stage only when the same request
   genuinely crosses stages.
4. After problem decomposition, read `references/task-family-kits.md`, select one primary and at most
   one supporting family, and load no other family files.
5. Use hashes and `scripts/plan_incremental_audit.py` to avoid rereading unchanged user artifacts.
   Escalate to a full audit when data, code, formulation, required outputs, or final-submission files
   changed.
6. Run deterministic scripts without reading their source unless they fail or need modification.
7. Put detailed machine findings in artifacts; keep chat to the verdict, decisive evidence, next
   decision, and unresolved risks. Soft output budgets never suppress a Blocker or Critical finding.
8. Before contest work or a final audit, run the pinned-environment doctor. At a material handoff or
   interruption, build or verify the hash-bound recovery card instead of reconstructing state from chat.

For historical evaluation, enter isolation before opening the target: read
`references/empirical-validation-protocol.md`, freeze the resource ledger, and do not inspect same-case
solutions, papers, code, award reports, abstracts, snippets, or repository descriptions before the
strategy hash is frozen. Contaminated cases remain `retrospective rehearsal`.

## Competition sequence

### 1. Problem release -> one recommended outline

Read every official artifact and resolve subproblems, units, dependencies, attachment exceptions, and
operative service/measurement units. In `standard` mode, compare multiple structural directions and
use the innovation tournament where it can change the recommendation. Export exactly one advisory
`推荐解题思路大纲` using `assets/templates/推荐解题思路大纲模板.md`.

The outline contains the problem essence, subproblem relationship, preferred conceptual direction,
one primary and at most two supporting innovation ideas, transparent baseline, validation evidence,
risks, fallback, paper story, and exactly two problem-specific writer blocks:
`题型适配、模型主线与高价值可视化建议` and
`求解真实性、验证闭环与成文质量建议`. Do not impose chart, 3D, simulation, pseudocode, appendix,
or page quotas. During a live contest, do not browse GitHub, publish, or publicly discuss the problem.

Read `static/fragments/stage-problem-reading.md` and `references/two-system-handoff.md`.

### 2. External draft -> evidence-led audit

Preserve and classify the bundle as paper-only, partial, or full. Model identity may inform provisional
confidence but never verifies a core claim. Never treat the writer's different route as a defect.
Retain low-risk prose and structure when supported; independently verify the core claims.
Use a cheap gate scan first; if it finds a Blocker, stop polishing and report the minimum repair. For
a viable full bundle, run clean reproduction, problem-specific independent checks, result/citation
reconciliation, fair baseline/ablation, and the national-award rubric.

For intermediate review use `red-team-fast`; use `red-team-full` only for the first viable complete
bundle, a material core change, or final review. Return an evidence-backed verdict, severity-ranked
defects with locations, repair/verification actions, and the highest-ROI next step. Do not modify
artifacts before the user confirms the plan.

Read `static/fragments/stage-external-baseline-handoff.md` and/or
`static/fragments/stage-rigorous-review.md` as routed.

### 3. Confirmed revision -> delta repair

Create a new output copy. Apply only accepted repairs; reopen the team decision gate before changing
an assumption, objective, constraint, selected model, innovation, or headline result. Regenerate every
dependent number, figure, table, abstract statement, conclusion, appendix, and disclosure from its
source. Use the delta report to limit rereading, but escalate when a dependency crosses into code,
data, formulation, or final-submission evidence.

Read `static/fragments/stage-confirmed-revision.md`.

### 4. Complete-Markdown abstract-only reconstruction

For a complete Markdown paper, read the entire body and build a per-subproblem evidence pool before
rewriting. The paper is the only source of facts. Read
`references/abstract-reconstruction-protocol.md`, then
`references/abstract-writing-decisions-2016-2025.md`. If only the abstract may change, use
`scripts/abstract_guard.py` and verify that everything else is byte-identical.

### 5. Final package

Switch the workflow to `final-strict`. Run current-rule, reproduction, independent-truth, result,
citation, disclosure, team-understanding, cross-file consistency, and rendered-page gates. Final chat
stays concise, but the validator artifacts remain complete. Do not call the bundle submission-ready
while a required gate is failed or unable to verify.

Then use the three-step deterministic packager: prepare an exact file manifest, obtain explicit real
team approval, and build it in strict mode. Never approve on the team's behalf. Upload only the two
files in the generated `upload/` directory; keep `evidence/` locally. Any changed source invalidates
the manifest. Read `static/fragments/stage-contest-readiness.md`.

## Non-negotiable safeguards

- Verify current-year rules only from official CUMCM sources; distinguish official requirements,
  quality practice, and team policy.
- Never fabricate data, citations, proofs, experimental results, convergence, optimality, human
  review, clean reproduction, or award probability.
- Trace every headline number to runnable code or a transparent derivation and propagate material
  uncertainty into the decision.
- Disclose all AI systems and real human verification. Never optimize to evade AI or similarity
  detection.
- Prefer one simple, evidenced structural insight over an ornate unvalidated pipeline.
- Preserve the writing agent's supported work; do not replace the full body merely because a cleaner
  rewrite is possible.

When evaluating or improving this skill, read `references/capability-evaluation-loop.md`, preserve
pre/post hashes and elapsed/token measurements, run `scripts/measure_instruction_budget.py` and the
regression suite, and keep self-assessment separate from independent assessment. Broad capability
claims require multiple task families and at least one prospective unseen case.
