# Plan: wire the declared-vs-actual files-touched comparator into close-out

Source brief: docs/loom/specs/2026-08-07-wire-files-touched-check.md
Goal: Wire check_files_touched.py in as a repo-internal Step 8 close-out sibling (script staying at repo root), after fixing the two parser gaps that would make the wiring emit false verdicts on this repo's own plans.
Stage: finishing
Total tasks: 4
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-07, round 1)

## Task 1 — parse letter-suffixed task headings
- Description: Make the plan parser recognize `## Task 3a` / `## Task 3b` headings (currently `_TASK_HDR` matches only integer ids, and the suffixed heading is silently consumed as a boundary with zero parse_errors); keep multi-digit integer ids working and surface a suffixed task under a stable string id.
- Module: scripts/check_files_touched.py
- Files touched: scripts/check_files_touched.py, scripts/test_check_files_touched.py
- Context paths:
  - scripts/check_files_touched.py
  - loom-code/skills/writing-plans/references/plan-format.md
- Acceptance:
  - RED: `scripts/test_check_files_touched.py::test_letter_suffixed_task_headings_parse` — parsing a plan containing `## Task 3a`, `## Task 3b`, `## Task 4` yields three distinct task entries (currently yields only `4`, the suffixed blocks vanish with empty parse_errors).
  - GREEN: all three headings parse to distinct task ids; a plain `## Task 4` still parses; no spurious parse_error introduced.
- External surfaces: none (stdlib `re` only).
- Dependencies: none
- Independent: true
- Brief item covered: "Letter-suffixed task headings … does not match `## Task 3a`; worse, the heading still matches `_TASK_BOUNDARY` … so the block is consumed as a boundary and vanishes with zero parse_errors"
- Status: done(3d07c0b3)
- Gloss: 讓比對器看得到 `## Task 3a` 這種帶字母的任務標題，不再靜默吞掉。

## Task 2 — parse annotated `Status: done(<sha>)` tails
- Description: Relax `_STATUS_DONE` so a `- Status: done(<sha>)` line with a trailing annotation (e.g. `  # spec-reviewer PASS; …`) still yields the sha join key, while a genuinely sha-less or foreign-vocabulary Status line still produces its parse_error.
- Module: scripts/check_files_touched.py
- Files touched: scripts/check_files_touched.py, scripts/test_check_files_touched.py
- Context paths:
  - scripts/check_files_touched.py
  - docs/loom/plans/2026-07-25-company-total-revenue.md
- Acceptance:
  - RED: `scripts/test_check_files_touched.py::test_annotated_status_done_tail_yields_sha` — `- Status: done(c301c7be)  # spec-reviewer PASS; code-quality-reviewer PASS_WITH_NOTES` extracts join key `c301c7be` (currently falls through to a "not in ledger vocabulary" parse_error, mis-reporting the whole plan as exit 2).
  - GREEN: the annotated line yields the sha; a bare `done(c301c7be)` still yields it; a `- Status: pending` or foreign token still parse_errors (no over-broadening).
- External surfaces: none (stdlib `re` only).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "`_STATUS_DONE` … is `$`-anchored, so a real annotated line … fails the match … This is gap 3b — a wiring-blocking must-fix"
- Status: done(b6f0a0a2)
- Gloss: 讓 `Status: done(sha)  # 註解` 這種帶註解的行仍能抽出 sha，接線後才不會空轉噪音。

## Task 3 — wire the Step 8 sibling check into finishing
- Description: Add one orchestrator-only, ONCE-per-branch sibling check to finishing-a-development-branch Step 8 that runs `<repo-root>/scripts/check_files_touched.py` against the branch's own plan — keyed on "a plan file exists for this branch" (silent skip when none, auditable from diff), loud N/A when the script is absent, gating on exit 1 (under-declaration) and reporting exit 2 (loud-empty) distinctly — matching the memory-store-integrity / backlog-close sibling house style.
- Module: loom-code/skills/finishing-a-development-branch/SKILL.md
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_files_touched_check.py
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md
  - scripts/check_files_touched.py
- Acceptance:
  - RED: `loom-code/scripts/test_finishing_skill_pins.py::test_step8_files_touched_sibling_present` — a grep-window pin test asserting Step 8 contains a files-touched sibling bullet carrying the four house-style tokens — `orchestrator-only`, `ONCE per branch`, a loud-N/A clause naming `check_files_touched.py`, and the exit-1-gates / exit-2-loud distinction — currently absent. (If no finishing-skill pin test file exists, the implementer creates loom-code/scripts/test_finishing_skill_pins.py or adds to the nearest existing loom-code SKILL-pin suite found in recon, adjusting Files touched + this test path to the real suite and recording the choice in the Decision Log.)
  - GREEN: the pin test passes; the bullet reads as a peer of the existing Step 8 siblings.
- External surfaces: none (prose + a grep-window pin test).
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "The Step 8 sibling check … orchestrator-only, ONCE per branch, keyed on 'a plan file exists for this branch' … calling `<repo-root>/scripts/check_files_touched.py` with a loud N/A when the script is absent … Gates on a real under-declaration (exit 1); reports exit 2 (loud-empty) distinctly."
- Status: done(4fe0db24)
- Gloss: 把比對器接成收分支站 Step 8 的一個檢查，只看有 plan 的新分支、腳本不在就大聲說 N/A。

## Task 4 — reconcile the backlog entry
- Description: Flip the decision-pending backlog entry to record the 2026-08-07 wire-in decision (placement = finishing Step 8, script stays repo-root, no version bump), and attach a `start:` re-trigger to each residual obligation that stays deferred (nested-bullet Files touched, multi-sha done(a+b), CJK paths, shared-commit semantics, weak-model consumption probe, residual 🟢 debt).
- Module: docs/loom/backlog/
- Files touched: docs/loom/backlog/2026-08-01-declared-vs-actual-files-touched-check-measured-wire-in-decision-pending.md, docs/loom/BACKLOG.md, scripts/test_files_touched_backlog_reconciled.py
- Context paths:
  - docs/loom/backlog/2026-08-01-declared-vs-actual-files-touched-check-measured-wire-in-decision-pending.md
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: `scripts/test_files_touched_backlog_reconciled.py::test_entry_records_decision_and_retriggers` — a diagnostic grepping the entry for the wire-in decision line plus a `start:` field on each deferred obligation; currently fails (entry is decision-pending, no decision recorded, no re-triggers). Paired with `python3 scripts/backlog_index.py --validate && --check` exit 0 as the GREEN gate.
  - GREEN: entry records the decision, deferred obligations each carry a `start:` re-trigger, `backlog_index.py --validate` and `--check` exit 0, BACKLOG.md regenerated.
- External surfaces: none (docs + backlog_index.py).
- Dependencies: none
- Independent: true
- Brief item covered: "flip … the decision-pending backlog entry … to record the wire-in decision, and attach `start:` re-triggers to the residual obligations that stay deferred"
- Status: done(52d9946f)
- Gloss: 把那條「決定待定」的 backlog 改記成已決定，殘餘項各補一個「何時再啟動」的觸發條件。

## Notes
- Verdict stamped PASS (round 1, plan-document-reviewer 15/15) — stamping the verdict, no re-review.
- Reviewer note (non-gating): Task 4's Module names a directory (docs/loom/backlog/) rather than a single file; matches its two-file set (the entry + BACKLOG.md aggregator), not a Check 4 violation. Left as-is.
- Task 1 and Task 4 are Independent: true at the same level (disjoint files — scripts/check_files_touched.py vs docs/loom/backlog/ — no semantic dependency), dispatchable in parallel. Task 2 serializes after Task 1 (same file). Task 3 depends on Task 2 (the wiring's correctness rests on both parser fixes — doc-mirrors-code).
- Task 3's exact pin-test file path is recon-dependent; the implementer adjusts Files touched to the real suite found, recording the choice in the Decision Log.

## Decision Log
- Task 3 pin test lives at `loom-code/scripts/test_finishing_files_touched_check.py` (new file), not the plan's placeholder `test_finishing_skill_pins.py` — the finishing suite is one-file-per-Step-8-checkpoint (test_finishing_backlog_close.py, test_finishing_memory_store_integrity.py, …), so a new checkpoint gets a new sibling file.
- Whole-branch review (docs arm) pinned the Step 8 command to `--variant R3` and named all three exit-1 triggers: the default `all` runs R1, which the 2026-08-01 measurement audit rates no-ship (2 false alarms) — an over-declared task would have falsely STOPped a clean close-out. Caught only at whole-branch scope (per-task reviewers never saw the audit's variant verdict).
- finishing-a-development-branch/SKILL.md body reached 4483 words after adding the sibling bullet (~17 words under the ~4500 cap). This tightens the case for audit item A1 (collapse Step 8's ONCE-per-branch checklists) — flagged, not fixed here (out of scope).
