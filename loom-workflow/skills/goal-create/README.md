# Goal Create

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Draft a goal condition. Two named modes: **SESSION** writes the
> four-field goal a long-running agent run is checked against; **ARC**
> drafts a repository's purpose artifact for the user to land.

---

## Overview — what this skill does

This skill drafts one of two things, chosen by what the user asks for —
never by the agent guessing from context.

- **SESSION mode** produces the four-field goal condition —
  `Outcome`, `Constraints`, `Verification`, `Stop-when` — that a
  long-running agent run is checked against, e.g. for Claude Code's
  `/goal` command. The field order and each field's definition are the
  authoritative content of `references/goal-shape.md`; the input slots a
  draft is built from, the refusal rule when one is empty, and the
  provenance tag each field must carry live in `references/input-floor.md`.
  Before presenting a draft, the skill runs it through a mechanical floor,
  `scripts/goal_lint.py` — structure only, never a judgment call on
  whether the prose actually reads as decidable.

- **ARC mode** produces a draft `Why` and `Done when` for the
  repository's purpose artifact, `docs/loom/PURPOSE.md`. It never writes
  that file itself — the draft is only ever landed by the user's own
  confirmation. When the repository has neither a purpose artifact nor
  any `docs/loom/` store at all, ARC reports itself not applicable and
  scaffolds nothing.

This README is a human-facing overview. `SKILL.md` in this folder is the
operational contract — the source both modes and both reference files
are read from; this file does not restate it.

---

## Invocation

This skill never fires on its own. It is named as an available option at
two points where the need for a goal is already visible:
`loom-workflow:handoff`'s Prepare mode, and the unanswered-purpose
message `loom-code`'s purpose-link check prints. Naming it there does not
invoke it.

---

## Files

```
goal-create/
├── README.md              <- English (this file)
├── README.ja.md           <- 日本語
├── README.zh-TW.md        <- 繁體中文
├── SKILL.md               <- operational file (for Claude)
├── references/
│   ├── goal-shape.md       <- the four-field goal shape, SESSION's SSOT
│   └── input-floor.md      <- input slots, refusal rule, bar, provenance tags
└── scripts/
    └── goal_lint.py        <- SESSION's mechanical floor
```
