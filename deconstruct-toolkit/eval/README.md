# Eval suite

Structural eval specs + a CI-runnable validator that catches structural problems before LLM evaluation runs.

## What this is

7 eval cases as YAML files in [`cases/`](cases/), each pairing a real-artifact fixture (in `skills/<skill>/assets/sample-*.md`) with a `must_find` checklist. The cases were defined in [`docs/design-proposal.md §9`](../docs/design-proposal.md) and locked at v0.1.0.

| Case | Skill | Fixture |
|---|---|---|
| `artifact-deconstruct-01-dropbox-landing` | artifact-deconstruct | Dropbox landing 2024 |
| `artifact-deconstruct-02-notion-onboarding` | artifact-deconstruct | Notion onboarding pack |
| `artifact-deconstruct-03-stripe-signup` | artifact-deconstruct | Stripe signup flow |
| `argument-deconstruct-01-op-ed` | argument-deconstruct | Op-ed on AI regulation |
| `argument-deconstruct-02-vc-pitch` | argument-deconstruct | Series A VC pitch memo |
| `assumption-surface-01-strategy-memo` | assumption-surface | Q3 SaaS strategy memo |
| `assumption-surface-02-tweet-thread` | assumption-surface | Productivity influencer thread |

## What this is NOT

This folder does **not** ship an LLM-eval runner. Running the actual deconstruction through Claude Code (manually, via SDK, or via a future runner) and scoring output against `must_find` happens **locally / on-demand**, not in CI.

The reasons:

- LLM evaluation costs real API budget; running 7 cases × 4 skills on every PR is wasteful
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

## Adding new cases

To add a new case for an existing skill:

1. Pick a real artifact (per design-proposal Q1: real public sources, ≤5KB, hand-converted from public DOM)
2. Drop the fixture in `skills/<skill-name>/assets/sample-<descriptive-name>.md`
3. Append `## Annotations for evaluator` block at the bottom listing must_find expectations
4. Create `eval/cases/<skill>-NN-<short-name>.yaml`
5. Run `python3 deconstruct-toolkit/scripts/check-eval-cases.py` to verify
6. Commit with `feat(deconstruct-toolkit): add eval case <name>`

For new skills (v0.2+), the same pattern applies — each new skill ships ≥2 fixtures + matching cases.
