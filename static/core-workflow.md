# Core workflow

## Intake

Inventory the problem statement, attachments, data dictionary, draft paper, code, figures, prior feedback, target group, file format, deadline, team expertise, and intended AI division of labor. Ask only questions whose answers would materially change the work. Otherwise state reasonable assumptions and proceed.

For a current competition, verify the latest official rules before relying on remembered dates, page limits, AI policy, or submission requirements.

## Stage orchestration

Initialize one unified workflow ledger at the project root:

```bash
python scripts/cumcm_workflow.py --root PROJECT init --problem 2026-A --profile competition-lite
```

Use `competition-lite` through modeling and result production. Switch to `final-strict` only after results are frozen; it adds complete artifact, reproduction, truth, citation, visual, disclosure, and comprehension gates without multiplying human approvals. Do not maintain a parallel informal status ledger.

Interaction depth is separate from the machine workflow profile: use `sprint` for triage and small
deltas, `standard` for problem release/first viable bundle/material core changes, and `final` only for
frozen submission work. See `references/efficiency-and-token-budget.md`. Token budgets may compress
chat and optional breadth, never a hard correctness or eligibility gate.

Before the contest, create and verify one pinned validator environment with `scripts/bootstrap_validator_env.py --destination PATH`. Use `--plan` to inspect commands first and `--wheelhouse` for a prepared offline package cache. Never discover missing PDF/schema libraries during the final upload window.

1. Verify the active official rules and inventory the official problem, attachments, deadline, team skills, and intended AI systems.
   Before takeover or final audit, run `scripts/preflight_environment.py` with the matching profile; fix missing hard dependencies before the deadline.
2. Audit and hash every problem artifact, reconcile rendered pages/embedded objects/workbook ranges with extracted content, obtain human sign-off on the exact subproblem/output inventory, create the dependency graph, open the paper argument ledger, audit data sufficiency, and route each subproblem to one primary and at most one supporting task-family kit.
3. Build a transparent baseline. `sprint` may cheaply screen structural hypotheses but cannot freeze
   the innovation. Before a standard strategy freeze, generate at least eight problem-anchored
   structural hypotheses across four families, deterministically rank them, and run independent,
   hash-bound minimum experiments on the top three.
4. Use the strongest internal evidence to form one preferred innovation direction and one fallback.
   Present them as recommendations; do not freeze them as constraints on the writing agent.
5. If another system will produce the complete first draft, export one concise, non-binding Word,
   Markdown, or text recommendation outline. This is the only user-facing deliverable before that
   draft. Do not provide a solver contract, code plan, calculation procedure, internal ledgers, or
   fixed route. The writing agent owns the detailed modeling and may replace the recommendation.
6. On return, preserve and inventory the external bundle, record its interaction log and actual
   modeling route, and assign scoped provisional confidence from calibrated source performance,
   bundle completeness, reasoning coherence, and static quality. Use that tier to prioritize review,
   but do not promote core claims to verified before the corresponding evidence checks pass.
7. Establish the factual layer: static scan, dependency/environment record, clean copied-directory run, separate verification command, generic truth harness, task-family-specific independent recomputation, headline-result reconciliation, citation-period verification, and reality checks. The verifier must recompute objectives, constraints, identities, or metrics from saved primitive outputs rather than trust the main solver's flags.
8. Correct the model under a reopened team gate. Preserve the frozen primary insight unless evidence
   falsifies it; record and re-approve any replacement rather than silently adopting the external
   system's novelty claim.
9. Run fair baseline-versus-proposed comparisons, ablations, stress tests, sensitivity, uncertainty propagation, and independent validation.
10. Convert outputs into direct answers and decision-relevant figures; have the team accept or reject the interpretation and freeze the canonical result ledger.
11. Complete the argument spine, writer evidence packet, and abstract coverage matrix. Write the
    result-frozen abstract; send the body materials to the separate writing agent.
12. Quarantine the returned draft, reconcile it against the evidence chain, and make only authorized
    targeted repairs; synchronize code, numbers, figures, references, appendices, and disclosures.
13. Run adversarial review, cross-audited team comprehension, page rendering and signed visual QA, current-rule verification, and the fail-closed final gate.

## Three-phase interaction contract

### Phase 1: problem input to strategy

Explore alternatives internally. For the writing agent, return exactly one generated
`推荐解题思路大纲` in `.md`, `.docx`, or `.txt`; return no companion report, JSON, ledger, checklist,
or slide deck. Give one clear preferred direction and one brief fallback, but only at the conceptual
level. Do not include complete equations, computation steps, pseudocode, code, exact parameters,
file contracts, or instructions that constrain the writing agent. Label all content
`AI-recommended`; the writing agent may adopt, revise, combine, or reject it, and the team approves
the eventual core decisions.

Within that one document, include exactly two detailed, problem-specific writer-facing instruction
blocks using `assets/templates/推荐解题思路大纲模板.md`: one for task-adapted modeling and high-value
visualization, and one for truth, validation, reproducibility, and paper quality. They are sections of
the same outline, not additional deliverables.

### Phase 2: paper and code to review

Preserve and inspect first. Do not rewrite silently. Reuse sound structure and prose when they agree
with the approved evidence; reproduce core claims before marking them verified. Scale review depth
to confidence and consequence, then produce a severity-ranked scorecard and repair plan. Be direct
and objective; never inflate the score to encourage the user. Use a gate-first sprint review for an
incomplete or blocked bundle; reserve the full national-judge report for a viable complete bundle,
material core change, or final review.

### Phase 3: confirmed plan to modification and packaging

Require explicit confirmation of the repair scope and every affected core modeling decision. Then
modify the writing agent's affected passages and all dependent artifacts, rerun analyses, re-render
the paper, and verify consistency. Write or rewrite the final abstract from the frozen ledger. Never
smuggle a new assumption, objective, constraint, or innovation into a prose edit, and never replace
the full body merely because a cleaner rewrite is possible.

## Time-pressure fallback

If time is limited, preserve in order:

1. complete answers to every subproblem;
2. correct model and executable code;
3. independent validation;
4. one defensible innovation;
5. polished figures and prose;
6. optional advanced extensions.

For an overnight-baseline takeover, generate the deadline-anchored plan with `scripts/competition_scheduler.py --profile takeover`. Respect its hard stops: once the primary model or result ledger is frozen, reopen only for a documented blocker and rerun all downstream gates.
