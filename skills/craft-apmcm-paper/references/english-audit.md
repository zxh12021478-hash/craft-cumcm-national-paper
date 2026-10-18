# English manuscript and scientific audit

## Draft from evidence, not from a translated promise

Use `assets/paper-template.md` as a working outline, not an official form. Do not invent missing values to fill it. Structure a summary around the task, the mechanism used, direct quantitative answers, validation, and a scope-qualified recommendation. Write it after results freeze. Preserve every task's answer; do not use space for a catalogue of algorithms.

Maintain a terminology sheet with symbol, English term, definition, unit, and role. For HVAC examples use `terminology.md`; use `polishing-examples.md` for six synthetic checks that a language edit preserves evidence. These are illustrative references, not a universal vocabulary blacklist. Check dimensional consistency before editing sentences. Distinguish mass fraction from relative humidity; electrical input from thermal capacity; volume flow from velocity; percent from percentage points; calibrated parameters from assumptions. Unit conversions belong in reproducible code.

## Four connected passes

1. **Task closure:** read the original question and attachments; map each requested condition, interval, scenario, data source, drawing and output file to a result location. A visually polished partial answer is incomplete. Mark data collection that remains undone explicitly.
2. **Scientific claims:** trace each headline number to frozen machine output or a transparent derivation. Check feasibility, objective calculation, denominators, time indexing, initial and boundary conditions, solver status, and independent residuals. Reconcile constraints across tasks. If optimization uses a surrogate, state its validation and domain.
3. **English and visuals:** check equation symbols against prose; figure axes, legends, colorbars, units and caption numbers against source tables; abstract and conclusion against results. Read every rendered PDF page. Automated text matching cannot inspect text baked into an image. Review numerical precision and rounding; never replace 'up to' with 'on average' or 'best among candidates' with 'optimal'.
4. **Decision value:** assess baseline fairness, ablation, sensitivity and failure regimes. Explain why the recommended model or design is preferable given the evidence and uncertainty. Repair evidence first, then prose. Log unresolved issues and avoid asserting what was not reproduced.

## Cross-equation and experiment checks

For coupled models, trace the same conserved quantity across equations: state definitions, reference density, changing volume and boundary flux must agree. A small residual in each separate equation does not establish consistent coupling. Use a simple independent balance, such as the energy associated with one unit of transferred mass.

Bind each result to its run configuration: inputs, code hash, grid, time step, scenario and baseline. Compare ablations at the same configuration or quantify the difference separately. For asymmetric sensitivity, report deviations from the stated baseline in both directions; half the response range is not a worst-case departure from an off-center baseline. Single-factor sums are not a proven joint bound. A jointly refined space/time experiment does not isolate spatial order.

## Headline ledger

Use the format in `bundle-contract.md`. Include repeated summary/conclusion/table occurrences as separate entries when necessary. Each entry needs an exact quote, numeric token, JSON pointer into result output, tolerance, unit, and interpretation. Context must be reviewed: matching the number 32 somewhere in a paper is not evidence that the right cost was reported.

A local automated pass checks bound files and mapped numbers. A reviewer separately marks all headline claims as covered, figure captions/labels reviewed, all question outputs covered, and core physical/model semantics checked. These declarations are evidence records, not automatic proof.

## Revision discipline

Keep baseline paper/code/results immutable. Any model or parameter change invalidates dependent numeric claims, figure captions, summary and conclusions. Regenerate them, repeat independent checks, then redo English QA. Record which meaningful failures the revision fixed; don't equate a lower word count or prettier layout with stronger modeling.
