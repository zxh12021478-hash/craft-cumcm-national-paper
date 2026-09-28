# Aspirational national-award rubric

Use this rubric for uncompromising review. Scores estimate artifact quality, not award probability.

## Scorecard

| Dimension | Weight | Full-credit evidence |
|---|---:|---|
| Problem interpretation and completeness | 8 | Every subproblem and required file is answered; dependencies and units are correct |
| Assumptions and mechanism | 10 | Minimal, falsifiable assumptions; equations follow the real mechanism; scope is explicit |
| Data quality and preprocessing | 8 | Provenance, leakage audit, missingness, anomalies, transformations, and uncertainty are documented |
| Mathematical formulation | 14 | Variables, objectives, constraints, boundary conditions, identifiability, and special cases are rigorous |
| Problem-specific innovation | 16 | At least one specific, necessary, evidenced, consequential innovation |
| Solver and numerical analysis | 10 | Structure-aware method, convergence/complexity, feasibility checks, reproducible settings, and justified precision |
| Validation and uncertainty | 14 | Independent analytical/numerical/empirical checks; uncertainty reaches the decision |
| Results and decision value | 8 | Direct answers, interpretable implications, thresholds, and limitations |
| Writing and visualization | 7 | One-page abstract, clear reasoning chain, legible figures/tables, consistent notation |
| Reproducibility and compliance | 5 | Clean run, complete support files, citations, anonymity, formatting, AI disclosure, traceable human approval of core decisions |
| **Total** | **100** | |

## Conservative verdict bands

- **95–100:** exceptional national-first candidate; no material weakness and at least one memorable insight.
- **90–94:** national-first competitive; strong enough for top review if execution and fit hold.
- **84–89:** national-second competitive; complete and credible but innovation or validation is not dominant.
- **76–83:** provincial-first competitive; conventional or uneven despite technical work.
- **65–75:** provincial award possible; important gaps remain.
- **Below 65:** not competitive or not submission-ready.

## Hard caps

- Any eligibility or integrity blocker: ineligible until fixed.
- Wrong interpretation or missing required subproblem: maximum 55.
- Core code cannot reproduce headline outputs: maximum 65.
- Leakage, circular validation, or invalid statistical split: maximum 55.
- No independent validation: maximum 74.
- No problem-specific innovation: maximum 79.
- Heuristic called globally optimal without evidence: maximum 82.
- Headline numbers contradict across artifacts: maximum 69.
- AI use not disclosed as required: ineligible until fixed.
- Claimed human verification or authorship contradicted by records: ineligible or not submission-ready until resolved.

## Reviewer questions

1. What is the one insight an expert evaluator will remember?
2. Which result would change if the key assumption failed?
3. Can the most important number be reproduced in under ten minutes from a clean entry point?
4. What independent evidence says the model is not merely self-consistent?
5. Does uncertainty alter the recommended decision?
6. Is the claimed innovation visible in formulation and results, or only in prose?
7. Which core decisions were made and verified by the team, and where is that evidence recorded?
