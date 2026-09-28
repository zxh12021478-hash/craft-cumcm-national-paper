# Two-system baseline handoff

Read this file with `references/ai-baseline-regression-protocol.md` when the team first asks Codex for the full strategy, when another AI system generates an overnight baseline, and when Codex takes over revision.

## Writing-agent division of labor

The writing agent owns the initial full-body prose. This skill owns innovation design, technical
artifacts, the frozen-result abstract, adversarial review, targeted repair, and final packaging.
Before the writer starts, hand off one consolidated, non-binding `推荐解题思路大纲` in Word,
Markdown, or text format. This is the only generated pre-draft deliverable. The writing agent owns
the final model choice, derivation, algorithms, computation, code, results, and complete first
draft. After the draft returns, evaluate its actual logic and evidence; do not penalize it merely
for choosing a direction different from the recommendation. Reject invented results, softened
limitations, unverified citations, and unsupported innovation language. Do not solve a weak draft by
silently authoring a different full paper; issue precise replacements or return a repair brief to
the writer, then package only the reconciled version.

## Phase A — strategy before generation

Export exactly one generated handoff document, preferably `推荐解题思路大纲.md` and optionally
`.docx` or `.txt`. The official problem and data attachments may accompany it; do not count those
source files as generated handoff documents. The document contains:

1. the problem's central tension and the relationship among subproblems;
2. one preferred overall direction and why it appears promising;
3. conceptual model or mechanism suggestions for each subproblem;
4. one primary and at most two supporting innovation ideas;
5. important validation directions, risks, and a brief fallback;
6. two substantial, problem-specific writer-facing instruction blocks covering task-adapted
   modeling/visualization and truth/validation/paper quality;
7. the central paper story the writing agent may emphasize;
8. an explicit statement that every recommendation is advisory and may be revised or rejected.
9. a short attachment-exception and operative-unit note: identify missing/truncated/singleton groups,
   ambiguous point-versus-edge/region/window semantics, and the exact question the writer must resolve.
10. an immediately executable transparent baseline and a fallback path that still answers every
    subproblem if the higher-risk innovation does not survive its pilot.

The outline should make a clear recommendation without attempting to settle the detailed model.
Do not include full equations, computation steps, pseudocode, code, parameter settings, result
contracts, or prohibited changes. The writing agent may use a different route; the team reviews and
approves the eventual core decisions.

### Two required problem-specific instruction blocks

Use `assets/templates/推荐解题思路大纲模板.md`. Near the end of the single outline, include exactly
two substantial numbered blocks addressed to the writing agent. They should have the directive
strength and detail of an expert competition brief, but every sentence must be reconstructed from
the actual problem, attachment structure, subproblem roles, and recommended route. They are not
generic boilerplate and not a hidden solver contract.

1. **`题型适配、模型主线与高价值可视化建议`** starts by classifying the actual task and
   explaining the evidence for that classification. It then maps each useful mechanism, principle,
   geometry, system-operation, or information-flow schematic to the subproblem it clarifies. It
   recommends problem-specific data and result views—such as distribution and anomaly diagnostics,
   temporal or spatial structure, change points, residuals, uncertainty, baseline comparison,
   feasible regions, tradeoffs, policy boundaries, or state evolution—and states the question each
   view must answer. A three-dimensional figure is optional and is recommended only when three
   genuine spatial, state, or parameter dimensions are simultaneously meaningful. “Advanced” means
   accurate encoding, coherent hierarchy, legibility, and decision value, not decoration or volume.
2. **`求解真实性、验证闭环与成文质量建议`** instructs the writer to use only real problem data,
   traceable parameters, and reproducible results; explain the decisive derivation and answer for
   every subproblem; and compare models with a transparent baseline, fair data or scenario controls,
   and a common metric. It identifies which assumption, parameter, stochastic event, or extrapolation
   requires sensitivity, robustness, ablation, uncertainty propagation, or independent validation.
   Recommend simulation and key-frame, trajectory, state-surface, or complementary 2D/3D displays
   only when the actual system evolves in time, space, iteration, or randomness. It also sets
   task-responsive expectations for readable figures, implementation-faithful flowcharts, concise
   reproducibility-oriented appendices, and a later evidence-dense abstract without inventing
   results before they exist.

Both blocks must be more specific than the generic example: they name the relevant subproblems,
variables or relationships, evidence questions, and failure risks. They remain conceptual and may
tell the writer what the complete draft should demonstrate, but they do not contain the actual
complete equations, calculation sequence, pseudocode, code, parameter settings, or fabricated
answers.

Before handoff, scan every attachment rather than extrapolating from its first rows. Surface any
entity whose data shape prevents the default route from running, and distinguish the actual unit of
service or measurement (for example node versus road segment, point estimate versus event window).
These are strategy decisions, not cleanup details. Pair an ambitious uncertainty, control, or
mechanism extension with a transparent baseline the writer can execute first and keep if the
extension proves too costly or has no decision effect.

Do not prescribe a number of 3D figures, chart types, flowcharts, pseudocode blocks, simulations, or
appendix pages. Do not require the abstract to fill a page or require boldface as a proxy for
information density. The pre-draft outline still contains no pseudocode, code, parameters, or exact
calculation steps. All presentation suggestions are advisory; the writing agent may improve,
replace, or omit them when its final model and evidence justify a different choice.

## Phase B — overnight external baseline

Treat the external system as a capable collaborator and preserve its output as a versioned intake.
Assign scoped provisional confidence using `ai-baseline-regression-protocol.md`; a strong calibrated
model and a complete, coherent bundle justify greater reuse and less repetitive low-risk review.
When available, record the interaction log, exact tool/model version, dependency declaration, entry
point, results, and known failures. Do not require the returned work to match the recommendation;
evaluate any different direction on its merits.

Do not ask the external system to invent references. Any references it suggests remain leads until a team member verifies the primary source.

Keep the problem and all generated material private. Do not publish, discuss, or upload competition content to public repositories or public discussion spaces during the contest.

## Phase C — quarantine gate

Inventory the returned bundle with `scripts/cumcm_workflow.py ingest-baseline`. Run `scripts/preflight_environment.py --profile takeover`, then `scripts/audit_external_handoff.py`. The final gate requires a single Python environment containing the pinned packages in `scripts/requirements-validator.txt`; create and test that environment before the contest rather than installing dependencies under deadline. Then:

Quarantine here is an immutable-original and reproducibility boundary, not a blanket distrust
judgment. Use the provisional confidence tier to concentrate effort on high-consequence claims while
preserving strong work.

- compare the chosen formulation with the earlier recommendation only to understand the reasoning,
  not to enforce conformity;
- send material core choices to the team for eventual approval;
- run static code QA and a clean execution in an isolated copy;
- run separate verification commands and `scripts/truth_harness.py` before trusting output;
- create the canonical result ledger and reconcile every headline number;
- verify citations from primary sources;
- score the baseline using the national-award rubric.

Until these checks pass, do not reuse the baseline abstract, conclusions, innovation claims, or numerical recommendations as facts.

## Three-day takeover

Use `scripts/competition_scheduler.py --profile takeover` against the real deadline.

- First third: forensic intake, clean run, model correction, and complete baseline coverage.
- Middle third: problem-specific innovation, comparator, ablation, sensitivity, uncertainty propagation, and result freeze.
- Final third: rebuild the argument spine and paper, render every page, red-team the work, audit team comprehension, verify AI disclosure, and rehearse upload.

Any change to data processing, assumptions, formulae, parameters, or solver invalidates downstream result, figure, abstract, conclusion, and validation approvals until rerun.

## AI disclosure

Record both systems separately in the PDF and `AI工具使用详情内部清单.json`: tool, exact version, provider, time, purpose, important prompts and responses, adopted material, rejected material, human modification, verification evidence, affected paper/code locations, and team sign-off. Never describe an externally generated model as independently developed by the team unless the team actually reconstructed, justified, approved, and verified it.
