# Changelog

All notable changes to the `loom-pipeline` plugin will be documented in
this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.6.0] — 2026-07-07

### Added

- **Family relay discipline SSOT** — `hooks/family-relay.md` becomes the
  single source of truth for relay behavior; `hooks/family-reception.md`
  keeps only a 2-line pointer to it, staying within its 60-line budget
  (Task 14 carrier).
- **Conversation-language detection helper** — `hooks/lang_detect.py`
  (Task 14 carrier).
- **Tail language-anchor hook** — PostToolUse on `Skill`, reasserting the
  conversation's target language after a skill invocation (Task 14
  carrier).
- **Stop-hook language-consistency validator** — enforces an absolute
  target-script-count rule at session Stop (Task 14 carrier).
- **Comms metrics recipe** — `scripts/comms_metrics.py` plus a baseline
  audit doc (Task 14 carrier).

### Verified

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-pipeline/scripts/ -q`
  — 150 passed.

## [0.5.0] — 2026-07-06

### Added

- **`loom-memory` skill** — three verbs over the repo-native
  practice-memory store at `docs/loom/memory/`: **record** a distilled
  practice/gotcha/process into the store per its charter, **recall**
  relevant memories by grepping the index then bodies (pull-based,
  honest no-hits), **prune** stale entries into a keep/merge/retire
  proposal (never auto-deletes). CONDITIONAL: fires only when the
  target repo has `docs/loom/memory/README.md` — otherwise
  `loom-memory: N/A` with the reason, loudly (Task 1).
- **Family-reception recall pointer** — `hooks/family-reception.md`
  gains a pointer-only recall note: when the target repo has
  `docs/loom/memory/`, run a recall pass via `loom-memory` before
  starting loom work; the hook preloads no memory content (Task 2).

## [0.4.0] — 2026-07-04

### Added

- **Family reception** — `hooks/family-reception.md` + `hooks/hooks.json` +
  `hooks/session-start` inject the loom family map, the three doors, and
  the on-ramp criteria table (SSOT) at the start of every session, mirroring
  loom-code's SessionStart hook mechanism (Task A1).
- **`§Intake` for `using-loom-pipeline`** — three steps (upstream check
  against the reception criteria, station check/handoff, and the
  unchanged N/A-loud fire-condition reaffirmation) added ahead of
  `§When it fires` (Task A2).
- **README §Family entries & naming convention** — documents the
  one-sentence rule (「要用 loom-X, 就從 using-loom-X 開始」), the
  `using-loom-*` entry vs. plain-name station convention, why
  `brainstorming` (loom-code's discovery skill) folds the family-entry
  intake into its own Axis 0 rather than duplicating a `§Intake` heading
  in `using-loom-code`, and a reception paragraph pointing at the
  `SessionStart` hook (Task A3).

## [0.3.1] — 2026-07-04

### Fixed

- **Dead `args.budget` plumbing removed (segment 3)** — `runSegment3`
  destructured a singular `budget` from args and threaded it through
  every station's opts, but nothing supplies that field (the run-input
  contract and the batch payload carry only `budgets` plural), so the
  value was always `undefined` and the ambient Workflow `budget` global
  did the real work via `resolveBudget`'s fallback. The pass-through is
  gone; `opts.budget` stays reserved for unit-test injection. Found by
  PR #483's whole-branch review; pre-existing since v0.1.0.
- **Adopt-if-valid is a cost-cut record, not an intervention** — the
  segment-1 principles preamble called an adopt a "cost-cut
  intervention", which mis-filed routine adopts into ledger bucket A
  (live-verify finding). The preamble now says: record the adopt in the
  verdict summary and do NOT file it as an `interventions[]` entry —
  interventions are for deviations needing triage (buckets A/B/C), not
  for taking the documented cheap path.

## [0.3.0] — 2026-07-03

### Added

- **Brief+plan freeze form** — `batch_queue.py`'s freeze predicate now
  accepts a second form: when no `docs/loom/<change-id>/` change folder
  exists, an entry is frozen if its (committed) plan file carries a
  `Plan-document-reviewer verdict: PASS` line. Real interactive work
  (observed live on a consumer project, 2026-07-03) produces
  brainstorm-brief + reviewer-PASSed plan with no OpenSpec change
  folder; v1.1's change-folder-only predicate would have SKIPPED every
  such entry. A change folder that exists but fails the validator is
  still a hard reject — never a fallback to the plan-verdict form.

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
