# Human-led AI collaboration protocol

Use this protocol to preserve independent team responsibility while gaining practical value from AI. It is a quality and provenance workflow; only clauses verified in current official documents are official requirements.

## Responsibility matrix

| Work item | AI role | Team authority and evidence |
|---|---|---|
| Problem interpretation | Extract ambiguities, dependencies, and alternative readings | Approve the operative reading and justify it against the statement |
| Assumptions | Challenge, classify, and test candidate assumptions | Select assumptions, scope, and failure conditions |
| Model design | Propose baselines and materially different families | Select variables, objective, constraints, and final route |
| Innovation | Find baseline deficiencies and possible modifications | Supply domain rationale, approve the claim, and accept the evidence test |
| Code and computation | Scaffold, implement, debug, automate, and cross-check | Inspect governing logic, run independently, and accept outputs |
| Figures and tables | Generate and format traceable outputs | Verify values and approve the interpretation |
| Writing | Outline, restructure, edit, and draft from approved reasoning | Provide or approve the reasoning, factual content, claims, and final wording |
| References | Find candidate primary sources and normalize formats | Open the source, verify existence and metadata, and decide whether it supports the claim |
| Review | Act as an adversarial evaluator and produce repair options | Decide which repairs to adopt and re-verify affected claims |

## Core-decision gates

Do not silently pass a gate. Record owner, rationale, rejected alternatives, evidence, and status.

1. **Problem contract:** subproblem interpretation, required outputs, units, and dependencies.
2. **Model contract:** assumptions, variables, objective, constraints, baseline, selected route, and solver.
3. **Innovation contract:** baseline deficiency, exact modification, domain mechanism, controlled test, and failure condition.
4. **Result acceptance:** canonical outputs, uncertainty, reality checks, failed tests, and decision implication.
5. **Manuscript sign-off:** abstract numbers, claims, citations, figures, limitations, AI markers, and supporting materials.

Until a gate is approved, label the output `AI-proposed` or `AI-recommended`. Approval does not equal verification; use `verified` only after a documented check.

## Model and experiment discipline

- Generate at least eight problem-anchored structural hypotheses across four families, pilot the top
  three independently, then normally present one primary model and one transparent baseline or
  informative comparator.
- Add complexity only for a named baseline deficiency.
- Treat adaptive heuristic parameters, extra weight layers, and model stacking as ordinary modifications unless a problem-specific mechanism and controlled comparison demonstrate a consequential benefit.
- Run the baseline and proposed method on the same data splits, scenarios, stopping rules, metrics, and hardware assumptions where possible.
- Report accuracy or objective value together with feasibility, uncertainty, runtime, and decision impact.
- Translate team domain expertise into explicit constraints, priors, costs, risk measures, or validation ranges; do not use a professional label as a novelty claim.

## Code protocol

Give AI-generated code provisional confidence from the source's calibrated performance and the
handoff evidence, but do not label it execution-verified until it has been inspected and run.

1. Map each module to equations and subproblems.
2. Test dimensions, indexing, units, edge cases, seeds, splits, and constraints.
3. Recompute at least one headline result by an independent implementation or transparent derivation.
4. Run from a clean entry point and regenerate figures, tables, and the result ledger.
5. Keep screenshots optional; they never substitute for runnable source, logs, and reproducible outputs.

## Writing and citation protocol

- For problem analysis, model construction, innovation, result interpretation, and limitations, obtain team-authored bullets or explicit approval of the reasoning before final prose.
- If no team reasoning exists, provide a short structural outline or ledger rather than a long fill-in-the-blanks draft; do not represent it as independently human-authored.
- Do not represent prose as submission-ready before the reasoning, evidence, summary-coverage, and manuscript-signoff gates pass.
- Freeze the result ledger and complete the abstract coverage matrix before drafting the final abstract or title. Include method, direct quantitative answers, central insight, and validation evidence with justified precision.
- Remove canned prose by replacing it with mechanism, data, quantities, and consequences—not by shuffling sentences to evade detection.
- Use AI-discovered citations only as search leads. Verify the primary source, authors, title, venue, year, identifier, and exact claim support.

## Red-team protocol

Before finalization, ask AI to attack:

- hidden assumptions and real-world implausibility;
- leakage, circular validation, and arbitrary weights;
- false optimality, causality, or robustness claims;
- code-paper number mismatches;
- unverified citations and fabricated metadata;
- generic limitations and innovations;
- disclosure gaps and unsupported claims of human verification.

Convert findings into a severity-ranked repair plan. The team decides and records accepted repairs.
