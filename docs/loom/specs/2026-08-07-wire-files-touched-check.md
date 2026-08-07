# Brief — wire the declared-vs-actual files-touched comparator into branch close-out

Date: 2026-08-07 · Stage: brainstorming brief (consumed by writing-plans)

## Problem

When an SDD plan declares each task's `Files touched:` and its `Status:
done(<sha>)`, nothing checks that the declared file set matches what the
commit actually changed. An under-declaration (the commit touched a file
the plan never listed — often a machinery-coupled file: a guard, a
schema, a sibling the author forgot) ships silently. The job: **at branch
close-out, catch a task whose real diff exceeds its declared `Files
touched`, so the plan's declaration stays honest and reviewers can trust
it.** A measurement already proved the defect is real — 11 true wild
under-declarations across 10 commits found retrospectively on this repo's
own plan corpus.

## Users

The close-out orchestrator (a Claude session running
`finishing-a-development-branch`) on a branch that carries an SDD plan
with a `done(<sha>)` ledger. Secondary: the human reviewing the PR, who
inherits a declaration the check has vouched for. Not a marketplace
consumer — the comparator stays a repo-internal close-out check (see
Decision).

## Smallest End State

The comparator (`scripts/check_files_touched.py`, 480 lines, already
built and measured) runs as one new orchestrator-only sibling check in
`finishing-a-development-branch` Step 8, against the branch's own plan,
gating close-out on a real under-declaration — plus the two parser fixes
without which the wiring produces false noise on this repo's own plans.

Concretely, three pieces:

1. **Two parser fixes (TDD, in `scripts/check_files_touched.py`)** —
   both are silent-drop bugs the wiring would otherwise surface as false
   verdicts:
   - **Letter-suffixed task headings.** `_TASK_HDR` (`:87`,
     `r"^##\s+Task\s+(\d+)\b.*$"`) does not match `## Task 3a`; worse, the
     heading still matches `_TASK_BOUNDARY` (`:92`, `^##\s`), so the block
     is consumed as a boundary and vanishes with **zero parse_errors** —
     the dangerous silent direction. 13 plans / 51 headings affected.
   - **`Status:` annotation tails.** `_STATUS_DONE` (`:108`,
     `r"^done\(([0-9a-fA-F]{7,40})\)$"`) is `$`-anchored, so a real
     annotated line `- Status: done(c301c7be)  # spec-reviewer PASS; …`
     fails the match, falls through to a "not in ledger vocabulary"
     parse_error, and the whole plan mis-reports as exit 2 (loud-empty).
     This is gap 3b — a **wiring-blocking must-fix**: without it, the
     first close-out of a branch whose plan uses annotated `Status` lines
     (the repo's normal shape) spins exit 2 noise.

2. **The Step 8 sibling check** (in
   `finishing-a-development-branch/SKILL.md`) — orchestrator-only, ONCE
   per branch, keyed on "a plan file exists for this branch" (auditable
   from the diff → silent skip when no plan), calling
   `<repo-root>/scripts/check_files_touched.py` with a **loud N/A** when
   the script is absent (consuming repos adopting the flow may not have
   it — identical to the memory-store-integrity and backlog-close
   siblings). Gates on a real under-declaration (exit 1); reports exit 2
   (loud-empty) distinctly.

3. **Backlog reconciliation** — flip
   `2026-08-01-declared-vs-actual-files-touched-check-measured-wire-in-decision-pending.md`
   to record the wire-in decision, and attach `start:` re-triggers to the
   residual obligations that stay deferred (below).

## Current State Evidence

- **Forward** (declared → checked): `finishing-a-development-branch/SKILL.md`
  Step 8 runs the ONCE-per-branch sibling checks — living-spec index
  (~`:186`), archive-on-close (`:195`), memory-timing (`:216`),
  memory-store integrity (`:226`), backlog-close (`:255`),
  attached-HEAD (`:271`). A new sibling slots next to backlog-close.
- **Reverse** (who owns the comparator): `scripts/check_files_touched.py`
  is a repo-root standalone (NOT distributed via `distribute.py`; it
  ships in no plugin). It stays repo-root — no SSOT/sync machinery
  touches it.
- **Error** (current failure surface): exit contract at `:68-82` — 0 OK
  (NO_JOIN rows report but don't gate while ≥1 join key survives), 1
  flagged/unresolved-sha/parse-error, 2 loud-empty (0 tasks or 0 join
  keys, wins over 1). The two parser gaps both currently manifest as
  false exit-2 / silent-drop.
- **Data**: plan format `writing-plans/references/plan-format.md` — task
  heading `## Task <N>`, `Files touched:`, `Status: done(<sha>)`. The
  parser's regexes must track this format's real (annotated, suffixed)
  shapes.
- **Boundary**: the check reads only the branch's own plan and its
  `done(<sha>)` commits — machine-local shas, one plan. It never sweeps
  the repo corpus.
- Evidence paths: `scripts/check_files_touched.py`,
  `loom-code/skills/finishing-a-development-branch/SKILL.md`,
  `docs/loom/backlog/2026-08-01-declared-vs-actual-files-touched-check-measured-wire-in-decision-pending.md`.

## Decision

Wire the comparator in as a repo-internal Step 8 sibling, **script staying
at repo root** (user decision 2026-08-07: not moved into
`loom-code/scripts/`, no marketplace ship, no version bump — matching the
two existing siblings that call repo-root scripts and degrade to loud N/A
where absent). Fix exactly the two parser gaps that would otherwise make
the wiring emit false verdicts on this repo's own plans; leave every other
corpus-compat obligation deferred with a re-trigger. We do NOT: move the
script, add a CLI/config surface, sweep the historical corpus, or fix the
residual 🟢 debt (merge-commit empty actual set, duplicate `Files touched`
unions, `_normalize_plan_path` `src/./a.py` case) — none blocks a correct
close-out check on a well-formed current branch.

## Alternatives Considered

- **Move script into `loom-code/scripts/` and ship it** — rejected by the
  user: turns an internal check into marketplace-published plugin content,
  binds a version bump, and diverges from the house style of the two
  existing repo-root-calling siblings. In-repo house-style evidence
  outweighed the "consumers auto-get it" upside; industry web-search was
  not run because the fork is a repo-internal convention decision, not a
  general tech choice, and the house-style precedent is the stronger,
  more-relevant evidence.
- **Wire at SDD per-task instead of close-out batch** — the backlog's
  obligation (1); superseded by the earlier user decision to place it at
  finishing (catches the same under-declarations one close-out later, no
  per-task loop cost).
- **Fix all corpus-compat gaps now (nested-bullet Files touched, multi-sha
  `done(a+b)`, CJK paths)** — deferred: they don't block a correct check
  on a well-formed current branch; each gets a `start:` re-trigger.

## Out of Scope

- Moving/renaming the script; any marketplace/version-bump change.
- Nested-bullet `Files touched` parsing (8 tasks, 07-13 plan) — deferred.
- Multi-sha `done(a+b)` vocabulary — deferred.
- CJK path handling (`-c core.quotepath=off`) — deferred.
- Shared-commit semantics (per-commit union vs per-task) — deferred.
- Weak-model consumption probe — deferred by design (backlog obligation 7).
- Residual 🟢 debt (merge-commit empty set, duplicate unions,
  `claimed(@x)`/`blocked` branch tests, `_normalize_plan_path` `src/./a.py`).

## Open Questions

None blocking. The script-home fork (the one irreversible/outward-facing
decision) was resolved by the user; every remaining choice is mechanical
and inferable from the plan format + house style.
