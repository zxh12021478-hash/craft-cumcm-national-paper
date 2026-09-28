# Stage: capability evaluation and improvement

Read `references/capability-evaluation-loop.md`. If a historical problem is involved, also read
`references/empirical-validation-protocol.md` and enter isolation before opening the target.

## Sequence

1. Before opening the target, freeze the skill version, evaluation rubric, allowed resources, and target-selection record. Do not pre-supply an evaluator-chosen model or task-family label.
2. Keep evaluator-only expectations outside the solver context. Pass raw problem artifacts, not the intended method or suspected weakness. Let the solver classify and hash the task family after official-problem decomposition but before model selection.
3. Preserve the produced strategy, code, results, logs, elapsed time, and human interventions by hash.
4. Record self-assessment and independent assessment separately in `能力盲测评估台账.json`.
5. Run `scripts/score_capability_benchmarks.py`; do not average away automatic failures or hash mismatches.
6. For an efficiency change, run `scripts/measure_instruction_budget.py` before and after, and record
   elapsed time plus input/output tokens when the host exposes them. Token reduction counts only if
   automatic-gate and independent-quality outcomes do not regress.
7. Diagnose the narrowest reusable cause, change the smallest routed reference/script/schema that addresses it, and rerun both regression tests and a fresh forward test.
8. Require coverage across task families and at least one prospective unseen case before describing evidence as broad. Never convert the score into an award probability.

## Evidence boundary

Synthetic cases test mechanics, historical cases test solution-isolated strategy generation, package
takeovers test reproduction, and real human calibration tests usefulness. Label exactly which level
was reached. A self-score or retrospective replay is diagnostic only.
