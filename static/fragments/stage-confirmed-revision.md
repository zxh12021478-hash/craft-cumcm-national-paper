# Stage: confirmed revision

Read only the stage fragments and references affected by the accepted repair plan. Load
`references/docx-output-spec.md` for document edits, `references/code-quality.md` for code changes,
and `references/ai-and-competition-compliance.md` when disclosure or final submission is affected.
Read `references/team-comprehension-audit.md` only in final mode.

## Procedure

1. Freeze a copy of the submitted artifacts and create a separate final-output directory.
2. Run `scripts/plan_incremental_audit.py` against the preserved and current copies. Convert the
   accepted repair plan and dependency closure into one traceable checklist; do not reload unchanged
   artifacts outside that closure unless a full escalation trigger fires.
3. Reopen the team decision gate before changing any assumption, objective, constraint, selected model, or innovation claim.
4. Repair foundational issues before prose: data, assumptions, formulation, solver, results, validation, figures, then writing.
5. Regenerate outputs from code. Never hand-edit a number in the paper without updating its source.
6. Write or rewrite the abstract from the frozen ledger; update only the writing agent's body passages affected by accepted defects. Synchronize the argument spine, assumption and notation ledgers, result ledger, abstract coverage matrix, title, conclusion, tables, figures, appendices, supporting files, decision record, and AI disclosure.
7. Run all relevant validators. Final readiness requires `scripts/validate_submission.py --strict --run-clean --render-dir ... --ai-used yes|no --external-baseline-used yes|no`, current-rule verification, and citation verification.
8. Render the current paper, inspect every page, record the current paper hash in the signed visual-QA record, and rerun the gate after any document change.
9. Run the cross-audited team-comprehension gate and repair any topic below threshold.
10. Compare the final argument spine and result ledger with every artifact.
11. Consolidate intermediate section files into the single required electronic paper and verify the final platform naming convention.
12. Deliver the full revised version, validator reports, change ledger, and unresolved risks.

For non-final deltas, run only the affected validators plus cross-artifact checks named by the delta
plan. A data, code, formulation, required-output, or headline-result change invalidates all downstream
approvals and requires full regeneration. Keep chat to completed P0/P1 items, verification results,
and unresolved risks; do not repeat complete logs.

Do not turn confirmed revision into an unrequested greenfield rewrite of the full paper body.

If an accepted change cannot be completed or validated, stop claiming completion and report the exact blocker.
