# Changelog

All notable changes to the `loom-pipeline` plugin will be documented in
this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-07-03

Batch implementation mode (v1.1): a queue of FROZEN change-folders runs
Segment 3 unattended, one change at a time — N ledgers + N `loom/<id>`
PR branches out, merge stays human. Human gates (a) change-id and (c)
cost policy move to freeze time (queue-entry authoring); no scheduler,
time-agnostic.

- New host-side bookkeeping CLI `scripts/batch_queue.py`
  (`next` / `mark` / `status`): parses the human-edited
  `docs/loom/QUEUE.toml` (stdlib `tomllib`), keeps machine-owned state
  in `docs/loom/queue-state.json`, verifies the freeze predicate
  (loom-spec validator exit-0 + plan committed), creates the per-change
  worktree/branch (`.worktrees/loom-<id>`, branch `loom/<id>`), and
  emits ready-to-use Workflow args JSON for Segment 3.
- Failure isolation: ineligible entries are SKIPPED loudly with the
  predicate's reason (uncommitted-plan skips tear the just-created
  worktree back down); a failed change never stalls the queue.
- Circuit breaker: 2 consecutive FAILED terminal outcomes halt the
  queue (exit 3); `--override-halt` bypasses after human review.
- SKILL.md §Batch mode: the dispatcher-only loop contract
  (`next` → `Workflow({segment: 3, …})` → `mark`) — the main agent
  never parses the queue file, never composes git commands, never
  diagnoses failures mid-batch.
- Zero driver changes: the v1 `assets/loom-pipeline.js` asset and all
  `driver_*.js` sources are byte-identical to 0.1.0.

## [0.1.0] — 2026-07-03

Conductor plugin born: the entry skill (`using-loom-pipeline`) plus the
build-assembled driver asset (`assets/loom-pipeline.js`, composed from
`scripts/driver_00_header.js` through `driver_60_ledger.js` — guard,
`runStation`, the 3 segments, ledger, and the `main` entrypoint).

- F1–F5 driver hardening baked in (per-station token budgets with
  fail-loud over-budget, wall-clock watchdog per station, rally cap
  ≤2 on critic↔writer loop-backs, change-strategy recovery ladder,
  stable-prefix dispatch convention).
- G1 (run-level + per-station token budgets), G3 (validator-checked
  Decisions section per artifact), and G6 (idempotent adopt-if-valid
  re-runs, journal resume, "checkpointed, not durable" naming) baked
  into the driver.
- G2 (critic false-positive rate) and G5 (per-judge verdicts,
  cross-vendor judging) recorded as ledger metrics — not solved in v1.
- Canonical 6-field run-input contract (change-id, project path,
  budgets, model policy, skillsRoot, optional resumeRunId), fail-loud
  on any missing required field.
- Fail-loud doctrine throughout: N/A conditions, missing fields, and
  over-budget runs all surface loudly rather than silently degrading
  or improvising a default.
