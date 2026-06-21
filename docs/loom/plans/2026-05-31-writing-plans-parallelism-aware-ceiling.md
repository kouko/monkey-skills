# Plan: writing-plans parallelism-aware ceiling + active parallel surfacing

Source brief: docs/loom/specs/2026-05-31-writing-plans-parallelism-aware-ceiling.md
Total tasks: 4 (≤5)
Execution order: parallel-where-possible (Task 1 ∥ Task 2; Task 3 after 1; Task 4 after all)
Plan-document-reviewer verdict: PASS (2026-05-31, 14/14)

## Task 1 — SKILL.md: depth-based ceiling + active parallel-marking pass
- Description: Edit `writing-plans/SKILL.md` two adjacent sections (one coherent
  "make planning parallelism-aware" change). (a) **Plan size ceiling** — rewrite
  from "≤5 atomic tasks (total count)" to "**critical-path DEPTH ≤5**" (longest
  chain of tasks linked by `Dependencies`); N independent tasks at the same level
  (disjoint `Files touched`, no semantic dep) count as **one level**, not N. State
  **no hard width cap** in the plan (declare `Independent: true`; the dispatch/
  harness layer queues concurrency — `dispatching-parallel-agents` names no number).
  Reframe "a 10-task plan is almost always a discovery failure" → a deep chain is;
  a wide-shallow plan is not. Keep the "split into N sequential briefs" path but
  fire it on DEPTH overflow, not width. (b) **Splitting framework** — add a
  post-split pass: "for each pair of same-level tasks, if `Files touched` are
  disjoint AND there is no semantic dependency (data/symbol/doc-mirrors-code), mark
  both `Independent: true`." Include the guard sentence: **disjoint files ≠
  independent** — a real semantic dep keeps tasks sequential regardless of file
  disjointness.
- Module: code-toolkit/skills/writing-plans/SKILL.md
- Files touched: code-toolkit/skills/writing-plans/SKILL.md
- Context paths:
  - docs/loom/specs/2026-05-31-writing-plans-parallelism-aware-ceiling.md
  - code-toolkit/skills/writing-plans/SKILL.md
- Acceptance:
  - RED: `grep -ci "critical-path depth\|critical path depth" SKILL.md` returns 0;
    the splitting framework has no parallel-marking pass.
  - GREEN: ceiling section keyed on depth (grep "critical-path"/"depth ≤5" or
    equiv); "no hard width cap" stated; the "10-task = discovery failure" line
    reframed to depth; splitting framework has the parallel-marking pass step with
    the "disjoint files ≠ independent / Dependencies is the floor" guard sentence
    present; SKILL.md body within ~6,000-token budget (`wc -w`); validate-skill-
    folder hook clean.
- Dependencies: none
- Independent: true
- Brief item covered: Decision §"depth-based ceiling" + Smallest End State items 1
  and 2 (depth ceiling + active parallel-marking pass).

## Task 2 — plan-document-reviewer: advisory Check 15 (missed-parallel)
- Description: Add **Check 15** to `references/plan-document-reviewer-prompt.md`:
  for any two tasks with disjoint `Files touched` AND no dependency edge between
  them but NOT marked `Independent: true`, emit a **NOTE** ("possible missed
  parallel opportunity") — **advisory / non-fatal**, NOT NEEDS_REVISION (the
  planner may have a real semantic reason the files don't reveal). This balances
  the existing one-directional Check 14 (which only catches over-claiming).
  Update the "Checks 13–14 N/A when no Independent task" note to clarify Check 15
  is advisory and runs regardless.
- Module: code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Files touched: code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Context paths:
  - docs/loom/specs/2026-05-31-writing-plans-parallelism-aware-ceiling.md
  - code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Acceptance:
  - RED: `grep -c "Check 15\|missed parallel\|missed-parallel" plan-document-reviewer-prompt.md` returns 0.
  - GREEN: Check 15 present, explicitly marked advisory/non-fatal (emits NOTE, not
    NEEDS_REVISION); names the condition (disjoint files + no dep + not marked
    Independent); existing Check 14 unchanged.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 3 (advisory reviewer Check 15);
  Decision §"symmetric advisory reviewer check".

## Task 3 — plan-format.md: depth definition + wide-parallel worked example
- Description: Add to `references/plan-format.md` (a) a one-line definition of
  "critical-path depth" (longest chain of tasks linked by `Dependencies`), and
  (b) a worked example showing N disjoint `Independent: true` tasks at one level
  counting as ONE level toward the depth ceiling (a wide-but-shallow plan that is
  NOT a discovery failure). Wording must stay consistent with the ceiling rewrite
  in Task 1.
- Module: code-toolkit/skills/writing-plans/references/plan-format.md
- Files touched: code-toolkit/skills/writing-plans/references/plan-format.md
- Context paths:
  - docs/loom/specs/2026-05-31-writing-plans-parallelism-aware-ceiling.md
  - code-toolkit/skills/writing-plans/references/plan-format.md
  - code-toolkit/skills/writing-plans/SKILL.md  (Task 1's ceiling wording, to mirror)
- Acceptance:
  - RED: `grep -ci "critical-path depth\|one level" plan-format.md` returns 0.
  - GREEN: depth definition + a wide-shallow worked example present; example shows
    N disjoint tasks = one depth level; terminology matches Task 1's SKILL.md.
- Dependencies: Task 1 completes first
- Independent: false  # doc-mirrors-spec: the worked example mirrors Task 1's
    ceiling wording (disjoint file from Task 1, but a genuine SEMANTIC dependency —
    deliberately sequential per the very guard this change introduces)
- Brief item covered: Open Question 1 (depth definition + worked example);
  Decision §"worked example in plan-format.md".

## Task 4 — Version bump 0.13.0 → 0.14.0 + CHANGELOG
- Description: Bump code-toolkit `0.13.0` → `0.14.0` in plugin.json (minor —
  additive planning guidance) and add a `[0.14.0]` CHANGELOG entry describing the
  parallelism-aware depth ceiling + active parallel-marking + advisory Check 15,
  grounded in Bazel critical-path / Kanban WIP / CPM (EN+JA agreement), with a
  provenance pointer to the brief. No backfill of prior missing entries.
- Module: release metadata (plugin manifest + changelog)
- Files touched: code-toolkit/.claude-plugin/plugin.json, code-toolkit/CHANGELOG.md
- Context paths:
  - code-toolkit/.claude-plugin/plugin.json
  - code-toolkit/CHANGELOG.md
  - docs/loom/specs/2026-05-31-writing-plans-parallelism-aware-ceiling.md
- Acceptance:
  - RED: `grep '"version": "0.13.0"' plugin.json` matches; no `[0.14.0]` in CHANGELOG.
  - GREEN: plugin.json version `0.14.0` (valid JSON); CHANGELOG `[0.14.0]` entry
    naming the depth-ceiling + active-marking + Check 15 + Bazel/WIP/CPM grounding +
    brief pointer.
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Open Question 2 (version target 0.13.0 → 0.14.0).

## Notes
- **Dogfoods the change being made**: Task 1 ∥ Task 2 is a genuine 2-wide wave
  (disjoint files — SKILL.md vs plan-document-reviewer-prompt.md — no semantic dep,
  no doc-mirror), so SDD MAY dispatch both implementers in one message. Critical-
  path DEPTH = Task 1 → Task 3 → Task 4 = 3 (≤5). Total count 4.
- **Also dogfoods the disjoint≠independent guard**: Task 3 touches a DIFFERENT file
  from Task 1 (disjoint), yet is marked `Independent: false` and sequenced after
  Task 1 — because the plan-format worked example mirrors Task 1's ceiling wording
  (doc-mirrors-spec semantic dependency). File-disjointness alone did NOT make it
  parallel-eligible; this is exactly the guard the change introduces.
- Doc-only skills: no pytest; acceptance is grep-diagnostic + validate-skill-folder
  hook + token budget. Behavioral validation (depth ceiling + advisory Check 15
  actually fire) is a review-stage / dogfood check, not a separate task.
- Task 4 touches 2 manifest/doc files as one release-metadata unit (repo convention).
