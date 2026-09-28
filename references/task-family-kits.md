# Task-family router

Use this file after subproblem decomposition and before model selection. Route each subproblem to
one primary family and load only that reference. Load one supporting family only when the output of
one family is a formal input to another; do not load every kit or stack their named methods.

| Canonical family | Use when the operative output is | Routed reference |
|---|---|---|
| `evaluation-ranking` | score, rank, select, or build an indicator system | `task-family-evaluation-ranking.md` |
| `forecasting-optimization` | predict a future quantity, especially before a decision | `task-family-forecasting-optimization.md` |
| `classification-warning` | label, recognize, detect, calibrate risk, or issue warnings | `task-family-classification-warning.md` |
| `optimization-scheduling` | allocate, route, schedule, pack, or choose under constraints | `task-family-optimization-scheduling.md` |
| `mechanism-simulation` | explain or simulate a physical/biological/economic mechanism | `task-family-mechanism-simulation.md` |
| `network-spatial` | reason over graphs, paths, locations, fields, or trajectories | `task-family-network-spatial.md` |
| `sequential-control` | choose actions over time with evolving information or interaction | `task-family-sequential-control.md` |

Record the primary family, supporting family if any, routing evidence, baseline, task-specific
verifier, and failure boundary in every subproblem contract. If the classification is ambiguous,
state conditional routes and keep model selection open.

Every routed family must still provide: a typed input schema and unit dictionary; one runnable entry
point; a separate verification command; canonical result-ledger metrics; a fair baseline comparison;
uncertainty and failure-condition evidence; and an explanation the team can reproduce orally.
