# Stage: model construction

Read `references/model-selection-playbook.md`, `references/innovation-patterns.md`,
`references/innovation-tournament.md`, `references/task-family-kits.md`,
`references/code-quality.md`, and `references/human-led-ai-collaboration.md`.
After routing, also read only the selected primary and, if justified, supporting family reference
from `manifest.yaml:task_family_routes`.

## Model-selection ladder

1. Define decision variables, states, parameters, objective, constraints, and outputs.
2. Build a complete transparent baseline.
3. Generate at least eight structural hypotheses across at least four families; these are innovation
   candidates, not eight models to stack.
4. Rank the hypotheses, pilot the top three independently, and reject claims that do not survive.
5. Compare viable model routes on mechanism fidelity, identifiability, data sufficiency,
   computability, interpretability, validation, and decision usefulness.
6. Recommend the simplest route that answers the full problem and supports the surviving primary
   innovation.
7. Obtain and record the team decision before treating the route, objectives, constraints,
   innovation, or assumptions as fixed.

## Construction rules

- Derive equations from the physical, statistical, economic, geometric, or operational mechanism.
- Check dimensions, domains, signs, boundary conditions, and degenerate cases.
- Establish existence, uniqueness, identifiability, or explain why only an approximation is possible.
- Exploit structure before brute-force search.
- Separate estimation uncertainty from optimization uncertainty.
- When using heuristics, specify encoding, constraints, initialization, operators, termination, complexity, seeds, and comparison baseline.
- When using machine learning, define split units, leakage controls, class imbalance handling, calibration, and out-of-sample metrics.
- For multiobjective problems, show the Pareto frontier or justify scalarization weights.
- Run a controlled comparison between the transparent baseline and proposed model; keep data splits, scenarios, metrics, and stopping rules aligned.
- Translate team domain knowledge into explicit quantities or constraints and test its consequence.

## Required artifact

Create a one-page model card plus the model-contract section of `assets/templates/核心建模决策记录模板.md`: purpose, inputs, outputs, equations, assumptions, learned parameters, solver, complexity, validation, limitations, failure conditions, decision owner, and approval status.
