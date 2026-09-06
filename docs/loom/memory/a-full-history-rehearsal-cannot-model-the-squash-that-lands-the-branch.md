---
name: a-full-history-rehearsal-cannot-model-the-squash-that-lands-the-branch
description: Rehearsing a branch's tests in a clone that keeps the branch's own commits proves only that they pass while those commits exist, so a test bound to any one of them stays green through the rehearsal and dies the moment a squash merge collapses the branch into a single commit — the rehearsal has to also run a shape where the branch is squashed onto its trunk, because that is the history the trunk will actually have
type: gotcha
origin: 2026-09-06 graduated-probes-survive-squash — the previous change's own rehearsal was green, then `plan-edits` went red on main after PR #798 squash-merged
---

A rehearsal built to model the trunk usually clones with full history: it
fetches everything, drops the local trunk branch, and runs the suite there.
That reproduces how a checkout differs from a working tree, and it catches a
test that depends on an unpushed local ref. It cannot catch the failure that
matters most at graduation, because every commit of the branch is still
reachable in that clone — so a test that finds one of them, by subject or by
sha, passes exactly as it did at home.

The trunk does not keep those commits. A squash merge replaces the whole
branch with one commit carrying a different subject and a different sha, and
every test that reached for an individual branch commit fails on the first
trunk run after the merge — where nobody is watching for it, in a run whose
failure reads as unrelated breakage rather than as the graduation that caused
it.

The two shapes fail differently and neither substitutes for the other: full
history catches ref-dependence, the squashed shape catches
individual-commit-dependence. A rehearsal that runs only the first reports
green on precisely the class of test the trunk is about to break.

**Why:** Graduation is the moment a branch-local test becomes everyone's
test, and it is the last moment the branch's author is still watching. A
rehearsal exists to move that failure earlier; one that models a history the
trunk will never have moves nothing, and its green is worse than no
rehearsal, because it was trusted.

**How to apply:** Rehearse every shape the trunk can actually take, in the
same run, before anything graduates — at minimum the full-history checkout
AND the branch squashed to one commit on top of its trunk. Read the exit
code, not the printed counts: a shape that finds no tests at all can print
zero failures while exiting non-zero. When no trunk resolves, say so rather
than skipping the shape silently. See
[[a-graduated-probe-that-pins-a-fact-of-the-moment-goes-red-at-the-next-change]]
for what such a test should recompute instead, and
[[a-commit-behind-no-ref-lives-only-on-the-machine-that-made-it]] for the
sibling failure where the commit survives locally but reaches no ref.
