# Evidence bundle contract

The scripts check file identity, linked numerical claims, required-output records and explicit review records. They do not independently establish physics, correctness of English interpretation, official-rule authenticity, authenticity of a human review, or prize quality. Never call a machine pass an independent scientific audit.

## Bundle JSON

Paths are relative to `--root`; traversal, absolute paths and symlinks outside that root are rejected. Include every dependent input/code/result/PDF/figure in `files`, each with its current SHA-256. Keep all reviewed versions immutable until a new audit.

```json
{
  "event": "APMCM",
  "event_year": 2024,
  "mode": "historical-rehearsal",
  "files": [{"path": "paper.md", "sha256": "64 hexadecimal characters"}],
  "paper": "paper.md",
  "results": "results.json",
  "claims": [{
    "id": "summary-cost", "quote": "The cost is 32 USD.",
    "token": "32", "pointer": "/cost", "unit": "USD",
    "absolute_tolerance": 0.005, "scale": 1
  }],
  "required_outputs": [{
    "id": "Q1", "status": "verified", "evidence": ["results.json"],
    "review_note": "Explain the actual content-level check, not just file existence."
  }],
  "reviews": {
    "semantic": {"status": "pass", "reviewer": "AI self-review", "evidence": "review.md"},
    "figures": {"status": "pass", "reviewer": "AI visual review", "evidence": "review.md"},
    "coverage": {"status": "pass", "reviewer": "AI self-review", "evidence": "review.md"},
    "reproduction": {"status": "pass", "reviewer": "executed clean rerun", "evidence": "reproduction.json"}
  }
}
```

All paths used by the paper/results/review/evidence fields must occur in `files`. JSON pointers use RFC6901 escaping and can address array indexes. `scale` makes an explicit unit conversion (e.g. fraction to percent, 100). `token` must appear as a standalone numerical token within the exact unique `quote` in the paper and match the source value within the declared nonnegative tolerance. A reviewer must ensure every important occurrence is covered; the script cannot discover all unlisted claims.

## Run

```bash
python3 scripts/audit_bundle.py --root PATH --manifest PATH/bundle.json --output PATH/audit.json
python3 scripts/package_bundle.py --root PATH --manifest PATH/bundle.json --output PATH/rehearsal.zip
```

The default packager accepts only training/historical-rehearsal and writes a clearly labeled local evidence archive. It recomputes validation immediately before packaging and checks hashes again while archiving. It is not an upload tool and never produces a signed control sheet.

For a current submission audit:

```bash
python3 scripts/audit_bundle.py --root PATH --manifest PATH/bundle.json \
  --rules assets/rules-2026.json --final --output PATH/final-audit.json
```

`--final` additionally requires a live-contest manifest, matching APMCM year, all required rules verified, source references, and recorded rule-specific checks. The bundled 2026 profile intentionally cannot pass while unresolved. For every required rule add `rule_checks.<rule>` with pass status, reviewer and a hash-bound evidence path explaining compliance. A metadata label alone is not an implementation of the actual rule. Live packages also require `team_approval` with `approved: true`, a real name, timestamp and the exact SHA-256 of the manifest before approval was added (canonical JSON, sorted keys, UTF-8, no whitespace). Never populate it on a team's behalf. Current scripts provide an evidence archive, not the official platform's set of upload files; inspect the rules and export the exact required files separately after confirmation.

Training records with incomplete required outputs remain failed even if a paper PDF exists. Preserve a failed report; don't change `unverified` to `verified` merely to build a ZIP. An ordinary archive of unfinished work may be kept separately and labeled incomplete.

## Binding current rules to approval

Before requesting team approval, set `manifest.rules_sha256` to `rules_hash(rules)` from `audit_bundle.py` (SHA-256 of the complete rules JSON canonicalized with sorted keys, UTF-8, no whitespace). The final audit requires an exact match. Because the manifest approval hash includes this digest, changing the rule profile invalidates the prior approval. Final local evidence archives include `RULES.json` for reconstruction of the audited rule basis. It is a reserved archive filename. This binds the recorded evidence; it does not authenticate an organizer source or certify a review.
