# Stage: rigorous review

Always read `references/national-award-rubric.md` and
`references/ai-baseline-regression-protocol.md`. Read `references/code-quality.md` only when code is
supplied, `references/visualization-standards.md` only when figures/layout are in scope,
`references/validation-playbook.md` for model/result validation, and
`references/ai-and-competition-compliance.md` for a live or final package. Read
`references/team-comprehension-audit.md` only in `final` mode. When the user requests a national-
judge simulation, red-team review, adversarial final review, or repair-ROI ranking, read
`references/red-team-judge-protocol.md`: use `red-team-fast` for sprint/delta review and
`red-team-full` only for the first viable complete bundle, a material core change, or final review.
Classify the reviewed subproblems with `references/task-family-kits.md` and load only the relevant
family references so the audit applies task-specific failure checks without bulk-loading every kit.

## Inspection sequence

1. Inventory all files and identify the intended entry points. If a preserved baseline and a revised
   bundle both exist, run `scripts/plan_incremental_audit.py` first. In `targeted` mode load only the
   changed files and dependency closure; in `full` mode continue the complete sequence below.
2. If another system generated the baseline, classify the package as paper-only, partial, or full;
   record its actual modeling route, provenance, and AI-use log. A route different from the earlier
   recommendation is not a defect; judge its logic and evidence. Keep the original preserved until
   static screening passes.
3. Before reading the abstract, conclusion, or claimed route, read the official problem and
   attachments and establish an independent evaluator baseline: every required output, unit,
   dependency, constraint, plausible route family, and decisive validation need. If the official
   problem is absent, mark task alignment `unable-to-verify` rather than inferring it from the paper.
4. Read the abstract, direct answers, and conclusion to extract claimed results, then trace every
   claim backward through equations, code, data, and assumptions.
5. Run the code from a clean copied directory and run a separate verification command; record failures and environment details.
6. Run the generic truth harness and problem-specific independent checks, reconcile headline results against the canonical result ledger, and verify citations online against primary or official sources and the competition-period cutoff.
7. Run `scripts/validate_submission.py` and relevant specialized validators. Use `--strict`, a render directory, and the explicit AI/external-baseline declarations when assessing final-submission readiness.
8. Inspect figures, tables, equations, citations, anonymity, layout, and page limits.
9. Score conservatively using the national-award rubric and apply hard caps before interpreting the
   weighted total.
10. In red-team mode, apply the mathematical-strict, applied-modeling, and national-selection lenses
    only after the common factual audit. Label them correlated simulated views, not independent
    judges; do not convert their mean into award probability.
11. Run the cross-audited comprehension gate covering model choice, formulas, parameters, code, reality checks, uncertainty, and failure conditions.
12. Run a provenance audit: distinguish actual team decisions and checks from unverified claims in the AI disclosure or manuscript.
13. Label takeover evidence precisely: `audit-only`, `partial-reproduction`,
    `end-to-end-reproduction`, or `implemented-takeover`. Report repository commit, license scope,
    dependency state, entry command, runtime, expected/actual outputs, and unresolved mismatch.

## Severity

- **Blocker:** disqualification risk, fabricated or unreproducible result, wrong problem, missing required output.
- **Critical:** invalid model, leakage, severe logical gap, broken code, contradicted headline result.
- **Major:** weak innovation, inadequate validation, unjustified assumptions, incomplete uncertainty, misleading visual.
- **Minor:** local clarity, notation, formatting, or efficiency defect.

Do not average away blockers with attractive presentation. A single blocker caps the verdict at not submission-ready.

If no matched comparison corpus exists, report national percentile as `not calibrated`. Never invent
Top-X placement or a percentage chance of receiving an award.

Do not modify the artifacts during this stage. Ask for confirmation after presenting the repair plan.
In `sprint`, return the verdict, evidence scope, triggered gates, at most five decisive P0/P1 defects,
and the next verification action. Keep full ledgers in files. Never repeat the same defect under
multiple simulated reviewer lenses merely to fill a report.
