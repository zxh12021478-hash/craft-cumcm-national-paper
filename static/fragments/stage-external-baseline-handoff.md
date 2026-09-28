# Stage: external baseline handoff and takeover

Read `references/two-system-handoff.md` and `references/ai-baseline-regression-protocol.md`. Read
`references/code-quality.md` when code is present, `references/human-led-ai-collaboration.md` when
core decisions/provenance need approval, and `references/ai-and-competition-compliance.md` for live or
final disclosure. Read `references/team-comprehension-audit.md` only in final mode.

## Before the overnight run

1. Read the complete problem and understand the relationship among its subproblems.
2. Compare plausible conceptual directions and identify one preferred recommendation plus one brief fallback.
3. Export one consolidated `推荐解题思路大纲.md`, `.docx`, or `.txt`; this is the only generated
   pre-draft deliverable. Do not send formulas, algorithms, code plans, JSON records, ledgers, score
   sheets, audit reports, or fixed implementation instructions.
4. State that the writing agent owns the final detailed route, derivation, computation, code, and
   complete first draft. It may improve or replace the recommendation.
5. The team approves the eventual core decisions after considering the writing agent's work.

## When the bundle returns

1. Preserve the original bundle and mark it `quarantined`; this label means immutable intake and
   evidence not yet qualified, not a judgment that the external agent is weak.
2. Classify it as `paper-only`, `partial-bundle`, or `full-bundle`. A paper-only package may receive only a paper-layer audit; do not recreate printed code and call that original-source reproduction.
3. If a prior baseline exists, run `scripts/plan_incremental_audit.py` before loading the new bundle.
   Then run `scripts/preflight_environment.py --profile takeover` and
   `scripts/audit_external_handoff.py` before executing code. The audit compares structured
   approved/implemented contracts rather than trusting the external system’s boolean declaration.
   Perform static code and secret scans first.
4. Assign provisional confidence as `high`, `standard`, or `low` using calibrated prior performance,
   package completeness, reasoning coherence, declared uncertainty, and static quality.
   `accepted_for_audit` authorizes inspection and scoped reuse, but does not mean that core results
   or the submission are verified.
5. Execute only after static Blocker/Critical findings are cleared. Run from a copied clean directory with recorded dependencies; install dependencies only after explicit trust review. This is reproducibility isolation, not a security sandbox.
6. Run `scripts/truth_harness.py` plus at least one problem-specific independent verifier. Reconcile every headline number through the result ledger, and verify every citation against its primary or official source.
7. Classify each section as retain, repair, replace, or delete. A high-confidence bundle should be
   retained by default when supported by evidence. Differences from the earlier recommendation are
   not defects by themselves.
8. Generate the three-day deadline plan with `scripts/competition_scheduler.py --profile takeover`.
9. Record both AI systems, their versions, purposes, key interactions, adopted content, manual changes, and verification in `AI工具使用详情`.

## Takeover priority

Facts before models; models before innovation; evidence before prose; paper rebuild before cosmetic polish. If the baseline cannot reproduce or violates the approved specification, do not spend time polishing it.

## Output

Return the handoff verdict, artifact inventory, recommendation-versus-actual route comparison,
reproducibility verdict, result/citation conflicts, severity-ranked repair plan, deadline schedule,
and the next team decision gate. The comparison explains choices; it does not enforce conformity.
Use a sprint summary for a blocked or incomplete bundle; do not spend tokens producing a full
national-judge report until the bundle is viable.
