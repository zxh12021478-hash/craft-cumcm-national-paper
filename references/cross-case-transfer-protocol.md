# Cross-case structural transfer protocol

## Purpose

Use prior high-quality papers as a library of reasoning moves, not as a catalog of answers. The
library in `assets/benchmarks/cross-case-structural-patterns.json` contains derived abstractions from
2020–2025 cases. It does not contain reusable paper prose, equations, figures, or code.

Official display-code matching and award grade are different facts. Never call a displayed paper a
national-first paper unless an official award source establishes that grade. The award ledger in
`assets/benchmarks/official-award-evidence.json` must link the award source to the paper through at
least two stable identity keys such as title, team, institution, problem, year, or display code.
Title variants must be recorded instead of silently normalized. Low-provenance cards must receive
lower retrieval priority and cannot support award-level claims.

Verified award status is a provenance signal, not a quality oracle. The retriever applies only an
8% tie-breaking multiplier after task-fit scoring. It must never promote a weak analogy over a
better target fit, erase reconstruction cost, or justify copying a model. A special-award paper can
still contain a move that fails on the new problem; a display-only paper can still contain a useful
move without supporting any award claim.

## Isolation classes

For a live problem, a frozen cross-case abstraction library is a generic resource. Record its path,
version, and hash in the exposure ledger.

For a historical blind test:

- same-case papers, solutions, code, repositories, abstracts, and method-revealing snippets remain
  forbidden before strategy freeze;
- a cross-case abstraction library frozen before the target was opened is permitted generic
  pretraining;
- if raw unrelated papers are selected or abstracted after the target is opened, record them and
  label the run `cross-case-assisted solution-isolated historical test`;
- cross-case assistance does not make the test contaminated, but it is weaker than a prospective
  canary with a pre-frozen library;
- never search for papers by wording distinctive to the target problem before freeze.

## Target signature

Before retrieving cards, write a machine-readable target signature:

- output: prediction, ranking, path, allocation, control, parameter, or policy boundary;
- object geometry: tabular, graph, spatial, sequential, compositional, repeated-measure, or dynamic;
- constraints: capacity, time window, conservation, balance, integrality, safety, or information
  timing;
- bottleneck: identifiability, dimensionality, solver scale, uncertainty, sparse data, or missing
  validation;
- cheapest independent truth: enumeration, analytic bound, alternate solver, synthetic truth,
  held-out scenario, or original-space recomputation.

Use `scripts/retrieve_cross_case_patterns.py` to retrieve three to five cards. Require at least two
source cases and prefer more than one year. Include one guardrail when the target has classification,
high accuracy, correlation-based scenarios, or complex model stacking.

Before competition, run the retriever once against its bundled award ledger. Any broken card-to-
evidence link is a library integrity failure. During competition, freeze and hash both the structural
library and the award ledger; logging only the card file is insufficient because award bonuses and
labels depend on the ledger.

## Reconstruction contract

For each candidate derived from a card, record:

1. borrowed card IDs and source cases;
2. the abstract move that was borrowed;
3. the exact target facts, units, variables, and constraints used to rebuild it;
4. the mathematical object changed in the target;
5. the counterfactual baseline;
6. the pre-registered measurable consequence and falsifier;
7. the non-copy boundary.

The borrowed move itself is not the innovation. Only the target-specific reconstruction and its
controlled consequence may be claimed as innovation.

Reject the candidate as `analogy decoration` if it cannot explain what target variable is removed,
what decision changes, what boundary is proved, or how a pilot could falsify it.

## Consensus and differentiator split

When multiple prior papers on a problem family converge on the same backbone, treat that backbone
as the transparent baseline, not novelty. Search for a differentiator in:

- a proof that removes computation;
- a regime boundary or identifiability condition;
- uncertainty entering the decision;
- a structure-aware solver tied to the actual limit;
- an independent certificate;
- a decision or data-collection boundary.

Do not describe changing a generic algorithm parameter or adding another fashionable model as a
primary differentiator.

## Copyright and reproducibility boundary

Never copy source prose, equations, figures, tables, or code. A paper-specific formula must be
re-derived from the target assumptions. A literature claim or reference must be independently
verified from the original source before appearing in the submission.

Keep the retrieved-card report, target signature, candidate lineage, pilot preregistration, and
evidence hashes with the strategy artifacts.
