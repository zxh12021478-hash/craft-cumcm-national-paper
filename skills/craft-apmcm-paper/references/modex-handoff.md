# Modex drafting handoff

Modex implements the solution and writes the initial full paper. This skill first produces the strategy handoff, then waits for the returned paper/code/results to audit and selectively repair. Reconstruct the final abstract only from the complete paper and verified results. Doubao is not part of this contest workflow. Explicit user requests can authorize a full rehearsal draft.

## Evidence handoff

Use `assets/strategy-handoff.md`. Give Modex the original problem, requirement matrix, recommended route and rationale, key equations and symbol/unit glossary, baseline, testable innovation, fallback trigger, sources, known gaps and validation plan. For each question specify the required output and how to calculate/check it. Identify parameters as given, measured, calibrated or assumed. Include existing code/results, figure/table sources, versions and rerun commands only when available. Label every item as supplied, executed, planned or missing. A new-problem handoff does not require finished numerical answers or a frozen result bundle; do not solve the whole problem merely to populate these fields.

Mark which conclusions are supported and which remain hypotheses. When validation rejects a recommendation, include the failed evidence and withdraw the claim before writing. A polished abstract cannot resolve a physical discrepancy. Do not convert simulated gains to measured gains, finite-set minima to unrestricted optima, or held-in calibration to held-out validation.

Suggested drafting request:

> Implement the recommended route and produce the complete English initial manuscript, executable code, machine-readable results, source figures and reproducibility instructions. Cover every problem requirement. Run the baseline and planned validation; distinguish actual runs from unfinished work. Preserve supplied facts and the scope of existing evidence. Explain consequential departures from the proposed route. Cite only verified sources; do not invent values, experiments or validation. Flag unresolved gaps. Return traceable equation, figure, table and claim identifiers so the skill can audit the actual artifacts.

## Audit and revision

Read the complete returned draft before rewriting its abstract. Compare it to the actual question, code, results and validation ledger. Return specific issues with location, evidence and minimal repair. Classify whether the repair needs new calculation or only wording. Run necessary local checks and repair affected artifacts; do not route the audit to Doubao. Reuse unchanged evidence and review changes plus affected claims, while still reading the complete first draft. Keep reasonable writing/model choices. Any numerical revision requires refreshed figures, repeated claims and a new frozen handoff version. Keep a short change record so Modex does not revive rejected claims in the next draft.

This reference is a handoff protocol; it does not authorize sending messages to another service or thread by itself.
