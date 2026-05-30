# Plan: distill-sessions v2.7.1 — propose.py target_skill_path filter

**Source brief**: implicit — bug discovered in v0.3 post-ship dogfood per [[distill-sessions-v0-3-post-ship-dogfood]] memory. propose.py's `extract_memory_items` flattens ALL merged.json entries without filtering by `target_skill_path`; result is that 3 proposal files generated for 3 different target skills are byte-identical except header line.
**Total tasks**: 2 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-05-25, 14/14 checks, 0 gaps)

B2 inline-TDD hotfix pattern (per v2.6.1 hotfix precedent + [[orchestrator-self-review-fallback]]): orchestrator inline-executes per-task TDD, single whole-branch `code-toolkit:code-reviewer` at end. ~30 LOC code+test + ~5 LOC version bump.

## Task 1 — propose.py `extract_memory_items` target_skill_path filter

- **Description**: Add `target_skill_path: str | None = None` kwarg to `dev-workflow/skills/distill-sessions/scripts/propose.py::extract_memory_items`. When non-None, filter input `results` to entries whose `target_skill_path` equals the kwarg before flattening. Default `None` preserves backward-compat (existing tests + the legacy behavior unchanged). In `main()`, pass `args.target_skill` to the call so the CLI argument actually filters as documented. Update docstring to note the filter contract.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/propose.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/propose.py`, `dev-workflow/skills/distill-sessions/scripts/test_propose.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/fix+distill-sessions-v2.7.1-propose-target-filter/dev-workflow/skills/distill-sessions/scripts/propose.py` (target: `extract_memory_items` at line 144; `main()` call site around line 727+)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/fix+distill-sessions-v2.7.1-propose-target-filter/dev-workflow/skills/distill-sessions/scripts/test_propose.py` (existing tests as regression baseline)
  - `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_post_ship_dogfood.md` (root-cause evidence)
- **Acceptance**:
  - **RED**: `test_propose.py::test_extract_memory_items_filters_by_target_skill_path` — fixture: 2 result entries with `target_skill_path` "A" and "B", each containing 2 memory_items. Assert `extract_memory_items(results, target_skill_path="A")` returns 2 items (only from entry A); `extract_memory_items(results, target_skill_path="B")` returns 2 items (only from entry B); `extract_memory_items(results)` (no kwarg) returns 4 items (backward-compat unchanged).
  - **GREEN**: new test passes; all existing `test_propose.py` tests stay green; `PYTHONDONTWRITEBYTECODE=1 python -m pytest dev-workflow/skills/distill-sessions/scripts/test_propose.py -v` reports PASS.
- **Dependencies**: none
- **Independent**: false  # lone wave-leader per [[independent-true-lone-wave-leader]]
- **Brief item covered**: dogfood memory §"NEW BUG: propose.py target_skill_path filtering missing" + §"Fix: v2.7.1 hotfix — add target_skill_path filter in propose.py's input loader. ~10 LOC + 1 test. B2-pattern."

## Task 2 — Version bump v2.7.0 → v2.7.1 + marketplace sync

- **Description**: Bump `dev-workflow/.claude-plugin/plugin.json` from `2.7.0` → `2.7.1` (patch — bug fix only, no new features). Sync `marketplace.json` description if needed (CI gate enforces match — likely no edit needed since description didn't change). `code-toolkit` plugin stays at `0.9.1`. SKILL.md frontmatter stays at `0.3.0` (v0.3 design complete; this hotfix is implementation correction, not redesign).
- **Module**: `dev-workflow/.claude-plugin/plugin.json` (single canonical version source)
- **Files touched**: `dev-workflow/.claude-plugin/plugin.json`, optionally `marketplace.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/fix+distill-sessions-v2.7.1-propose-target-filter/dev-workflow/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/fix+distill-sessions-v2.7.1-propose-target-filter/marketplace.json`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/fix+distill-sessions-v2.7.1-propose-target-filter/scripts/check-marketplace-description-sync.py`
- **Acceptance**:
  - **RED**: `python3 -c 'import json; print(json.load(open("dev-workflow/.claude-plugin/plugin.json"))["version"])'` returns `2.7.0`.
  - **GREEN**: plugin.json version = `2.7.1`; `python3 scripts/check-marketplace-description-sync.py` exits 0; full distill-sessions test suite stays GREEN (98 + 1 new from T1 = 99); `PYTHONDONTWRITEBYTECODE=1 python -m pytest dev-workflow/skills/distill-sessions/scripts/ -q` invocation evidence in commit.
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: hotfix ship-commit pattern per v2.6.1 precedent.

## Notes

- **Whole-branch reviewer dispatch at end**: after T1+T2 land, dispatch one `code-toolkit:code-reviewer` for whole-branch review. Single subagent call; include `PYTHONDONTWRITEBYTECODE=1` discipline per [[whole-branch-reviewer-pycache-discipline]].
- **Total estimated LOC**: T1 ~15 LOC + T2 ~5 LOC = ~20 LOC + 1 new test (~30 LOC).
- **Backward compatibility**: kwarg default `None` preserves existing test fixtures + any external callers; behavior change only fires when `target_skill_path` is explicitly passed (in `main()` after this fix).
