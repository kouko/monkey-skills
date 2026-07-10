---
name: count-only-regression-pins-false-confidence
description: Regression tests that pin only element COUNTS can be coincidentally satisfied by the pre-change (broken) state — pin at least one exemplar value per collection plus a shape assertion that the known-bad form violates, and verify each parametrized case individually went RED
type: practice
origin: branch feat-principles-replay-loop-l1-l2 (2026-07-11) — seed3 oracle count-pin was never RED
---

A parametrized regression test pinned per-key token COUNTS for 6
normalized data files. One file's counts (seed3: 6/0/3) were identical
before and after normalization — its tokens were still prose-glued and
functionally broken, but the count matched, so that sub-case never
failed and could never catch a re-regression of the same shape.

**Why:** aggregate RED ("the test fails on the old state") can be true
while individual parametrized cases are silently green on the old
state; counts are the weakest possible pin.

**How to apply:** when pinning normalized/migrated data, assert per
case (1) at least one exemplar value expected verbatim, and (2) a shape
predicate the known-bad form provably violates (verify against
`git show <pre-commit>:<path>`). Check RED per parametrized case, not
just for the suite.
