# Abstract-writing decisions distilled from the 2016--2025 local corpus

Use this reference only after the complete-paper evidence pass in
`references/abstract-reconstruction-protocol.md`. It is a decision prior for selecting, ordering,
compressing, and presenting facts. It is never a source of facts, wording, model choices, or
results for the user's paper, and it must not influence the pre-draft `推荐解题思路大纲`.

## Provenance and claim boundary

- Corpus: 134 unique PDFs from the user-provided 2016--2025 CUMCM excellent/displayed-paper
  collection: 15, 18, 13, 17, 17, 17, 11, 5, 16, and 5 papers by year respectively.
- Extraction: 46 abstracts from usable text layers and 88 by page rendering plus macOS Vision OCR.
- Review: every extracted abstract was read as a complete semantic unit before this synthesis.
- Integrity: the text-free paper-level ledger is
  `assets/benchmarks/abstract-corpus-provenance-2016-2025.json`; it records source paths, container
  and PDF hashes, abstract hashes, extraction method, derived features, and review status. It stores
  no abstract text.
- Award boundary: local filenames, folders, and public-display status do not independently prove a
  national first-prize grade. Treat this as an excellent/displayed-paper corpus, not an exhaustive or
  award-verified set of national first-prize papers.
- OCR boundary: OCR can corrupt symbols, punctuation, and digits. Corpus-level writing decisions
  were read semantically; no OCR-derived number or equation may be reused as a factual exemplar.

Deterministic corpus descriptors are context, not targets: 92.5% use explicit question-oriented
structure, 89.6% contain at least one number with a nearby unit or count marker, 65.7% mention some
form of validation, uncertainty, error, or sensitivity, while 42.5% narrate software use and 25.4%
point readers to body tables, figures, appendices, or result files. The median extracted Chinese-
character count is 884, but formatting and OCR vary; do not infer an ideal word count from it.

## Central synthesis

The most useful abstracts minimize the evaluator's retrieval cost. They let a reader recover, for
every required subproblem:

`what was decided -> what structural idea made it solvable -> what the answer was -> why to trust it`

Model names, numerical density, and polished adjectives do not substitute for this chain. Strong
abstracts expose the problem mechanism and direct answer; weaker examples often spend the same
space on software, chronology, long value vectors, or generic evaluation.

## Selection decisions

Apply these decisions after support status and S/A/B/C value have been assigned.

1. **Select answers before methods.** Reserve space first for every required direct answer, including
   the scenario, unit, direction, and material qualifier. A method without the answer it produced is
   normally incomplete.
2. **Select the operative mechanism, not a method inventory.** Keep the physical balance, geometric
   relation, state transition, dependence structure, decision tradeoff, or information bottleneck
   that explains why the method fits. Omit routine implementation details and most solver names.
3. **Use numerical hierarchy.** Prefer a decision value, optimum, threshold, interval, ranking,
   improvement against a baseline, or uncertainty bound. Compress or omit long coordinate lists,
   schedules, class labels, and parameter vectors that belong in a table or supporting file.
4. **Keep evidence adjacent to the claim it qualifies.** A validation metric, independent route,
   holdout result, error band, sensitivity boundary, or comparator belongs next to the headline
   result whenever possible. A detached final sentence saying the model is reliable adds little.
5. **Describe innovation by consequence.** Use
   `specific baseline deficiency -> structural change -> verified consequence`. Do not promote a
   renamed routine, a model stack, or an optimizer substitution as innovation.
6. **Prefer decision consequences over paper navigation.** Replace “see Table X” or “results are in
   the attachment” with the smallest decisive conclusion that the body supports. Use a body pointer
   only when the requested output is inherently too large for the abstract.
7. **Include limitations selectively.** State a limitation or operating boundary when it changes the
   interpretation, feasibility, transfer, or safety of a headline answer. Do not append a generic
   strengths-and-weaknesses paragraph.
8. **Do not fill space.** Background, tool narration, boilerplate conclusions, and generic praise are
   C candidates even when they occur frequently in the corpus. The controlling constraint is the
   current rendered-page rule, not a fixed number of words or a requirement to fill the page.

## Ordering and compression decisions

- Open with the research object and the central mathematical perspective in one compact move. Use
  background only if it changes the reader's understanding of the decision problem.
- Default to dependency order: establish data or mechanism, then inference or prediction, then
  optimization or decision. Prompt order is secondary when it obscures the actual dependency chain.
- Use one functional unit per subproblem as a default:
  `action + fitting mechanism + direct result + credibility/implication`. Merge coupled subproblems
  only when they genuinely share the same evidence chain.
- Give the central contribution more space than routine subproblems. Equal paragraph length is not
  a quality criterion.
- Report only precision justified by the body and frozen result ledger. Do not transfer all printed
  decimal places merely because an optimizer emitted them.
- Close on the final decision, verified gain, applicable boundary, or main reliability result. Avoid
  a generic “the model is practical and can be widely promoted” ending.

## Task-family emphasis

These are emphasis choices, not templates.

- **Mechanism and measurement:** preserve governing mechanism, identifiable parameters, direct
  estimates, and an analytical/numerical or measured/model cross-check. Mention an approximation
  boundary if it limits use.
- **Forecasting and classification:** state the prediction target and horizon or class target,
  leakage-safe evaluation split, decisive out-of-sample metric, uncertainty or calibration where
  available, and the resulting operational decision. Training accuracy alone is not headline proof.
- **Optimization and scheduling:** state the objective and decisive constraints in plain language,
  give the feasible policy or optimum and baseline tradeoff, and report robustness or feasibility
  evidence. Do not dump full schedules into prose.
- **Data analysis and evaluation:** state the exact object being compared or ranked, the structural
  reason for the indicator or transformation, the main ordering or driver, and stability evidence.
  A familiar weighting method is not itself a contribution.
- **Sequential, network, and spatial problems:** surface state dependence, geometry, or information
  flow, then report the policy/path/threshold and performance or error boundary.

## Corpus-derived anti-patterns

Do not imitate these merely because they occur in selected papers:

- lengthy social or industry background before the actual task;
- lists of MATLAB, SPSS, Excel, Python, CAD, libraries, functions, or file names;
- equation dumps, complete routes, coordinate vectors, class-label tables, or full parameter lists;
- high-precision outputs with no unit, scenario, uncertainty, or decision meaning;
- “good fit,” “reasonable,” “robust,” “innovative,” or “widely applicable” without a measured test;
- validation performed only on the training data or described without a metric;
- filling missing evidence with random values, convenient priors, invented data, or undocumented
  assumptions;
- fixed closing paragraphs on advantages, limitations, and promotion that add no decision value;
- citations or references to body locations instead of an independently readable answer;
- model stacking or algorithm renaming presented as novelty.

## Reconstruction procedure using this knowledge

1. Complete the full-paper fact pool and original-abstract loss audit without consulting this
   reference for paper facts.
2. Freeze all verified S facts and select A facts that explain or qualify them.
3. Use this reference to break ties among supported facts: prefer direct answer, mechanism,
   discriminative evidence, uncertainty, and decision value over chronology and ornament.
4. Draft a claim map before prose. Each planned sentence must cite candidate IDs and have one
   primary function.
5. Draft anew, then run two deletion passes: remove unsupported claims first; remove low-value
   narration and duplicated conclusions second.
6. Reconcile every value and qualifier with the body and result ledger, render against the current
   first-page constraint, and use `scripts/abstract_guard.py` when only the Markdown abstract may
   change.

## Final decision audit

The abstract fails if any answer is “yes”:

- Is a required subproblem represented only by a model name or paper pointer?
- Does a number lack its unit, scenario, denominator, direction, or material qualifier?
- Is the claimed innovation missing a concrete baseline deficiency or verified consequence?
- Is confidence implied by adjectives rather than comparison, error, uncertainty, or an independent
  check?
- Does any sentence introduce a fact that cannot be located in the user's complete paper?
- Could deleting software narration, generic background, or boilerplate free space for a direct
  answer?
- Was length, paragraph count, bolding, or page filling treated as a substitute for evidence?

