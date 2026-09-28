# Stage: historical benchmark isolation

Read `references/empirical-validation-protocol.md` and
`references/cross-case-transfer-protocol.md`. Never read same-case solutions, papers, repositories,
award reports, abstracts, or method-revealing search snippets until the strategy artifacts have
been frozen and hashed. A pre-frozen, unrelated cross-case abstraction library is permitted when
its path, version, and hash are logged.

## Sequence

1. Select cases from official CUMCM problem pages only.
2. Create one `历史评测隔离台账.json` per case before opening the problem.
3. Record every pre-freeze resource actually exposed to the model, including routed skill
   references, retrieved cross-case cards, raw unrelated papers, and search snippets.
4. Audit and hash the problem bundle. A human reconciliation remains a human gate; never fill its
   reviewer fields with an AI identity.
5. Produce the structural-insight tournament and solver-ready strategy from the official problem
   and attachments. Freeze and hash the discovery shortlist plus every pilot metric, threshold,
   failure rule, and time budget **before** running the first pilot; preserve the pre-pilot manifest.
6. Run all top-three micro-experiments before unblinding. Close every official subproblem and
   required output through `历史盲测输出闭环.json`; run
   `scripts/audit_benchmark_output_closure.py --strict`. A strategy package may remain E2 evidence,
   but it cannot pass the capability rubric when an official answer, workbook, range, policy, or
   other required output is missing.
7. Freeze the tournament, pilot evidence, selector report, output-closure manifest, and every strategy artifact with SHA-256
   and run
   `scripts/audit_benchmark_isolation.py`.
8. If the audit reports contamination, stop calling the case blind. Preserve the frozen artifact,
   downgrade it to `retrospective rehearsal`, and continue only as a diagnostic comparison.
9. After a clean freeze, unblind against same-case public papers or code. Keep award provenance separate
   from method comparison.
10. Append real post-unblinding human outcomes to the innovation calibration ledger without changing
   the frozen tournament.
11. Append the frozen strategy/package, canonical task family, self-score, independent score, time,
    and intervention count to the capability benchmark ledger; run `scripts/score_capability_benchmarks.py`.
12. Report evidence levels and limitations. A prospective unseen problem is stronger than any
    historical replay.

If raw unrelated papers were selected or abstracted after the target was opened, label the run
`cross-case-assisted solution-isolated historical test`; this is not same-case contamination, but
it is weaker than a prospective canary with a pre-frozen library.

Never let a later comparison rewrite the frozen strategy. Put improvements in a separately hashed
post-unblinding artifact.
