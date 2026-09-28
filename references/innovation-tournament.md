# Structural-insight tournament

## Purpose

Use this protocol before strategy freeze. Its job is not to decorate a standard pipeline with an
“innovation point”; it forces a broad search over problem-specific mathematical structure, spends a
small budget disproving weak ideas, and preserves the human-approved survivor as hash-bound evidence.

The selector is a decision aid, not an award predictor. Its bundled weights are
`default_uncalibrated` until enough genuinely isolated blind-test cases exist.

## Blind input boundary

For a live problem, use only the official problem bundle, team expertise, and generic method
references that do not contain same-case solutions. During a historical blind test, obey
`references/empirical-validation-protocol.md`. Record every exposed resource in `blind_context`;
search snippets count. If same-case solution material was seen, set `solution_blind=false` and label
the run `retrospective_rehearsal`.

## Candidate-generation contract

Before selecting a route:

1. Build a complete transparent baseline and name one observable limitation.
2. Read `references/cross-case-transfer-protocol.md`, write a target signature, and retrieve three
   to five diverse cards with `scripts/retrieve_cross_case_patterns.py`. A retrieved move is not
   itself an innovation.
3. Generate at least eight falsifiable candidates spanning at least four structural families.
4. Search in this order: structural reduction, regime boundary, identifiability, uncertainty-to-
   decision closure, strategy boundary, value of information, structure-aware solver, independent
   certificate, and decision-focused learning.
5. Anchor every candidate to a page, table, field, unit, constraint, or other exact prompt fact.
6. State which mathematical object changes: objective, constraint, state, geometry, information,
   identifiability, uncertainty, solver, or validation.
7. Write the counterfactual, expected measurable consequence, falsifier, fallback, and failure
   conditions before seeing pilot results.
8. When a candidate borrows a card, fill `transfer_lineage`: card IDs, target-specific
   reconstruction, and non-copy boundary. Reject candidates that only rename the borrowed move.

Changing only crossover probability, mutation rate, learning rate, generic ensemble weights, or a
fashionable model name is not a structural candidate. Such tuning may improve implementation, but
it cannot be the primary innovation unless a problem-specific formulation change and controlled
consequence are also demonstrated.

Use `assets/templates/结构洞察淘汰赛模板.json`. The template contains search prompts, not approved
claims. Replace every placeholder and score each selector dimension from 0 to 4:

- specificity: tied to exact problem evidence;
- necessity: repairs a named baseline failure;
- evidenceability: can be tested independently under the deadline;
- consequence: changes a result, decision, bound, or complexity materially;
- feasibility: fits the remaining compute and team budget;
- independence: the pilot does not reuse the same failure path as the main method;
- paper value: strengthens the argument spine without model stacking.

## Top-three micro-experiment

The deterministic ranking proposes three candidates. Humans may override the order, but must record
why. All three shortlisted candidates—not only the eventual winner—must complete a bounded pilot
before strategy freeze.

Before executing any pilot, write a pre-pilot manifest that hashes the discovery tournament and
records every shortlisted ID, metric, threshold, failure rule, seed, and time budget. Hash this
manifest and append its timestamp plus SHA-256 to the execution log. If the manifest is created or
changed after a pilot starts, the case has a freeze-order failure; rerunning the pilot cannot repair
the original benchmark, although a separately labeled fresh run may be started in a new context.

For each pilot:

1. pre-register one metric, threshold, time budget, and failure rule;
2. build the smallest instance that can distinguish the structural claim from its counterfactual;
3. use an independent enumerator, alternate solver, held-out scenario, analytical bound, synthetic
   truth, or other basis that does not share the key implementation path;
4. save machine-readable evidence and bind it by SHA-256;
5. mark the result `pass` or `fail`; never rewrite the threshold after observing it;
6. obtain a real team review with rationale.

Select exactly one primary innovation and at most two supporting innovations from the three tested
candidates. A primary candidate should normally change structure or decision semantics. A failed
pilot is useful evidence and should be rejected, not cosmetically reframed.

The discovery shortlist is immutable after pilots start. At freeze, do not reinterpret a failed
shortlisted candidate as a selector override merely because its failure penalty changes the
post-pilot ranking. Keep the original three in `shortlisted`, mark the failed one `rejected`, and
select only passing candidates. Preserve pre-pilot and post-pilot rankings separately.

Run discovery and freeze through the unified workflow:

```bash
python scripts/cumcm_workflow.py --root PROJECT innovation-audit \
  --manifest strategy/结构洞察淘汰赛.json --phase discovery

python scripts/cumcm_workflow.py --root PROJECT innovation-audit \
  --manifest strategy/结构洞察淘汰赛.json --phase freeze
```

The `model_selection` human gate and strategy freeze remain closed until the freeze-phase audit
passes. The solver-ready strategy contract must bind the tournament file, audit report, hashes,
primary candidate, and supporting candidates. An external overnight system may implement this
contract but may not silently substitute another innovation.

## Blind-test calibration

After an isolated case is unblinded, record real human outcomes in
`assets/templates/创新盲测校准台账模板.json`. Audit:

- top-one and top-three hit rate;
- false-novelty rate among the proposed top three;
- implementation survival after the pilot;
- regret between the selected and human-best candidate.

Evidence weights are intentionally conservative: prospective canary 1.0,
solution-isolated historical 0.7, cross-case-assisted historical 0.55, and retrospective rehearsal
0.25. Record the canonical task family for every case. Fewer than three prospective-equivalent
cases, twelve labeled candidates, or three covered task families is diagnostic only and cannot
change the default weights. At six effective cases, twenty-four candidates, and four covered task
families, the script may emit a bounded candidate update, still requiring team approval.

```bash
python scripts/cumcm_workflow.py --root PROJECT calibrate-innovation \
  --ledger validation/创新盲测校准台账.json \
  --output-weights validation/innovation-weights-proposal.json
```

Never silently activate proposed weights, fabricate reviewers, or describe retrospective tuning as
prospective validation.
