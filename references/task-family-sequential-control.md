# Sequential decision, control, and dynamic-game kit

## Applicability and baseline

Use when actions change future states or information, or multiple actors interact over time. Write the
within-period order—observation, action, interaction, transition, cost, replenishment, settlement—before equations.
Start with finite-horizon dynamic programming or time-expanded optimization under one approved information structure.

## Construction contract

- Define typed state, action, transition, feasibility, terminal value, and what is known at each decision.
- Do not invent a probability law, cooperation assumption, equilibrium concept, or risk preference.
- For robustness, define the ambiguity set or risk criterion and compare value of information.
- For games, define actors, shared constraints, ties, congestion, fairness, and solution concept.

### Information-set firewall

- Write a decision-time field ledger with each input marked `observable_now`, `observable_history`,
  `latent_truth`, or `evaluation_only` before implementing the policy.
- The production policy entry point may accept only observable fields. Keep ground-truth state,
  target coordinates, future disturbances, simulator state, and answer labels in a separate
  simulator/evaluator object; never pass them as optimizer starts, anchors, convenience geometry,
  or hidden defaults.
- Add an independent forbidden-information test: hold the observable history fixed, perturb every
  latent/evaluation-only field, and require the chosen action to remain unchanged. Also fail static
  inspection when the policy call graph reads a forbidden field.
- A controller that reproduces a trajectory while consuming unavailable state violates the model's
  information constraint even when every numerical residual is small.

## Independent verifier

Enumerate reduced states/actions, audit Bellman event order, recompute trajectories and costs, run
the information-set firewall and latent-field perturbation test, test
reachability/viability, and evaluate policy survival on held-out scenarios. For games, report
best-response or exploitability residual rather than labeling an unchecked fixed point an equilibrium.

## Outputs and failure boundary

Deliver the event-order table, state/action/trajectory schema, policy and viability maps, conflict
table, regret, and conditional recommendations. A named “DP + simulation + game” pipeline is invalid
until information timing, uncertainty, and interaction semantics are fixed.
