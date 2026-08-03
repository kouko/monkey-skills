# Plan: SDD mechanical review-weight exemption

Source brief: docs/loom/specs/2026-07-08-sdd-mechanical-review-weight.md
Total tasks: 6
Critical-path depth: 3
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-08, 14/14, round 2)

Shared field/marker facts (referenced by tasks below):
- New per-task plan field: `Review-weight: mechanical` (opt-in; default
  = field absent = today's full-triad behavior, unchanged).
- Co-condition (encoded in plan-format.md + validated by
  plan-document-reviewer Check 16): a task may declare `Review-weight:
  mechanical` ONLY when its Description is an identical or
  near-identical edit reproducible from an exact spec (a concrete
  literal string/diff quoted in the task) — never for logic,
  heuristic, hook, or security-surface changes, regardless of size.
- SDD behavior when set: after the implementer returns DONE, the
  orchestrator SKIPS the spec-reviewer + code-quality-reviewer
  dispatch; instead runs a deterministic self-check (grep the exact
  expected literal string in each of the task's `Files touched`).
  Match → task resolves DONE, no reviewer verdict needed. Mismatch
  (string absent, or diff touches files/lines beyond declared scope)
  → fail-closed, falls back to the full triad.
- Test location CORRECTED from the brief's literal wording ("matching
  test_family_relay.py convention", which lives in
  loom-pipeline/scripts/) to `loom-code/scripts/`: this change is
  loom-code-internal (writing-plans + subagent-driven-development are
  both loom-code skills) and `.github/workflows/loom-code-ci.yml`
  only collects `loom-code/scripts/` + `scripts/` + `.claude/hooks/`,
  not `loom-pipeline/scripts/`. Style (grep-based marker assertions)
  still follows test_family_relay.py's pattern; location follows
  loom-code's own CI wiring.
- Exact current strings in plan-document-reviewer-prompt.md that
  Task 3 edits (verified on disk before writing this plan):
  - line 47 (after Check 15's row): insert a new Check 16 row.
  - line 53: `checks_passed: <N>/<14>          # Check 15 is advisory; it never counts toward pass/fail`
  - line 55: `  - check_id: <1-14>             # Check 15 NEVER appears here — it is advisory, surfaces in notes`
  - line 66: "...Checks 13–14 are N/A when no task declares `Independent: true`..."
  - line 67: "**NEEDS_REVISION**: any applicable check **1–14** failed."

## Task 1 — mechanical regression test file (RED-first)
- Description: Create loom-code/scripts/test_sdd_review_weight_marker.py
  with three test functions: (a) test_plan_format_has_review_weight_field
  — reads plan-format.md, asserts it contains the literal substring
  `Review-weight: mechanical` AND the substring "identical or
  near-identical edit"; (b) test_plan_document_reviewer_has_check_16 —
  reads plan-document-reviewer-prompt.md, asserts it contains "Check 16",
  "Review-weight: mechanical", and the updated denominator token
  "<15>" (replacing the old "<14>"); (c)
  test_sdd_skill_has_mechanical_skip_branch — reads
  subagent-driven-development/SKILL.md, asserts it contains (case-
  insensitive) "Review-weight: mechanical", "skip", and "self-check".
  Run it: all three FAIL (target files don't have the markers yet —
  this is the RED state for Tasks 2/3/4 below).
- Module: loom-code/scripts/test_sdd_review_weight_marker.py
- Files touched: loom-code/scripts/test_sdd_review_weight_marker.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md
  - loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
  - loom-code/skills/subagent-driven-development/SKILL.md
- Acceptance:
  - RED: PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts/test_sdd_review_weight_marker.py -v → all 3 fail (markers absent), no import/syntax errors
  - GREEN (this task only): file exists, is collectible, each of the 3 functions fails for the right reason (a marker-absence AssertionError)
- Dependencies: none
- Independent: false
- Brief item covered: "Ship a mechanical regression test (grep-based ...) asserting the schema field, the check, and the SDD branch text all exist and cross-reference consistently" (brief §Decision)

## Task 2 — plan-format.md schema field
- Description: Edit loom-code/skills/writing-plans/references/plan-format.md:
  (a) in the per-task block schema, add a new optional field line
  `- Review-weight: mechanical` with inline doc describing it as
  opt-in (default absent = full triad) and stating the co-condition
  verbatim: "may ONLY be set when this task is an identical or
  near-identical edit reproducible from an exact spec — never for
  logic, heuristic, hook, or security-surface changes"; (b) add one
  worked-example block (parallel to the existing `Independent: true`
  micro-example) showing 2-3 sibling tasks with identical one-line
  edits, each declaring `Review-weight: mechanical`.
- Module: loom-code/skills/writing-plans/references/plan-format.md
- Files touched: loom-code/skills/writing-plans/references/plan-format.md
- Context paths:
  - loom-code/scripts/test_sdd_review_weight_marker.py (the RED test this makes GREEN)
- Acceptance:
  - RED: loom-code/scripts/test_sdd_review_weight_marker.py::test_plan_format_has_review_weight_field fails
  - GREEN: same test passes; the other two tests in the file remain RED (by design, for Tasks 3/4)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Add `Review-weight: mechanical` as an opt-in per-task field ... across: `plan-format.md` (schema + worked example)" (brief §Decision)

## Task 3 — plan-document-reviewer-prompt.md Check 16
- Description: Edit loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md:
  add Check 16 as a new row after Check 15 (line 47): "If a task
  declares `Review-weight: mechanical`, its Description must read as
  an identical/near-identical edit reproducible from an exact spec
  (quote a concrete literal string/diff) — never for logic/heuristic/
  hook/security-surface work. | Task claims `Review-weight:
  mechanical` but Description describes logic/heuristic/hook/
  security-surface work, OR gives no concrete exact-spec quote".
  Update line 53's `checks_passed: <N>/<14>` → `<N>/<15>` (14 original
  pass/fail checks + new Check 16 = 15; Check 15 stays excluded from
  the denominator exactly as today). Update line 55's `check_id:
  <1-14>` → `check_id: <1-14, 16>`. Update line 66 to add "Check 16 is
  N/A when no task declares `Review-weight: mechanical` (opt-in)."
  Update line 67's "any applicable check **1–14** failed" → "**1–14,
  16**".
- Module: loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Files touched: loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Context paths:
  - loom-code/scripts/test_sdd_review_weight_marker.py (the RED test this makes GREEN)
- Acceptance:
  - RED: loom-code/scripts/test_sdd_review_weight_marker.py::test_plan_document_reviewer_has_check_16 fails
  - GREEN: same test passes; sibling tests remain RED (by design)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "plan-document-reviewer-prompt.md (Check 16 verifying this co-condition holds, not just that the field is present)" (brief §Decision)

## Task 4 — SDD per-task triad skip branch
- Description: Edit loom-code/skills/subagent-driven-development/SKILL.md:
  in "Process — per-task triad" (after step 3's reviewer dispatch,
  ~line 102-106), add a subsection "**Mechanical review-weight
  exemption.**" stating: when a task declares `Review-weight:
  mechanical` and the implementer returns DONE, the orchestrator SKIPS
  the spec-reviewer + code-quality-reviewer dispatch and instead runs
  a deterministic self-check (grep the task's declared exact-spec
  literal string in each of its `Files touched`); a match resolves the
  task as DONE with no reviewer verdict; a mismatch (string absent, or
  diff touches files/lines beyond declared scope) falls back to the
  full triad — fail-closed toward review, never toward silently
  skipping on ambiguity. Note this exemption is gated by
  plan-document-reviewer Check 16 upstream — a plan setting the field
  without satisfying Check 16 never reaches SDD. Add one Red Flags
  table row: agent says "this is basically mechanical, I'll skip
  review even though the plan didn't mark it" → refuse (the marker is
  plan-document-reviewer-validated, never an on-the-fly implementer/
  orchestrator judgment call).
- Module: loom-code/skills/subagent-driven-development/SKILL.md
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md
- Context paths:
  - loom-code/scripts/test_sdd_review_weight_marker.py (the RED test this makes GREEN)
- Acceptance:
  - RED: loom-code/scripts/test_sdd_review_weight_marker.py::test_sdd_skill_has_mechanical_skip_branch fails
  - GREEN: same test passes; all 3 tests in the file now GREEN
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "subagent-driven-development/SKILL.md (the per-task triad's skip branch + self-check procedure)" (brief §Decision)

## Task 5 — release metadata: loom-code plugin manifest bump
- Description: Bump loom-code version 0.27.1→0.27.2 in BOTH
  .claude-plugin/plugin.json and .codex-plugin/plugin.json (use
  `python3 scripts/sync_codex_manifests.py loom-code` for the codex
  one — a drift hook guards direct edits). Both files are kept in sync
  by that one script and are treated as a single conceptual module
  (the plugin manifest) for this task's scope.
- Module: loom-code plugin manifest
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Context paths:
  - loom-code/.claude-plugin/plugin.json (current version)
- Acceptance:
  - RED: `grep -q '"version": "0.27.2"' loom-code/.claude-plugin/plugin.json` fails before edit
  - GREEN: both plugin.json report 0.27.2
- Dependencies: Tasks 2, 3, 4 complete first
- Independent: true
- Brief item covered: "Ship as a `loom-code` version bump (both plugin manifests + a `CHANGELOG.md` entry), per this repo's existing release convention" (brief §Decision)

## Task 6 — release metadata: loom-code CHANGELOG entry
- Description: Add a CHANGELOG.md entry for 0.27.2 describing the
  `Review-weight: mechanical` field + Check 16 + SDD skip branch,
  citing this brief (docs/loom/specs/2026-07-08-sdd-mechanical-review-weight.md),
  and stamping the real test count from
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts/ -q`.
- Module: loom-code/CHANGELOG.md
- Files touched: loom-code/CHANGELOG.md
- Context paths:
  - loom-code/CHANGELOG.md (entry format)
- Acceptance:
  - RED: `grep -q '0.27.2' loom-code/CHANGELOG.md` fails before edit
  - GREEN: CHANGELOG entry present with the measured test count
- Dependencies: Tasks 2, 3, 4 complete first
- Independent: true
- Brief item covered: "Ship as a `loom-code` version bump (both plugin manifests + a `CHANGELOG.md` entry), per this repo's existing release convention" (brief §Decision)

## Notes

- Critical path: Task 1 → {Task 2, 3, 4} → {Task 5, 6} = depth 3 (≤5).
  Tasks 5 and 6 are `Independent: true` (disjoint files, both name the
  literal version 0.27.2 already, no need to read each other's output).
- Task 1 is marked `Independent: false` despite having no dependency
  of its own — it is a solo predecessor Tasks 2-4 depend on, not a
  same-level parallel-wave member; `Independent: true` describes a
  task's relationship to SIBLINGS in its own wave, which Task 1 has
  none of.
- Test location deviates from the brief's literal "test_family_relay.py
  convention" wording: placed in loom-code/scripts/ (not
  loom-pipeline/scripts/) — see the shared facts block above for why.
- No LOC threshold introduced anywhere in this plan's own changes
  (consistent with brief §Decision and §Out of Scope).
