# Plan: Inline rule-sheet — reviewer standards-loading optimization (V1)

**Source brief**: docs/loom/specs/2026-05-18-inline-rule-sheet.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: sequential (with Tasks 1 + 2 parallel-safe — see Notes)
**Plan-document-reviewer verdict**: PASS (2026-05-18, 14/14 checks)

## Task 1 — Write `_rule-sheet.md` SSOT content

- **Description**: Create new file `code-toolkit/scripts/_rule-sheet.md` containing the canonical text of the inline rule-sheet. Required sections: ① preamble (purpose + scope: "these are the deltas between general LLM knowledge and code-toolkit specifics"); ② code-toolkit house thresholds table (20-line soft / 50-line hard / 100-line gate-warning for function length; verdict aggregation rules); ③ dimension → standard path mapping table (6 dimensions to standard file paths); ④ cite-on-fire discipline table (which citation sources MUST `Read` before quoting vs may cite from memory). Target ≤1.5K chars (~250-300 tokens).
- **Module**: `code-toolkit/scripts/`
- **Files touched**: `code-toolkit/scripts/_rule-sheet.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/scripts/_baseline.md` (file format reference — same shape)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/subagent-driven-development/rubrics/quality-gate.md` (verdict rule source)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/code-quality-reviewer.md` (existing dimension table at lines 281-288)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-18-inline-rule-sheet.md` (brief — cite-on-fire table is verbatim)
- **Acceptance**:
  - **RED**: file does not exist at `code-toolkit/scripts/_rule-sheet.md`; `wc -c` would return error
  - **GREEN**: file exists; `wc -c` returns ≤1,536 bytes; contains all 4 required sections (verified by `grep -c '^## '` ≥ 4)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State §"Sheet contains"; Decision §"Single canonical text"

## Task 2 — Insert `rule-sheet-v1` BEGIN/END markers + restructure Standards section in 4 agent files

- **Description**: Edit 4 plugin-level agent files. (a) Insert `<!-- BEGIN rule-sheet-v1 ... -->` and `<!-- END rule-sheet-v1 -->` marker pair in each, positioned after the existing `<!-- END reviewer-discipline-v1 -->` marker (for reviewer agents) or after `<!-- END baseline-v1 -->` (for implementer). Place placeholder text `<!-- populated by distribute.py from scripts/_rule-sheet.md -->` between the markers — Task 3 will replace this with canonical text via `distribute.py`. (b) In 3 agents that currently preload the 7-standards list (`implementer.md:164-171`, `code-quality-reviewer.md:212-225`, `code-reviewer.md` analogous section), remove that preload list and replace with a one-paragraph "Standards (load on cite)" note pointing readers at the cite-on-fire discipline now embedded via rule-sheet. `spec-reviewer.md` has no standards preload list to remove — marker insertion only.
- **Module**: `code-toolkit/agents/`
- **Files touched**: `code-toolkit/agents/implementer.md`, `code-toolkit/agents/spec-reviewer.md`, `code-toolkit/agents/code-quality-reviewer.md`, `code-toolkit/agents/code-reviewer.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/implementer.md` (target — see lines 164-171 for preload list to remove)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/spec-reviewer.md` (target — marker insertion only)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/code-quality-reviewer.md` (target — see lines 212-225 for preload list to remove; line 218 for "Standards (load on demand)" header)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/code-reviewer.md` (target — line 236 analogous header)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/scripts/distribute.py` (lines 164-203 — reference marker pattern from `_baseline.md` / `_reviewer-discipline.md`)
- **Acceptance**:
  - **RED**: `grep -l 'BEGIN rule-sheet-v1' code-toolkit/agents/*.md | wc -l` returns 0 (no markers yet); `grep -l 'load via Read' code-toolkit/agents/*.md` returns ≥1 (preload list still there)
  - **GREEN**: `grep -l 'BEGIN rule-sheet-v1' code-toolkit/agents/*.md | wc -l` returns 4 AND `grep -l 'END rule-sheet-v1' code-toolkit/agents/*.md | wc -l` returns 4; `grep -l 'standards/naming-and-functions.md' code-toolkit/agents/{implementer,code-quality-reviewer,code-reviewer}.md | wc -l` returns 0 (preload list removed from those 3 files)
- **Dependencies**: none (placeholder text between markers; Task 3 replaces it)
- **Independent**: true
- **Brief item covered**: Decision §"Inject `_rule-sheet.md` into all 4 plugin-level agents"; Smallest End State §"Replace upfront `Read` of 7 standards"

## Task 3 — Extend `distribute.py` to route `_rule-sheet.md` into 4 agents

- **Description**: Edit `code-toolkit/scripts/distribute.py`. Add (a) constants `AGENT_RULE_SHEET_SSOT_REL = "scripts/_rule-sheet.md"`, `AGENT_RULE_SHEET_BEGIN`, `AGENT_RULE_SHEET_END` (matching the marker text inserted in Task 2); (b) target list `AGENT_RULE_SHEET_TARGETS = list(AGENT_BASELINE_TARGETS)` (all 4 agents — same routing as baseline); (c) helper `expected_rule_sheet_text()` returning the body of `_rule-sheet.md`; (d) extend `expected_agent_text(agent_rel)` with a third `_rebuild_marker_block` call (after baseline + reviewer-discipline) — applies to all 4 agents (no conditional gate); (e) update `main()` output message to mention rule-sheet sync count.
- **Module**: `code-toolkit/scripts/`
- **Files touched**: `code-toolkit/scripts/distribute.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/scripts/distribute.py` (target file — see lines 163-203 for baseline pattern; 187-202 for reviewer-discipline pattern)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/scripts/_rule-sheet.md` (Task 1 product — SSOT being routed)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/*.md` (Task 2 products — destinations carrying the markers)
- **Acceptance**:
  - **RED**: pre-edit, running `python3 code-toolkit/scripts/distribute.py` writes baseline + reviewer-discipline but leaves rule-sheet block as placeholder text (`<!-- populated by distribute.py -->`); `grep -A1 'BEGIN rule-sheet-v1' code-toolkit/agents/implementer.md | grep 'populated by'` matches
  - **GREEN**: post-edit, running `python3 code-toolkit/scripts/distribute.py` produces output line containing `rule-sheet` for ≥1 agent; `grep -A2 'BEGIN rule-sheet-v1' code-toolkit/agents/implementer.md` shows canonical rule-sheet content (e.g. matches first heading from `_rule-sheet.md`); idempotent (second run reports 0 rewrites)
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false (touches a file Tasks 1 + 2 also depend on conceptually; sequential after them)
- **Brief item covered**: Decision §"existing `_baseline.md`-style BEGIN/END marker mechanism"; Acceptance criteria §"`distribute.py` populates rule-sheet block correctly"

## Task 4 — Add `rule-sheet-v1` coverage to `verify-drift.py` regression test

- **Description**: `verify-drift.py` already iterates over `AGENT_BASELINE_TARGETS` and calls `expected_agent_text` (which after Task 3 includes rule-sheet rebuild) — so drift detection auto-extends. But the test suite has no regression check that asserts rule-sheet markers must exist + rule-sheet drift is detected. Add a new shell test at `code-toolkit/tests/integration/test-rule-sheet-drift.sh` that: (1) runs `distribute.py` to produce clean state; (2) corrupts the rule-sheet block in `implementer.md` (replaces canonical text with `CORRUPT`); (3) runs `verify-drift.py` and asserts exit code is 1 AND output contains `INJECTION-DRIFT.*implementer.md`; (4) restores via `distribute.py` and asserts exit code 0. Follow existing test pattern at `code-toolkit/tests/integration/test-code-team-coexistence.sh`.
- **Module**: `code-toolkit/tests/integration/`
- **Files touched**: `code-toolkit/tests/integration/test-rule-sheet-drift.sh`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/test-code-team-coexistence.sh` (existing test pattern reference)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/README.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/scripts/verify-drift.py` (lines 99-129 — agent injection drift section)
- **Acceptance**:
  - **RED**: `test -x code-toolkit/tests/integration/test-rule-sheet-drift.sh` fails (file does not exist or not executable)
  - **GREEN**: file exists, executable, and `bash code-toolkit/tests/integration/test-rule-sheet-drift.sh` exits 0 (test passes — verify-drift correctly detects corruption then accepts restored state)
- **Dependencies**: Task 3 completes first (verify-drift needs distribute.py extension to test against)
- **Independent**: false
- **Brief item covered**: Acceptance criteria §"`python3 scripts/verify-drift.py` exits 0 after distribute"; supports drift-control invariant in Decision

## Task 5 — Add CHANGELOG v0.9.0 entry + run full verify cycle

- **Description**: (a) Add a new top entry in `code-toolkit/CHANGELOG.md` under heading `## v0.9.0 — 2026-05-18` describing the change: standards loading switched from upfront preload to inline rule-sheet (`_rule-sheet.md`) + on-demand `Read` for citations; references the brief at `docs/loom/specs/2026-05-18-inline-rule-sheet.md`. (b) Run `python3 code-toolkit/scripts/distribute.py` and `python3 code-toolkit/scripts/verify-drift.py`; document the byte-count of the rule-sheet block in 1 reviewer agent (before-state baseline for V2 measurement). Do NOT bump `code-toolkit/.claude-plugin/plugin.json` version in this task — version bump is a separate PR-finalize step.
- **Module**: `code-toolkit/`
- **Files touched**: `code-toolkit/CHANGELOG.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/CHANGELOG.md` (target — see existing entries for format)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-18-inline-rule-sheet.md` (brief to reference)
- **Acceptance**:
  - **RED**: `grep -c 'v0.9.0' code-toolkit/CHANGELOG.md` returns 0
  - **GREEN**: `grep -c 'v0.9.0' code-toolkit/CHANGELOG.md` returns ≥1; entry includes link to brief; running `distribute.py` then `verify-drift.py` both exit 0; rule-sheet block byte-count documented in CHANGELOG entry (a single number, for V2 measurement baseline)
- **Dependencies**: Tasks 3, 4 complete first (distribute + verify-drift must be green to write CHANGELOG)
- **Independent**: false
- **Brief item covered**: Acceptance criteria §"CHANGELOG entry documenting the change"

## Notes

Task 1 and Task 2 have disjoint `Files touched` (`code-toolkit/scripts/_rule-sheet.md` vs `code-toolkit/agents/*.md`) and both declare `Independent: true` — `dispatching-parallel-agents` MAY dispatch their implementers concurrently in one assistant message. Tasks 3, 4, 5 are strictly sequential after Tasks 1+2.

**Sequencing diagram**:

```
Task 1 ─┐
        ├─→ Task 3 ─→ Task 4 ─→ Task 5
Task 2 ─┘
        (parallel)     (sequential downstream)
```

**Cite-on-fire mechanism reminder for SDD orchestrator**: this V1 PR does NOT change reviewer behavior at flag-firing time — the cite-on-fire discipline is encoded in `_rule-sheet.md` content (read by the agent every dispatch). Verifying that reviewers actually follow cite-on-fire is V2 / observation-phase work, not a V1 acceptance criterion.
