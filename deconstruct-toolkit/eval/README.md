# Eval suite

Structural eval specs + a CI-runnable validator that catches structural problems before LLM evaluation runs.

## What this is

15 eval cases as YAML files in [`cases/`](cases/), each pairing a fixture (in `skills/<skill>/assets/sample-*.md`) with a `must_find` checklist.

- 7 v0.1.0 cases — original Anglo / EN-register fixtures, locked per [`docs/design-proposal.md §9`](../docs/design-proposal.md)
- 8 v0.2.0 cultural-variant cases — JP and ZH-register fixtures testing the language variants of the 4 culturally-sensitive lenses (per [`docs/v0.2.0-cultural-variants-design-proposal.md §8`](../docs/v0.2.0-cultural-variants-design-proposal.md))

### v0.1.0 cases (Anglo / EN register)

| Case | Skill | Fixture |
|---|---|---|
| `artifact-deconstruct-01-dropbox-landing` | artifact-deconstruct | Dropbox landing 2024 (real-fetched) |
| `artifact-deconstruct-02-notion-onboarding` | artifact-deconstruct | Notion onboarding pack (synthetic-representative) |
| `artifact-deconstruct-03-stripe-signup` | artifact-deconstruct | Stripe signup flow (synthetic-representative) |
| `argument-deconstruct-01-op-ed` | argument-deconstruct | Op-ed on AI regulation |
| `argument-deconstruct-02-vc-pitch` | argument-deconstruct | Series A VC pitch memo |
| `assumption-surface-01-strategy-memo` | assumption-surface | Q3 SaaS strategy memo |
| `assumption-surface-02-tweet-thread` | assumption-surface | Productivity influencer thread |

### v0.2.0 cultural-variant cases (JP + ZH register)

All 8 are synthetic-representative artifacts with explicit honesty flags in metadata (per design proposal §11 Q3). Each eval case names the SPECIFIC variant in `expected_lenses` (e.g. `lens-rhetoric-ja`, NOT `lens-rhetoric`) and includes a `variant-named-in-output` must_find item to ensure the analysis attributes which language variant was applied (anti-Anglo-default safeguard).

| Case | Skill | Variant tested | Fixture |
|---|---|---|---|
| `artifact-deconstruct-04-ja-op-ed` | artifact-deconstruct | `lens-rhetoric-ja` | 社説「学校のICT化」(kishōtenketsu) |
| `artifact-deconstruct-05-ja-ec-lp` | artifact-deconstruct | `lens-persuasion-ja` | 老舗薬房 養心丸 定期購入 LP |
| `artifact-deconstruct-06-ja-business-letter` | artifact-deconstruct | `lens-genre-ja` | 取引開始のご挨拶 (7-move 拝啓-formula) |
| `artifact-deconstruct-07-ja-political-speech` | artifact-deconstruct | `lens-frame-ja` | 経産大臣 記者会見 (建前/本音 + 空気) |
| `artifact-deconstruct-08-zh-op-ed` | artifact-deconstruct | `lens-rhetoric-zh` | 社論〈青年返鄉與地方創生〉(通變 + 用典) |
| `artifact-deconstruct-09-zh-ec-lp` | artifact-deconstruct | `lens-persuasion-zh` | 永和阿婆豆漿粉 LP (老字號 + 關係 + 面子) |
| `artifact-deconstruct-10-zh-gongwen` | artifact-deconstruct | `lens-genre-zh` | 函 三段式 (TW 行政院 公文 conventions) |
| `artifact-deconstruct-11-zh-political-speech` | artifact-deconstruct | `lens-frame-zh` | 縣長施政總質詢答詢 (面子 + 陰陽 + 圈子) |

## What this is NOT

This folder does **not** ship an LLM-eval runner. Running the actual deconstruction through Claude Code (manually, via SDK, or via a future runner) and scoring output against `must_find` happens **locally / on-demand**, not in CI.

The reasons:

- LLM evaluation costs real API budget; running 15 cases × 4 skills on every PR is wasteful
- LLM scoring is judgment-based; CI gates should be deterministic
- v0.1 priorities: structural correctness first, automated quality eval is v1.0 work

## What CI does check

[`scripts/check-eval-cases.py`](../scripts/check-eval-cases.py) validates:

1. **Each eval YAML well-formed** — has `name`, `skill`, `fixture`, `input_query`, `must_find` keys; `must_find` is a non-empty list of `{id, description, ...}` dicts
2. **Each fixture file exists** on disk
3. **Each fixture has the `## Annotations for evaluator` block** that documents what `must_find` should detect
4. **Each lens reference has primary-source citation** (`> **Source(s)**: ...` in the first 1000 characters)
5. **Each skill folder has flat single-level subfolders only** (CLAUDE.md compliance)

```bash
# Run from anywhere in the repo
python3 deconstruct-toolkit/scripts/check-eval-cases.py
python3 deconstruct-toolkit/scripts/check-eval-cases.py --verbose  # show passes too
```

Exit 0 = all structural checks pass. Exit 1 = at least one FAIL.

## How to run an actual LLM eval (local workflow)

Until automated runners ship in v1.0, the manual workflow is:

1. Pick a case YAML and read its `input_query`, `expected_lenses`, and `must_find`
2. Open the corresponding fixture, copy the artifact body (above the `## Annotations for evaluator` line) into a Claude Code conversation
3. Invoke the relevant skill: `/deconstruct-toolkit:artifact-deconstruct` (or argument / assumption)
4. Compare the skill's output against the fixture's `## Annotations for evaluator` block — that block is the ground-truth score sheet
5. Score: 🟢 PASS (100% must_find satisfied) / 🟡 PARTIAL (70%+) / 🔴 FAIL (<70% or wrong lens)

Tracking results in `docs/eval-results-vX.Y.Z.md` is recommended for posterity.

## Cultural-variant eval workflow (v0.2.0+)

For artifacts in JP / ZH register, the variant-selection happens BEFORE applying the lens. The eval workflow:

1. Read the case YAML — note `expected_lenses` value (specific variant: `lens-rhetoric-ja`, etc.)
2. Open the fixture; confirm the artifact body language + register match what the variant claims
3. Invoke `/deconstruct-toolkit:artifact-deconstruct` with the artifact
4. Verify the skill's output:
   - Explicitly states which variant was applied (e.g., "Applied lens-rhetoric-ja")
   - Surfaces the variant-specific moves listed in the fixture's `## Annotations for evaluator` block (起承転結 4-part / 六觀 6-perspective / 公文 三段式 / etc.)
   - Does NOT silently fall back to `-anglo` analysis on a non-EN artifact (this is the failure mode `variant-named-in-output` must_find guards against)

If the analysis silently uses `-anglo` on a JP/ZH artifact without acknowledgement, that is a 🔴 FAIL even if the surface findings look reasonable — it reproduces the v0.1.0 grounding gap that v0.2.0 was designed to close.

## Adding new cases

To add a new case for an existing skill:

1. Pick a real artifact (per design-proposal Q1: real public sources, ≤5KB, hand-converted from public DOM) OR a synthetic-representative fixture (if real-fetch is impractical) WITH explicit honesty flag in metadata
2. Drop the fixture in `skills/<skill-name>/assets/sample-<descriptive-name>.md`
3. Append `## Annotations for evaluator` block at the bottom listing must_find expectations
4. Create `eval/cases/<skill>-NN-<short-name>.yaml`
5. For cultural-variant cases: name the SPECIFIC variant in `expected_lenses` (not the universal-core lens name) + include a `variant-named-in-output` must_find item
6. Run `python3 deconstruct-toolkit/scripts/check-eval-cases.py` to verify
7. Commit with `feat(deconstruct-toolkit): add eval case <name>`

For new skills (v0.2+), the same pattern applies — each new skill ships ≥2 fixtures + matching cases.
