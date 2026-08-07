---
name: 2026-08-01-declared-vs-actual-files-touched-check-measured-wire-in-decision-pending
description: Declared-vs-actual `Files touched` check — wired into finishing-a-development-branch Step 8; six residual obligations remain, each re-triggered
status: SHIPPED
origin: HANDOFF-2026-08-01 P1, agreed after the Reuse-adequacy arc's seven-vs-zero caveat; evidence base `docs/loom/memory/files-touched-misses-machinery-coupled-files.md`.
---

- Origin: HANDOFF-2026-08-01 P1, agreed after the Reuse-adequacy arc's
  seven-vs-zero caveat; evidence base
  `docs/loom/memory/files-touched-misses-machinery-coupled-files.md`.
- Decision (2026-08-07): wired into `finishing-a-development-branch`
  Step 8 as an orchestrator-only sibling check (NOT SDD per-task) — it
  runs once per branch close-out, not once per task. The script stays
  at repo root `scripts/check_files_touched.py` — NOT moved into
  `loom-code/scripts/`, no marketplace ship, no version bump (user
  decision 2026-08-07); rationale: matches the memory-store-integrity /
  backlog-close siblings that call repo-root scripts and degrade to
  loud N/A where absent. Shipped in this branch: the two parser fixes
  (letter-suffix headings; annotated `Status:` comment tails) + the
  Step 8 wiring.
- What shipped: `scripts/check_files_touched.py` (parse → R1/R2/R3 verdict
  engine → git layer + CLI; parse errors gate an otherwise-clean exit),
  the frozen-key measurement
  (`docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`:
  R3 = 4 hits / 0 miss / 0 false alarms; retro-fit flags all three known
  real instances), and the repo sweep
  (`docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md`:
  11 true wild under-declaration tasks / 10 commits / 19 paths).
- Ship-arc obligations (recorded in the audit §Recommendation + sweep §5):
  1. Placement decision — RESOLVED (2026-08-07): wired into
     `finishing-a-development-branch` Step 8 as an orchestrator-only
     sibling check (NOT SDD per-task) — see the Decision bullet above.
  2. Absorb or delete SDD `SKILL.md:86`'s prose subset rule — RESOLVED
     (2026-08-07): moot under the decision above — the SDD per-task
     placement path was not chosen, so `SKILL.md:86`'s prose subset rule
     needs no absorption or deletion; the manual-diff advice in
     `files-touched-misses-machinery-coupled-files.md` §How-to-apply
     stands unsuperseded.
  3. Letter-suffixed task headings (`## Task 3a`) — RESOLVED (2026-08-07,
     shipped this branch): the parser now recognizes SINGLE-letter
     suffixed headings across the 13 plans / 51 headings that were
     previously invisible, closing the SILENT non-coverage gap for that
     shape. Still deferred: multi-letter suffixes (`## Task 3ab`) remain
     the same accepted silent-drop limitation (documented in the parser's
     own `_TASK_HDR` comment), and multi-sha `done(a+b)` vocabulary seen
     on the same plan.
     - start: next time a plan uses a multi-letter task suffix, or records
       a multi-sha `done(a+b)`-style vocabulary the comparator needs to
       resolve into individual commits.
  4. `Status:` comment tails — RESOLVED (2026-08-07, shipped this
     branch): the parser now handles annotated `Status:` comment tails,
     so a fully-ledgered plan's join keys (e.g.
     `2026-07-25-company-total-revenue.md`, 11 tasks) are no longer
     dropped.
  5. Nested-bullet `Files touched` declarations (8 tasks, 07-13 plan).
     - start: next time a plan declares `Files touched` via nested
       bullets under a task (as the 07-13 plan did) and the parser needs
       to consume them.
  6. Shared-commit semantics: siblings ledgering one sha cross-flag each
     other (commit = union of sibling declarations) — the comparison unit
     needs a decision (per-commit union vs per-task).
     - start: next time two sibling tasks ledger the same commit sha and
       cross-flag each other under the check.
  7. Weak-model consumption probe (deferred by design: the mechanism is a
     deterministic script; tier matters only at the consumption seam,
     which exists only after wiring) — headless probe methodology per
     `docs/loom/memory/verify-agent-mechanisms-on-disk-not-self-report.md`.
     - start: once the Step 8 wiring has run across enough branch
       close-outs that a weak-model (e.g. haiku-tier) consumption probe
       becomes measurable at the now-live consumption seam.
  8. CJK paths: `git show` C-quotes non-ASCII paths by default
     (`core.quotepath`) → false UNDER; the fix is `-c core.quotepath=off`,
     deferred past this wiring until a CJK path first appears (see start:).
     - start: next time a task's declared or actual path contains
       non-ASCII (CJK) characters and the comparator's git layer needs
       `-c core.quotepath=off` to read it correctly.
- Residual 🟢 debt from reviews (all recorded, none blocking): merge-commit
  sha yields an empty actual set (guard or caveat); duplicate
  `Files touched` lines union silently while duplicate `Status` is loud;
  `claimed(@x)`/`blocked` regex branches untested; one integration test
  lacks the named `is_file` guard; `_normalize_plan_path` is stronger than
  token normalization (declared `src/./a.py` false-UNDERs).
  - start: next time any one of these surfaces in a live Step 8 run — a
    merge-commit close-out, a duplicate `Files touched` line, a
    `claimed(@x)`/`blocked` branch actually exercised, or a declared path
    shaped like `src/./a.py`.
