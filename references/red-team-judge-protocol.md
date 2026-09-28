# Red-team national-judge protocol

Use this protocol when the user asks for a strict CUMCM judge simulation, national-award red-team
review, adversarial final review, or the shortest repair path toward national-first competitiveness.
It supplements `national-award-rubric.md`; it does not replace the evidence, reproduction, task-family,
or compliance workflows.

## Nature of the judgment

- Treat the exercise as a conservative quality stress test, not an official review or award forecast.
- Score artifact quality under the evidence actually supplied. Never convert a score into an award
  probability without an independently calibrated benchmark that matches the year, task family,
  review stage, and artifact completeness.
- Simulated reviewer lenses produced in one run are correlated views from one system. They are not
  three independent human judges and their mean is not independent evidence.
- Keep criticism actionable. Do not inflate scores to encourage the team and do not invent defects
  merely to sound strict.

## Evidence states

Tag every material judgment with one of these states when ambiguity matters:

- `verified`: independently recomputed, derived, or checked against the authoritative source;
- `supported-not-reproduced`: directly supported by supplied artifacts but not independently rerun;
- `inference`: a reasoned evaluator judgment whose premise is stated;
- `unable-to-verify`: missing problem, data, code, environment, appendix, citation, or output prevents
  the claimed check.

Never phrase `supported-not-reproduced` or `inference` as `verified`. A paper-only review cannot
approve code reproduction, data provenance, or numerical closure.

## Stage routing

Detect the real stage before selecting output depth.

| Stage | Judge focus |
|---|---|
| Selection | problem structure, team fit, closure risk, differentiation, validation feasibility; never prefer a problem letter by folklore |
| Modeling | interpretation -> assumptions -> variables/objective/constraints -> model; no prose-first review |
| Solving | code path, parameters, feasibility, units, numerical stability, leakage, and result closure |
| Draft writing | argument spine, direct answers, figures, abstract coverage, citations, and claim strength |
| Final bundle | full hard gates, reproduction, scorecard, three lenses, adversarial case, repair ROI, compliance, and rendered-page checks |

Use `red-team-fast` under deadline or when the user asks for the most important problems only. Use
`red-team-full` for a complete draft plus the relevant code/data/supporting bundle or when explicitly
requested. For a revised bundle with a preserved baseline, run `scripts/plan_incremental_audit.py`;
use the fast contract on a targeted dependency closure and the full contract only when the delta
changes code, data, formulation, required outputs, headline results, or final-submission evidence.
Do not force a full terminal-review report onto an incomplete draft or a cosmetic delta.

## Pre-anchor judge baseline

Before reading the paper's abstract, conclusion, or claimed route:

1. Read the official problem and attachments and record their hashes or stable identifiers.
2. State the actual decision or inference target of every subproblem, its required outputs, units,
   constraints, dependencies, and likely failure paths.
3. Establish a small evaluator reference set of plausible model families and decisive validation
   evidence. This is a reference frame, not a mandatory answer key.
4. If the official problem is absent, mark task alignment and completeness `unable-to-verify`; do not
   reconstruct the problem from the manuscript and then claim independent understanding.

Only then read the manuscript's claims. Judge a route on its own logic and evidence, not on whether it
matches the evaluator's preferred route or the earlier recommendation outline.

## Gate audit

Apply the hard caps in `national-award-rubric.md` before interpreting the weighted score. At minimum,
test these gate classes:

1. eligibility, anonymity, originality, citation, AI disclosure, and other current official rules;
2. wrong problem, missing major subproblem, or missing required direct answer;
3. invalid core mathematics, statistics, objective, constraints, boundary/initial conditions, or
   implementation-to-paper mismatch;
4. contradicted, infeasible, implausible, or unreproducible headline result;
5. unknown or fabricated data, destructive preprocessing, selection bias, leakage, circular
   validation, or invalid split;
6. absent independent validation for a core claim;
7. conclusion strength exceeding what the model and evidence can establish.

Do not average a gate failure away with presentation, model count, or algorithm prestige. Map findings
to the existing severity vocabulary: `Blocker`, `Critical`, `Major`, or `Minor`.

## Evidence-led audit

For each subproblem, trace:

`requested output -> paper claim -> formulation -> data/code/derivation -> independent check -> direct answer`

For every core model, answer:

- **Why:** what named structural need or baseline failure justifies it?
- **What:** which subproblem target does it solve?
- **How:** what formulation and solver/estimator produce the output?
- **Result:** what explicit, unit-bearing answer follows?
- **Validation:** what evidence could falsify the claim and what happened?

Use the routed task-family reference for specialized checks. Use `validation-playbook.md` for fair
baseline and ablation design rather than repeating generic model comparisons. Complexity without a
measured, decision-relevant gain can reduce model-rationality and innovation scores.

For formula defects, report the artifact location, original expression, defect, corrected form or
repair direction, and consequence for downstream results. Check domains, dimensions, units, signs,
normalization, bounds, initial/boundary conditions, feasibility, optimality language, and precision.

For data-driven work, inspect provenance, sample construction, missingness, anomalies, transformations,
split logic, leakage, residuals, calibration, imbalance, overfitting, and subgroup/temporal/spatial
validity as applicable. For optimization, independently check objective semantics, constraint closure,
feasibility, bound/certificate status, stability, and implementability. For figures, judge information
density and claim support rather than visual novelty or chart count.

Audit the abstract separately after the result ledger is established: subproblem coverage, method
specificity, quantitative results, decision meaning, supported innovation, and unsupported claims.

## Three correlated reviewer lenses

After the common factual audit, apply three lenses to the same evidence:

1. **Mathematical-strict lens:** formulation, derivation, identifiability, numerical correctness,
   assumptions, and proof or certificate strength.
2. **Applied-modeling lens:** reality fit, data semantics, decision usefulness, implementability,
   uncertainty, and scope.
3. **National-selection lens:** asks what memorable, evidenced reason justifies advancing this paper
   over other already strong papers and which weakness would remove it from national-first discussion.

Show the three scores only in `red-team-full` or when requested. If their spread exceeds eight points,
explain the disputed dimension. A displayed arithmetic mean is diagnostic only and must be labeled
`correlated simulated mean`; never present it as independent panel evidence.

## Adversarial case

In `red-team-full`, construct at least five strongest evidence-based arguments against national-first
selection. For each attack state:

- the exact claim being attacked;
- the evidence or missing evidence that makes the attack credible;
- the manuscript's present defense, if any;
- whether the attack survives (`yes`, `partial`, or `no`);
- the minimum repair and the check that would close it.

Do not create straw-man attacks. End with an attack-resistance verdict: `strong`, `mixed`, or `weak`.

## Repair ROI

Rank repairs by decision impact, time to implement and verify, dependency risk, and confidence in the
benefit. Use:

- `P0`: eligibility, correctness, missing answer, reproduction, or other gate failure;
- `P1`: likely to change national-award competitiveness materially;
- `P2`: worthwhile after P0/P1 close;
- `P3`: cosmetic, redundant, speculative, or too costly for the expected benefit.

For the top repairs, name the artifact, exact action, downstream files that must stay synchronized,
verification command or evidence, and residual risk. Estimated score recovery is a diagnostic range,
not a promise; do not make increments sum mechanically to a target score.

## Output contracts

### `red-team-fast`

Return, in this order:

1. verdict and evidence scope;
2. triggered gates and score caps;
3. conservative rubric scorecard;
4. top five dangerous defects with locations and repairs;
5. P0/P1 repair order and shortest verification plan;
6. final simulated recommendation: `strongly recommend`, `recommend`, `borderline`, or `do not recommend` for national-first discussion.

Keep the active repair queue to at most five P0/P1 findings. Save longer formula/code/evidence ledgers
as artifacts instead of repeating them in chat. A Blocker or Critical finding is never hidden by the
soft output budget.

### `red-team-full`

Return the fast output plus:

- independent problem baseline and per-subproblem audit;
- formula/data/code error ledger by severity;
- innovation baseline/ablation verdict;
- abstract-only score and its three most consequential defects;
- the three correlated reviewer lenses and disagreement explanation;
- adversarial case and attack-resistance verdict;
- P0-P3 repair ROI;
- shortest evidence-backed route from the current band to the next band.

Use the verdict bands from `national-award-rubric.md`. If no matched comparison corpus exists, state
`national percentile: not calibrated`. Do not invent Top-X placement or percentage award chances.
