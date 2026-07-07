# Brief: loom-memory recording timing — same branch, not post-merge

## Design-side on-ramp

Axis 0 negative guard applies (process/convention fix on existing loom
machinery) — silently skipped.

## Problem

JTBD: when I (the orchestrator) discover a durable, already-known fact
during a branch's work, I need the branch's own close-out flow to
prompt me to record it on THAT branch — so recording a practice never
costs a separate post-merge branch+PR cycle.

## Users

The loom-code orchestrator, at the moment it runs
`finishing-a-development-branch`'s close-out flow — the one mandatory
checkpoint every branch passes through before push, regardless of when
during the branch's life an insight was discovered.

## Smallest End State

1. `docs/loom/memory/README.md` charter gains a `## When to record`
   section: a fact already known before the branch closes (not
   merge-required to observe) MUST land in that same branch/PR, never
   a separate post-merge branch. The one exception — a fact only
   confirmable by observing real post-merge/installed behavior — still
   requires a follow-up branch, but should be batched, not one-PR-per-
   discovery.
2. `finishing-a-development-branch/SKILL.md`'s Step 8 git-hygiene list
   gains one sub-bullet (parallel to the existing "Living-spec index
   regen" bullet) pointing at the charter's new section — never
   copying its rule body.
3. One grep-marker regression test.

**Explicitly out of scope**: no change to the `docs/loom/memory/`
jurisdiction table itself, no change to `record`/`recall`/`prune` verb
logic — this is purely a "when" addition, not a "what" or "how" change.

## Current State Evidence

- **Forward** — `docs/loom/memory/README.md` (charter) has no section
  addressing WHEN a fact should be recorded relative to a branch's
  lifecycle — only WHERE (the jurisdiction table).
- **Reverse** — `finishing-a-development-branch/SKILL.md` Step 8
  (git hygiene before the close-out commit) already has a precedent
  for exactly this shape: an orchestrator-only, once-per-branch,
  fold-into-this-commit action (the "Living-spec index regen" bullet).
  The new bullet follows that same pattern.
- **Error** — today's failure mode, observed twice in one session: two
  durable facts (kind-gate review-weight; cold-reader process
  dogfood), both known before their respective branches closed, were
  recorded only AFTER merge — once as a direct-to-main commit
  (bypassing review) and the pattern would otherwise have required a
  second branch+PR cycle. Confirmed by the user's explicit complaint.

## Decision

Add a `## When to record` section to the loom-memory charter (SSOT)
and one pointer bullet in `finishing-a-development-branch`'s Step 8,
plus a grep-marker regression test.

## Out of Scope

- Jurisdiction table changes, verb-logic changes (record/recall/prune).
- Retrofitting the two already-recorded practices from this session
  (historical; not touched).
- Any change to `loom-pipeline:loom-memory`'s own SKILL.md — the fix
  lives entirely in the charter (what all verbs already point to) and
  in the one skill that runs at branch-close time.

## What Becomes Obsolete

Nothing removed — this closes a documented gap, not a stale rule.
