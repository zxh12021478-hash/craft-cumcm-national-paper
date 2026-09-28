# Core delivery requirements

## Pre-draft deliverable

Before the writing agent produces the complete first draft, return exactly one generated
`推荐解题思路大纲` in `.md`, `.docx`, or `.txt`. The user supplies the official problem and data
attachments separately. The outline contains:

1. a concise judgment of the problem's essence and central difficulty;
2. the logical relationship among the subproblems and what role each plays in the whole solution;
3. one preferred overall modeling direction and the main reason it is promising;
4. recommended model families or mechanisms for each subproblem at a conceptual level;
5. one primary and at most two supporting innovation ideas, stated as the weakness addressed, the
   conceptual change, and the expected value;
6. the most important validation directions and evidence the eventual solution should seek;
7. major risks, likely failure modes, and one brief fallback direction;
8. exactly two substantial, problem-specific writer-facing blocks:
   `题型适配、模型主线与高价值可视化建议` and
   `求解真实性、验证闭环与成文质量建议`. Together they map the actual subproblems and variable
   relationships to useful mechanism/principle diagrams, decisive diagnostics, model comparison,
   uncertainty, simulation when genuinely dynamic, readable figures, reproducibility expectations,
   and later abstract priorities. They must be more specific than generic coaching text while
   imposing no fixed visual, simulation, pseudocode, appendix, or page quota;
9. paper narrative emphasis: what central story and innovation the complete draft could foreground;
10. an explicit statement that the writing agent has discretion to adopt, refine, combine, or reject
   the recommendation and owns equations, algorithms, calculations, code, results, and first-draft
   composition.

Do not include full derivations, complete equations, calculation steps, pseudocode, code, parameter
settings, exact workbook mappings, result schemas, fixed decisions, prohibited deviations, or
return-package requirements. The outline should be insightful and directional, not comprehensive or
controlling. A different route chosen by the writing agent is not a defect; assess it later on its
actual logic and evidence.

Build this document from `assets/templates/推荐解题思路大纲模板.md`, replacing every template
instruction with actual problem-specific content. The two writer-facing blocks are mandatory parts
of the one document, not two companion files.

## Review deliverable

Lead with verdict and gating defects. Use exact artifact locations. For each finding state:

- severity;
- evidence;
- why it matters to an evaluator;
- concrete repair;
- verification after repair.

End with a prioritized checklist and a conservative post-repair competitiveness estimate.
Include an explainability audit: the questions each team member should be able to answer about the formulation, parameters, solver, validation, and limitations.
For an external baseline, begin with a trust verdict: preserved intake, accepted for audit, or
rejected. State whether its code reproduces its numbers and explain its chosen route on its own
merits; do not score conformity to the earlier recommendation.

In `sprint`, keep at most five P0/P1 findings active and put detailed evidence in a report artifact.
Use the full scorecard/red-team output only for the first viable complete bundle, a material core
change, or final review. Never omit a Blocker or Critical finding to meet a chat budget.

## Final artifact deliverable

Start from the separate writing agent's draft. This skill may rewrite the abstract and repair
specific defective passages, but it must not create a replacement full paper body without an
explicit task-specific override.

Return:

- one consolidated final electronic paper in the requested source format and PDF where possible;
- complete runnable code and dependency file;
- data provenance/readme inside supporting materials;
- regenerated figures and tables;
- AI-use disclosure when applicable;
- internal core-decision and human-verification record;
- completed paper argument, assumption, notation, result, and abstract-coverage ledgers;
- validator reports;
- concise change ledger;
- unresolved limitations.
- external-baseline handoff and interaction record when used;
- signed page-by-page visual QA record whose paper hash matches the delivered file;
- cross-audited team comprehension record.
- task-family-specific independent verification report with no unresolved failed core checks.

Keep the executive answer concise, but do not hide caveats that affect validity or eligibility.
