# finishing-a-development-branch: fire the docs/loom/memory self-check at Step 6, not buried in Step 8

## Problem

`finishing-a-development-branch`'s docs/loom/memory self-check ("Memory-
timing check... record it into docs/loom/memory/ NOW") already exists,
but lives as one bullet among several inside Step 8's git-hygiene
checklist — procedurally disconnected from Step 6, the moment
`dev-workflow:git-memory` actually returns Decision/Learning/Gotcha
trailer content. This session hit the resulting lapse twice (documented
in machine-local memory `feedback_fold_repo_memory_writes_into_same_branch_pr.md`):
rich, clearly cross-branch-reusable trailer content got written into a
commit body, and the orchestrator (this agent) treated "trailers
written" as "memory handled," never separately asking whether any of
that same content also belonged in `docs/loom/memory/`. Per this
session's own institution-maintenance-style convention, 2 occurrences of
the same lapse crosses the threshold from "record it as a memory entry"
to "fix the rule/process itself." The job: make the self-check fire at
the moment its own trigger condition (non-empty trailer content) becomes
true, not at a later, easy-to-treat-as-mechanical checklist pass.

## Users

Whoever (human or orchestrating agent) runs `finishing-a-development-
branch` on a branch whose `git-memory` call returns a non-empty trailer
set — i.e. any memory-worthy branch close-out in this repo.

## Smallest End State

Edit `loom-code/skills/finishing-a-development-branch/SKILL.md`'s
Default-flow Step 6 and Step 8 only:

- **Step 6** gains one sentence: as soon as the trailer set is returned,
  if it's non-empty, immediately ask the Step-8 Memory-timing question
  using that trailer content as the direct input — do not defer to
  Step 8's pass.
- **Step 8**'s existing Memory-timing bullet is retargeted to say it
  should already have fired at Step 6; Step 8's role for this item
  narrows to "stage whatever docs/loom/memory/ file that check
  produced," matching its existing role for the Living-spec index bullet
  immediately above it (which is also "stage the artifact," not "decide
  whether to produce one").

No new mechanism, no new file, no schema change — pure re-sequencing of
an existing check to its natural trigger point.

## Current State Evidence

- **Forward**: `finishing-a-development-branch/SKILL.md:129-131` (Step
  6, git-memory invocation) and `:144-148` (Step 8's Memory-timing
  bullet) are both read by whoever executes the Default flow — same
  file, same skill, no cross-file coupling risk this time (unlike the
  prior mechanical-exemption change).
- **Reverse**: not a distributed/synced file (confirmed no
  `distribute.py` reference to this skill's SKILL.md body).
- **Error path**: today, nothing stops an orchestrator from reaching
  Step 8, silently skimming past the Memory-timing bullet as "just file
  staging," and never actually asking the underlying question — this
  session's own 2 occurrences are the evidence.
- **Data/Boundary**: N/A — pure documentation, no runtime data shape.

Evidence paths:
`loom-code/skills/finishing-a-development-branch/SKILL.md`.

## Decision

Move the trigger, keep the rule. Edit Step 6 to fire the self-check
immediately on trailer receipt; narrow Step 8's bullet to the staging
action only. Verify via fresh-context cold-read (this is orchestration
procedure, not an exemption/gate an implementer could game — lower
adversarial-review need than the prior mechanical-exemption branch, per
`docs/loom/memory/cold-read-and-adversarial-review-catch-different-failures.md`'s
own distinction — but still gets a real whole-branch review since it's
bundled onto a branch that already has substantive content).

## Out of Scope

- Baking `docs/loom/memory` awareness into `dev-workflow:git-memory`
  itself — that skill is intentionally repo-portable/generic; this fix
  stays in the loom-code-specific consumer.
- Any change to `docs/loom/memory/README.md`'s own "When to record"
  rule or its one exception — unchanged, just triggered earlier.
- Retroactively fixing PR #519/#520 — already shipped; the 3 lessons
  from PR #520 are being caught up in the sibling commit already on this
  branch.

## What Becomes Obsolete

The failure mode itself (treating trailer-writing as memory-handled)
becomes structurally harder once the two are the same procedural step —
nothing to delete in the file, but the *behavior* this fix targets is
what's being retired.
