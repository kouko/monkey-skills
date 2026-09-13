# W0-01 baseline — three Loom skill packages

Baseline date: 2026-09-13  
Pinned revision: `d5548b0d10f15769093c5aa18336395cef0cbaac`

This snapshot predates every candidate refactor. The package gate exported each
skill from the pinned Git revision, rather than from mutable working-tree bytes.
The three `test-prompts.json` files are evaluation inputs and are intentionally
outside the package word totals below.

## Reproduction

Resolve `<gate>` to the installed `skill-refactor/scripts/package_gate.py` and
run, once per row:

```sh
python3 "<gate>" verify \
  --manifest "<manifest>" \
  --manifest-sha256 "<external digest>"

python3 "<gate>" account \
  --manifest "<manifest>" \
  --manifest-sha256 "<external digest>" \
  --candidate-root "<manifest directory>/skill" \
  --target-file SKILL.md
```

The canonical manifests remain outside the repository under
`/Users/kouko/.codex/baselines/2026-09-13-shrink-three-loom-skill-entrypoints/`.
The digests in this document are the externally retained orchestration values;
they must not be recomputed from a manifest during later verification.

## Immutable exports and measurements

| Skill | Manifest suffix | External manifest SHA-256 | Verify | `SKILL.md` words / bytes | Package words / bytes | 10% package target |
|---|---|---|---|---:|---:|---:|
| `write-plan` | `write-plan/baseline/manifest.json` | `3640966106aca26f5a10075cf25374b216ec466cd9211e06eab40d145e2e6101` | PASS | 4,498 / 29,872 | 6,364 / 42,124 | at most 5,727 words |
| `capture-intent` | `capture-intent/baseline/manifest.json` | `177330ec403a2ea2ac2e71a93cd0d1241baa936797fdc48f6a9e4a8a47e9243c` | PASS | 3,553 / 22,925 | 4,822 / 30,711 | at most 4,339 words |
| `independent-advisor` | `independent-advisor/baseline/manifest.json` | `313a90b9aff9af452cef011f9573274b7b14af561e6bc8a58a2acbb05d974663` | PASS | 4,035 / 24,828 | 7,620 / 54,806 | at most 6,858 words |

The target is calculated as the largest integer strictly no greater than 90%
of the baseline package word count. Bytes are diagnostic only. Moving prose
from `SKILL.md` into a bundled resource leaves the package total unchanged and
therefore cannot satisfy the target by itself.

## Invariant snapshots

### `write-plan`

- Frontmatter: `name: write-plan`, `version: 1.0.1`; only `description` is
  allowed to change under the refactor gate.
- Declared runtime dependencies: installed `loom_checker.py`,
  `contract/templates/intent.md`, `contract/templates/PRINCIPLES-interview.md`,
  `contract/templates/spec-minimal.md`, `contract/templates/plan.md`,
  `second_vendor_policy.py`, and the three bundled references below.
- Frozen package files: `SKILL.md`, `references/codex-first-contact.md`,
  `references/one-way-door.md`, and
  `references/second-vendor-ask-and-docs-lint.md`.
- Required behavior anchors for prompts 1–3: `Decision boundary`,
  `write-plan.no-plan-without-confirmed-intent`, `Step 4 — Does this need a
  spec?`, `write-plan.product-spec-needs-confirmed-behavior`, `Step 5 — Write
  the plan`, and `Step 6 — Commit and hand off`.

### `capture-intent`

- Frontmatter: `name: capture-intent`, `version: 1.0.0`; only `description` is
  allowed to change under the refactor gate.
- Declared runtime dependencies: installed `loom_checker.py`, the bundled
  interview and second-vendor references, the intent template supplied by the
  installed Loom contract, and downstream `write-spec` / `write-plan` handoffs.
- Frozen package files: `SKILL.md`, `references/interview.md`, and
  `references/second-vendor.md`.
- Required behavior anchors for prompts 1–3: `Step 1 — Interview`, `Step 2 —
  Write the intent`, `capture-intent.product-problem-plain-words`, `Step 4 —
  Decision point ①: restate and confirm`,
  `capture-intent.no-confirmed-without-restatement`, and `Step 5 — Hand off`.

### `independent-advisor`

- Frontmatter: `name: independent-advisor`, `version: 0.1.0`; only
  `description` is allowed to change under the refactor gate.
- Declared runtime dependencies: the three bundled references for executor
  detection, dispatch, and reporting, plus the available external executor
  commands selected at the checkpoint.
- Frozen package files: `SKILL.md`, three localized `README` files,
  `references/dispatch-protocol.md`, `references/executor-detection.md`,
  `references/report-contract.md`, and
  `scripts/test_independent_advisor_readmes.py`.
- Required behavior anchors for prompts 1–3: `Mode routing`, `Static detection`,
  `When the candidate set cannot support a second opinion`, `The single
  checkpoint`, `The egress disclosure`, `The live probe`, `frontier fails
  loud`, and `Three roles and blind judging`.

All frozen files had non-executable Git modes. Their byte-level SHA-256 values
remain in the canonical manifests and are checked by `verify`; duplicating the
full hash list here would create a second mutable source of truth.

## Behavioral baseline status

The prompt set freezes current documented behavior with one happy path, one
failure or refusal case, and one stress boundary per skill. No prompt names a
proposed extraction, shortened wording, or candidate structure. Automated host
replays and output captures are intentionally deferred to each isolated Wave 1
round, immediately before its candidate is created. This respects the user's
instruction not to use Claude Code validation; a later equivalence verdict must
not claim PASS until the current and candidate outputs have been run and judged
with permitted executors.
