# Modex drafting handoff

Modex implements the solution and writes the initial full paper. This skill first produces the strategy handoff, then waits for the returned paper/code/results to audit and selectively repair. Reconstruct the final abstract only from the complete paper and verified results. Doubao is not part of this contest workflow. Explicit user requests can authorize a full rehearsal draft.

## Evidence handoff

Use `assets/strategy-handoff.md` and attach `assets/modex-return.md` as the return checklist. Give Modex the original problem, requirement matrix, recommended route and rationale, key equations and symbol/unit glossary, baseline, testable innovation, fallback trigger, sources, known gaps and validation plan. For each original question assign a stable ID and specify input → executable equation/algorithm → required output → acceptance check. Explain inter-question dependencies. Separate the required original outputs from optional extensions; do not let optional novelty displace task coverage. For a complex task, freeze a small `requirements.json` from the original question (see `bundle-contract.md`) before drafting, so omitted questions cannot disappear from the later audit. Identify parameters as given, measured, calibrated or assumed. Include existing code/results, figure/table sources, versions and rerun commands only when available. Label every item as supplied, executed, planned or missing. A new-problem handoff does not require finished numerical answers or a frozen result bundle; do not solve the whole problem merely to populate these fields.

Mark which conclusions are supported and which remain hypotheses. When validation rejects a recommendation, include the failed evidence and withdraw the claim before writing. A polished abstract cannot resolve a physical discrepancy. Do not convert simulated gains to measured gains, finite-set minima to unrestricted optima, or held-in calibration to held-out validation.

Keep original requirements distinct from chosen implementation and local acceptance criteria. A bit width, model order, kernel, restart count or performance threshold chosen for the route is not an organizer requirement. Preserve its rationale and revisability without rewriting the frozen original question; a fallback must still cover that question.

Suggested drafting request:

> Implement the recommended route and produce the complete English initial manuscript, executable code, machine-readable results, source figures and reproducibility instructions. Cover every problem requirement. Run the baseline and planned validation; distinguish actual runs from unfinished work. Preserve supplied facts and the scope of existing evidence. Explain consequential departures from the proposed route. Cite only verified sources; do not invent values, experiments or validation. Flag unresolved gaps. Return traceable equation, figure, table and claim identifiers so the skill can audit the actual artifacts.

## Summary priority in the handoff

The package plus original inputs must be usable without this conversation. Specify answer-changing conventions: index/time order, sign and units, initial/terminal conditions, boundary scope, missing-data handling, solver stopping/acceptance and output format where relevant. A receiver may choose a harmless implementation default and record it; an unresolved convention that changes the answer must be flagged rather than silently guessed. This does not require an extra paid readback round in the contest workflow.

Follow `abstract-priority.md`. Ask Modex to write the Summary after the body and actual results, with direct answers for each original question, the main mechanism, a comparable baseline and decisive validation/limits. Return body/result locators for headline claims, reusing the existing coverage table and ledger. Before execution specify these as required outputs, never promised gains. The skill will prioritize evidence-based Summary reconstruction after substantive repairs.

## Audit and revision

Read the complete returned draft before rewriting its abstract. Compare it to the actual question, code, results and validation ledger. Triage answer-changing failures first (missing questions, infeasibility, leakage, wrong calculations), then unsupported claims/uncertainty, then English/layout. Return each issue with location, evidence, effect on the answer, minimal repair and a concrete recheck. A missing output or materially wrong answer cannot be compensated by polished prose. Classify whether the repair needs new calculation or only wording. Run necessary local checks and repair affected artifacts; do not route the audit to Doubao. Reuse unchanged evidence and review changes plus affected claims, while still reading the complete first draft. Keep reasonable writing/model choices. Any numerical revision requires refreshed figures, repeated claims and a new frozen handoff version. Keep a short change record so Modex does not revive rejected claims in the next draft. Stop once requested issues are resolved and relevant checks pass; do not initiate unrelated model exploration. Do not send messages to Modex without the user's authorization; provide a usable package locally when no authorized execution interface is available.

This reference is a handoff protocol; it does not authorize sending messages to another service or thread by itself.
