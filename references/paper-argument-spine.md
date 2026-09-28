# Paper argument spine

Use an argument spine to make the paper read as one defensible chain rather than a chronology of software operations or a stack of named models.

## Spine schema

For every required subproblem, trace:

`decision need → given evidence → transparent baseline → named deficiency → selected mechanism/model → solver or estimator → validation → direct answer → downstream use`

The spine must work in both directions:

- every stated problem ends in an explicit answer;
- every model, figure, table, and metric serves a stated problem or validation need;
- every later-stage input points to its generating result;
- the conclusion introduces no new evidence or claim.

## Construction procedure

1. Start from the subproblem dependency graph, not from preferred algorithms.
2. State the paper’s central mathematical insight in one sentence.
3. Assign one canonical output and validation target to every subproblem.
4. Identify the minimum baseline and the exact deficiency repaired by the main model.
5. Remove orphan methods that do not change an answer, validation result, or decision.
6. Use `assets/templates/论文论证台账模板.md` as the internal source of truth.

Before the operative task, mechanism, and data sufficiency are established, describe named methods only as conditional candidates. Do not label a pipeline `AI-recommended`.

## Task-family skeletons

Treat these as argument patterns, not mandatory pipelines.

- **Evaluation:** decision and stakeholders → defensible criteria → explicit preference or weighting rationale → score, order, or partial order → rank stability → action.
- **Forecast-to-optimization:** leakage-safe data → naive forecast and uncertainty baseline → selected forecast → uncertainty-aware objective and constraints → optimized policy → scenario and regret analysis.
- **Classification-to-warning:** information available at decision time → transparent classifier → calibrated probabilities or costs → operating threshold → grouped or out-of-sample validation → warning policy.
- **Mechanism or inverse problem:** observation mechanism → identifiable parameters → baseline estimator → structure-aware model → residual and boundary checks → inferred quantity and usable range.

Do not present preprocessing, weighting, fitting, optimization, simulation, and plotting as independent innovations merely because they are separate software steps.

## Narrative checks

- Explain why the model is appropriate before displaying its equations.
- Separate formulation, solution method, numerical result, validation, and interpretation.
- Use paragraphs for arguments, tables for repeated mappings, lists for genuine enumerations, and equations for mathematical relations.
- Keep the main line visible; move secondary derivations, diagnostic detail, and long code to appendices or supporting materials when allowed.
