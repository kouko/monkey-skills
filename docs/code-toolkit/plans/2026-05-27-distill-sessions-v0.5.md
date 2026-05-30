# Plan: distill-sessions v0.5 — Sonnet advisory analyst architecture

**Source brief**: docs/code-toolkit/specs/2026-05-27-distill-sessions-v0.5-brief.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: sequential with T4 + T5 parallel-eligible after T3
**Plan-document-reviewer verdict**: PASS (2026-05-27, 14/14 checks)

## Context summary (for SDD orchestrator)

v0.5 replaces v0.4.1's stdlib-only heuristic clustering + Python template renderer in `scripts/report.py` with a single Sonnet-tier "advisory analyst" subagent dispatch. Architecture A locked (single subagent, no fallback, no `--mode heuristic` opt-in per user Q-v0.5-3 = A clean break). Output: same 7-section advisory at `docs/skill-mining/<date>-advisory-report.md`, but with (a) semantically-clustered anti-patterns, (b) ≤5 real CLAUDE.md candidates (LLM dedup of surface-word noise), (c) code blocks around copy-pasteable text, (d) prose in user's working language via mandatory `--lang zh-TW|en|ja` flag (no default per Q-v0.5-2 = C).

**Pattern parity**: `report.py` mirrors `main.py`'s Stage 3 contract — emits a JSON dispatch payload to stdout; the Claude Code orchestrator dispatches the Sonnet subagent via the `Agent` tool and writes the returned markdown to the report's declared `output_path`. `report.py` itself stays pure-Python (no anthropic SDK; no LLM call inside the script).

**Brief inconsistency note**: brief §"What Becomes Obsolete" lines 213-216 and §"Handoff to writing-plans" line 259 mention a `--mode heuristic` opt-in flag. This contradicts Q-v0.5-3's lock A ("No fallback — fail-fast"; "~120 LOC of heuristic code deleted entirely (not preserved under `--mode heuristic` flag)"). User reconfirmed Q-v0.5-3 = A in 2026-05-27 dialogue ("完全砍掉，clean break；不保留 `--mode heuristic` opt-in；~120 LOC 直接刪"). **The plan follows the Q-lock, not the residual brief prose.** No `--mode` flag; heuristic functions deleted outright.

## Task 1 — Create Sonnet advisory-analyst subagent prompt

- **Description**: Author `dev-workflow/skills/distill-sessions/agents/prompt-advisory-analyst.md` mirroring the sibling `prompt-failure-analysis.md` / `prompt-success-analysis.md` shape — YAML frontmatter (`role: advisory-analyst`, `model: claude-sonnet-4-6`, `input_contract`, `output_contract`, `hard_constraints`, `language`) plus role-play body. Body defines: (a) input is the full merged.json Memory Item set; (b) output is one rendered markdown advisory report covering 7 sections (header / top anti-patterns / per-target SKILL.md breakdown / CLAUDE.md candidates / new-skill candidates / 數字摘要 / action steps); (c) semantic clustering instruction (≤5 distinct anti-patterns; reject surface-word transitive merges); (d) code-block wrapping rule for all copy-pasteable text (suggested edits, command lines, file path references that would be pasted); (e) language-enforcement rule — explanatory prose MUST be in `{{lang}}` (one of `zh-TW`, `en`, `ja`); only code blocks stay English. Pure markdown — no tests.
- **Module**: `dev-workflow/skills/distill-sessions/agents/prompt-advisory-analyst.md`
- **Files touched**: `dev-workflow/skills/distill-sessions/agents/prompt-advisory-analyst.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/agents/prompt-failure-analysis.md`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/agents/prompt-success-analysis.md`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/docs/code-toolkit/specs/2026-05-27-distill-sessions-v0.5-brief.md`
- **Acceptance**:
  - **RED**: `dev-workflow/skills/distill-sessions/scripts/test_prompts_parseable.py` (existing structural-parse smoke-test on agents/*.md) fails because `prompt-advisory-analyst.md` is missing OR has malformed YAML frontmatter.
  - **GREEN**: `PYTHONDONTWRITEBYTECODE=1 pytest dev-workflow/skills/distill-sessions/scripts/test_prompts_parseable.py -v` passes; the new prompt file's YAML frontmatter parses; required keys (`role`, `model`, `input_contract`, `output_contract`, `hard_constraints`) all present; body contains the 7-section output template + code-block + language-enforcement rules verbatim per the brief's §"Smallest End State".
- **External surfaces**:
  - Internal sibling-team contract: `agents/prompt-failure-analysis.md` + `agents/prompt-success-analysis.md` YAML-frontmatter shape — grounding: in-repo evidence (both files Read in Context paths).
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "Forward (new file) ... agents/prompt-advisory-analyst.md (NEW) — Sonnet subagent prompt; defines analyst role + input/output contracts + code-block formatting rules + language enforcement" (brief §Current State Evidence table) + "agents/prompt-advisory-analyst.md (NEW) — Sonnet subagent prompt mirroring failure/success prompts' YAML-frontmatter shape" (brief §What Becomes Obsolete §New).

## Task 2 — Add analyst-dispatch path + mandatory --lang flag to report.py (TDD; heuristic functions still present)

- **Description**: In `scripts/report.py`, add (a) module-level constant `SUBAGENT_MODEL_ID = "claude-sonnet-4-6"` (parity with `main.py:63`); (b) new pure function `build_dispatch_payload(merged_data, lang, date_str, output_path) -> dict` that returns `{"dispatch_payload": {"prompt_path": "agents/prompt-advisory-analyst.md", "model": SUBAGENT_MODEL_ID, "input": {"merged_data": merged_data, "lang": lang, "date_str": date_str}}, "output_path": str(output_path)}`; (c) CLI `--lang` flag MANDATORY (`required=True`, `choices=["zh-TW", "en", "ja"]`) — argparse exits non-zero on missing or invalid value. Update `main()` so that when invoked normally it (1) reads merged.json, (2) computes `output_path` (existing logic preserved), (3) calls `build_dispatch_payload` and prints the resulting JSON to stdout (so the Claude Code orchestrator can consume it), (4) returns 0. The existing heuristic functions (`cluster_by_title_keyword`, `extract_claude_md_candidates`, `_render_*`, `render_advisory_markdown`, `_STOP_WORDS`, `_tokenize_title`) and the legacy `output_path.write_text(...)` call remain intact for now — T3 removes them. New tests in `scripts/test_report.py` cover the new function + flag behavior.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/report.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/report.py`, `dev-workflow/skills/distill-sessions/scripts/test_report.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/scripts/report.py`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/scripts/test_report.py`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/scripts/main.py` (lines 60-65 for `SUBAGENT_MODEL_ID` constant pattern; lines 312-334 for dispatch payload shape parity)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/scripts/fixture_report_merged.json`
- **Acceptance**:
  - **RED**: New test `test_build_dispatch_payload_emits_correct_schema` in `test_report.py` fails because `build_dispatch_payload` does not exist. Companion test `test_main_requires_lang_flag` fails because argparse currently accepts invocation without `--lang`.
  - **GREEN**: `PYTHONDONTWRITEBYTECODE=1 pytest dev-workflow/skills/distill-sessions/scripts/test_report.py -v` passes; the new function returns a dict with keys `dispatch_payload` (containing `prompt_path` == `"agents/prompt-advisory-analyst.md"`, `model` == `"claude-sonnet-4-6"`, `input` with `merged_data` + `lang` + `date_str`) + `output_path`; CLI invocation without `--lang` exits non-zero; with `--lang zh-TW|en|ja` returns 0 and emits the payload JSON to stdout; with `--lang invalid` exits non-zero.
- **External surfaces**: (omit — pure internal logic; no external API/SDK/CLI/MCP calls. The dispatch payload is a JSON structure consumed by the parent Claude Code orchestrator, which is the same-process caller, not an external surface.)
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: "Forward (target to replace) ... scripts/report.py:464-490 main() argparse | Kept; add --lang flag" + "v0.5 dispatches same way; orchestrator (Claude Code session) issues `Agent` call; report.py outputs payload-for-dispatch the way `main.py` does for Stage 3" (brief §Current State Evidence table) + brief §Decision pipeline steps 1-3.

## Task 3 — Remove heuristic functions + obsolete tests from report.py

- **Description**: From `scripts/report.py` delete (a) `_STOP_WORDS` frozenset; (b) `_tokenize_title` helper; (c) `cluster_by_title_keyword`; (d) `extract_claude_md_candidates`; (e) all 7 `_render_*` helpers (`_render_header`, `_render_anti_patterns_section`, `_render_skill_breakdown_section`, `_render_claude_md_section`, `_render_new_skill_section`, `_render_summary_section`, `_render_action_steps_section`); (f) `render_advisory_markdown`; (g) the legacy `output_path.write_text(...)` line in `main()`. Update module docstring to describe the new architecture (Sonnet analyst dispatch payload emission; no inline rendering). Net delete ~400 LOC. From `scripts/test_report.py` delete tests that target the deleted functions (every test whose subject is one of the deleted symbols). Keep tests added in T2 and any structural tests that still apply (e.g. `parse_merged_json` if exercised; `main` CLI tests for the new emission path).
- **Module**: `dev-workflow/skills/distill-sessions/scripts/report.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/report.py`, `dev-workflow/skills/distill-sessions/scripts/test_report.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/scripts/report.py` (after T2)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/scripts/test_report.py` (after T2)
- **Acceptance**:
  - **RED**: A new test `test_heuristic_functions_removed` in `test_report.py` asserts the deleted symbols (`cluster_by_title_keyword`, `extract_claude_md_candidates`, `render_advisory_markdown`, `_STOP_WORDS`, `_tokenize_title`, all 7 `_render_*` helpers) raise `AttributeError` when accessed on the `report` module — this test currently fails (symbols still present after T2).
  - **GREEN**: `PYTHONDONTWRITEBYTECODE=1 pytest dev-workflow/skills/distill-sessions/scripts/test_report.py -v` passes; `getattr(report, "<deleted_symbol>", None) is None` for every deleted symbol; `report.py` LOC reduced by ≥300 from the post-T2 baseline (sanity check that the removal actually landed); no orphan tests remain in `test_report.py` that reference deleted symbols.
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: "Forward (target to replace) ... cluster_by_title_keyword (~66 LOC; loose heuristic) | Gets replaced by subagent dispatch; function deleted" + "extract_claude_md_candidates (~57 LOC; cross-target keyword heuristic) | Gets replaced by subagent dispatch; function deleted" + "all 7 _render_* helpers + render_advisory_markdown (~190 LOC; pure-Python template) | Most deleted" (brief §Current State Evidence table) + brief §What Becomes Obsolete same-PR-removal list.

## Task 4 — Update SKILL.md Stage 5c prose + version bump 0.4.1 → 0.5.0

- **Description**: In `dev-workflow/skills/distill-sessions/SKILL.md`, (a) bump frontmatter `version: 0.4.1` → `0.5.0`; (b) update the §Stage 5c block to describe the new Sonnet advisory-analyst architecture (replace heuristic-clustering prose with subagent-dispatch prose mirroring how Stage 3 is described); document the mandatory `--lang zh-TW|en|ja` flag; document that the orchestrator must dispatch the Sonnet 4.6 subagent at `agents/prompt-advisory-analyst.md` and write the returned markdown to the `output_path` reported by `report.py`; remove any residual reference to `_render_*` template helpers / heuristic clustering; preserve the v0.4.1 fixture path and output-location convention. ASCII pipeline diagram (if present) updated so Stage 5c shows a subagent dispatch like Stage 3.
- **Module**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Files touched**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/skills/distill-sessions/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/docs/code-toolkit/specs/2026-05-27-distill-sessions-v0.5-brief.md`
- **Acceptance**:
  - **RED**: `grep -n "0.4.1\|cluster_by_title_keyword\|extract_claude_md_candidates" dev-workflow/skills/distill-sessions/SKILL.md` returns ≥1 match (current SKILL.md still references the heuristic + old version).
  - **GREEN**: SKILL.md frontmatter shows `version: 0.5.0`; the same grep returns 0 matches in the Stage 5c block (incidental matches in changelog/version-history sections, if any, are acceptable and intentional); `--lang` flag is documented; analyst-subagent dispatch is described; pipeline diagram (if present) shows Stage 5c as subagent dispatch.
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: "Error (skill version + plugin version) ... SKILL.md:25 version: 0.4.1 → 0.5.0" + "SKILL.md updates: §Stage 5c prose describes analyst architecture; flag documentation; pipeline ASCII updated (Stage 5c now dispatches subagent like Stage 3 does); version 0.4.1 → 0.5.0" (brief §Current State Evidence + §Handoff T4).

## Task 5 — Bump plugin version 2.8.1 → 2.9.0

- **Description**: Edit `dev-workflow/.claude-plugin/plugin.json` to bump `"version": "2.8.1"` → `"2.9.0"`. Minor version bump per brief Q-v0.5-1 (new architecture, not a patch).
- **Module**: `dev-workflow/.claude-plugin/plugin.json`
- **Files touched**: `dev-workflow/.claude-plugin/plugin.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/distill-sessions-v0.5/dev-workflow/.claude-plugin/plugin.json`
- **Acceptance**:
  - **RED**: `grep -c '"version": "2.8.1"' dev-workflow/.claude-plugin/plugin.json` returns `1` (current value still present).
  - **GREEN**: `grep -c '"version": "2.9.0"' dev-workflow/.claude-plugin/plugin.json` returns `1`; the file remains valid JSON (`PYTHONDONTWRITEBYTECODE=1 python -c "import json; json.load(open('dev-workflow/.claude-plugin/plugin.json'))"` exits 0).
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: "Error (skill version + plugin version) ... plugin.json:3 \"version\": \"2.8.1\" → \"2.9.0\" (minor — new architecture)" (brief §Current State Evidence) + brief §What Becomes Obsolete "dev-workflow/.claude-plugin/plugin.json `\"version\": \"2.8.1\"` → `\"2.9.0\"`".

## Notes

- **Wave structure** for SDD: Wave 1 = T1. Wave 2 = T2. Wave 3 = T3. Wave 4 = T4 + T5 in parallel (both `Independent: true`, disjoint `Files touched`: SKILL.md vs plugin.json). Per [[independent-true-lone-wave-leader]], T1/T2/T3 are wave-leaders with no parallel sibling, so `Independent: false`.
- **TDD note for T2**: the implementer follows the working-tree RED-before-GREEN order (write failing test, see it fail, write code, see it pass, commit) but commit-level atomicity is NOT a TDD iron-law floor per [[reviewer-misaggregation-enforce-rule]] family memory; reviewer 🔴 flags on commit-atomicity may be overridden + documented if working-tree TDD discipline was observed.
- **Plan reviewer self-test**: the heuristic-deletion test in T3 RED depends on the new test being added in T3 itself. This is intentional — T3's test asserts a property of the deletion (post-deletion symbol absence) that cannot exist before T3 lands; the test is the GREEN-condition oracle, not a pre-existing failure. T3 is a refactor task where the "RED" is a test that asserts a refactor invariant; the failing-test-first discipline reads slightly differently than for new-behavior tasks but is preserved (test exists before the deletion lands; deletion makes it pass).
- **Operational gotchas** (carried from user instruction):
  1. Worktree commit form: `cd <worktree> && git commit` — not `git -C <worktree> commit` (bash-guard reads branch from caller cwd; see [[git-c-worktree-bash-guard-quirk]]).
  2. Pytest invocations MUST prefix `PYTHONDONTWRITEBYTECODE=1` — every test in Acceptance.GREEN uses it.
  3. `__pycache__` cleanup via two-pass `find -delete` (not `rm -rf`).
  4. `Files touched` paths are flat (no nested subfolder; see [[plan-files-touched-no-nested-subfolder]]).
  5. Conventional-commits format `<type>(dev-workflow): <subject>` mandatory for CI (`.github/workflows/skill-structure.yml`).
- **Cost estimate**: full pipeline run (after v0.5 ship) is still dominated by Stage 3 (~$3-8 per real-vault run). Stage 5c advisory adds ~$0.23 per run (1 Sonnet 4.6 call × ~50K input + ~5K output tokens at $3/$15 per MTok). Negligible vs Stage 3.
