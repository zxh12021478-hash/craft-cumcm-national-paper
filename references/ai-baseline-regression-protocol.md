# AI baseline regression and takeover protocol

Use this protocol when another system returns a polished paper, code bundle, figures, or numerical
results. Treat a capable external agent as a valuable collaborator and use its calibrated quality as
a prior. Appearance or model reputation alone is not evidence that the governing model or numbers
are correct.

## Scoped provisional confidence

Assign one intake tier before detailed review:

- `high`: strong calibrated prior, complete coherent bundle, explicit uncertainties, clean static
  scan, and no unexplained result gaps;
- `standard`: capable source but incomplete calibration, ordinary documentation, or minor unresolved
  handoff gaps;
- `low`: missing provenance or inputs, unexplained contradictions, unverifiable citations, hard-coded
  answers, contradictory artifacts, or prior failed reproduction.

Model identity may inform the prior but cannot determine the tier by itself. Use the tier to allocate
effort: retain and lightly reconcile low-risk prose, formatting, and organization from a
high-confidence bundle; sample-check ordinary transformations; deeply verify formulation, official
input mapping, headline numbers, feasibility, innovation evidence, citations, and final conclusions
regardless of tier. Raise confidence after successful reproduction and independent checks; lower it
immediately when a material contradiction appears. `Quarantined` means the received version is
preserved and not yet evidence-qualified, not that its author is presumed incompetent.

## Intake classes

Classify the received package before scoring:

- `paper-only`: manuscript without executable source and machine-readable outputs;
- `partial-bundle`: some code or results are present, but the entry command, dependencies, inputs, or required outputs are missing;
- `full-bundle`: original paper source, code, inputs, dependency lock, one entry command,
  machine-readable outputs, figures, interaction log, and known limitations are present.

`paper-only` permits a paper-layer audit only. It cannot receive an end-to-end reproducibility verdict. Do not reconstruct source code from a printed appendix and then describe the reconstructed program as the original implementation.

## Evidence states

Use exactly one state:

1. `quarantined`: received and hashed, with a provisional confidence tier but not yet evidence-qualified;
2. `audit-only`: prose, equations, layout, and static code were inspected;
3. `partial-reproduction`: some outputs were regenerated, but not every headline result and required official file;
4. `end-to-end-reproduction`: a clean copied-directory run regenerated all contracted outputs;
5. `implemented-takeover`: the team-approved revised formulation, code, results, paper, and disclosures were rebuilt and passed the final gates.

Appearance, internal assertions, or a code listing in a PDF cannot advance the evidence state.

## First-hour triage

1. Hash and preserve the original bundle.
2. Record tool, model/version, generation time, competition context, and key interaction log.
3. Determine whether the artifact is live-period authentic or retrospective. Never use a post-competition source as evidence that a historical paper could have been written during the original contest.
4. Run page, anonymity, attachment, citation, secret, and static code scans.
5. Extract all abstract and conclusion claims into a result ledger.
6. Compare the implemented formulation with the earlier recommendation to understand what the
   writing agent retained, improved, or replaced; a difference is not a defect by itself.
7. Stop prose polishing if any of these are absent: correct problem coverage, runnable entry point, required input files, or a coherent governing formulation.

## Five human gates

Only people may approve:

1. `problem_reconciliation`: exact prompt, attachments, output ranges, units, and ambiguities;
2. `model_selection`: interpretation, assumptions, objectives, constraints, route, innovation hypothesis, and validation thresholds;
3. `modeling_route_review`: the writing agent's actual assumptions, objectives, constraints,
   innovation, and rationale, regardless of whether they match the earlier recommendation;
4. `result_acceptance`: headline values after passing clean reproduction and independent truth checks;
5. `final_submission`: the exact rendered paper/supporting package after the strict report passes.

Use `scripts/cumcm_workflow.py` to record these gates. AI identities, missing evidence files, failed reproduction, or failed truth reports must not be accepted as approvals.

## Layered audit

Keep separate scores and verdicts for:

- eligibility and current format;
- problem interpretation and model semantics;
- code execution and artifact reproduction;
- independent truth and uncertainty;
- writing and visualization;
- provenance, citations, AI disclosure, and team understanding.

Report a raw paper-layer score and then apply hard caps from `national-award-rubric.md`. Never average a reproducibility blocker away with strong typography or sophisticated formulas.

## Independent truth matrix

At least one required check must avoid merely calling the same main implementation:

| Family | Minimum independent checks |
|---|---|
| Optimization | constraint residuals plus reduced exact enumeration, bound/gap, or independent policy recomputation |
| Dynamics/simulation | conservation or invariant plus time-step convergence and special-case recovery |
| Geometry | distance/rigidity invariant plus coordinate round-trip, analytic special case, or independent collision construction |
| Prediction/classification | split/leakage integrity plus baseline improvement, calibration/coverage, and subgroup/temporal robustness |

Use `scripts/truth_harness.py` for the generic checks and add a problem-specific verifier when the headline result needs stronger evidence.

Solver agreement is weak evidence if both solvers share the same geometry, objective, data transformation, or incorrect formula. State what is actually independent.

## Compression to the current paper budget

Build a page budget before rewriting:

- retain the direct-answer chain, defining equations, one transparent baseline, the key structural insight, decisive comparison, validation, uncertainty, and decision interpretation;
- move repetitive derivations, full parameter sweeps, complete constraint tables, logs, and code into allowed supporting material;
- delete duplicated flowcharts, repeated prose explanations, decorative charts, and validations that do not test a distinct failure mode;
- never solve page overflow by making code, captions, axes, or equations unreadably small.

The one-page abstract must contain only verified ledger values. Write the title and abstract after the result ledger and argument spine are frozen.

## Stop conditions

Return to a team decision gate when:

- the external system changed an assumption, objective, constraint, information timeline, or requested output;
- a headline value cannot be regenerated;
- an independent truth check fails;
- the innovation disappears under a fair ablation;
- the central theorem applies only after silently fixing a freedom allowed by the prompt;
- a citation cannot be verified or lies outside the live competition evidence cutoff;
- the final rendered artifact differs from the visually reviewed hash.
