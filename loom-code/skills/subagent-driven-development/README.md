# subagent-driven-development

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Splits a >1-hour or >1-module task into atomic ≤5-min units and dispatches three subagents per unit: **implementer** (worker, under the TDD iron law) + **spec-reviewer** + **code-quality-reviewer** (both evaluators). Verdicts grounded in 7 functional-copied standards + 2 rubrics + 2 checklists from `domain-teams:code-team`.

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## When this skill fires

Auto-routed by `using-loom-code` when **either**:

- the task is estimated >1 hour, OR
- the task touches >1 module / >1 file boundary.

Below either threshold, the agent goes directly to `tdd-iron-law` — three subagents per one-line change is not free.

## The triad

| Subagent | Role | Verdicts | Reads | Writes |
|---|---|---|---|---|
| `implementer` | worker | (status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) | task, spec, standards | code, tests, commits |
| `spec-reviewer` | evaluator | PASS / NEEDS_REVISION + gap list | artifact, spec, `checklists/spec-consistency.md` | verdict only |
| `code-quality-reviewer` | evaluator | PASS / PASS_WITH_NOTES / NEEDS_REVISION + seven-dimension scores + flags (🔴 / 🟡 / 🟢) | artifact, rubrics, checklist, 9 standards | verdict only |

Each task ships through one implementer round + one parallel reviewer round. Reviewer scopes are deliberately non-overlapping: spec-reviewer never grades quality; code-quality-reviewer never grades spec coverage. Blending them collapses the orchestrator's resolution signal.

## Acceptance test (Phase 1)

For a 4-task plan, SDD dispatches **12 subagents** (4 × 3) and returns 12 verdicts. All four task slots resolve `DONE` after at most 3 re-dispatch rounds each. This is the test `tests/skill-triggering/prompts/` covers in Phase 1.

## Knowledge layer (functional copies)

All `standards/`, `rubrics/`, `checklists/` files under this skill are byte-identical functional copies of `domain-teams/skills/code-team/{standards,rubrics,checklists}/` with a 5-line SSOT header prepended. To change a rule:

1. Edit canonical in `domain-teams:code-team`.
2. Run `python3 loom-code/scripts/distribute.py` in the same commit.
3. CI runs `loom-code/scripts/verify-drift.py`; any byte diff fails.

## Reviewer-output discipline (v0.7.0+)

The 3 reviewer agents (`spec-reviewer`, `code-quality-reviewer`, `code-reviewer`) each embed an **additional** in-file SSOT injection block — **reviewer-discipline-v1** — between BEGIN/END markers. Canonical text lives in `loom-code/scripts/_reviewer-discipline.md`:

- **R1** — every verdict carries a `standards_version` field (read from `plugin.json` `version`), so future readers can date the review against a specific rubric revision.
- **R2** — every flag / finding / gap must include an evidence-citation field (`where:` / `artifact:` / `spec_ref:`). Missing evidence flips the whole verdict to `NEEDS_REVISION` (opaque outputs are unfixable).

Auto-injected by `distribute.py` alongside the 12-rule engineering baseline. The implementer does NOT carry this block — it doesn't produce verdicts. `verify-drift.py` covers both blocks via the shared `expected_agent_text` function.

## What this skill does NOT do

- Does not write code — dispatches the implementer.
- Does not produce gate verdicts — dispatches reviewers.
- Does not decide whether SDD applies — `using-loom-code` routes.
- Does not produce the plan — `writing-plans` does (Phase 2; until then inline plan).
- Does not run after the final task — `finishing-a-development-branch` (Phase 3) closes the branch and delegates to `dev-workflow:git-memory`.

## See also

- [`SKILL.md`](SKILL.md) — orchestration spec.
- [`agents/implementer-prompt.md`](agents/implementer-prompt.md) / [`agents/spec-reviewer-prompt.md`](agents/spec-reviewer-prompt.md) / [`agents/code-quality-reviewer-prompt.md`](agents/code-quality-reviewer-prompt.md) — role prompts.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — iron law the implementer works under.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; routing rule for "when to use SDD."
- [`../../scripts/canonical/README.md`](../../scripts/canonical/README.md) — SSOT pointer + drift policy.
