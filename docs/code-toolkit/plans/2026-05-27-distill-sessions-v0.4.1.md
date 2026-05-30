# Plan: distill-sessions v0.4.1 — advisory report generator

**Source brief**: docs/code-toolkit/specs/2026-05-27-distill-sessions-v0.4.1-brief.md
**Total tasks**: 3 (≤5 ✓)
**Execution order**: parallel-where-possible (Wave 1 = T1; Wave 2 = T2 + T3 dispatch-parallel)
**Plan-document-reviewer verdict**: PASS 14/14 (2026-05-27)

## Task 1 — Create scripts/report.py + test_report.py + snapshot fixture (TDD bundle)

- **Description**: In the v0.4.1 worktree, add `scripts/report.py` — a stdlib-only post-processor that consumes the same `merged.json` Stage 4 output as `propose.py` and renders a human-readable advisory report matching the exemplar at `/tmp/v0.4-proposals/2026-05-27-advisory-report.md`. Module exports: (a) `parse_merged_json(path) -> list[dict]` (reuses `extract_memory_items` from propose.py if accessible OR inlines equivalent), (b) `cluster_by_title_keyword(items) -> dict[keyword, list[item]]` (loose: 1+ non-stop-word token overlap, stop-word strip applied — see Q-v0.4.1-3), (c) `extract_claude_md_candidates(items_by_target) -> list[dict]` (items whose title keywords appear across ≥2 target skills), (d) `render_advisory_markdown(...) -> str` (zh-TW prose matching exemplar shape: TL;DR / Top N anti-patterns / SKILL.md modifications per target / CLAUDE.md candidates / 新 skill 候選 / 數字摘要 / 你現在能做的事), (e) `main()` with argparse `--input merged.json --output path.md`. Bundle the snapshot fixture at `scripts/fixtures/v0.4.1-merged-snapshot.json` (copy from `/tmp/v0.4-dispatch/merged.json` — the real Stage 4 output from this session). Write co-located tests in `scripts/test_report.py` with structural assertions: section headings present, item counts match input, output is non-empty for non-empty input, CLAUDE.md candidate count is ≥0, no crashes on empty merged.json.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/report.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/report.py`, `dev-workflow/skills/distill-sessions/scripts/test_report.py`, `dev-workflow/skills/distill-sessions/scripts/fixtures/v0.4.1-merged-snapshot.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/propose.py` (sibling model — argparse + render flow shape; especially `extract_memory_items` and `render_proposals_markdown`)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_propose.py` (test pattern model — fixture-based structural assertions, not byte-identity)
  - `/tmp/v0.4-dispatch/merged.json` (real Stage 4 output to use as fixture — copy into `scripts/fixtures/v0.4.1-merged-snapshot.json` as part of this task)
  - `/tmp/v0.4-proposals/2026-05-27-advisory-report.md` (exemplar output — render_advisory_markdown's structural target; aim for semantic equivalence, not byte-identity)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-27-distill-sessions-v0.4.1-brief.md` (§Decision + Q-v0.4.1-1 to Q-v0.4.1-5 lock decisions)
- **Acceptance**:
  - **RED**: new test `test_report.py::test_render_advisory_markdown_includes_required_sections` fails — asserts the rendered markdown contains all required section headings (`你最常重複的`, `該改的`, `CLAUDE.md 候選`, `新 skill 候選`, `數字摘要`, `你現在能做的事`); fails because `scripts/report.py` does not exist yet
  - **GREEN**: same pytest run passes; `python scripts/report.py --input scripts/fixtures/v0.4.1-merged-snapshot.json --output /tmp/v0.4.1-report.md` produces a non-empty markdown file containing all required sections + at least 1 anti-pattern entry (from the real fixture's 33 items) + ≥1 CLAUDE.md candidate (the cross-target AskUserQuestion / Current State Evidence patterns from the fixture)
  - All existing pytest still green: `PYTHONDONTWRITEBYTECODE=1 pytest dev-workflow/skills/distill-sessions/scripts/ -v` returns 100+N passing (where N is the new test count, expected ≥4)
- **Dependencies**: none (wave leader)
- **Independent**: false  # wave leader with no parallel partner; T2 + T3 depend on T1's module landing
- **Brief item covered**: §Smallest End State "new advisory report at `docs/skill-mining/<date>-advisory-report.md` matching the exemplar shape" + §Decision "Build `scripts/report.py` — a Stage 5c sibling to `propose.py`" + all 4 heuristic clusterings from §Decision (Top N anti-patterns / SKILL.md modifications / CLAUDE.md candidates / 新 skill 候選 placeholder)

## Task 2 — SKILL.md updates: description + pipeline ASCII + §Stage 5c prose + version bump

- **Description**: In the v0.4.1 worktree's [`dev-workflow/skills/distill-sessions/SKILL.md`](../../../dev-workflow/skills/distill-sessions/SKILL.md), make 4 coordinated edits:
  1. **Frontmatter `description:` field** (L4-22 currently mentions `docs/skill-mining/<date>-<target>-proposals.md` output): extend to mention `docs/skill-mining/<date>-advisory-report.md` as a sibling human-readable output. Single short clause insertion.
  2. **§Pipeline ASCII diagram** (L142-160 area, after the propose.py box): add a parallel branch from `merged.json` to a new box `scripts/report.py (Stage 5c)` → `docs/skill-mining/<date>-advisory-report.md`. Keep ASCII alignment.
  3. **§Pipeline §Step <N> — Stage 5c advisory report**: add a new prose subsection (after the existing §"Step 4 — Stage 5a propose.py" block, before §"Step 5 — Stage 5b apply.py" if it exists, OR at end of pipeline steps) describing report.py's role: post-processing, reads merged.json, renders zh-TW human-readable advisory, NOT required for apply.py flow (independent surface), suggested invocation post-propose.py.
  4. **Frontmatter `version:` field** L23: `0.4.0` → `0.4.1`.
- **Module**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Files touched**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.4.1/dev-workflow/skills/distill-sessions/SKILL.md` (the file being edited)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-27-distill-sessions-v0.4.1-brief.md` (§"What Becomes Obsolete" → "Updated on v0.4.1 ship" lists exact edit locations)
- **Acceptance**:
  - **RED**: `grep -n "report.py\|Stage 5c\|advisory-report" /Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.4.1/dev-workflow/skills/distill-sessions/SKILL.md` returns 0 matches (current state — no mention of advisory report); `grep -n "^version: 0.4.0" SKILL.md` matches L23
  - **GREEN**: grep for `report.py` returns ≥2 matches (ASCII + prose section); grep for `Stage 5c` returns ≥1 match (prose section heading); grep for `advisory-report` returns ≥1 match (description field OR prose); `grep -n "^version: 0.4.1" SKILL.md` matches L23 (and `0.4.0` returns empty for the version line)
- **Dependencies**: Task 1 completes first (so SKILL.md prose accurately describes a script that actually exists)
- **Independent**: true  # Files touched (SKILL.md) is disjoint from T3 (plugin.json)
- **Brief item covered**: §What Becomes Obsolete "Updated on v0.4.1 ship" — SKILL.md description + §Pipeline ASCII + version field

## Task 3 — Plugin version bump 2.8.0 → 2.8.1

- **Description**: In [`dev-workflow/.claude-plugin/plugin.json`](../../../dev-workflow/.claude-plugin/plugin.json) L3, change `"version": "2.8.0"` → `"version": "2.8.1"`. Single-line patch bump (additive feature per semver patch convention; v0.4.1 = patch-level skill change → patch-level plugin version).
- **Module**: `dev-workflow/.claude-plugin/plugin.json`
- **Files touched**: `dev-workflow/.claude-plugin/plugin.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.4.1/dev-workflow/.claude-plugin/plugin.json` (the file being edited)
- **Acceptance**:
  - **RED**: `grep '"version"' /Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.4.1/dev-workflow/.claude-plugin/plugin.json` returns `"version": "2.8.0",`
  - **GREEN**: same grep returns `"version": "2.8.1",`
- **Dependencies**: Task 1 completes first (semantic ordering — version bump represents new feature; should land after feature exists)
- **Independent**: true  # Files touched (plugin.json) is disjoint from T2 (SKILL.md)
- **Brief item covered**: §What Becomes Obsolete "Updated on v0.4.1 ship" — dev-workflow plugin.json version 2.8.0 → 2.8.1

## Notes

### Wave structure

- **Wave 1**: T1 alone (creates report.py module that T2's prose describes)
- **Wave 2 (dispatch-parallel)**: T2 + T3 — both `Independent: true` with disjoint `Files touched` (SKILL.md / plugin.json). Per [`code-toolkit:dispatching-parallel-agents`](../../../code-toolkit/skills/dispatching-parallel-agents/SKILL.md), SDD MAY dispatch their implementers in **one assistant message** with two `Agent` calls.

### Brief-to-task coverage map

| Brief §Smallest End State / §Decision item | Covering task(s) |
|---|---|
| New `scripts/report.py` stdlib-only post-processor | T1 |
| Reads `merged.json` Stage 4 output | T1 (parse_merged_json) |
| Renders advisory markdown matching exemplar shape | T1 (render_advisory_markdown) |
| 4 heuristic clusterings (Top N / SKILL.md mods / CLAUDE.md candidates / 新 skill placeholder / 數字摘要) | T1 |
| Output to `docs/skill-mining/<date>-advisory-report.md` | T1 (argparse default OR documented behavior) |
| Co-located tests + fixture | T1 (test_report.py + scripts/fixtures/v0.4.1-merged-snapshot.json) |
| SKILL.md description mentions advisory report | T2 (edit 1) |
| SKILL.md pipeline ASCII shows report.py branch | T2 (edit 2) |
| SKILL.md §"Step 5c" prose | T2 (edit 3) |
| SKILL.md version 0.4.0 → 0.4.1 | T2 (edit 4) |
| dev-workflow plugin.json 2.8.0 → 2.8.1 | T3 |

All brief items covered; no orphan tasks.

### Iron-law verification trail

T1 is TDD-iron-law subject (new behavior + new module). Sequence:
1. Implementer writes `test_report.py` FIRST with failing test asserting required section headings
2. Runs pytest → confirms RED (module doesn't exist → ImportError, OR module exists but no required sections rendered)
3. Writes `report.py` to make RED → GREEN
4. Bundles fixture file (copy from /tmp/v0.4-dispatch/merged.json)
5. Final pytest run: all green

T2 and T3 are NOT new-behavior TDD subject (T2 = doc updates; T3 = single literal swap). Both use **grep diagnostics** as RED per plan-format §"specific failing diagnostic" allowance — consistent with v0.4 T4's SKILL.md edit task precedent.

### Operational notes for SDD orchestrator

- All tasks happen in worktree `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.4.1/`
- Use `cd <worktree> && git commit` form (NOT `git -C <worktree> commit` per [[git-c-worktree-bash-guard-quirk]] memory)
- Set `PYTHONDONTWRITEBYTECODE=1` on all pytest invocations
- Conventional-commits format: `feat(dev-workflow):` for T1, `docs(dev-workflow):` for T2, `chore(dev-workflow):` for T3
- If `__pycache__` accumulates, use `find ... -delete` two-pass (NOT `rm -rf` — hook-blocked per [[dcg-heredoc-scan-blocks-descriptive-text]])

### Post-ship validation (NOT an SDD task — operator-manual)

After PR merges:
1. Re-run main.py against `~/.claude/projects` → produces fresh merged.json
2. Run `python scripts/report.py --input <merged.json> --output docs/skill-mining/2026-05-27-advisory-report.md`
3. Verify output matches exemplar shape AND is readable in 60 seconds AND surfaces ≥1 anti-pattern + ≥1 CLAUDE.md candidate from the fresh dataset
4. Optional: write `project_distill_sessions_v0_4_1_first_dogfood.md` if findings differ meaningfully from v0.4 first-dogfood

Belongs to operator-manual validation per v0.1 bare-invocation protocol.
