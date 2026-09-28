# Empirical evidence log

## Purpose

This is an append-only index of completed capability exercises. It records what
was actually demonstrated and prevents a successful historical replay from
silently becoming evidence for blind strategy quality or award prediction.
Detailed artifacts remain outside the skill directory; hashes bind each entry.

## Completed records

### E3-2024A-Bench-Dragon-20260829

- Case: CUMCM 2024 A, public Bench Dragon paper/code package.
- Mode: contaminated retrospective historical rehearsal.
- Isolation: `solution_blind=false`; same-case paper, code and award metadata
  were exposed before the formal ledger.
- Source: GitHub commit
  `1cbca6040277e7d240c397ba0edabe760e256705`, MIT license; archive SHA-256
  `77cff5596f841ebfe7239eef699642700f1e8683a753455a5b1da817bf202378`.
- Reached state: `end-to-end-reproduction` for the numerical package.
- Direct evidence: clean copied-directory run regenerated all three official
  workbooks, machine-readable headline results and 19 PNGs; verifier passed
  29/29 checks; primary and clean workbooks differed by 0 in every cell.
- Independent implementation check: maximum full-workbook difference
  `1.13e-10`; independence is implementation-level, not interpretation-level.
- Original-package diagnosis: `partial-reproduction` due to undeclared output
  directory, truncated Q1/Q4 time ranges, disabled Q2 headline root, stochastic
  Q3 output and display-only/coarsely sampled figures.
- Reusable correction: require an official-output contract, untouched baseline
  run, deterministic headline boundary tests, full-workbook comparison,
  evidence-oriented figure sampling and a result-free clean rerun before an E3
  package may reach `end-to-end-reproduction`.
- Withheld claims: blind strategy performance, `implemented-takeover`, human
  calibration and award probability.
- Evidence root:
  `<local-evaluation-workspace>/E3-rehearsal-2024A-bench-dragon`.
- Final assessment SHA-256:
  `39cd7b621566d0174cfc5a62af527b07ac64372b73390f8a6c9e326132f7f936`.
- Verification report SHA-256:
  `0dcd2a6279da3eede21c576365475d2edc844e238fea5de96be7fcb9ffb39312`.
- Clean-run comparison SHA-256:
  `eb14d7417c08d81e9fdf1200924d589c1ad8cd5ebca1eb8f1d7895646a409252`.

## Capability implication

This record raises confidence in E3 package-inventory, reproduction, numerical
verification and repair mechanics. It does not change the skill's uncompleted
3-case isolated historical benchmark, prospective unseen-case, or independent
human-review status.

### E3-2022C-Ancient-Glass-20260829

- Case: CUMCM 2022 C, public paper/code/data package for ancient-glass
  composition analysis and classification.
- Mode: contaminated retrospective E3; no blind-strategy claim.
- Source: GitHub commit
  `88911f5a4a18465628e8b074238d586a47fa9ced`; archive SHA-256
  `310b09fea8780658d1080a57ede01632946ddd184760498c44da2fdb8d314ac0`;
  MIT code and CC BY-NC paper/data according to repository license files.
- Reached state: `end-to-end-reproduction` for the public Python artifact
  contract, excluding MATLAB and Typst compilation.
- Direct evidence: eight of eight public Python stages ran; 17 artifacts were
  generated; verifier passed 19/19 checks; clean rerun workbooks were
  cell-identical and deterministic CSV/SVG artifacts were byte-identical.
- Independent checks: exact CLR closure from raw data, nested leave-one-out
  accuracy `0.9850746269`, fixed-feature ten-fold mean `0.9833333333`, exact
  unknown-sample mapping, and 500-trial clustering perturbation audit.
- Material warnings: public classifier code reports in-sample accuracy rather
  than the paper's stated split/CV protocol; subclass scores are circular with
  cluster-generated labels; question-4 marginal K-S tests do not directly test
  correlation-structure differences.
- Reusable correction: an E3 data package requires independently recomputed
  invariants from raw inputs, leakage-aware out-of-sample checks, deterministic
  stochastic tests and a clean copied-directory rerun.
- Evidence root:
  `<local-evaluation-workspace>/empirical-expansion-v1/e3-data-classification`.
- Final assessment SHA-256:
  `465de59ad7fd2d537d206cbfaff9997896916568cc99f4b9f4cd79895466f9a9`.
- Verification report SHA-256:
  `d324c7bdb6e0c3f6bfcfd5cc3b698a918ad7b0477e547dccc174f12ff7d1ce90`.
- Clean-run comparison SHA-256:
  `f4fd792ffcb3f6200d78feac4441178769895bbcf103e02a89a1d9ea08c2edbd`.

### E3-2020B-Desert-Dynamic-20260829

- Case: CUMCM 2020 B, public desert dynamic-programming/game package.
- Mode: contaminated retrospective E3; upstream award claim not used as
  official evidence.
- Source: GitHub commit
  `d5757bbb41e3435b22278bd36156bd8ba2d6274a`; archive SHA-256
  `4def4b5d6d23c1e85dbdd4aaf266006f7ceefd29cb75c3d418d519ac9eba3971`;
  no declared license, so the derivative remains local and non-redistributable.
- Reached state: `partial-reproduction` with deterministic local takeover.
- Original diagnosis: all five public entry points failed from broken paths,
  deprecated plotting or undeclared commercial `xpress` dependency.
- Direct evidence: selected DP values 10470 and 12730 reproduced; frozen
  feasible-neighborhood probes, independent graph routes/key node and packaged
  artifact audits passed 28/28 checks; clean-run top-level artifacts were
  byte-identical.
- Withheld claims: no exhaustive global rerun, no 1000-game rerun and no global
  optimality certificate. The shipped game sample has 148 rows and tie-aware
  high-risk top share `35.36036%`; Q2 workbook has two unexplained local-ledger
  anomalies; later paper sections are incomplete.
- Reusable correction: enforce feasibility at adapter boundaries, expose
  deferred accounting states, reconcile simulation sample size/claims, and
  stop at the exact lower evidence state when the public contract is incomplete.
- Evidence root:
  `<local-evaluation-workspace>/empirical-expansion-v1/e3-dynamic-optimization`.
- Final assessment SHA-256:
  `898fc278429f7e41146682a838773c58676840fbb9d8c9d5c92e03b9a5f62816`.
- Verification report SHA-256:
  `a3e2f4441c610a8d78c27d21a4a21181d3cf2ad20660b1c972c3b56e0532878b`.
- Clean-run comparison SHA-256:
  `4319f0f0b9023df6bc52df6c6defe2fb5fb52fe98605afd6fecf5f67f3630f04`.

### E2-Outline-Trio-2011B-2013C-2015C-20260829

- Cases and families: 2011B network/spatial optimization, 2013C geometric
  measurement/trend, and 2015C astronomical mechanism/event-window prediction.
- Mode: three `solution_isolated_historical` outline-only tests. Official
  problem/attachments were the only same-case material before strategy freeze;
  model memory remains unknown, so none is called zero-knowledge blind.
- Freeze evidence: each case preserved an attachment/resource ledger,
  requirement map, innovation candidates, risk register, fixed rubric and one
  `推荐解题思路大纲.md`; strict isolation and outline-coverage audits passed.
- Post-unblind self scores on the frozen 0–4 outline rubric: 2011B `3.7143`,
  2013C `3.5714`, 2015C `3.8571`; mean `3.7143`. No automatic failure occurred.
- Honest status: all three are `SELF_ONLY`. There is no independent AI or real
  human blind assessment, so the scores do not calibrate the selector.
- Main misses: road-segment versus node service semantics (2011B), explicit
  missing-layer/tower-tip branches (2013C), and an immediately executable
  numeric baseline before the higher-cost ephemeris uncertainty chain (2015C).
- False-novelty corrections: bipartite matching, tilt/bend/twist decomposition
  and astronomical time-window intersection are valid structures but are not
  innovations by themselves.
- Reusable correction: before handoff, profile every attachment's irregular
  entity shapes, resolve the operative service/measurement unit, and pair every
  ambitious primary direction with a transparent survivable baseline.
- Evidence root:
  `<local-evaluation-workspace>/empirical-expansion-v1/historical-outline-tests`.
- Frozen outline SHA-256 values: 2011B
  `dba279b809dae03801aba609c1cd9a05864e4db05be5118a6b7337aebfa2b98a`;
  2013C `e6b5f50ade829fe70c5da2bf1adada858b5677224ff44018e32aeb725a3618e3`;
  2015C `9baf8d1254dce4b46a15460d8fa6ebe17271b4d1b7fd0a477a97c2475044d129`.

### Prospective-2026-Prepared-20260829

- State: `prepared_not_executed`.
- A hash-bound pre-release protocol, fixed evaluator rubric, empty official
  input drop zone, initialized isolation ledger and activation runbook exist;
  the frozen skill state is v23.
- This is not a prospective test and contributes no forward-test score until a
  genuinely unseen official problem is received, a strategy is frozen and the
  later unblinding comparison is completed.
- Evidence root:
  `<local-evaluation-workspace>/empirical-expansion-v1/prospective-2026`.
- Pre-release manifest SHA-256:
  `db6fc660e60c6c6cd82390558db0f6dbaaab4fbab0da6de7579bafc819189a4c`.

## Current capability implication

The skill now has one end-to-end E3 mechanism/geometry package reproduction,
one end-to-end E3 data/classification artifact-contract reproduction, one
partial E3 dynamic-optimization takeover, and three solution-isolated E2
historical outline tests across different families. This materially increases
confidence in package takeover and first-pass strategy-handoff mechanics.

The weakest evidence remains unchanged in kind: no actually executed
prospective unseen case and no identified real-human blinded review. Therefore
the empirical claim is `stronger diagnostic evidence`, not broad calibration,
national-first-prize validation or award prediction.
