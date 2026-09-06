# Blind run — spec round 1

## Result

The cold walk of the spec at `9dc50834` was not independently executable.
Acceptance #1 was partly operational; Acceptance #2 through #5 required
hidden knowledge of the risk policy, lane contract, compatibility behaviour,
or replay measurement.

## Acceptance walk

1. **Partly:** a multi-task plan could demonstrate that the next task starts
   without review, but the record did not define formal-review events or make
   failing tests block dependencies.
2. **Not yet:** the reader could not prove that every requirement had a
   negative case, that high-risk authorship was independent, or that retained
   cases ran and passed.
3. **Not yet:** the reader could not determine each lane's obligations or prove
   Ship stayed blocked until a passing verdict.
4. **Not yet:** "unchanged" named contracts without a versioned behavioural
   baseline.
5. **Not yet:** the historical change, baseline, event clock, permanent tests,
   and finding-equivalence oracle were not fixed.

## Existing data

The change should not rewrite existing plans. The original spec did not say
what a new runtime does when a committed plan still contains
`review: after-task`, so the reader could not test compatibility.

## Agent-decided points

- Waves remain scheduling and integration boundaries.
- Automatic `after-task` and `wave-end` reviews are removed, while explicit
  user-requested diagnostics remain available.
- Task TDD, integration checks, full-lane adversary-first work, lane-specific
  branch-end review, and Ship gates remain.
- Dispatch waiting is reported separately from defect-fix time.

## Resolution

The revised spec defines the missing event categories, failure gates, positive
and negative case coverage, effective-lane baseline, legacy-plan behaviour,
and fixed replay protocol. A fresh reviewer must judge the revised bytes; this
report does not claim they pass.
