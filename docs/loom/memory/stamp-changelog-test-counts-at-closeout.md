---
name: stamp-changelog-test-counts-at-closeout
description: CHANGELOG test counts go stale during multi-round review fix-ups — stamp the number with pytest --collect-only at branch close-out, not mid-branch
type: practice
origin: PR #492 (loom-code 0.23.0 mechanical gates, 2026-07-04)
---

A CHANGELOG entry that quotes a test count ("41 tests") goes stale
during multi-round review fix-ups, because each fix round adds
tests. On PR #492 the recorded number went stale twice before merge.

**Why:** a wrong test count in the CHANGELOG is a small but
credibility-eroding inaccuracy, and re-editing it every round is
wasted churn.

**How to apply:** do not write the final test count mid-branch.
Stamp it once at close-out (just before the final commit/push) using
the runner's own count, e.g. `pytest --collect-only -q` and take the
collected total.
