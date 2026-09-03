---
name: checkpoints-are-two-phase-under-the-verdict-sha-tie
description: Because push.reviewed-sha ties every latest-round verdict sha to reviewed_sha, the adversary's probe file and the blind-run report must be committed BEFORE the two readers are dispatched, so the readers can record the final HEAD — dispatching all checkpoint arms in one message makes the reviewers' recorded sha stale
type: gotcha
origin: 2026-09-03-loom-post-merge-seams
---

A checkpoint review has readers (fresh-context reviewers producing a
verdict) and non-readers (the adversary writing probe files, the
blind-runner writing a report) whose artifacts land as commits on the
branch. `push.reviewed-sha` requires every latest-round verdict's `sha`
field to equal `reviewed_sha` — the commit HEAD the checkpoint is meant
to certify. If the adversary's and blind-runner's commits land AFTER the
readers already recorded their verdict's `sha`, that `sha` is now stale:
it names a HEAD that existed before the probe/report commits, not the
final one.

**Why:** dispatching all checkpoint arms (readers + adversary +
blind-runner) in a single message treats them as independent, but they
are not — the readers' verdict must describe the state of the branch
AFTER every other arm's artifact is committed, or `push.reviewed-sha`
fails on a technically-correct review.

**How to apply:** run a checkpoint in two phases. Phase 1: dispatch the
adversary and blind-runner, and commit their probe file(s) and report.
Phase 2: only then dispatch the two readers, so their verdict's `sha`
can equal the true final HEAD. Do not dispatch all arms in one message.
