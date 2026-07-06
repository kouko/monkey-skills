# Loom Family Reception

You have the loom family of plugins available. One rule covers all of it:

> **要用 loom-X, 就從 using-loom-X 開始.** Every plugin's entry point is its
> `using-loom-*` skill — start there, it routes you the rest of the way.

## Family map

- `using-loom-product-principles` — jurisdiction: product constitution
  (north star + falsifiable principles). Start here for a new product idea.
- `using-loom-interface-design` — jurisdiction: UI/UX surface (DESIGN.md +
  ui-flows.md). Start here to design how a feature looks and behaves.
- `using-loom-spec` — jurisdiction: requirement fan-out (spec draft, edge
  cases, acceptance criteria). Start here to expand a feature into a spec.
- `using-loom-code` — jurisdiction: implementation (brainstorm, plan, build,
  review, ship). Start here to write or change code.
- `using-loom-pipeline` — jurisdiction: orchestration (drives the other four
  end-to-end via Workflow segments, interactive or batch). Start here only
  when you explicitly want the whole pipeline run for you.

## Three doors

1. **Interactive design-side** — `using-loom-product-principles`,
   `using-loom-interface-design`, `using-loom-spec` answer direct asks and
   also recommend the next station in the journey.
2. **Interactive loom-code** — `using-loom-code` answers direct asks to
   write/change/review code, and is the unskippable gate before any brief.
3. **Explicit Workflow (pipeline + batch)** — `using-loom-pipeline` drives
   all four stations end-to-end, single-run or batched. This door is
   **described here for awareness only — it is never auto-opened**. It
   fires **only on explicit user invocation** ("run the loom pipeline",
   "全管線跑一遍"); no ambient signal ever opens it on its own.

## On-ramp criteria table (SSOT)

This table is the single source of truth. Every family entry's §Intake
references it — do not copy its rows elsewhere.

| # | Condition | Recommendation |
|---|-----------|-----------------|
| 1 | No `docs/loom/PRINCIPLES.md` in the target repo AND the work is product-shaped (new product/feature idea, not an increment) | Suggest **using-loom-product-principles first** |
| 2 | The work touches a user-facing surface AND no `DESIGN.md`/`ui-flows.md` already covers it | Suggest **using-loom-interface-design first** |
| 3 | The work is multi-state/multi-object behavior AND no spec or change-folder exists for it | Suggest **using-loom-spec first** |
| Negative guard | The work is a bug fix, a refactor, or a test-covered increment | **Do not interrupt** — proceed directly, skip the recommendation silently |

**Recommend ONCE, never nag.** Surface the recommendation a single time,
record the user's choice, then proceed either way — do not re-ask on
follow-up turns of the same task.

## Intake hygiene

**Batch the intake.** When an entry skill needs input it cannot proceed
without (the seed idea, target directory, git state), collect everything
missing in ONE ask — never serially across turns — and fold the on-ramp
recommendation (if one fired) into that same single ask. PRINCIPLES.md
and design docs stay governed by the on-ramp table above: they are
recommendations to surface once, never blocking prerequisites.
(Evidence + contamination caveats: monkey-skills
`docs/harness-audit/2026-07-06-iteration-roadmap.md` item 7.)

## Recall before you start

If the target repo has `docs/loom/memory/`, run a recall pass via the
`loom-memory` skill before starting loom work — recorded practices and
gotchas surface before you re-commit them.

> **Pointer only.** This hook preloads no memory content; recall pulls
> on demand (pull-not-push stays intact).
