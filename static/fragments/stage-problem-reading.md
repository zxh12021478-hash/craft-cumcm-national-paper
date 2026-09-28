# Stage: problem reading

Read `references/task-family-kits.md` and `references/two-system-handoff.md`. In `standard` mode,
also read `references/model-selection-playbook.md` and `references/innovation-tournament.md`.
Read `references/paper-argument-spine.md` only when the requested outline needs a paper-story repair
that is not already covered by the handoff template. When historical comparison
is useful, read `references/official-sample-index.yaml` only after confirming that the task is not a
pre-freeze historical benchmark. Benchmark isolation takes precedence.

## Procedure

Current team preference: prepare for problem A. Unless the user asks to reconsider, focus on the
provided A problem without spending time comparing A/B/C. Infer the actual task family from its
contents; the letter A alone does not imply a physics model or a higher award chance. This preference
does not constrain historical tests or an explicitly supplied different problem.

1. Inventory and hash every official problem/attachment file with `scripts/audit_problem_bundle.py`. Run it once without `--strict` to obtain the bundle digest and deterministic risk IDs. Render all PDF/DOCX pages; inspect equations, maps, drawings, OLE objects, hidden sheets, merged headers, formulas, units, and requested workbook output ranges.
   Before recommending a direction, freeze an attachment-structure profile: sheet/table/image counts,
   row and column shapes, missingness by required entity, irregular group sizes, singleton or truncated
   groups, duplicated identifiers, and any entity for which the default model cannot run. A generic
   “handle missing values later” sentence is not enough; name the exceptional cases the writing agent
   must branch on, without inventing their repair.
2. Populate `assets/templates/题面核对签字模板.json`, binding every official artifact hash, every risk ID, and every prompt subproblem to human review evidence. Rerun `scripts/audit_problem_bundle.py --reconciliation 题面核对签字.json --strict`; do not approve a strategy from a text-only extraction or an audit with open reconciliation findings.
3. Classify every statement as given fact, decision variable, latent parameter, constraint, objective, requested output, or ambiguity. Explicitly identify the operative service/measurement unit—point,
   edge, route, region, individual, event, time window, or aggregate—and test whether an alternative
   interpretation would leave official objects unserved or change feasibility. Then route every
   subproblem through `references/task-family-kits.md`; load only its primary and, when materially necessary, one supporting family file.
4. Draw the dependency chain between subproblems. Identify which outputs become later inputs.
5. Separate modeling difficulty from computational difficulty and data difficulty.
6. Identify the hidden evaluation target: prediction, explanation, measurement, control, design, allocation, ranking, or policy.
7. List at least one immediately executable transparent baseline and the exact reason it is
   insufficient. For every higher-risk primary innovation, pair it with a fallback that still closes
   all subproblems if the pilot fails; complexity without a survivable baseline is a handoff defect.
8. Search for structure before selecting algorithms. In `sprint`, screen candidates compactly and
   label the direction provisional. Before a `standard` strategy freeze, populate the structural-
   insight tournament with at least eight falsifiable candidates across four families and run the
   discovery audit without narrating every candidate in chat.
9. State the minimum assumptions needed. Do not add convenient assumptions without testing their consequence.
10. Open `assets/templates/论文论证台账模板.md` and populate the initial subproblem, dependency, assumption, and notation-planning rows.
11. In `standard` strategy freeze, pilot the top three structural candidates on independent minimum
    experiments, bind their evidence hashes, record real team decisions, select one primary and at
    most two supporting innovations, and pass the freeze-phase tournament audit. `sprint` may stop
    after screening but cannot call the innovation frozen.
12. Translate the analysis into one non-binding `推荐解题思路大纲` using
    `assets/templates/推荐解题思路大纲模板.md`: central difficulty, subproblem relationships,
    preferred conceptual direction, innovation ideas, validation directions, risks, fallback, paper
    story, and exactly two substantial writer-facing blocks named
    `题型适配、模型主线与高价值可视化建议` and
    `求解真实性、验证闭环与成文质量建议`.
13. Reconstruct both blocks for the actual problem. The first maps task type, subproblems, mechanisms,
    variables, and evidence questions to useful visual forms. The second maps actual failure risks to
    model comparison, reproducibility, sensitivity, robustness, uncertainty, simulation where
    genuinely dynamic, readable presentation, appendix discipline, and later abstract priorities.
    Both must be detailed enough to guide the writer but remain conceptual.
    The blocks must also name attachment exceptions and operative-unit ambiguities that can change
    the model, plus the transparent baseline the writer should implement before any optional complex
    extension.
14. Do not include exact equations, calculation steps, pseudocode, code, parameter settings,
    workbook mappings, result contracts, or fixed implementation instructions. State that the
    writing agent owns the detailed route and may revise or replace the recommendation.
15. Do not impose counts for 3D figures, chart types, flowcharts, simulations, pseudocode, or
    appendix pages. A 3D display is optional and requires three genuinely meaningful dimensions.

## Output

Produce a concise problem-restatement table with columns: subproblem, role, dependency, conceptual
direction, innovation opportunity, validation direction, and major risk. Then write the single
recommendation outline. If it will be passed to the writing agent, keep it advisory and conceptual;
do not append a solver-ready specification. Keep internal candidate tables and validator logs out of
the user-facing handoff; the default standard outline should be concise enough to guide the writer
without duplicating the official problem or consuming tokens on implementation detail.

## Red flags

- solving an easier problem than the one asked;
- converting qualitative constraints into arbitrary weights;
- treating provided data as error-free without justification;
- optimizing a proxy that is not aligned with the requested objective;
- using the same model for subproblems with different causal or temporal structure.
- recommending a named model pipeline before the operative task, mechanism, and data sufficiency are established.
- assuming every sheet, layer, group, route, or time series has the regular shape seen in its first rows.
- modeling points when the real service obligation is on edges/regions, or reporting a single time when the requested object is a feasible window.
