# Plan: code-toolkit Continuous Mode (spec-frozen → PR auto-advance)

Source brief: docs/loom/specs/2026-06-17-continuous-mode-auto-advance.md
Total tasks: 2
Critical-path depth: 2 (≤5)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-06-17, round 2)

## Task 1 — RED structural test for the Continuous-mode router section
- Description: Create `code-toolkit/scripts/test_continuous_mode_router.py`, a stdlib-only
  (`pathlib` + `re`) structural grep-test that asserts the load-bearing PHRASES of the
  Continuous-mode section in `using-code-toolkit/SKILL.md` (mirror the style + docstring of
  `test_brainstorming_greenfield_nudge.py`: tolerant lowercase substring checks that guard
  meaning, not exact wording). Assert presence of: (a) a "continuous mode" + "opt-in"
  section/heading; (b) entry = frozen **spec** + design/spec human-gated + plan auto-generated &
  gated; (c) every stop-contract trigger term — `BLOCKED`, plan critical-path `depth >5`,
  plan-document-reviewer 2-round, review-revision loop bound, debug anchored-thinking/WebSearch
  guard, scope/decision not specified, self-declared assumption, whole-branch NEEDS_REVISION →
  stop, PASS_WITH_NOTES → auto-advance + accumulate, PR-open → stop / never auto-merge;
  (d) the crutch line — must-NOT `re-plan` / `re-scope` / `re-route`; (e) escalation — stop-and-wait
  baseline + optional proactive notification (graceful degrade); (f) the "does not auto-invoke
  downstream skills" caveat carries an explicit opt-in continuous-mode exception.
- Module: code-toolkit/scripts/test_continuous_mode_router.py
- Files touched: code-toolkit/scripts/test_continuous_mode_router.py
- Context paths:
  - code-toolkit/scripts/test_brainstorming_greenfield_nudge.py
  - docs/loom/specs/2026-06-17-continuous-mode-auto-advance.md
- Acceptance:
  - RED: `PYTHONDONTWRITEBYTECODE=1 python -m pytest code-toolkit/scripts/test_continuous_mode_router.py -q` runs and FAILS (assertions trip because SKILL.md has no Continuous-mode section yet).
  - GREEN (later, via Task 2): the same invocation passes.
  - Test is not a no-op: each assertion targets a real phrase from the brief's stop contract.
- External surfaces: none (stdlib + pytest)
- Dependencies: none
- Independent: false
- Brief item covered: "Tests: a grep/structure test asserting the continuous-mode section + stop-contract terms exist in the router (mirrors the repo's existing skill-structure test style). TDD: RED first."

## Task 2 — Add Continuous-mode section + amend the auto-invoke caveat in the router
- Description: Edit `code-toolkit/skills/using-code-toolkit/SKILL.md` to add a new section
  "## Continuous mode (opt-in): spec-frozen → PR auto-advance" carrying: entry conditions
  (explicit opt-in + human-approved frozen spec; design/spec human-gated; plan auto-generated and
  gated by plan-document-reviewer); the full stop-contract table (0a plan depth >5, 0b plan
  reviewer 2-round NEEDS_REVISION, 1 implementer BLOCKED, 2a review-revision ×2, 2b debug
  anchored-thinking guard, 3 scope/decision not in spec, 4 self-declared assumption, 5
  whole-branch NEEDS_REVISION → stop [no auto-remediate], 6 PASS_WITH_NOTES → auto-advance +
  accumulate to PR, 7 PR-open → stop, never auto-merge); the crutch-vs-verification line
  (auto-advance may re-attempt within existing gate bounds but must NOT re-plan / re-scope /
  re-route — those halt); the two-layer escalation (stop-and-wait baseline + optional proactive
  push that degrades gracefully). Amend the "Does not auto-invoke downstream skills" bullet in
  §"What this router does NOT do" with an explicit opt-in continuous-mode exception pointer.
  Reference (do not duplicate) systematic-debugging / SDD / finishing.
- Module: code-toolkit/skills/using-code-toolkit/SKILL.md
- Files touched: code-toolkit/skills/using-code-toolkit/SKILL.md
- Context paths:
  - docs/loom/specs/2026-06-17-continuous-mode-auto-advance.md
  - code-toolkit/scripts/test_continuous_mode_router.py
- Acceptance:
  - RED (inherited from Task 1): `code-toolkit/scripts/test_continuous_mode_router.py` currently FAILS (the Continuous-mode section does not yet exist); this task drives those assertions to GREEN.
  - GREEN: `PYTHONDONTWRITEBYTECODE=1 python -m pytest code-toolkit/scripts/test_continuous_mode_router.py -q` passes.
  - Full package suite green: `PYTHONDONTWRITEBYTECODE=1 python -m pytest code-toolkit/scripts/ -q`.
  - SKILL.md body ≤ ~6k tokens after the edit (router is already large — verify; if it would
    overflow, STOP and surface — do not silently trim load-bearing router content).
  - flat-skill hook not triggered (no new subfolders; test lives in scripts/, not the skill dir).
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "code-toolkit/skills/using-code-toolkit/SKILL.md — new section 'Continuous mode (opt-in) …' + amend the 'does not auto-invoke downstream skills' caveat with the opt-in exception."

## Notes
- Sequential, not parallel: Task 2 edits the file Task 1's test asserts against (doc-mirrors-code
  semantic dependency), so `Independent: false` despite disjoint `Files touched`.
- **Token-budget watch (Task 2):** the router SKILL.md is already substantial. If the +35–55-line
  section pushes the body over ~6k tokens, that is a real stop-and-escalate condition — surface it;
  the fallback (extract the stop-contract table to a `references/continuous-mode.md` and point to
  it) changes the artifact shape and needs a brief amendment, so it is out of scope for silent
  application here.
- No new skill, no plugin-manifest / marketplace change (Shape 1). verify-drift untouched (no
  synced-standard edit). git-memory at commit; identifiable-token grep before commit per guardrails.
