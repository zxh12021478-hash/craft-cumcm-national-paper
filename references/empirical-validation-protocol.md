# Empirical validation protocol

## Purpose

Use this protocol when testing whether the skill can generate or improve competitive CUMCM work.
It prevents a polished historical replay from being mislabeled as a blind validation.

## Evidence levels

- **E1 — workflow mechanics:** schemas, validators, deterministic utilities, render checks, and
  regression tests pass.
- **E2 — strategy forward test:** a strategy is frozen from official problem artifacts before any
  same-case solution material is exposed. For historical problems call this
  `solution-isolated historical test`, not zero-knowledge.
- **E3 — real package takeover:** a paper and code package is inventoried, statically audited,
  reproduced from a clean environment, independently checked, corrected, and regenerated.
  Report the exact reached state: `audit-only`, `partial-reproduction`,
  `end-to-end-reproduction`, or `implemented-takeover`.
- **E4 — independent human calibration:** identified real humans review blinded artifacts using
  a fixed rubric. An AI reviewer, invented name, or unsigned placeholder never counts.

Award prediction is outside these evidence levels.

For completed E3/E4 exercises, read and append only evidence-backed outcomes to
`references/empirical-evidence-log.md`. Keep contaminated retrospective cases
separate from forward tests; never let an E3 reproduction result silently raise
an E2 strategy or E4 human-calibration claim.

## Isolation boundary

Before freezing a historical strategy, permitted inputs are:

- the official problem page and official attachments;
- generic skill principles and task-family methods that do not disclose the same case;
- a hash-bound cross-case abstraction library frozen before the target was opened;
- tool and format instructions;
- environment diagnostics.

Forbidden pre-freeze inputs include:

- same-case sample papers, solution notes, code repositories, abstracts, award reports, or search
  snippets;
- benchmark scorecards that reveal the expected model family or numerical result.

Raw unrelated papers or the official sample casebook may be used only under the cross-case transfer
protocol. If they are selected or abstracted after opening the target, record every exposure and
label the run `cross-case-assisted solution-isolated historical test`. Do not call it a prospective
canary or a pre-trained-library test.

Record every actually exposed resource, not only files intentionally opened. Search-result snippets
count as exposure. If a forbidden resource is exposed, mark the case contaminated; restarting the
write-up without a genuinely isolated context does not remove that fact.

## Freeze contract

For every case, preserve:

- official source URLs and artifact hashes;
- the exact pre-freeze resource ledger;
- strategy artifact paths and SHA-256 values;
- freeze timestamp and unblinding timestamp;
- evaluator rubric fixed before unblinding;
- contamination findings and evidence label.
- the pre-unblinding innovation tournament, top-three pilot evidence, selector ranking, and human
  selection as separate hash-bound artifacts.
- a pre-pilot manifest frozen before the first experiment, plus an official-output closure manifest
  proving that every required direct answer, workbook/range, policy, figure, and file exists and
  passes at least one content-level check.

Use `assets/templates/历史评测隔离台账模板.json` and run:

```bash
python scripts/audit_benchmark_isolation.py \
  历史评测隔离台账.json --root 项目目录 --strict
```

Before the isolation freeze, also run:

```bash
python scripts/audit_benchmark_output_closure.py \
  历史盲测输出闭环.json --root 项目目录 --strict
```

A clean audit supports only the declared evidence class. It does not establish national-award
quality without executed results and stronger calibration.

## Scoring

After strategy freeze, classify the primary task family and use
`references/capability-evaluation-loop.md`. Score requirement coverage, formulation validity,
structural insight, reproducibility, independent validation, cross-artifact consistency, and
decision value from 0 to 4 with artifact evidence.

Pass only when every dimension is at least 2, at least four dimensions are at least 3, and no
automatic failure remains. Missing a required subproblem/output range, changed frozen hash,
unreproduced headline result, material constraint violation, or mislabeled contamination is an
automatic fail. Keep self-scores and independent scores separate and run
`scripts/score_capability_benchmarks.py`; do not average away a blocker.

## Unblinding and comparison

Use official display papers to compare method coverage, but do not infer their award grade merely
from display status. Use official award lists for award labels; otherwise label repository or author
claims as unverified.

Public code without a compatible license may be inspected and locally executed where lawful, but
do not redistribute or publish patched derivatives. Record the commit hash and license boundary.

After unblinding, append real candidate outcomes to
`assets/templates/创新盲测校准台账模板.json` and run
`scripts/calibrate_innovation_selector.py`. Report top-one/top-three hit rate, false novelty,
implementation survival, and selection regret. Do not claim the selector is calibrated below its
minimum effective-case threshold, and never rewrite a frozen case to improve those metrics.

## Prospective canary

The strongest practical test is the next genuinely unseen problem:

1. freeze the protocol before release;
2. accept only official problem artifacts;
3. timestamp and hash the strategy, code, results, and paper at each gate;
4. disclose all AI assistance;
5. obtain real human review where available;
6. compare later feedback or outcome without rewriting the frozen record.
