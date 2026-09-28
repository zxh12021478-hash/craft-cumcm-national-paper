# Stage: contest readiness and deterministic delivery

Read `references/contest-readiness-and-recovery.md`.

1. Before contest work, run `scripts/contest_doctor.py --strict`; add `--online` when current official
   rules must be checked. Use the reported pinned interpreter for final validators.
2. At a material handoff, freeze, or interruption, build the recovery card. On resume, verify it before
   trusting cached state; rebuild it after any hash mismatch.
3. For final packaging, prepare the exact allowlist and show the manifest to the team. Do not execute
   `approve` until a real team member explicitly confirms it.
4. After approval, run `build --strict`. Upload only the contents of `upload/`; retain `evidence/`
   locally. Any changed input requires a new manifest and approval.
