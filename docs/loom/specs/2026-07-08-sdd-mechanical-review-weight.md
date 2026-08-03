# Brief: SDD per-task mechanical review-weight exemption

## Design-side on-ramp

Axis 0 negative guard applies (bug-fix/refactor-shaped change to existing
loom-code machinery, not new product-shaped work) — silently skipped.

## Problem

JTBD: when `subagent-driven-development` (SDD) dispatches a task whose
content is an **identical, exact-spec mechanical edit** (e.g. inserting
the same one-line pointer into N sibling files), the orchestrator needs
a way to have SDD skip the full implementer+spec-reviewer+code-quality-
reviewer triad and rely on a deterministic self-check instead — so
review effort concentrates on tasks that carry real logic/behavior risk.

This is NOT "make review faster generically" — the review mechanism
itself (two-reviewer union, full 9-dimension scoring) is validated and
must stay untouched for logic-bearing changes. The job is narrower:
give SDD's existing plan schema a way to EXPRESS task kind so the triad
process can honor it, where today no such expression exists.

## Users

The loom-code orchestrator (any session running SDD) — specifically,
whoever authors a `writing-plans` plan (today: the same orchestrator)
and whoever executes it via SDD.

## Smallest End State

Add ONE opt-in per-task field, `Review-weight: mechanical`, to
`writing-plans`' plan schema — parallel in spirit to the existing
`Independent: true` opt-in marker:

- **Default (field absent) = today's behavior, unchanged.** Every
  existing plan and every task that doesn't set this field still gets
  the full implementer + spec-reviewer + code-quality-reviewer triad.
- **Co-condition, not a free-standing flag**: a task may only set
  `Review-weight: mechanical` when its Description is an identical or
  near-identical edit reproducible from an exact spec (a concrete
  string/diff the implementer must match verbatim) — never for logic,
  heuristic, hook, or security-surface changes, regardless of size.
  `plan-document-reviewer` gets a new check (Check 16) verifying this
  co-condition holds, not just that the field is present.
- **SDD's per-task triad**: when a task carries `Review-weight:
  mechanical` and the implementer returns `DONE`, SDD skips the
  spec-reviewer + code-quality-reviewer dispatch. Instead the
  orchestrator runs a deterministic self-check (e.g. grep/diff
  confirming the exact expected string landed in each target file). A
  match resolves the task with no reviewer verdict needed; a mismatch
  falls back to the full triad (fail-closed toward review, never
  toward skipping on ambiguity).
- **No LOC threshold anywhere.** The gate is task KIND, not size.

**Explicitly out of scope for this change**: `requesting-code-review`
(whole-branch review) is untouched. Per this session's `proposal-
critique` verdict, introducing a new whole-branch-level lightweight
tier is **DEFERRED** — no evidence yet that one is needed (every
whole-branch review this session either touched real logic/hooks, or
was a small-but-genuine behavior nudge where the existing full panel
produced real, if minor, findings). Do not build it now.

## Current State Evidence

- **Forward** — `loom-code/skills/subagent-driven-development/SKILL.md:100-103`:
  the per-task triad's step 3 unconditionally dispatches
  `spec-reviewer` + `code-quality-reviewer` for every `DONE` /
  `DONE_WITH_CONCERNS` task. No branch anywhere consults task kind.
- **Reverse** — `loom-code/skills/writing-plans/references/plan-format.md`:
  the schema's only existing per-task opt-in markers are `Independent:
  true` + `Files touched` (both scoped to parallelism, §"Parallel-
  dispatch markup"); no field expresses review-weight or task kind.
- **Boundary** — `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md:45-47`
  (Checks 13-15): the precedent pattern for validating a per-task
  opt-in marker against a co-condition (Check 13/14 validate
  `Independent: true` against `Files touched` disjointness). A new
  Check 16 for `Review-weight: mechanical` follows this exact pattern.
- **Error** — today, an *informal* version of this convention already
  exists and is inert: this session's own plan
  (`docs/loom/plans/2026-07-07-loom-user-communication-overhaul-tasks.md`,
  Tasks 8-10) noted "batch-mechanical, identical edit" in prose, but
  nothing reads or enforces that note — confirmed by execution: all
  three tasks got full triads anyway (21 subagent dispatches for 3
  identical one-line edits).
- **Data**: N/A — no data model change.

## Decision

Add `Review-weight: mechanical` as an opt-in, kind-gated per-task field
across three files: `plan-format.md` (schema + worked example),
`plan-document-reviewer-prompt.md` (Check 16), and
`subagent-driven-development/SKILL.md` (the per-task triad's skip
branch + self-check procedure). Ship a mechanical regression test
(grep-based, matching this repo's existing `test_family_relay.py`
convention) asserting the schema field, the check, and the SDD branch
text all exist and cross-reference consistently.

Ship as a `loom-code` version bump (both plugin manifests + a
`CHANGELOG.md` entry), per this repo's existing release convention for
loom-code plugin changes.

## Out of Scope

- `requesting-code-review` / whole-branch review tiering (DEFERRED —
  see Smallest End State).
- Any LOC-based threshold, anywhere.
- Retrofitting the already-merged `2026-07-07-loom-user-communication-
  overhaul-tasks.md` plan (historical record; not touched).
- A middle "Standard" review tier (DEFERRED per this session's
  proposal-critique — no evidenced need).

## Alternatives Considered (Axis 4)

Already covered by this session's `dev-workflow:proposal-critique`
pass (with WebSearch verification) — not re-run:

1. **Diff-size (LOC) tiering** — rejected. Counter-evidence within this
   same session: a 20-30-line logic change (Stop-hook threshold fix)
   would have fallen into a "<50 lines → light review" bucket and
   plausibly shipped a real false-positive bug the full two-reviewer
   panel caught; conversely 1-line pointer edits got full triads
   despite being trivially mechanical. LOC is a weak proxy for
   review-need; task KIND is not.
2. **"Top AI-agent frameworks use dual-identical-review as standard
   practice"** — the industry-comparison argument for keeping the
   status quo untouched — checked via WebSearch and found **incorrect
   as cited**: AutoGen's documented pattern is *specialized* reviewer
   agents (different prompts per dimension), the opposite of identical-
   prompt redundancy; SWE-agent's core architecture is a single-agent
   ACI, no dual-review design found. The underlying *mechanism*
   (redundant same-prompt sampling reduces variance-driven misses) is
   independently grounded via self-consistency / ensemble-decoding
   research and this repo's own G4 dogfood data — that citation
   survives; the named-framework claim does not.
3. **Do nothing / rely on operator discipline** — rejected as
   insufficient: this session is the counter-example — the informal
   convention already existed in prose and was not followed, precisely
   because nothing made it mechanically checkable.

## What Becomes Obsolete

The informal, unenforced "batch-mechanical, identical edit" prose
convention (as used ad hoc in plan `Notes` sections) becomes obsolete,
replaced by the formal `Review-weight: mechanical` field +
plan-document-reviewer Check 16 + SDD's explicit skip branch.

## Open Questions

None — all axes resolved from this session's own evidence; no user
input required before planning.
