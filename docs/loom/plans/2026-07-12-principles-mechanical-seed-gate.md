# Plan: principles station — mechanical seed-coverage gate

Source brief: docs/loom/specs/2026-07-12-principles-mechanical-seed-gate.md
Change-folder input: N/A — no non-archived `docs/loom/<change-id>/` exists
(layer (ii) count = 0); proceeding on the brainstorming brief, loudly.
Total tasks: 4
Critical-path depth: 3 (≤5) — T2→T3→T4
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-12, round 2 — round-1 Check-8 oracle-isolation traceability gap fixed and re-verified; 14/14)

## Notes

- **Report filename**: Write tool refuses basename `report.md` — any record
  file in this plan uses a distinct basename; dispatch packets repeat this.
- **Guard obligations** (matrix tasks): every `agent()`/`workflow()` result
  null-guarded; stages `async` with `return await` inside try; any arg
  reaching courier Bash text allow-listed per segment — per
  `docs/loom/memory/workflow-agent-results-and-courier-args-need-guards.md`.
- **Oracle isolation** (matrix tasks): no new prompt string may contain any
  path under `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/`
  or the word "oracle" — same static-pin discipline as the L3 fixer
  (`test_improve_loop_workflow.py` precedent). The inventory lives in the
  run sandbox.
- **Inventory format SSOT** = the checker's parser contract
  (`check_seed_traceability.py:4-29`): keys `named_anchors:` /
  `deferred_items:` ONLY (never `negative:` — must-be-ABSENT semantics),
  `;`-separated tokens, `|` alternatives, empty sentinel
  `none in this seed`. T1 and T2 both cite this contract; neither cites
  the other (prevents doc-mirrors-doc drift).
- **T4 execution**: live matrix runs require the Workflow tool — the
  orchestrator executes the runs itself; an evaluator reviews the
  committed record (same shape as the L3 arc's smoke task).

## Decision Log

1. chose **pipeline-enforced checker (harness runs it), never a drafter instruction** because EN+JA research is unanimous (every shipped system — Aider/Guardrails/Instructor/ZOZO — enforces in pipeline code; DeepMind evidence that intrinsic self-correction degrades accuracy) and this family's own 0/2 preload evidence converges — cost of change: medium (moving enforcement later would rewrite the matrix leg).
2. chose **fix bound = 1 round now, telemetry recorded, reversal to 3 documented** because ZOZO/Kalvium data shows round 1 catches most misses and Aider's hardcoded cap exists to kill unfixable loops — cost of change: low (one constant + recorded reversal condition in the brief).
3. chose **inventory in the checker's existing oracle format (two keys)** because the parser is source-agnostic (zero script changes, `check_seed_traceability.py:227-248`) and a second format would need a second parser — cost of change: low.
4. chose **the prose "post-draft seed walk" bullet is superseded, not kept alongside** (brief Axis 5) because keeping both would instruct the model to do by memory what the pipeline now enforces mechanically — the exact redundancy this arc removes — cost of change: low (text restore).

## Task 1 — station SKILL.md: inventory step + Step-8 checker gate

- Description: in `product-principles/SKILL.md` (a) add an
  inventory-authoring step to §Headless/seeded mode — BEFORE drafting
  sections, extract every seed-named entity into `seed-inventory.md` per
  the inventory format SSOT (Notes), Write-only, no scripts; (b) extend
  Step 8 (validate-then-fix, :203-222) so interactive sessions ALSO run
  `check_seed_traceability.py <artifact> <inventory>` and fix to exit 0
  (wording precedent `writing-plans/SKILL.md:216,230`); (c) REPLACE the
  prose "Post-draft seed walk" bullet (:264-267) with a pointer to the
  mechanical gate (supersession per Decision Log 4) — the traceability
  invariant prose (:239-263) stays.
- Module: loom-product-principles/skills/product-principles/SKILL.md
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/scripts/check_seed_traceability.py (:4-29 format contract; :202-210 negative semantics to warn against)
  - loom-code/skills/writing-plans/SKILL.md (:216, :230 exit-0 wording precedent)
- Acceptance:
  - RED: `test_product_principles_skill.py::test_inventory_step_and_checker_gate_present` fails (markers absent)
  - GREEN: static pins pass — inventory step present in headless section
    naming the two allowed keys AND warning against `negative:`; Step 8
    names the checker command with exit-0 gating; the old "Post-draft
    seed walk" self-report wording is GONE (negative pin); word count
    stays ≤4,500 (`python3 scripts/check-skill-structure.py
    loom-product-principles` passes); package pytest green.
- External surfaces: none (prose + static tests)
- Dependencies: none
- Independent: true
- Brief item covered: "Inventory authoring (drafting agent, Write-only)" + "Interactive — Step 8 … exit-0 gated" + Decision "prose seed walk superseded"

## Task 2 — matrix: replay-prompt inventory step + self-check courier

- Description: in `principles-replay-matrix.js` (a) extend the REPLAY
  agent prompt STEPS (:164-170) — before drafting, Write
  `<sandbox>/<runLabel>/<seedId>-inventory.md` per the inventory format
  SSOT (agent keeps Write-only; STEP 5's "do NOT run scripts" stays for
  the replay agent); (b) add a self-check courier stage after replay:
  Bash-runs `check_seed_traceability.py <artifact> <inventory>`,
  schema-forced return {exitCode, missLines[]}; per-seed row gains
  additive fields `selfCheckExit`, `selfCheckMisses` (GRADE stage and its
  oracle verdict untouched). All new stages follow the guard obligations
  (Notes).
- Module: .claude/workflows/principles-replay-matrix.js
- Files touched: .claude/workflows/principles-replay-matrix.js, loom-product-principles/scripts/test_replay_matrix_workflow.py
- Context paths:
  - .claude/workflows/principles-replay-matrix.js (:151-256 pipeline, :160-171 replay prompt, :210-218 grade courier Bash pattern)
  - loom-product-principles/scripts/check_seed_traceability.py (CLI + format contract)
  - docs/loom/memory/workflow-agent-results-and-courier-args-need-guards.md
- Acceptance:
  - RED: `test_replay_matrix_workflow.py::test_inventory_step_and_selfcheck_courier_present` fails
  - GREEN: static pins — inventory STEP in replay prompt naming the two
    keys; self-check courier invoking the checker; additive row fields;
    replay agent still forbidden from running scripts; no corpus-folder
    path and no "oracle" in any NEW prompt string; dry-parse still
    passes; package pytest green.
- External surfaces: Claude Code Workflow agent()/courier Bash — grounded
  by the same file's grade courier (:210-218).
- Dependencies: none
- Independent: true
- Brief item covered: "L1 matrix … a Bash courier runs check_seed_traceability.py <draft> <inventory> (zero script changes)" + "Oracle isolation preserved: no replay/fix/courier prompt may name any path under the seed-corpus folder"

## Task 3 — matrix: fix agent + re-check wiring (1 bounded round)

- Description: after a self-check exit 1, dispatch ONE fresh fix agent
  (schema-forced): input = the draft path + the VERBATIM missLines +
  the additive-patch instruction (missing Anchors rows use the
  `(agent-decided)` version convention; missing deferred items land as
  `## Open Questions` entries with `— re-trigger:`); the agent edits the
  artifact in the sandbox (Write/Edit only); then the self-check courier
  re-runs ONCE; per-seed row gains `selfCheckFixed` (misses cleared by
  round 1) + final `selfCheckExitAfterFix` — the reversal-condition
  telemetry. Fix bound = 1 (Decision Log 2). Fix-agent prompt carries the
  wording-is-contract-surface warning and NO oracle references. GRADE
  stage untouched.
- Module: .claude/workflows/principles-replay-matrix.js
- Files touched: .claude/workflows/principles-replay-matrix.js, loom-product-principles/scripts/test_replay_matrix_workflow.py
- Context paths:
  - .claude/workflows/principles-improve-loop.js (fixer schema + oracle-exclusion + inert-data marker precedents)
  - docs/loom/memory/preamble-wording-is-contract-surface.md
- Acceptance:
  - RED: `test_replay_matrix_workflow.py::test_fix_round_wired_and_bounded` fails
  - GREEN: static pins — fix agent dispatched only on exit 1; exactly one
    re-check (bound marker); telemetry fields present; oracle-exclusion
    pin over the fix prompt; guards (null/throw/await-in-try) on the new
    stages; dry-parse; package pytest green.
- External surfaces: Workflow agent() schema-forced output — same-file precedent.
- Dependencies: Task 2 completes first (same files)
- Independent: false
- Brief item covered: "on exit 1 a fix agent receives the VERBATIM miss list and patches additively … 1 fix round now, budget for 3" + Open Question "fix bound telemetry" + Decision "oracle isolation intact"

## Task 4 — acceptance: ≥2 live matrix runs vs baseline + committed record

- Description: run the updated `principles-replay-matrix` live ×2
  (orchestrator-executed via the Workflow tool, fresh runLabels), collect
  per-seed pass rows + self-check telemetry, and commit a comparison
  record at `docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline/`
  (files: `gate-baseline.md` + `runs.json` — NEVER basename `report.md`)
  against the committed 4/18 baseline
  (`calibration-baseline-2026-07-11.md`): the dominant class-D anchor-drop
  count must measurably shrink; deferred/negative checks must not regress.
  Both outcomes are honestly recorded — if the gate does NOT move the
  number, that is a recorded negative result, not a hidden one.
- Module: docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline/
- Files touched: docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline/gate-baseline.md, docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline/runs.json
- Context paths:
  - docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/calibration-baseline-2026-07-11.md (:16-42 baseline table + signal reading)
- Acceptance:
  - RED (diagnostic): the dogfood folder does not exist
  - GREEN: folder committed with both files; ≥2 runs' per-seed rows +
    self-check telemetry recorded; explicit before/after comparison of
    class-D drop counts; an honest verdict line (improved / unchanged /
    regressed).
- External surfaces: live Workflow runs (~12 haiku replays per run + fix agents)
- Dependencies: Tasks 1, 3 complete first
- Independent: false
- Brief item covered: "Acceptance (whole arc): ≥2 post-change L1 matrix runs vs the committed 4/18 baseline"
