# Evidence-anchored abstract reconstruction

Use this protocol when the user supplies a complete Markdown CUMCM paper and asks to rewrite,
reconstruct, complete, or intensify only its abstract. This is a full-paper evidence synthesis task,
not an abstract-only language-polishing task.

After completing the full-paper evidence pass, read
`references/abstract-writing-decisions-2016-2025.md`. Its corpus-derived rules guide only selection,
ordering, compression, and presentation. They do not supply facts for the paper and do not influence
the separate pre-draft recommendation-outline route.

## Scope and truth boundary

- Treat the supplied paper as the only source from which the revised abstract may acquire facts.
  Problem statements, code, data, and ledgers may verify a paper claim, but they do not authorize a
  new abstract claim that the body does not support. Repair the body first under the confirmed-
  revision workflow if a verified fact must be added.
- Read the complete paper, including problem analysis, data and preprocessing, model construction,
  solution, results, validation, evaluation or limitations, and conclusion. Record absent or
  truncated sections. Do not call the output a full-paper reconstruction when the full paper was not
  available.
- Treat the original abstract as a fallible index, not as a factual authority or a ceiling on the
  reconstruction. Preserve a fact only after locating its body evidence.
- Historical papers may guide information selection, ordering, compression, and presentation only.
  Never import their problem facts, wording, equations, numerical results, or novelty claims.
- The user-provided 2016--2025 local collection has a paper-level, text-free provenance ledger at
  `assets/benchmarks/abstract-corpus-provenance-2016-2025.json` and a frozen v20 semantic synthesis.
  That establishes review coverage for this local 134-paper collection only. It does not establish
  that the collection is exhaustive or that every paper won a national first prize. Official sample
  and award-evidence records remain separate sources for any award-status claim.

If the full paper is unavailable, provide an abstract-only diagnosis or a clearly labeled
provisional revision; do not imply that omitted facts, cross-section consistency, or complete
subproblem coverage were verified.

## Full-paper evidence pass

Read by logical section rather than searching only for model names or numbers. For every required
subproblem, collect candidate facts in the abstract-fact pool of
`assets/templates/论文论证台账模板.md`. Each candidate needs:

- a candidate ID and subproblem;
- one atomic fact or claim;
- its function: problem lens, modeling action, mechanism, direct result, validation, uncertainty,
  innovation consequence, limitation, or decision value;
- a precise body locator such as heading plus paragraph, equation, table, or figure identifier;
- any result-ledger ID, value, unit, direction, uncertainty, scope, and qualifier;
- support state: `verified`, `body-supported`, `ambiguous`, `contradicted`, or `unsupported`;
- original-abstract coverage and final selection decision.

Split compound sentences into atomic candidates when different parts have different evidence.
Never repair an ambiguous value through plausible inference. Resolve it from the frozen result
ledger and generating evidence or omit it and report the conflict.

## S/A/B/C value ordering

Assign value only after support is established. The labels rank contribution to a one-page abstract;
they do not rank the scientific importance of an entire paper and have no fixed quota.

- **S -- indispensable answer:** a required subproblem's direct answer; a headline value, threshold,
  ordering, policy, or feasible range; the central structural innovation with a measured
  consequence; or a limitation that materially changes how the main result may be used.
- **A -- strong explanatory evidence:** the main mechanism and why it fits, independent validation
  or robustness evidence, decision-relevant uncertainty or boundary, and the consequence that makes
  an innovation more than a renamed method.
- **B -- conditional support:** a preprocessing, estimator, solver, secondary metric, or comparison
  detail that materially improves credibility or distinguishes otherwise similar claims.
- **C -- normally omit:** generic background, software narration, routine operations, model-name
  inventory, repeated conclusions, unsupported praise, and detail that consumes space without
  changing the answer or its credibility.

Do not select a lower-supported S candidate over a verified A candidate merely because the intended
claim sounds more important. Evidence status is the first gate; value is the second.

## Original-abstract loss audit

Map every S and A candidate to the original abstract and mark it `complete`, `partial`, `missing`,
`distorted`, or `not-applicable`. Separately flag:

- claims present in the abstract but unsupported by the body;
- number, sign, order, unit, denominator, scenario, or precision mismatches;
- methods named without the action they perform or the answer they produce;
- results stated without their decision implication or material uncertainty;
- innovation adjectives without a baseline deficiency and measured consequence;
- redundant background, generic transitions, software steps, and duplicated conclusions.

Record the disposition of each issue. The audit is an internal selection instrument; do not dump it
into the replacement abstract unless the user asks for the audit report.

## Reconstruction decisions

Draft from the selected candidate pool, not by line-editing the old abstract.

1. Establish the concrete problem lens and central mathematical perspective quickly; keep background
   only when it changes how the modeling choices are understood.
2. Give every required subproblem a direct answer using the smallest readable unit of
   `action -> mechanism/method -> result -> implication`. Merge subproblems only when the body shows
   that they share one genuine inference or decision chain.
3. Integrate the main innovation where its consequence is reported:
   `baseline deficiency -> structural change -> measured consequence`. Do not create an isolated
   list of fashionable models.
4. Place validation or uncertainty beside the claim it qualifies when possible. Include a
   limitation when omitting it would make a headline answer misleading.
5. Allocate space by evidence value and dependency, not by equal paragraph length, equal treatment
   of model names, or a fixed character target. The rendered official page limit controls.
6. Use only precision, units, scenarios, and qualifiers copied from the frozen result ledger or
   body-supported evidence. Do no new arithmetic while drafting prose.
7. Apply the corpus-derived decisions only after the evidence selection is paper-complete. If a
   corpus preference conflicts with body truth, current rules, rendered readability, or a direct
   answer, the corpus preference loses.

Reject citations, background padding, software names, generic praise, decorative terminology,
unexplained abbreviations, method inventories, and claims that merely rename ordinary modeling
steps. Historical exemplars may inspire these decisions, never their phrasing.

## Pre-replacement acceptance gates

Do not label the reconstructed abstract final unless all are true:

1. the complete paper was read and every required subproblem is represented in the candidate pool;
2. every selected sentence is traceable to one or more body locators and all numbers reconcile with
   the frozen result ledger;
3. every required subproblem receives a direct answer, not only a method description;
4. the main innovation, validation, uncertainty, and decision implication are included when the body
   supports them, with no unsupported elevation;
5. contradictions and unsupported old-abstract claims are resolved or explicitly reported;
6. the team has accepted the headline facts and the final abstract fits the current rendered-page
   rule.

## Markdown preservation guard

When the user requests an otherwise unchanged Markdown paper, replace the abstract body with the
deterministic guard rather than manually rewriting the full file:

```bash
python scripts/abstract_guard.py replace \
  --source paper.md \
  --abstract revised-abstract.txt \
  --output paper.abstract-rebuilt.md \
  --report abstract-change-report.json
```

Then verify the delivered file independently:

```bash
python scripts/abstract_guard.py verify \
  --original paper.md \
  --revised paper.abstract-rebuilt.md \
  --report abstract-verification.json
```

The guard must fail closed if it cannot identify exactly one abstract heading followed by a keyword
marker. A passing report proves that the abstract heading, keywords, and every byte outside the
abstract body are unchanged; it does not prove that the new abstract is factually correct. Keep the
evidence audit and preservation report as separate checks.
