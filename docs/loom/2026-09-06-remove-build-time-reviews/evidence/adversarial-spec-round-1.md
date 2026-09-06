# Adversarial spec pass — round 1

Reviewed `docs/loom/2026-09-06-remove-build-time-reviews/spec.md` at
`9dc508341b9df5be1a4ed3aa77f613c36a35334e` with the spec lens.

## Result

`NEEDS_REVISION`. The red team found seven blocking ambiguities:

1. Required task and integration checks ran, but their failure did not
   explicitly block dependent tasks.
2. The final task or wave could still trigger an intermediate review before
   the closing branch-end review.
3. Low-risk requirements were not guaranteed a negative or boundary case.
4. The retained positive and negative cases were not required to run or pass.
5. Ship was blocked on a branch-end review running, not on that review passing.
6. Existing speed modes and their branch-end strength were not explicitly
   preserved against a versioned baseline.
7. The replay fixture, revisions, clock, dispatch definition, tests, and
   finding oracle were unspecified; legacy `review: after-task` markers also
   had no compatibility rule.

## Fix applied

REQ-1 through REQ-5 now make each condition observable and blocking. The spec
pins loom-code 1.7.0 at `130b4ca1` as the unchanged-contract baseline, pins the
historical replay to `2026-09-03-small-change-lane`, defines the dispatch and
blocking-time metrics, and makes legacy plan markers readable but inert under
the new runtime without migrating an already-running Build.
