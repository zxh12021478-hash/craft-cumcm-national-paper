# Evaluation and ranking kit

## Applicability and baseline

Use when the requested output is a score, rank, tier, or indicator system. Start with transparent
direction normalization and equal or explicitly approved weights. Define the decision that the rank
serves; do not manufacture a scalar score when the prompt asks for a profile or threshold decision.

## Construction contract

- Define indicator meaning, unit, direction, missingness rule, redundancy, and aggregation semantics.
- Separate data-derived weights, expert judgments, and team policy; do not disguise one as another.
- Test rank reversal, correlated indicators, normalization choice, outliers, missing data, and weight perturbation.
- Compare at least one alternative weighting or outranking baseline on the same entities and data.

## Independent verifier

Recompute normalized indicators, weights, component contributions, final scores, and ranks from the
saved raw table in a separate script. Verify weight sums, dominance relations, tied ranks, and rank
stability under predeclared perturbations.

## Outputs and failure boundary

Deliver the indicator dictionary, weight and contribution tables, subdimension profiles, stability
table, and decision interpretation. A stable aggregate score still fails if compensation hides a
mandatory weakness or if the recommended decision changes under plausible preprocessing choices.
