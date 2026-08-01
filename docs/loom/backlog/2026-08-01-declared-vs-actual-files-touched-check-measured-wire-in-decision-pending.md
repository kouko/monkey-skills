---
name: 2026-08-01-declared-vs-actual-files-touched-check-measured-wire-in-decision-pending
description: Declared-vs-actual `Files touched` check — measured, wire-in decision pending
status: OPEN
origin: HANDOFF-2026-08-01 P1, agreed after the Reuse-adequacy arc's seven-vs-zero caveat; evidence base `docs/loom/memory/files-touched-misses-machinery-coupled-files.md`.
---

- Origin: HANDOFF-2026-08-01 P1, agreed after the Reuse-adequacy arc's
  seven-vs-zero caveat; evidence base
  `docs/loom/memory/files-touched-misses-machinery-coupled-files.md`.
- What shipped: `scripts/check_files_touched.py` (parse → R1/R2/R3 verdict
  engine → git layer + CLI; parse errors gate an otherwise-clean exit),
  the frozen-key measurement
  (`docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`:
  R3 = 4 hits / 0 miss / 0 false alarms; retro-fit flags all three known
  real instances), and the repo sweep
  (`docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md`:
  11 true wild under-declaration tasks / 10 commits / 19 paths).
- Ship-arc obligations (recorded in the audit §Recommendation + sweep §5;
  none started):
  1. Placement decision — SDD per-task step vs finishing-branch batch
     (trade-offs argued in the audit; decision left to the user).
  2. Absorb or delete SDD `SKILL.md:86`'s prose subset rule; supersede the
     manual-diff advice in
     `files-touched-misses-machinery-coupled-files.md` §How-to-apply.
  3. Letter-suffixed task headings (`## Task 3a`) — 13 plans / 51 headings
     invisible to the parser; the one SILENT non-coverage gap (dangerous
     direction). Also: multi-sha `done(a+b)` vocabulary seen on the same
     plan.
  4. `Status:` comment tails drop all join keys of a fully-ledgered plan
     (`2026-07-25-company-total-revenue.md`, 11 tasks) — loud but wrongly
     shaped as "no ledger".
  5. Nested-bullet `Files touched` declarations (8 tasks, 07-13 plan).
  6. Shared-commit semantics: siblings ledgering one sha cross-flag each
     other (commit = union of sibling declarations) — the comparison unit
     needs a decision (per-commit union vs per-task).
  7. Weak-model consumption probe (deferred by design: the mechanism is a
     deterministic script; tier matters only at the consumption seam,
     which exists only after wiring) — headless probe methodology per
     `docs/loom/memory/verify-agent-mechanisms-on-disk-not-self-report.md`.
  8. CJK paths: `git show` C-quotes non-ASCII paths by default
     (`core.quotepath`) → false UNDER; add `-c core.quotepath=off` at
     wiring time.
- Residual 🟢 debt from reviews (all recorded, none blocking): merge-commit
  sha yields an empty actual set (guard or caveat); duplicate
  `Files touched` lines union silently while duplicate `Status` is loud;
  `claimed(@x)`/`blocked` regex branches untested; one integration test
  lacks the named `is_file` guard; `_normalize_plan_path` is stronger than
  token normalization (declared `src/./a.py` false-UNDERs).
