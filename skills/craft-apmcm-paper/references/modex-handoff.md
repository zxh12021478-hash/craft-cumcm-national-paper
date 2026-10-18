# Modex drafting handoff

Modex writes the initial full paper. This skill supplies evidence, audits the resulting manuscript, reconstructs the final abstract from the complete paper, and makes targeted repairs. Explicit user requests can authorize a full rehearsal draft.

## Evidence handoff

Give Modex the original problem and requirement matrix, frozen model/results version, formulas and symbol/unit glossary, figure/table source files, source provenance, and a claim ledger. For each question include the direct answer, assumptions, method, numerical output, validation evidence and limitations. Identify parameters as given, measured, calibrated or assumed. Include a command and environment for rerunning.

Mark which conclusions are supported and which remain hypotheses. When validation rejects a recommendation, include the failed evidence and withdraw the claim before writing. A polished abstract cannot resolve a physical discrepancy. Do not convert simulated gains to measured gains, finite-set minima to unrestricted optima, or held-in calibration to held-out validation.

Suggested drafting request:

> Draft the full English manuscript from this frozen evidence package. Cover every requirement and use the supplied definitions and results. Preserve their scope and uncertainty. Cite only verified sources. Do not invent values, experiments or validation. Flag missing evidence instead of silently completing it. Return the manuscript with traceable equation, figure, table and claim identifiers.

## Audit and revision

Read the complete returned draft before rewriting its abstract. Compare it to the actual question, code, results and validation ledger. Return specific issues with location, evidence and minimal repair. Classify whether the repair needs new calculation or only wording. Keep reasonable writing/model choices. Any numerical revision requires refreshed figures, repeated claims and a new frozen handoff version. Keep a short change record so Modex does not revive rejected claims in the next draft.

This reference is a handoff protocol; it does not authorize sending messages to another service or thread by itself.
