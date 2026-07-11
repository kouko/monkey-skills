# Plan: principles replay loop — L3 autonomous improvement loop

Source brief: docs/loom/specs/2026-07-11-principles-replay-l3-loop.md
Change-folder input: N/A — no non-archived `docs/loom/<change-id>/` folder exists
(layer (ii) count = 0); proceeding on the brainstorming brief, loudly.
Total tasks: 7
Critical-path depth: 4 (≤5) — T3→T4→T5→{T6|T7}
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-11, round 2 — round-1 Check-8 dry-parse gap fixed and re-verified; 14/14)

## Notes

- **Report filename**: the Write tool refuses basename `report.md`
  (machine-local memory `feedback_write_tool_refuses_report_md_basename.md`).
  All report artifacts in this plan are named `loop-report.md` by design —
  no task may create a file with basename `report.md`. Dispatch packets must
  repeat this.
- **Static-test convention**: workflow JS is pinned by pytest static tests
  (regex/marker presence), following
  `loom-product-principles/scripts/test_replay_matrix_workflow.py`.
- **Guard obligations** (every workflow task): every `agent()` result
  null-guarded; stage bodies `async` with `return await` inside try;
  operator args allow-listed per segment — per
  `docs/loom/memory/workflow-agent-results-and-courier-args-need-guards.md`.
- **T7 execution**: the live smoke invocation requires the Workflow tool,
  which implementer subagents do not drive; the orchestrator executes the
  invocation itself and an evaluator reviews the committed record.
- **Isolation decision (Decision Log candidate)**: candidate edits are
  applied to the arc branch's working tree (this branch is dedicated),
  with a clean-status precondition on the station file paths and
  `git checkout --` restore on rejection; accepted edits are committed.
  Chosen over a separate worktree because the replay path resolves the
  plugin from the repo checkout — cost of change: localized to the
  apply/revert courier (T4).

## Decision Log

1. chose **verdict logic in a Python helper (`improve_loop_verdict.py`), JS stays thin** because the family's verdict-path discipline is deterministic pytest-covered scripts (L1 acceptance: "grade stage invokes ONLY deterministic scripts") and workflow JS has no unit-test infra — cost of change: medium (JS inline rewrite would drop test coverage).
2. chose **working-tree apply + git-restore over worktree isolation** because replays resolve the plugin from the repo checkout and the arc branch is dedicated — cost of change: low (courier-local).
3. chose **held-out = cold-operator + seed5** per brief §Open Questions (human-grounded seed must be unseen; seed5's run variance makes regressions visible) — **one-way door, user-confirmed at kickoff briefing 2026-07-11** (a fixer-exposed seed can never return to clean held-out duty). Reversal condition recorded: if 4 visible seeds prove too thin (rounds rejected for lack of failure diversity), seed5 may move visible — irreversibly.

4. chose **folding T1's 🟡 review finding (duplicate-seedId silent dict-overwrite on the verdict path → must exit 2) into T2's dispatch** because T2 touches the same module next and the fix is exemplar-testable there — cost of change: low (revertible edit); alternative (separate fix task) rejected as dispatch overhead for a ~10-line change.

5. chose **stash-push + verified stash-drop for the revert courier, superseding the planned `git checkout -- <paths>`** because this repo's dangerous-command-guard blocks `checkout --` (in-repo evidence: loom-code environment-gotchas.md:36-38 "Undo with stash, not checkout"; surfaced by T4's quality review as EXT-1 🔴) — cost of change: low (courier-local); this entry recorded at close-out per the whole-branch review's coherence nit. The plan Notes' and Task 4's original `git checkout --` wording is superseded by this entry.

## Task 1 — verdict helper: compare + held-out smoke

- Description: create `improve_loop_verdict.py` with `compare` (aggregate ≥1
  baseline runs per seed vs one candidate run; exit 0 only when no visible
  seed is worse AND ≥1 seed is better) and `smoke` (exit 0 only when no
  held-out seed is newly failing vs its baseline) subcommands; JSON rows in,
  exit codes 0/1/2 (2 = malformed input) mirroring
  `check_seed_traceability.py:48-50` convention.
- Module: loom-product-principles/scripts/improve_loop_verdict.py
- Files touched: loom-product-principles/scripts/improve_loop_verdict.py, loom-product-principles/scripts/test_improve_loop_verdict.py
- Context paths:
  - loom-product-principles/scripts/check_seed_traceability.py (exit-code + argparse convention)
  - .claude/workflows/principles-replay-matrix.js (row shape `{runLabel, rows, passRate}` at :272)
  - docs/loom/specs/2026-07-11-principles-replay-l3-loop.md (§Smallest End State item 4)
- Acceptance:
  - RED: `test_improve_loop_verdict.py::test_compare_accepts_only_no_worse_and_one_better` fails (module missing)
  - GREEN: pytest passes at package level; compare/smoke exit codes verified
    per the rule above, incl. the trade case (seed A better + seed B worse →
    exit 1) and malformed-JSON → exit 2. New suite runs under the existing
    `pytest loom-product-principles/scripts/` command surface (no new verb).
- External surfaces: none (stdlib argparse/json only)
- Dependencies: none
- Independent: true
- Brief item covered: "Verify (two-stage accept, per GEPA) — no visible seed worse AND ≥1 seed better … pass the held-out smoke"

## Task 2 — verdict helper: brakes (wordcap + plateau)

- Description: add `wordcap` (exit 1 when the target file's `wc -w` count
  exceeds the cap arg, default 4500) and `plateau` (exit 1 = stop when the
  round-ledger JSON shows 2 consecutive rounds with no accepted proposal;
  exit 0 = continue) subcommands to `improve_loop_verdict.py`.
- Module: loom-product-principles/scripts/improve_loop_verdict.py
- Files touched: loom-product-principles/scripts/improve_loop_verdict.py, loom-product-principles/scripts/test_improve_loop_verdict.py
- Context paths:
  - scripts/check-skill-structure.py (WORD_HARD_CAP = 4500 at :298 — mirror the counting method)
  - docs/loom/specs/2026-07-11-principles-replay-l3-loop.md (§Smallest End State item 5)
- Acceptance:
  - RED: `test_improve_loop_verdict.py::test_plateau_stops_after_two_empty_rounds` fails (subcommand missing)
  - GREEN: pytest passes; wordcap boundary (exactly 4500 = pass, 4501 = fail)
    and plateau sequences ([miss,miss]→stop, [hit,miss]→continue,
    [miss,hit,miss,miss]→stop) verified.
- External surfaces: none (stdlib)
- Dependencies: Task 1 completes first (same module file)
- Independent: false
- Brief item covered: "Brakes (guardrails 2+3) — word-cap … hard cap 3 rounds … plateau early-exit = 2 consecutive rounds with no accepted proposal"

## Task 3 — workflow skeleton: meta, args, seed split, baseline phase

- Description: create `.claude/workflows/principles-improve-loop.js` with
  pure-literal meta (name `principles-improve-loop`, phases), `runLabel`
  arg allow-list (`/^[A-Za-z0-9._-]+$/`) + absolute-path per-segment
  allow-list for any path arg (mirror matrix `:57-97`), a `maxRounds` arg
  (integer, allow-listed to 1-3, default 3 — consumed by Task 5's loop and
  Task 7's smoke), seed-split
  constants (HELD_OUT = cold-operator + seed5; VISIBLE = seed1–4, derived
  by exclusion), and a Baseline phase invoking
  `workflow('principles-replay-matrix', {runLabel…, seeds: VISIBLE})` ×2
  with per-seed aggregation of the returned rows; every nested-workflow
  result null-guarded, stages async with `return await` inside try.
- Module: .claude/workflows/principles-improve-loop.js
- Files touched: .claude/workflows/principles-improve-loop.js, loom-product-principles/scripts/test_improve_loop_workflow.py
- Context paths:
  - .claude/workflows/principles-replay-matrix.js (meta :1-8, allow-lists :57-97, seeds narrowing :100-120, return :272)
  - loom-product-principles/scripts/test_replay_matrix_workflow.py (static-test pattern)
  - docs/loom/memory/workflow-agent-results-and-courier-args-need-guards.md
- Acceptance:
  - RED: `test_improve_loop_workflow.py::test_meta_seed_split_and_guards_present` fails (file missing)
  - GREEN: static test passes — meta literal, allow-list regexes, HELD_OUT
    constant excludes its members from VISIBLE, `workflow('principles-replay-matrix'`
    call present ×2-run loop, null-guard + await-in-try markers present;
    AND the suite includes a dry-parse assertion of the workflow file
    (follow `test_replay_matrix_workflow.py`'s existing parse-check
    pattern; fall back to a `node --check`-equivalent if none exists).
    New suite runs under the existing pytest command surface.
- External surfaces: Claude Code Workflow primitive (`workflow()` nesting,
  saved-name registry) — grounded by the live-verified sibling
  `.claude/workflows/principles-replay-matrix.js` and Workflow tool docs
  (nesting is one level; L3→matrix is exactly one).
- Dependencies: none
- Independent: true
- Brief item covered: "Seed split (guardrail 1)" + "Baseline — nests the existing matrix by name … ×2 runs, aggregated per seed" + "Ships with … a dry-parse test"

## Task 4 — fixer stage: schema-forced proposal + apply/revert courier

- Description: add the Fixer phase — one `agent()` per round,
  schema-forced output `{invariant, rationale, edits:[{file, old, new}]}`
  (exactly one invariant), prompt carries failing rows + station file
  path(s) + failure-class description and MUST NOT reference any oracle
  file path (seed-corpus paths excluded); plus an apply courier (applies
  edits with the Edit tool after a clean-status precondition on the target
  paths) and a revert courier (`git checkout -- <paths>` on rejection).
- Module: .claude/workflows/principles-improve-loop.js
- Files touched: .claude/workflows/principles-improve-loop.js, loom-product-principles/scripts/test_improve_loop_workflow.py
- Context paths:
  - docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/README.md (:18-23 oracle file names — for the exclusion test)
  - loom-product-principles/skills/product-principles/SKILL.md (the edit target)
  - docs/loom/memory/preamble-wording-is-contract-surface.md (fixer prompt must warn the agent that station wording is contract surface)
- Acceptance:
  - RED: `test_improve_loop_workflow.py::test_fixer_prompt_excludes_oracle_paths` fails (fixer stage missing)
  - GREEN: static test passes — fixer schema fields present, corpus oracle
    path fragments absent from the fixer prompt string, apply/revert courier
    markers + clean-status precondition + allow-listed paths present.
- External surfaces: Claude Code Workflow `agent()` schema-forced output —
  grounded by matrix GRADE stage precedent (:193-255).
- Dependencies: Task 3 completes first (same files)
- Independent: false
- Brief item covered: "Fixer stage — one agent proposes ONE fix per round … never the oracle files"

## Task 5 — round loop: two-stage accept, brakes, ledger, report

- Description: wire the per-round sequence — apply candidate → visible
  matrix run → `improve_loop_verdict.py compare` → (win) confirmation
  re-run + compare again → held-out matrix run + `smoke` → `wordcap` gate →
  accept (commit on arc branch with a Decision Log-shaped message) or
  revert; ROUND_CAP = 3; `plateau` consulted between rounds; per-round
  ledger entries (imitating `recordLedger` validation,
  `loom-pipeline/scripts/driver_60_ledger.js:33-55`); final
  `loop-report.md` (NEVER basename `report.md`) written to the run's output
  dir; script returns `{runLabel, rounds, accepted, ledger}`.
- Module: .claude/workflows/principles-improve-loop.js
- Files touched: .claude/workflows/principles-improve-loop.js, loom-product-principles/scripts/test_improve_loop_workflow.py
- Context paths:
  - loom-pipeline/scripts/driver_60_ledger.js (:33-55 ledger validator pattern)
  - loom-code/skills/writing-plans/references/plan-format.md (§Decision Log entry shape for accept commits)
  - docs/loom/specs/2026-07-11-principles-replay-l3-loop.md (§Smallest End State items 4-6)
- Acceptance:
  - RED: `test_improve_loop_workflow.py::test_two_stage_accept_and_brakes_wired` fails (markers missing)
  - GREEN: static test passes — ordered markers for
    verify→confirm→held-out-smoke, all four verdict subcommand invocations
    present, ROUND_CAP=3 literal, ledger entries per round, report basename
    `loop-report.md`, return-shape keys present; no auto-merge/push strings
    (`git merge`/`git push`/`gh pr` absent from the script).
- External surfaces: Workflow `agent()` couriers running git/pytest via
  Bash — same surface as matrix GRADE couriers.
- Dependencies: Tasks 1, 2, 4 complete first
- Independent: false
- Brief item covered: "Verify (two-stage accept…)" + "Brakes" + "Output (guardrail 4) — round ledger … Decision Log-shaped entries … never merges and never pushes"

## Task 6 — BACKLOG discharge + cross-links

- Description: update `docs/loom/BACKLOG.md`'s replay-harness entry — the
  "remaining open item is Level 3" wording (:76-81) becomes a pointer to
  the built `principles-improve-loop` workflow + this plan/brief, with the
  residual re-triggers (skill-tuning diversification; checker first-cell
  precision stays in its own entry) preserved, not deleted.
- Module: docs/loom/BACKLOG.md
- Files touched: docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/BACKLOG.md (:46, :74-81)
  - docs/loom/specs/2026-07-11-principles-replay-l3-loop.md (§Decision — the NOT-building list with re-triggers)
- Acceptance:
  - RED (diagnostic): `grep -c 'principles-improve-loop' docs/loom/BACKLOG.md` returns 0
  - GREEN: grep finds the pointer; the entry no longer names L3 as the open
    item; the two residual re-triggers remain greppable.
- External surfaces: none
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: "BACKLOG harness entry … L3 pointer :76-81" (Current State Evidence — Boundary; discharge on build)

## Task 7 — live smoke invocation + durable record

- Description: run one real `principles-improve-loop` invocation with
  ROUND_CAP overridden to 1 (arg `maxRounds: 1` — T3 must accept it,
  allow-listed integer 1-3, default 3), on the calibrated corpus; commit
  the ledger + `loop-report.md` to
  `docs/loom/dogfood/2026-07-11-l3-loop-smoke/` as the durable record
  (replay artifacts are ephemeral, per the calibration-baseline precedent).
  Executed by the orchestrator (Workflow tool); success = the run completes
  with zero crashed/null rows and the record is committed — an accepted OR
  rejected/plateaued proposal are BOTH valid smoke outcomes.
- Module: docs/loom/dogfood/2026-07-11-l3-loop-smoke/
- Files touched: docs/loom/dogfood/2026-07-11-l3-loop-smoke/loop-report.md, docs/loom/dogfood/2026-07-11-l3-loop-smoke/ledger.json
- Context paths:
  - docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/calibration-baseline-2026-07-11.md (durable-record precedent :11-14)
- Acceptance:
  - RED (diagnostic): the dogfood folder does not exist
  - GREEN: folder committed with both files; ledger validates against the
    entry shape; loop-report names the round outcome and per-seed rows.
- External surfaces: live Workflow invocation (haiku replays ≈ 18-30)
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: "Ships with … one live smoke invocation before close-out"
