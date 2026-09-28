# Stage: abstract and writing-agent handoff

Read only the writing references required by the requested artifact: `references/writing-template.md`
for body/section repair, `references/paper-argument-spine.md` for reasoning structure,
`references/docx-output-spec.md` for DOCX delivery, `references/visualization-standards.md` for figure
work, and `references/ai-and-competition-compliance.md` for live/final disclosure. For a complete-
Markdown abstract-only request, read `references/abstract-reconstruction-protocol.md` and, only after
the full-paper evidence pass, `references/abstract-writing-decisions-2016-2025.md`.

## Responsibility split

The separate writing agent owns the first draft of the full body. This skill owns the evidence
packet, the complete result-frozen abstract, and later audit/repair. Do not independently draft the
full body unless the user gives a task-specific override.

Before the first draft, provide only the single recommendation outline defined by the fixed role
boundary. The evidence packet below belongs to a later evidence-frozen repair or reconciliation
handoff; it is not an additional pre-draft deliverable.

Give the writer, at minimum: the argument spine; approved assumptions and notation; canonical
result ledger; required equations; figure/table files and intended claims; validation and
uncertainty evidence; limitations; verified citations; AI-provenance markers; and a section coverage
map. Mark every unresolved item instead of filling it with plausible prose.

## Abstract order and gates

Use these gates:

1. **W0 reasoning ready:** problem and model contracts are team-approved; assumption, notation, and argument-spine ledgers exist.
2. **W1 evidence frozen:** code regenerates canonical figures, tables, and the result ledger; the team accepts headline results.
3. **W2 summary covered:** every required subproblem has a row in the abstract coverage matrix with a direct answer and validation evidence.
4. **W3 submission signed:** title, abstract, body, conclusion, citations, AI markers, and final rendered file pass team sign-off.

Work in this order: ledgers, figures/tables, writer evidence packet, body draft by the writing agent,
technical reconciliation, abstract, then title. Do not write a submission-style abstract or title
before W1. Before W1, provide only a short reasoning outline or coverage matrix grounded in supplied
facts; do not create a long fill-in-the-blanks pseudo-abstract.

Before final prose for problem analysis, model construction, innovation, result interpretation, or limitations, obtain team-authored reasoning bullets or explicit approval of the reasoning outline. If absent, produce a clearly labeled candidate draft and keep the decision gate open.

## Abstract acceptance test

Require every substantive sentence to perform at least one of five jobs: state the problem lens,
name a justified modeling action, give a direct result, state validation/uncertainty evidence, or
explain decision value. Across the whole abstract require all five.

- Cover every requested subproblem with `action → method/mechanism → canonical answer`; merge only
  when the subproblems are genuinely coupled.
- State the primary innovation as `baseline limitation → structural change → measured consequence`,
  not as a list of model names.
- Include at least one independent validation or robustness result and any limitation that changes
  how a headline number may be used.
- Copy all numbers, units, directions, and qualifiers from the frozen result ledger; never calculate
  or round them inside prose.
- Remove background padding, software narration, unsupported adjectives, generic transitions, and
  claims such as “效果良好” without a metric.
- End with three to five discriminative keywords. Select the title after the abstract is frozen.
- Fit the current official first-page limit after rendering. “Perfect” means complete, precise,
  evidence-dense, readable, and compliant—not ornate or guaranteed to win.

## Complete-Markdown abstract-only mode

Do not treat this as ordinary polishing. Read the complete paper and populate the abstract-fact
candidate pool before judging the old abstract. Require a body locator for every selected fact, then
rank supported candidates S/A/B/C and audit S/A omissions, distortions, unsupported old claims,
number/unit/scenario mismatches, method inventories, and wasted space. Draft from the selected pool;
do not let the old abstract constrain the reconstruction.

When the user requires the rest of the Markdown to remain unchanged, use
`scripts/abstract_guard.py replace` and independently run `scripts/abstract_guard.py verify`.
Require a passing report showing that the abstract heading, keywords, and all content outside the
abstract body are byte-identical. Fail closed on ambiguous headings or keyword boundaries. The
preservation report proves edit scope only; W1/W2 and evidence reconciliation prove factual quality.

## Body review requirements

- Make the abstract answer every subproblem with methods, principal numerical results, validation, and the central innovation.
- Select the title only after results are frozen. Prefer the research object, decision, or central mechanism over a laundry list of model names; never force a `基于X的Y研究` formula.
- Keep problem restatement short and non-derivative.
- Align notation across equations, tables, code, and text.
- Record every material assumption with its rationale, mathematical consequence, test, and failure impact.
- Record every symbol with meaning, unit or dimension, domain or index, first definition, and code mapping when applicable.
- Explain why each model is used before presenting formulas.
- Separate model construction from numerical results.
- Place decisive figures near the corresponding argument.
- Quantify model strengths and limitations.
- Use references for external facts, data, and borrowed methods.
- Avoid unsupported superlatives, canned transitions, and generic AI prose.
- Replace generic language with mechanism, quantities, evidence, and implications. Never shuffle wording merely to conceal AI involvement.
- Verify every AI-suggested reference against the primary source before citing it.
- Choose paragraphs, lists, equations, or tables according to information structure. Do not impose a blanket “no bullet points” rule.

## Final consistency pass

Complete `assets/templates/论文论证台账模板.md`. Check every canonical value in abstract, body, tables, figures, conclusion, and files. Verify the rendered abstract fits the current official page limit, then obtain team sign-off on the title, abstract, limitations, and final paper before running the document and submission validators.
