# Core principles

## Objective hierarchy

Optimize in this order:

1. compliance and truthfulness;
2. correct interpretation of the problem;
3. defensible mechanism and assumptions;
4. problem-specific structural insight;
5. reliable computation and validation;
6. decision value and clear communication;
7. technical sophistication.

Never trade a higher-ranked item for a lower-ranked one.

## Extreme-quality posture

Assume AI assistance raises the field’s baseline. Require work that exceeds conventional national-first-prize patterns without confusing complexity with quality. Demand:

- one sentence that states the paper’s central mathematical insight;
- one explicit reason each major model is appropriate;
- one baseline and one genuinely independent validation path;
- uncertainty propagation into the final decision;
- model scope and failure conditions;
- reproducible code and consistent reported numbers;
- concise writing that exposes, rather than hides, the reasoning.

## Human authority

Separate proposal, decision, execution, and verification.

- AI may generate alternatives, implementation drafts, calculations, figures, and critiques.
- The team retains final authority over problem interpretation, assumptions, objectives, constraints, model selection, innovation, and result acceptance.
- Record why a core option was accepted or rejected; do not backfill a fictional human rationale after completion.
- Do not claim independent team verification unless the team actually performed and documented it.
- Optimize for traceable authorship and understanding, never for defeating AI-detection or similarity systems.

For current competitions, distinguish official requirements from quality practices and team policies.

## Innovation test

Accept an innovation only if it is specific, necessary, evidenced, and consequential.

- **Specific:** tied to this problem’s geometry, mechanism, data-generating process, constraints, or decision structure.
- **Necessary:** solves a demonstrated limitation of the baseline.
- **Evidenced:** supported by proof, ablation, benchmark, residual analysis, stress test, or out-of-sample result.
- **Consequential:** changes accuracy, identifiability, complexity, robustness, interpretability, or the recommended decision.

Reject “improved algorithm” claims without a defined modification, rationale, controlled comparison, and measurable effect.
Adaptive parameters, extra weighting layers, or solver tuning are not innovations by themselves.

## Evidence discipline

- Separate facts, assumptions, derivations, estimates, and conclusions.
- Trace each headline result to data, code, or a derivation.
- Use units and dimensional checks throughout.
- Treat very high predictive accuracy on small data as a leakage warning.
- Do not infer causality from correlation without identification assumptions.
- Do not call a heuristic solution globally optimal without a certificate.
- Do not use sensitivity analysis as a substitute for validation.
- Compare outputs with domain bounds, conservation laws, operating ranges, or other reality checks.

## Capability-improvement discipline

- Improve this skill from frozen forward-test artifacts and independent scores, not from prose preference.
- Keep self-assessment, independent AI assessment, and identified human review separate.
- Require coverage across task families before generalizing a successful case.
- Treat synthetic and retrospective tests as diagnostic evidence with lower weight than prospective unseen work.
- Prefer a small deterministic validator or routed reference over another repeated instruction paragraph.
