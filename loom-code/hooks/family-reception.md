# Loom Family Reception

You have the loom family of plugins available. One rule covers all of it:

> **要用 loom-X, 就從 using-loom-X 開始.** Every plugin's entry point is its
> `using-loom-*` skill — start there, it routes you the rest of the way.

## Plain-relay trigger card

<PLAIN-RELAY>
Before EVERY user-visible reply while a loom skill is active:
- 1st line = plain-language conclusion, in the conversation language.
- Translate every internal token (PASS_WITH_NOTES, Axis, Wave, 🔴🟡🟢) — glossary: loom-code/hooks/plain-relay.md.
- Default reply ≤10 lines; ONE decision per ask (≤3 options + a recommended default).
- Never lead with a raw gate/error string — plain words first.
</PLAIN-RELAY>

## Brief before a complex fork

When a fork this router surfaces is genuinely complex — **≥3 trade-offs,
≥2 implementation paths, or architectural blast radius** — brief before
you ask: run `dev-workflow:brief-before-asking` first, then fire the
ask. The brief's first line states, in plain words, *what this choice
changes for the user and why it matters* — the stakes come before the
options, because a user can read three well-framed options and still
not see the point. `dev-workflow:brief-before-asking` owns the 6-block
briefing format (Mental Model first); the trigger threshold above is
the canonical gate for when a fork is complex enough to warrant it.
This is a floor, not politeness: an unbriefed complex fork hands the
user a choice they cannot evaluate. The 6 router/skill copies of this
rule point here — edit the threshold or framing in this section, not
in the copies.

## Family map

- `using-loom-design` — jurisdiction: the design side — discovery (problem
  space: user-insights / business-value), product constitution
  (product-principles), UI/UX surface (design-system / interaction-flows /
  design-critic), requirement fan-out (spec-expansion / completeness-critic).
  Start here for product-shaped work or when unsure which design-side skill
  applies.
- `using-loom-code` — jurisdiction: implementation (brainstorm, plan, build,
  review, ship). Start here to write or change code.
- `using-loom-pipeline` — jurisdiction: orchestration (drives the four
  Workflow-driven stations end-to-end; discovery stays interactive). Start
  here only when you explicitly want the whole pipeline run for you.

## Three doors

1. **Interactive design-side** — `using-loom-design` answers direct asks
   across discovery / product-principles / interface-design / spec and also
   recommends the next station in the journey.
2. **Interactive loom-code** — `using-loom-code` answers direct asks to
   write/change/review code, and is the unskippable gate before any brief.
3. **Explicit Workflow (pipeline + batch)** — `using-loom-pipeline` drives
   the four Workflow-driven stations end-to-end, single-run or batched. This door is
   **described here for awareness only — it is never auto-opened**. It
   fires **only on explicit user invocation** ("run the loom pipeline",
   "全管線跑一遍"); no ambient signal ever opens it on its own.

## On-ramp criteria table (SSOT)

This table is the single source of truth — every family entry's §Intake references it; do not copy its rows elsewhere.

| # | Condition | Recommendation |
|---|-----------|-----------------|
| 1 | No `docs/loom/PRINCIPLES.md` in the target repo AND the work is product-shaped (new product/feature idea, not an increment) | Suggest **using-loom-design first** (routes to the product-principles station) |
| 2 | The work touches a user-facing surface AND no `DESIGN.md`/`ui-flows.md` already covers it | Suggest **using-loom-design first** (routes to the interface-design station) |
| 3 | The work is multi-state/multi-object behavior AND no spec or change-folder exists for it | Suggest **using-loom-design first** (routes to the spec station) |
| Negative guard | The work is a bug fix, a refactor, or a test-covered increment | **Do not interrupt** — proceed directly, skip the recommendation silently |
| 4 | The work is product-shaped AND no `docs/loom/discovery/*/user-insights.md` already covers it AND the problem/users cannot yet be articulated with evidence (the user would be guessing at who-needs-what) | Suggest **using-loom-design first** (routes to the discovery station) |
| 5 | Neither `docs/loom/backlog/` nor `docs/loom/DIRECTION.md` in the target repo (the queue layer is not adopted; the verb refuses on either existing) AND the work is loom-family-scoped | Suggest running **loom-init** once — the scaffold verb shipped in loom-code |

When both row 4 and row 1 fire, recommend discovery first — the principles station consumes discovery's value-commitment output.

**Recommend ONCE, as a standalone ask.** Surface the recommendation a
single time — on Claude Code via the `AskUserQuestion` tool, on any
other host as a prose ask whose only question is this choice — never
as a bullet folded into another briefing. The brief's
`## Design-side on-ramp` line stays `pending` until the user answers;
the agent may state a recommendation (e.g. "direct — prior vault notes
cover the principles station") but never records the answer on the
user's behalf. Once answered, never re-raise it on follow-up turns of
the same task.

### On-ramp standing choices

A repo may pre-answer a row for every future arc instead of asking
each time. Record that in `docs/loom/DIRECTION.md` under
`## On-ramp standing choices`, one entry per row:

`- row <n> (<station>): standing <direct|detour> — <reason> (<YYYY-MM-DD>)`

A standing entry lets Axis 0 write the `standing` form on the brief
line without asking. It is a decision, revisited only by editing
DIRECTION.md.

## Intake hygiene

**Batch the intake.** When an entry skill needs input it cannot proceed
without (the seed idea, target directory, git state), collect everything
missing in ONE ask — never serially across turns. The on-ramp choice is
NOT part of that batch — it is asked on its own (§On-ramp above) once
the seed is known, since the rows cannot be evaluated before the seed
exists. PRINCIPLES.md and design docs stay governed by the on-ramp
table above: never a prerequisite to *run* loom-design — but the
*choice* is gated, because writing-plans intake and the plan-commit
guard refuse an unresolved on-ramp line. See `handoff-brief-format.md`
for the brief line's grammar. (Evidence + contamination caveats:
monkey-skills `docs/harness-audit/2026-07-06-iteration-roadmap.md`
item 7.)

## DIRECTION.md charter

Rules for editing `docs/loom/DIRECTION.md`: [`direction-charter.md`](direction-charter.md) (read on demand, never copied here).

## Recall before you start

If the target repo has `docs/loom/memory/`, run a recall pass via the
`loom-memory` skill before starting loom work — recorded practices and
gotchas surface before you re-commit them.

> **Pointer only.** This hook preloads no memory content; recall pulls
> on demand (pull-not-push stays intact).

User-facing narration follows the family relay discipline — read
`loom-code/hooks/family-relay.md` on demand (pull, not preload).
