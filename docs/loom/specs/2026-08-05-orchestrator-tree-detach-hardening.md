# Brief: orchestrator-tree detach hardening + round-3 retro residue

Date: 2026-08-05
Status: frozen (user goal-locked: 「直接做——四項一次收掉吧」)
Consumer: writing-plans → SDD

## Problem

During the 0.55.0 extraction-batch arc, a reviewer arm dispatched with
`isolation: worktree` still operated on the ORCHESTRATOR'S main working
tree — the dispatch packet names absolute paths under the main repo, so
worktree isolation does not constrain where the agent runs git — and
left it on a detached HEAD. The close-out commit then landed detached
(`[detached HEAD 7cea792e]`); recovery needed an ff-merge plus autostash.
The 0.52.0 worktree dispatch guidance teaches `git show` retrieval but
never forbids checking out in someone else's tree, and finishing has no
mechanical check that HEAD is attached before the close-out commit.

Two smaller residues from the same round-3 retrospective, both
adjudicated memory-grade (single occurrence, no rule change):

- The batch brief's Smallest-End-State clause "residues + pointers" was
  not itemized as a named deliverable inside Partition C, and rdr
  shipped with no pointer to its own design-evidence.md — three plan
  rounds and six per-task reviewers passed it; only a whole-branch docs
  arm caught it.
- Two word-count conventions (`wc -w` vs `len(text.split())`) differ by
  1 on the same file (4119 vs 4118), which cost two reviewer findings
  and a Decision Log clarification before the convention was named.

## Users

- Future orchestrators running finishing on this repo (mechanical gate).
- Worktree-isolated reviewer/implementer subagents reading the dispatch
  guidance (prose rule of the verifiable-action type).
- Future brief authors and reviewers (memory store recall).

## Smallest End State

1. `dispatch-hygiene-notes.md` §Worktree-isolated reviewer dispatch
   carries a fourth bullet: never `git checkout` / `git switch` in the
   orchestrator's main working tree; read via `git show`, execute in
   your own worktree. Pinned in
   `test_dispatch_hygiene_worktree_section.py` (fourth bolded phrase).
2. `finishing-a-development-branch/SKILL.md` Step 8 carries an
   attached-HEAD check bullet: `git symbolic-ref -q HEAD` must resolve
   to the branch being finished before the close-out commit; detached →
   STOP and reattach, never commit detached. Pinned in a new
   `test_finishing_attached_head_check.py`.
3. `docs/loom/memory/` carries two new entries (brief-obligation
   itemization; word-count convention naming) with byte-identical index
   lines, and `reviewer-dispatch-isolated-worktree.md` gains the third
   variant (isolation granted but bypassed via absolute paths).
4. loom-code bumps to 0.56.0 with a CHANGELOG entry; the shipping-version
   pin test moves to 0.56.0.

## Alternatives considered

- dcg-level mechanical block of `git checkout` in the main tree during
  dispatch windows — rejected: heavier machinery than the incident
  warrants; the finishing attached-HEAD gate already provides the
  mechanical backstop, and the prose rule is of the verifiable-action
  type that weak-model probes have shown survives.
- Backlog entry instead of fixing now — rejected by the user's
  goal-lock; both hardening lines are one-bullet cheap.

## What becomes obsolete

Nothing removed. The 0.52.0 worktree bullets stay; the new bullet
composes with them (checked against the falsified-neighbor pass: the
section preamble and sibling bullets make no claim the new bullet
contradicts).

## Out of scope

- Any change to reviewer agent contracts (`agents/*.md`) — the rule
  targets dispatch packets and the orchestrator's own gate, not the
  contract files; by-path probing machinery not needed this arc.
- The SDD ~80-word provenance cluster and family-wide audience-misplaced
  markers (ride-along list, untouched).
- loom-spec watch-list files.
- Retro-fitting the word-count convention into existing documents —
  forward-only, per the memory entry's own rule.

## Decisions

- The finishing bullet lands in Step 8 (git hygiene), immediately before
  the `git status --short` bullet — it is a pre-commit tree-state check,
  same family as its siblings.
- The two prose rules are the fix; no store entry duplicates them (the
  skill text IS the enforcement). The store additions cover only the two
  non-mechanized lessons plus the existing entry's new variant.
- Word-count counting convention for this arc's own documents:
  `len(text.split())` (matches the pin-test convention).
