---
name: a-commit-behind-no-ref-lives-only-on-the-machine-that-made-it
description: A check pinned to a commit that no pushed ref reaches passes on every machine whose object store still holds that commit and dies on every fresh clone before a single assertion runs, so a green local run is evidence about one machine's unreclaimed garbage rather than about the branch — and no clone depth recovers it, because depth fetches what refs reach and a commit behind no ref is behind no depth
type: gotcha
origin: PR #748 (goal-create — the two-test CI repair, 2026-08-27)
---

A behaviour-evidence suite pinned its instruction surface to a commit from the
pre-rebase branch. The rebase replaced that commit and the force-push left it
behind no ref, but every developer checkout still held the object, so the suite
was green for everyone who ran it. CI cloned from the remote and `git ls-tree`
exited 128 — the whole module died before any assertion, which is why the
failure read as infrastructure rather than as a stale pin. The workflow already
set `fetch-depth: 0`, and a comment there named that setting as the guarantee.
It never was one.

**Why:** the two halves of the trap reinforce each other. A dangling commit is
unreachable from refs but perfectly alive in the local object store until gc
runs, so the environment that would catch the defect is the only environment
that never sees it. And the obvious remedy is the wrong axis: depth answers
*how far back along a ref*, never *is there a ref at all*, so a maintainer
reading "we fetch full history" concludes the shas are covered. Rebasing,
squash-merging, and force-pushing all produce this state routinely — the
commit a branch measured itself against is exactly the kind that stops being
reachable. Compare [[a-recorded-package-hash-is-only-valid-as-the-last-edit]],
where the recorded value also describes a tree that no longer exists; there the
tree moved, here the name of the tree stopped resolving.

**How to apply:** any commit a check hands to git needs an assertion that it is
an ancestor of HEAD, not merely that the object exists — `git cat-file -e`
passes on the dangling commit and is the check that fools you. Assert
reachability for every pinned sha, not the newest one, and mutation-check the
assertion by pointing it at a known-dangling commit. When a pin's target
genuinely cannot survive — its bytes are gone from every clone — record the
derived value as a constant and say in the same place that it is no longer
re-derivable; a fingerprint nobody can recompute is honest, a fingerprint whose
source silently fails to resolve is not. Re-anchor the still-computable half on
a commit reachable from a pushed ref, so the guard keeps working forward even
where it can no longer look back.
