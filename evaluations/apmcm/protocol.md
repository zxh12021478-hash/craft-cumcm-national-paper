# APMCM Skill development acceptance protocol

This is a development benchmark, not an organizer scoring rubric or a prize predictor. Do not load its answer keys in contest strategy work. The runtime remains Skill handoff → Modex implementation/draft → Skill audit/repair; Doubao is used here only as a development executor.

## Target standard

A release aiming at a top standard should satisfy these observable conditions:

- Original required outputs are covered; optional novelty does not displace a question.
- The proposed route is implementable from the data, equations, constraints and stated assumptions.
- No silently infeasible plan, future-information leakage, manufactured observation or unsupported unconditional winner.
- Improvements are relative to a fair baseline and a specific mechanism; untested gains remain hypotheses.
- Material headline results can be traced and independently checked; revisions propagate to figures, abstract and conclusion.
- New-problem work ends at a usable handoff; initial manuscript production remains with Modex.
- Cost improvement is assessed using actual usage and total work through accepted revision, at matched quality. File length, script runtime and a completed synthetic task cannot establish token savings.

No fixed number of synthetic passes proves a 10/10 skill. Track unresolved failures and evidence gaps instead of inflating a score.

## Reproducible probes

`inputs/` contains three synthetic short requests: forecasting with release-time constraints, ranking with unknown preferences and perturbed observations, and dispatch with capacity/efficiency constraints. `audit-input/` contains a separate synthetic returned paper/code/results bundle with deliberately introduced errors and a correct control statement. These are targeted regression probes, not unseen complete contest papers or real Modex outputs.

For strategy comparison, run task-only and task-plus-skill in fresh separate chats with the same model setting, the same input files and output request. Do not give the executor the expected answers, other condition's output or past conclusions. Do not permit it to score itself. Preserve actual artifacts and executed checks. Record deviations from the protocol and compare substantive correctness and implementability, not required-word matches.

For draft audit, give the evaluator only the original question, draft, code/results and skill. Compare its evidence-backed findings with the separately frozen defect inventory; inspect false positives and whether proposed fixes remain feasible. A correct rejection is useful even when the supplied problem has no feasible solution.

Use fresh tasks for future broad validation: these public probes become regression tests after disclosure. Repeat paired trials if estimating an effect; one pass per condition cannot establish superiority or generalization. Real Modex end-to-end validation requires its actual returned artifacts and remains distinct from these probes.

## Observed development run

See [2026-10-18 results and limits](results-20261018.md). First-pass failures, feedback-informed repairs and root-reviewed artifacts are separated. These results do not establish a final-release treatment effect.
