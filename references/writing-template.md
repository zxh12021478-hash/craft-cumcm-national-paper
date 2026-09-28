# CUMCM paper architecture

## Title

Choose the title after freezing the main results. Generate at least three candidates centered respectively on the research object, central mechanism, or decision value. Select the shortest accurate title that distinguishes the work without implying an unsupported innovation. A `基于X模型的Y问题研究` construction is optional, never mandatory.

## Abstract

Keep within the current official one-page requirement after verifying it. Include:

1. problem and central modeling perspective;
2. complete coverage of every subproblem with method, canonical result, and direct answer;
3. central innovation and its measured consequence;
4. validation and robustness evidence;
5. three to five precise keywords.

Avoid background padding, citations, unsupported adjectives, and vague “good results.”
Use precision supported by input quality and uncertainty; do not force every result to two decimal places.
Use one compact paragraph per subproblem as a default, not a rigid rule. Merge tightly coupled subproblems or split a dense one when clarity improves. Do not enforce a fixed word count when the controlling rule is a rendered-page limit.

Complete the abstract coverage matrix in `assets/templates/论文论证台账模板.md` before prose. Do not call an action an improvement, fusion, or construction merely by changing the verb; require the innovation evidence test.

For a full-Markdown abstract-only reconstruction, follow
`references/abstract-reconstruction-protocol.md`: build the body-located fact pool, perform the
S/A/B/C selection and old-abstract loss audit, then use the Markdown preservation guard. An
abstract-only input can be diagnosed or provisionally edited, but cannot support claims of complete
body coverage or cross-section factual consistency.

Use provenance-tracked samples only to learn abstract functions, never sentences. The user-provided
2016--2025 local collection has complete paper-level review coverage for its 134 unique PDFs, but it
is neither exhaustive nor award-verified; read
`references/abstract-writing-decisions-2016-2025.md` for its frozen v20 synthesis. The transferable
pattern is evidence compression: establish the central lens quickly, answer each subproblem
directly, expose the one structural move that matters, and close with validation or decision
implications. Method inventories without answers, high-precision numbers without units or
uncertainty, and adjectives without comparisons are anti-patterns even when they appear in a
displayed paper.

This skill may author the final abstract after the result ledger is frozen. The separate writing
agent authors the first full-body draft.

## Main text

1. Problem restatement
2. Problem analysis and dependency diagram
3. Assumptions with justification, mathematical consequence, test, and failure impact
4. Symbols with meaning, units or dimensions, domains or indices, and code mapping
5. Data source, audit, and preprocessing
6. Baseline model
7. Model construction and derivation by subproblem
8. Solver and implementation
9. Results with direct answers
10. Validation and uncertainty
11. Sensitivity, scenario, and strategy-boundary analysis
12. Model strengths, limitations, failure conditions, and extensions
13. Conclusion
14. References
15. Appendices and supporting-material index

## Paragraph logic

Use claim → rationale/equation → evidence/result → implication. Do not let a section become a list of software operations.
Use prose for connected reasoning, lists for real enumerations, and tables for repeated-field comparisons. Do not ban bullets globally.

For core reasoning sections, start from team-authored bullets or a team-approved reasoning outline. AI may restructure and polish that content, but must not invent a retrospective human rationale or conceal its contribution.

## Result ledger

Maintain a table with result ID, subproblem, canonical value, unit, uncertainty, generating script, source table/figure, and every paper location where it appears.

Maintain the argument-spine, assumption, notation, result, and abstract-coverage ledgers as a linked system. Freeze the result ledger before writing the final conclusion, abstract, or title.

## Style rules

- Define symbols before use.
- Use one notation for one concept.
- State units in equations, tables, and axes.
- Give precision supported by inputs.
- Cite external data and methods at the point of use.
- Prefer active, concrete statements over formulaic prose.
- Replace generic transitions with the specific mechanism, comparison, quantity, or consequence.
- Do not rearrange sentences or insert artificial errors to evade AI detection.
- Never copy sample-paper phrasing.
