# Contest readiness, recovery, and deterministic delivery

## 1. Fixed validator environment

Before the contest and before every `final` run, execute `scripts/contest_doctor.py --strict`.
Use the `recommended_validator_python` returned by the report for all final validators; do not mix
system, bundled, and virtual-environment interpreters. The doctor checks pinned package versions,
required rendering binaries, write access, disk space, regression tests, and instruction budget.
Use `--online` when network access is allowed and current official rules must be rechecked.

If the pinned environment is missing, recreate it with `scripts/bootstrap_validator_env.py` and the
offline wheelhouse named in `assets/workflows/validator-runtime.json`. Never overwrite an existing
environment: create a new versioned directory and rerun the doctor.

## 2. Recovery card

After a material gate decision, result freeze, external-agent handoff, or before a long interruption,
run `scripts/recovery_card.py build`. It produces one human-readable Markdown card and one canonical
JSON card bound to the workflow, problem, registered artifacts, result ledger, gates, declarations,
and current high-severity findings.

On return, run `scripts/recovery_card.py verify` before relying on the card. If the workflow, problem,
or any registered artifact changed, rebuild from current evidence. The recovery card is a compact
resume index, not a substitute for the source files and not evidence that an unresolved gate passed.

## 3. Deterministic final package

Use `scripts/build_submission_package.py` in three separate steps:

1. `prepare` builds an exact hash-bound allowlist for the paper and supporting files. Review this
   manifest with the team; excluded files stay excluded.
2. `approve` is run only after a real team member confirms the exact manifest. The agent must never
   fabricate the approver or approve on the team's behalf. An approved manifest is immutable.
3. `build --strict` verifies every source hash and produces a fresh output directory with:
   - `upload/`: only the two files intended for the competition portal;
   - `evidence/`: hashes and the machine validation report, retained locally and not uploaded unless
     an official instruction explicitly requires them.

The supporting ZIP is sorted with fixed timestamps and permissions, so unchanged approved inputs
produce the same ZIP hash. Any source change invalidates the manifest and requires a new prepare,
team review, approval, and build cycle. The current official competition instructions override local
default filenames or size limits whenever they differ.
