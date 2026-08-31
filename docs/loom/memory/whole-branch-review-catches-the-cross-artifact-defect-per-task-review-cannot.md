---
name: whole-branch-review-catches-the-cross-artifact-defect-per-task-review-cannot
description: A claim restated across several artifacts can pass every per-task review and still be false at the branch level, because each task reviewer sees only its own slice; only a whole-branch cross-artifact pass compares the copies against each other
type: practice
origin: 2026-09-01 — prose-edit self-sweep arc; whole-branch opus review found 3 stale/false-self-claim defects (98 vs 104 finding count, a nonexistent "second test", a stale sibling-path date) that all six per-task reviews had passed
---

Every per-task reviewer on this arc returned PASS on its own artifact,
yet the whole-branch review found three defects — a statistic restated
with the pre-recount number, a CHANGELOG claim of a test that does not
exist, and one artifact citing a sibling's old path date. Each is a
stale-neighbour or false-self-claim defect: true within one file's
slice, false once the copies are read against each other. A per-task
reviewer structurally cannot see them, because it is handed one task's
files, not the set they must agree with.

**Why:** These are the exact defect classes (edit-consistency: one copy
changed, its neighbours not) that dominate real docs-review load — and
they are invisible to any review whose scope is a single artifact. The
irony that they shipped in the very branch introducing a writer-side
sweep against them is the strongest available argument for the
whole-branch scope, not against the sweep.

**How to apply:** Treat whole-branch review as non-optional whenever a
branch restates the same claim (a count, a capability, a path, a
version) across more than one artifact. Do not let an all-PASS set of
per-task reviews stand in for it — they answer a different question.
