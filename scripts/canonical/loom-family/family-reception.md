# Loom Family Reception

You may have one or more loom plugins available. One rule covers every installed
member:

> **要用 loom-X, 就從 using-loom-X 開始.** Every plugin's entry point is its
> `using-loom-*` skill — start there, it routes you the rest of the way.

**Sibling plugins are optional.** Never claim an uninstalled loom plugin or its
skills are available. A reference to another loom plugin is a recommendation or
handoff only: use it when that public skill is available; otherwise keep the
current plugin's completed artifact intact and state that the optional handoff
is unavailable.

## Plain-relay trigger card

<PLAIN-RELAY>
Before EVERY user-visible reply while a loom skill is active:
- 1st line = plain-language conclusion, in the conversation language.
- Translate every internal token (PASS_WITH_NOTES, Axis, Wave, 🔴🟡🟢) — glossary: packaged `plain-relay.md`.
- Default reply ≤10 lines; ONE decision per ask (≤3 options + a recommended default).
- Never lead with a raw gate/error string — plain words first.
</PLAIN-RELAY>

## Brief before a complex fork

When a fork this router surfaces is genuinely complex — **≥3 trade-offs,
≥2 implementation paths, or architectural blast radius** — brief before
you ask. If `dev-workflow:brief-before-asking` is available, use it; otherwise
produce the complete local six-block fallback: **Mental Model** explains the
thing and stakes, **Situation** gives current evidence, **Why this is a fork**
names the competing consequences, **Options** compares 2–3 paths, **My take**
recommends one with reasons, and **Open ends** states remaining uncertainty.
The brief's first line states, in plain words, *what this choice changes for the
user and why it matters* — stakes before options. The trigger threshold above is
the canonical gate for when a fork is complex enough to warrant it.
This is a floor, not politeness: an unbriefed complex fork hands the
user a choice they cannot evaluate. The 6 router/skill copies of this
rule point here — edit the threshold or framing in this section, not
in the copies.

## Family map

- `using-loom-design` (when installed) — jurisdiction: the design side — discovery (problem
  space: user-insights / business-value), product constitution
  (product-principles), UI/UX surface (design-system / interaction-flows /
  design-critic), requirement fan-out (spec-expansion / completeness-critic).
  Start here for product-shaped work or when unsure which design-side skill
  applies.
- `using-loom-code` (when installed) — jurisdiction: implementation (brainstorm, plan, build,
  review, ship). Start here to write or change code.
- `using-loom-pipeline` (when installed) — jurisdiction: orchestration (drives the four
  Workflow-driven stations end-to-end; discovery stays interactive). Start
  here only when you explicitly want the whole pipeline run for you.

## Three doors

1. **Interactive design-side** — `using-loom-design` answers direct asks
   across discovery / product-principles / interface-design / spec and also
   recommends the next station in the journey.
2. **Interactive loom-code** — when work enters code and its public skill is available,
   `using-loom-code` is the unskippable implementation gate. If unavailable, the
   owning plugin's path continues and reports the optional code handoff as unavailable.
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
| 4 | The work is product-shaped AND no `docs/loom/discovery/<date>-<slug>/user-insights.md` already covers it AND the problem/users cannot yet be articulated with evidence (the user would be guessing at who-needs-what) | Suggest **using-loom-design first** (routes to the discovery station) |
| 5 | Neither `docs/loom/backlog/` nor `docs/loom/KICKOFF-DEFAULTS.md` in the target repo (the queue layer is not adopted; the verb refuses on either existing) AND the work is loom-family-scoped | If the public **loom-init** capability is available, suggest running it once; otherwise skip this optional recommendation |

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
each time. Record that in `docs/loom/KICKOFF-DEFAULTS.md` under
`## On-ramp standing choices`, one entry per row:

`- row <n> (<station>): standing <direct|detour> — <reason> (<YYYY-MM-DD>)`

A standing entry lets Axis 0 write the `standing` form on the brief
line without asking. It is a decision, revisited only by editing
KICKOFF-DEFAULTS.md.

## Intake hygiene

**Batch the intake.** When an entry skill needs input it cannot proceed
without (the seed idea, target directory, git state), collect everything
missing in ONE ask — never serially across turns. The on-ramp choice is
NOT part of that batch — it is asked on its own (§On-ramp above) once
the seed is known, since the rows cannot be evaluated before the seed
exists. PRINCIPLES.md and design docs stay governed by the on-ramp
table above: never a prerequisite to *run* loom-design. The *choice* is gated
only when the receiving public skill makes it part of its own contract.
When the public `loom-code:writing-plans` skill is available, its own intake,
plan-commit guard, and packaged handoff grammar govern the on-ramp choice;
otherwise the owning plugin continues under its local artifact contract. (Evidence + contamination caveats:
monkey-skills `docs/harness-audit/2026-07-06-iteration-roadmap.md`
item 7.)

## Recall before you start

If the target repo has `docs/loom/memory/` and the public `loom-memory` skill is
available, run a recall pass before starting loom work — recorded practices and
gotchas surface before you re-commit them. If that skill is unavailable, keep
working from the current plugin's local contract; recall is an optional handoff.

> **Pointer only.** This hook preloads no memory content; recall pulls
> on demand (pull-not-push stays intact).

User-facing narration follows the family relay discipline — read the packaged
`family-relay.md` on demand (pull, not preload).
