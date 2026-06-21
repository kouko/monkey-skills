# Plan: distill-sessions v2.6.1 — known-bugs hotfix

**Source brief**: implicit (no formal brief file) — scope = 3 known bugs confirmed by PR #332 ship retrospective + §Future audit. See [`distill-sessions-v0-3-part-1-shipped`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_part_1_shipped.md) memory + [`haiku-sdd-implementer-conventional-commits`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/feedback_haiku_sdd_implementer_conventional_commits.md) memory for evidence.
**Total tasks**: 4 (≤5 ✓)
**Execution order**: parallel-where-possible (T1+T2+T3 disjoint files; T4 last)
**Plan-document-reviewer verdict**: PENDING

Hotfix bundle following the **B2 inline-TDD pattern** validated by [v0.2 narrow hotfix](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_2_narrow_hotfix.md) per [[orchestrator-self-review-fallback]] — orchestrator inline-executes per-task TDD (no full SDD triad dispatch), single whole-branch `code-toolkit:code-reviewer` subagent at end. Justification: each task is mechanical (≤30 LOC code + ~15 LOC docs), no design space to explore, parallels v0.2 hotfix shape.

## Task 1 — `propose.py` heading state machine fix

- **Description**: In `dev-workflow/skills/distill-sessions/scripts/propose.py`, modify `extract_skill_md_headings` to track fenced-code-block state via a triple-backtick toggle. Lines that match `^```` (with optional language tag) flip the in-code-block flag; while inside a fenced block, `## heading` lines do NOT register as headings. Re-using the existing return shape; no new external surface. Closes the §Future "Heading-extraction state machine (v0.3+)" item.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/propose.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/propose.py`, `dev-workflow/skills/distill-sessions/scripts/test_propose.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/dev-workflow/skills/distill-sessions/scripts/propose.py` (find `extract_skill_md_headings`)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/dev-workflow/skills/distill-sessions/scripts/test_propose.py`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/dev-workflow/skills/distill-sessions/SKILL.md` (§Future bullet to remove on close)
- **Acceptance**:
  - **RED**: `test_propose.py::test_extract_skill_md_headings_skips_fenced_code_block_content` — fixture markdown with `## Real Heading` outside a fenced block AND `## not a heading` inside a fenced code block; assert returned list contains only the outside heading. Test fails on current code (returns both).
  - **GREEN**: new test passes; all existing `test_propose.py` tests stay green; `PYTHONDONTWRITEBYTECODE=1 pytest dev-workflow/skills/distill-sessions/scripts/test_propose.py -v` passes 100%.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Future "Heading-extraction state machine (v0.3+)" — `propose.py`'s `extract_skill_md_headings` does NOT currently skip headings nested inside fenced code blocks (SKILL.md L398-403).

## Task 2 — SKILL.md §Operating notes — `PYTHONDONTWRITEBYTECODE` discipline

- **Description**: Add a new §Operating notes bullet to `dev-workflow/skills/distill-sessions/SKILL.md` documenting the `PYTHONDONTWRITEBYTECODE=1` environment-variable discipline for running pytest in this skill's `scripts/` directory. Explain the chicken-and-egg with `conftest.py` (its own bytecode is written before `sys.dont_write_bytecode = True` runs). Also briefly note the `dcg` safety hook workaround (`shutil.rmtree` via Python for cache cleanup, not `rm -rf`). One short paragraph (~80-120 words) so SKILL.md body stays well under the ~6000 token / ~4500 word cap.
- **Module**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Files touched**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/dev-workflow/skills/distill-sessions/SKILL.md` (§Operating notes around lines 358-388)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/dev-workflow/skills/distill-sessions/scripts/conftest.py` (canonical statement of the chicken-and-egg)
- **Acceptance**:
  - **RED**: `grep -F 'PYTHONDONTWRITEBYTECODE' dev-workflow/skills/distill-sessions/SKILL.md` returns 0 matches (current state).
  - **GREEN**: after edit, `grep -F 'PYTHONDONTWRITEBYTECODE' dev-workflow/skills/distill-sessions/SKILL.md` returns ≥1 match in §Operating notes; SKILL.md body ≤4500 words; YAML frontmatter intact.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: PR #332 Learning — "`__pycache__` hook chicken-and-egg" memory entry — operator must know to use `PYTHONDONTWRITEBYTECODE=1` to avoid the validate-skill-folder hook blocking edits during pytest workflows.

## Task 3 — `code-toolkit/agents/implementer.md` — conventional-commits guidance

- **Description**: Add a new "Role contract — behavioral rule" item (immediately before the BEGIN baseline-v1 marker, in the top "Role contract — behavioral rules" numbered list) to `code-toolkit/agents/implementer.md` documenting that commit subjects MUST follow `<type>(<scope>): <subject>` per the monkey-skills `.github/workflows/skill-structure.yml` regex. Include the type whitelist (`refactor|feat|fix|chore|docs|test`), the kebab-case scope format, AND two examples (one for RED test commit, one for GREEN implementation commit) showing the right vs wrong shape. Roughly +20 LOC. NOT in the `_baseline.md` SSOT block (that propagates to reviewers who don't write commits) — keep implementer-only.
- **Module**: `code-toolkit/agents/implementer.md`
- **Files touched**: `code-toolkit/agents/implementer.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/code-toolkit/agents/implementer.md` (Role contract — behavioral rules section at top)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/.github/workflows/skill-structure.yml` (the regex being documented — lines 170-175)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/code-toolkit/scripts/_baseline.md` (NOT modified — confirm via Read that this is the SSOT and changes there would propagate cross-agent)
- **Acceptance**:
  - **RED**: `grep -F 'conventional' code-toolkit/agents/implementer.md` (case-insensitive: `grep -iF 'conventional commits' code-toolkit/agents/implementer.md`) returns 0 matches.
  - **GREEN**: after edit, `grep -iF 'conventional commits' code-toolkit/agents/implementer.md` returns ≥1 match; `grep -F '<type>(<scope>)' code-toolkit/agents/implementer.md` returns ≥1 match; the new rule is OUTSIDE the BEGIN/END baseline-v1 and BEGIN/END rule-sheet-v1 markers (verify: `awk '/BEGIN baseline-v1/,/END baseline-v1/' code-toolkit/agents/implementer.md` does NOT contain the new text).
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: PR #332 root-cause memory `haiku-sdd-implementer-conventional-commits` — Haiku-tier implementer on TDD tasks emits non-conventional `RED test:` / `GREEN:` / bare `fix:` subjects that fail CI. Mitigation in implementer Role contract surfaces the rule at dispatch time.

## Task 4 — Version bumps + marketplace sync (ship commit)

- **Description**: Bump `dev-workflow/.claude-plugin/plugin.json` from `2.6.0` → `2.6.1` (patch — bug fixes only, no new features) AND `code-toolkit/.claude-plugin/plugin.json` from `0.9.0` → `0.9.1` (patch — agent role-contract addition). Sync `marketplace.json` description fields for BOTH plugins so `python3 scripts/check-marketplace-description-sync.py` exits 0. Both plugin versions bump in same commit because the changes belong to one logical hotfix unit.
- **Module**: `marketplace.json` (single canonical sync source; plugin.json changes are paired prerequisites — analogous to v0.3 part-1 T5 pattern)
- **Files touched**: `dev-workflow/.claude-plugin/plugin.json`, `code-toolkit/.claude-plugin/plugin.json`, `marketplace.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/dev-workflow/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/code-toolkit/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/marketplace.json`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v2.6.1-known-bugs-hotfix/scripts/check-marketplace-description-sync.py` (CI gate)
- **Acceptance**:
  - **RED**: `python3 scripts/check-marketplace-description-sync.py` exits 0 currently (sync state); after bumping both plugin.json files without touching marketplace.json, CI gate stays exit 0 IF descriptions match (versions aren't checked); IF descriptions diverge, exits non-zero — that's the RED.
  - **GREEN**: after edits — `dev-workflow/.claude-plugin/plugin.json` shows `"version": "2.6.1"`; `code-toolkit/.claude-plugin/plugin.json` shows `"version": "0.9.1"`; `python3 scripts/check-marketplace-description-sync.py` exits 0; full distill-sessions pytest suite still 82/82 GREEN plus 1 new test from T1 = 83/83 GREEN; `PYTHONDONTWRITEBYTECODE=1 python -m pytest dev-workflow/skills/distill-sessions/scripts/ -q` invocation evidence.
- **Dependencies**: Tasks 1, 2, 3 complete first (version bump = ship commit; everything must already be green)
- **Independent**: false
- **Brief item covered**: hotfix ship-commit pattern from v0.3 part-1 T5 — bundle plugin version bumps + marketplace sync as the final atomic task.

## Notes

- **Parallel-dispatch eligibility (informational)**: Tasks 1+2+3 all declare `Independent: true` with disjoint `Files touched` sets (T1=`propose.py`+`test_propose.py`, T2=`SKILL.md`, T3=`code-toolkit/agents/implementer.md`). Per [`code-toolkit:dispatching-parallel-agents`](../../code-toolkit/skills/dispatching-parallel-agents/SKILL.md) they MAY run concurrently. **However**, this plan executes via B2-inline (no implementer subagents dispatched) — orchestrator runs each task sequentially with Edit + Bash. Mark the markup for future reference but ignore the parallel mechanism in execution.
- **Whole-branch reviewer dispatch (at end, not per-task)**: after Tasks 1-4 land, dispatch one `code-toolkit:code-reviewer` subagent for whole-branch review per [`code-toolkit:requesting-code-review`](../../code-toolkit/skills/requesting-code-review/SKILL.md). This is the single subagent call in the entire SDD flow for this hotfix.
- **Total estimated implementer LOC**: T1 ~30 + T2 ~15 docs + T3 ~20 docs + T4 ~10 mechanical = ~75 LOC total.
- **Cross-plugin scope**: this hotfix touches both `dev-workflow/` (Tasks 1+2+4) AND `code-toolkit/` (Tasks 3+4). Conventional-commits regex allows scope `<plugin>` or `<plugin>/<sub>` per `.github/workflows/skill-structure.yml`. Use `fix(distill-sessions): ...` for T1+T2, `fix(code-toolkit): ...` for T3, `chore(dev-workflow): ...` for T4 (or split T4 into two commits if cleaner).
