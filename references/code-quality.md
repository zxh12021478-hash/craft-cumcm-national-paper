# Code and reproducibility standard

## Required bundle

- one documented entry point such as `run_all.py` or `main.m`;
- dependency specification and runtime version;
- deterministic seeds or a recorded stochastic protocol;
- relative paths and configurable input/output directories;
- raw-data read only; derived data written separately;
- scripts/modules mapped to paper subproblems;
- generated tables and figures saved with stable names;
- machine-readable result ledger;
- logs for solver status, convergence, and constraint violations.

## Review checks

- syntax and import success;
- missing files and absolute user paths;
- hidden manual steps;
- hard-coded headline answers;
- leakage across train/test or future/past;
- inconsistent units and indexing;
- unbounded loops and silent exception handling;
- stochastic instability;
- mismatch between code output and paper;
- licenses and attribution for external code.
- traceability from AI-generated or modified modules to the AI-use log;
- evidence that governing equations, units, constraints, and key branches were inspected by the team.

Run semantic counterexample checks in addition to syntax:

- unordered containers returned into positional unpacking;
- morning/afternoon, sign, coordinate-frame, angle-unit, and indexing symmetry mistakes;
- formulas that can divide by zero or drive probabilities/efficiencies outside valid bounds;
- incomplete geometric predicates, unused barycentric variables, and silent shape approximations;
- mutation of a list or array while iterating over it;
- copied problem constants that differ from the official statement;
- a neighbor search that excludes a fixed record instead of the active record;
- an optimization objective whose reported direction disagrees with the physical definition.

For each high-severity finding, construct the smallest deterministic counterexample. Do not infer
correctness from successful execution alone.

## Solver reporting

Record model size, solver, version, tolerances, initialization, seed, stopping rule, runtime, objective, feasibility residual, and optimality gap when available.

## Reproduction protocol

Run from a clean temporary output directory. Compare generated outputs against the result ledger with justified tolerances. Treat any headline mismatch as a critical defect.

Classify the reproduction state:

- `audit-only`: source and paper inspected, but no trustworthy run;
- `partial-reproduction`: some scripts or claims regenerate;
- `end-to-end-reproduction`: one clean command regenerates every required result and figure;
- `implemented-takeover`: accepted repairs are implemented and all downstream artifacts regenerate.

Never promote one state to the next merely because defects were identified.

Assign AI-generated code provisional confidence from calibrated source performance, reasoning
coherence, and bundle completeness. Reuse strong code where appropriate, but mark it execution-
verified only after inspection, testing, and execution. Require a controlled baseline-versus-
proposed run and independently recompute at least one headline result. Runtime screenshots may
supplement logs but never replace runnable source, dependency records, and generated outputs.
