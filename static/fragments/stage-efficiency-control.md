# Stage: efficiency control

Read `references/efficiency-and-token-budget.md`.

1. Identify the current contest stage, deadline pressure, artifact completeness, and whether the
   request changes a core dependency.
2. Select `sprint`, `standard`, or `final`; state the choice in one short sentence only when it affects
   what will be checked or delivered.
3. If two artifact versions exist, run `scripts/plan_incremental_audit.py` before loading the revised
   bundle. Follow its dependency closure and escalation verdict.
4. Put detailed logs and ledgers in files. Chat contains the decision, decisive evidence, next action,
   and unresolved Blocker/Critical risks.
5. Run `scripts/measure_instruction_budget.py --strict` when modifying the skill or diagnosing route
   bloat. Token savings never waive a hard quality gate.
