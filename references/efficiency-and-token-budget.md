# Contest efficiency and token budget

## Governing metric

Maximize verified national-first competitiveness gained per contest minute and per Codex token,
subject to non-negotiable eligibility, task-correctness, mathematical-validity, reproduction, and
independent-validation floors. Measure saved tokens only when the same decision quality is retained;
omitted verification is not efficiency.

## Mode selection

### `sprint`

Use for initial bundle triage, a narrow question, unchanged evidence, small prose/layout changes, or
deadline-driven P0/P1 closure. Perform the cheapest decisive checks first. Chat target: no more than
five findings and roughly 1,800 Chinese characters, excluding unavoidable code/error excerpts.
Store longer evidence in a report. Stop immediately on a Blocker that makes downstream polish moot.

### `standard`

Use for the official problem's recommendation outline, the first viable complete Claude bundle, or
changes to task interpretation, data construction, formulation, solver, main innovation, or headline
results. Complete the required stage evidence, but keep chat to verdict, score/gates, highest-ROI
repairs, and the next decision. Detailed ledgers remain files. Default chat target: roughly 3,500
Chinese characters; exceed only when the user explicitly requests the full report in chat or a
critical ambiguity cannot be compressed safely.

### `final`

Use once results are frozen or the user asks whether the package is ready to submit. Run every strict
gate and render every page. Do not repeat raw validator logs in chat. Default final summary target:
roughly 2,500 Chinese characters plus links to final artifacts and unresolved blockers.

## Progressive work ladder

1. **Inventory and delta:** hash the baseline and current bundle. If unchanged, reuse verified state.
2. **Gate scan:** task coverage, required outputs, code entry point, headline contradictions,
   eligibility, and obvious leakage/feasibility failures.
3. **Risk-ranked verification:** verify formulation, transformations, headline values, innovation,
   citations, and conclusions before low-risk prose.
4. **Independent truth:** recompute the decisive objective, constraint, identity, metric, or special
   case without trusting the main solver's success flags.
5. **Presentation and final gates:** only after factual closure.

Do not execute a later rung when an unresolved earlier Blocker makes it valueless. Resume at the
earliest failed rung after repair.

## Loading policy

- Load `SKILL.md`, `manifest.yaml`, `static/runtime-core.md`, one active stage fragment, and only its
  necessary references.
- A stage may name several conditional references. Read only those whose condition is present in the
  supplied artifacts or requested deliverable.
- Load one primary and at most one supporting task-family file after the family decision is frozen.
- Do not load historical papers, sample casebooks, abstract decisions, compliance details, document
  internals, or red-team-full guidance before their routed stage.
- Within one logical task, do not reread unchanged instruction resources or user artifacts merely to
  restate them. Use hashes, summaries, and saved ledgers.
- Run deterministic scripts without opening their source unless execution fails or a patch is needed.

## Innovation budget

Cheaply score at least eight problem-anchored structural hypotheses across four families when a
standard strategy is being frozen. Use scripts or a compact ledger rather than narrating every
candidate. Pilot the top candidates only when the result can change the recommended direction.
`sprint` may perform screening and return a provisional direction, but it cannot claim the innovation
is frozen. A submission-level innovation freeze still follows `references/innovation-tournament.md`
and its hash-bound evidence requirements.

## Review budget

- Use `red-team-fast` for intake, intermediate revisions, and small deltas.
- Use `red-team-full` for the first viable complete bundle, a material core change, or the final
  national-selection decision—not after every cosmetic edit.
- After a confirmed revision, run `scripts/plan_incremental_audit.py`. Review the changed files and
  dependency closure; rerun the full audit only when the report says `full` or the user requests it.
- Keep at most five P0/P1 items active at once. Queue P2/P3 without expanding them until P0/P1 close.
- Report only the minimum evidence necessary to justify each finding; do not repeat the same defect
  under multiple reviewer personas.

## Escalation triggers

Ignore the soft token budget and escalate when any of these occurs: wrong or ambiguous task object;
missing official artifact; changed data or preprocessing; changed objective, constraint, assumption,
information timeline, solver, or main metric; unreproduced headline result; independent-check failure;
innovation lost under ablation; citation or AI-disclosure uncertainty; current official-rule change;
or final-submission request.

## Measurement

Before and after an efficiency refactor, run `scripts/measure_instruction_budget.py --strict` and
record route word/byte counts. For real runs, record elapsed minutes, input/output token counts when
available, number of human interventions, artifacts loaded, scripts executed, and whether any quality
gate regressed. Lower token use without equal or better gate outcomes is a failure.
