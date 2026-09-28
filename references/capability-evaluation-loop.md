# Capability evaluation and regression loop

## Purpose

Use this protocol to improve the skill from evidence instead of adding instructions after an
anecdotal success or failure. It measures strategy quality, reproducibility, independent checking,
innovation evidence, cross-artifact consistency, decision value, time, and human intervention. It
does not predict awards.

## Frozen evaluation contract

Before a forward test, record:

1. skill version and hash;
2. target problem/artifact hashes and permitted resources;
3. isolation label and pre-freeze exposure ledger;
4. the routing rule; after official-problem decomposition, the solver must classify and hash one
   primary task family and any supporting family before model selection—never pre-supply an
   evaluator-chosen family that could reveal the expected route;
5. fixed dimension rubric and automatic-failure rules;
6. evaluator-only expectations kept outside the solver context;
7. start time, compute budget, instruction-route size, input/output tokens when available, and how
   human intervention will be counted.

For historical targets, follow `empirical-validation-protocol.md` before opening the problem. Same-
case exposure before freeze permanently downgrades the case. Synthetic tests are useful for mechanics
but carry little evidence about real competition performance.

## Score dimensions

Score each dimension from 0 to 4 and attach concrete artifact evidence:

- `requirement_coverage`: every reconciled subproblem, required field, range, unit, and output is closed;
- `formulation_validity`: variables, mechanisms, objectives, constraints, timing, and assumptions match the task;
- `structural_insight`: the selected insight is problem-specific, falsifiable, and consequential;
- `reproducibility`: a clean entry point regenerates the reported outputs;
- `independent_validation`: a separate failure path recomputes headline results and tests failure cases;
- `cross_artifact_consistency`: paper, code, figures, ledgers, and disclosures agree;
- `decision_value`: uncertainty, scope, and failure conditions reach a direct usable answer.

Automatic failures include a missing required subproblem, changed frozen hash, unreproduced headline
number, material hard-constraint violation, same-case contamination mislabeled as blind, fabricated
human review, or unsupported optimality/award claim. Do not average an automatic failure away.

## Independent assessment

Record self-assessment and independent assessment separately. Give an independent evaluator the raw
frozen artifacts, fixed rubric, and allowed context—not the intended answer, suspected weakness, or
prior diagnosis. An AI evaluator counts as independent AI assessment, never as human review.

A case passes only when every dimension is at least 2, at least four dimensions are at least 3, and
no automatic failure remains. Missing independent assessment leaves the case `self_only`.

## Aggregation and claims

Use `assets/templates/能力盲测评估台账模板.json` and run:

```bash
python scripts/score_capability_benchmarks.py \
  validation/能力盲测评估台账.json --root PROJECT --strict
```

Weight prospective unseen evidence above solution-isolated historical, cross-case-assisted,
retrospective, and synthetic evidence. Require multiple task families and at least one prospective
case before describing the evidence as broad. Report score gaps, failures, elapsed time, human
interventions, routed instruction words/bytes, available token counts, and family coverage; never
convert them into a national-first-prize probability. Run `scripts/measure_instruction_budget.py`
before and after any context-efficiency refactor.

## Minimal-change iteration

For each failure:

1. identify the narrowest reusable cause;
2. decide whether it belongs in a routed reference, deterministic script/schema, core invariant, or nowhere;
3. change the smallest component that can prevent recurrence;
4. run unit/regression tests;
5. run a fresh isolated forward test from raw artifacts;
6. preserve both pre-change and post-change records.

For efficiency changes, require equal or better automatic-gate outcomes. Fewer tokens accompanied by
weaker requirement coverage, validation, or cross-artifact consistency is a regression, not a gain.

Remove or merge instructions that duplicate a deterministic validator. Reject changes that improve
one known case by leaking its expected route, weaken isolation, or increase complexity without a
measured reduction in failures.
