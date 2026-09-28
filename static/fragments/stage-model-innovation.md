# Stage: model innovation

Read `references/innovation-patterns.md`, `references/innovation-tournament.md`, and
`references/human-led-ai-collaboration.md`. Also read
`references/cross-case-transfer-protocol.md` before generating candidates.
For live problem solving or ordinary post-freeze comparison, also read
`references/official-sample-casebook.md` and only the relevant sections of
`references/official-sample-index.yaml`. Never load either sample reference before a historical
benchmark strategy has been frozen and its isolation ledger has passed.

## Innovation search order

1. Freeze a target signature and retrieve three to five diverse cross-case structural cards.
2. Reframe the requested output around the true decision or mechanism.
3. Prove a structural property that removes variables, cases, or computations.
4. Identify a model-regime boundary or identifiability condition.
5. Couple uncertainty to the final decision rather than adding post-hoc sensitivity.
6. Add value-of-information or optimal-data-collection analysis.
7. Design a problem-specific solver that exploits structure.
8. Add an independent validation or optimality certificate.

## Claim template

For every proposed innovation state:

- baseline limitation;
- exact modification;
- mathematical or domain rationale;
- measurable consequence;
- evidence test;
- failure condition;
- one-sentence claim suitable for the abstract.

Before strategy freeze, generate at least eight falsifiable candidates across at least four families,
rank them, and run hash-bound independent micro-experiments on the top three with
`scripts/innovation_tournament.py`. Select one primary innovation and at most two supporting
innovations from those tested candidates. One deep verified innovation outranks several shallow
additions.
Record cross-case lineage, but never count a borrowed move as novelty. The innovation claim begins
at the target-specific reconstruction and its measured consequence.
Mark proposed innovations as `AI-proposed` until the team supplies or approves the problem-specific mechanism and the controlled evidence test.
The selector weights are decision-support defaults, not empirically calibrated evidence, until the
blind-test ledger clears `references/innovation-tournament.md`.
