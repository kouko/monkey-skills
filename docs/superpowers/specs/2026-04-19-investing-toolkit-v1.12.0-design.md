# Design Spec: investing-toolkit v1.12.0 + domain-teams v5.2.0 — Pattern C UX improvements

**Date**: 2026-04-19
**Cross-plugin**: investing-toolkit + domain-teams
**Previous release**: investing-toolkit v1.11.0 (PR #94, merged 2026-04-19); domain-teams v5.1.0

## 1. Goal

Pattern C demo (2026-04-19 NVDA investment memo walk-through) exposed 3 UX issues:

1. **No file-write default** — 2500-word memo lived only in chat transcript; risks VS Code UI collapse, session-end loss, inconsistent with `grounding-vX.X.X.md` pattern (those ARE persisted)
2. **Skill drift** — `investment-memo-writer` SKILL.md references `domain-teams:investing-team` but that skill isn't loaded; `domain-teams:research-team` covers the use case per its description
3. **Agent silence** — Phase 3 deep memo dispatch runs ~2 min silent; user can't distinguish "working" from "stuck"; broader skill-design gap affecting all domain-teams workflow skills

v1.12.0 fixes all three. Cross-plugin because visibility convention is `skill-team` level concern (affects 7 workflow skills across `domain-teams`).

## 2. Context

### 2.1 Pattern C observed execution (NVDA demo)

- Phase 1 (inline Bash data fetch): visible ✓
- Phase 2 (inline regime reasoning): visible ✓
- Phase 3 (research-team via general-purpose agent): ~2 min silent black box ✗

### 2.2 User requirements (from brainstorming, 2026-04-19)

| Requirement | Decision |
|-------------|----------|
| D1 default path | `$CLAUDE_PLUGIN_DATA/memos/` (plugin convention) |
| D2 chat display | Option A: executive summary + gate verdicts + file link; full memo only in file |
| D3 versioning | Overwrite by default; deep vs quick mode get separate filenames |
| D4 scope | Only `investment-memo-writer` this round |
| Obsidian mode | Auto-detect vault + read vault CLAUDE.md + use obsidian skills |
| Responsiveness | 軸 1 (narration) + 軸 2 (TaskUpdate emission) — 60s max silence |

### 2.3 Why cross-plugin

- Commits 1, 2, 3, 5 = investing-toolkit (`investment-memo-writer` SKILL.md edits)
- Commit 4 = domain-teams (skill-team convention + 7 workflow skills)
- Single PR keeps commit stack coherent; v1.9.0 cross-plugin precedent (investing-team ISQ gate)

## 3. Scope — single PR, 6 commits

### 3.1 Commit 1 — file-write default

**Files modified**:
- `investing-toolkit/skills/investment-memo-writer/SKILL.md` — Phase 5 adds file-write logic

**Behavior**:

Write path: `$CLAUDE_PLUGIN_DATA/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`
- `{mode}` ∈ `{deep, quick}` (D3 mode-separated filenames)
- Overwrite on same-day same-mode re-run
- If `$CLAUDE_PLUGIN_DATA` unset (standalone invocation), fallback to `~/.cache/investing-toolkit/memos/`

Required frontmatter:
```yaml
---
title: "{ticker} investment memo"
date: YYYY-MM-DD
ticker: {TICKER}
mode: {deep|quick}
recommendation: {Buy|Hold|Sell}
confidence: {IPCC AR5 scale}
target_base: {$}
target_bull: {$}
target_bear: {$}
stop_loss: {$}
tags: [investment-memo, {ticker-lower}, {sector}, {regime-phase}]
---
```

Chat display after write (D2 Option A):
- 📄 File path link at top
- Executive summary (~150 words, memo's §1)
- Gate verdicts table (from memo's "Gate Results Summary")
- Note: "Full memo at {path} — see for scenarios, risks, valuation detail"

### 3.2 Commit 2 — Obsidian mode integration

**Files modified**:
- `investing-toolkit/skills/investment-memo-writer/SKILL.md` — Obsidian mode branch

**Detection logic**:
1. Explicit skill param `output=obsidian` OR natural-language intent ("寫成 Obsidian 筆記" / "save to Obsidian" / "put in vault")
2. Resolve vault path:
   - a. `$OBSIDIAN_VAULT_PATH` env var (if set)
   - b. Probe common paths: `~/kouko-obsidian-vault/`, `~/Documents/Obsidian/`, `~/iCloud Drive/Obsidian/`
   - c. If none found, fall back to default path (Commit 1) with warning "Obsidian vault not detected"
3. Read `{vault}/CLAUDE.md` if exists — extract folder convention for research notes (look for patterns like `research/`, `投資/`, etc.)
4. Default target within vault: `{vault}/research/{YYYY-MM-DD} {ticker} investment memo.md` unless CLAUDE.md specifies otherwise
5. Use `obsidian:obsidian-markdown` skill for frontmatter + wikilinks + Obsidian-specific formatting

**Invocation examples**:
- `investment-memo-writer --ticker NVDA --output obsidian`
- User: "幫我跑 NVDA memo 存成 Obsidian 筆記" → Claude detects intent, routes to Obsidian mode

### 3.3 Commit 3 — Phase 3 target fix (skill drift)

**Files modified**:
- `investing-toolkit/skills/investment-memo-writer/SKILL.md` — replace `domain-teams:investing-team` references

**Changes**:
- Phase 3 target: `domain-teams:research-team` (instead of `domain-teams:investing-team`)
- Update pipeline description to reflect research-team's "investment or macro analysis" scope
- Add note: "Previously targeted domain-teams:investing-team (v5.0.0-v5.1.0 transient); v1.12.0 routes to research-team which covers the investment analysis use case per its description"

**Verification**:
```bash
grep "investing-team" investing-toolkit/skills/investment-memo-writer/SKILL.md
# Expected: 0 matches in directive text; historical note acceptable
```

### 3.4 Commit 4 — Visibility Convention in skill-team + 7 workflow skills

**Files modified** (domain-teams plugin):
- `domain-teams/skills/skill-team/SKILL.md` — add Visibility Convention section
- 7 workflow skills: `research-team`, `code-team`, `design-team`, `docs-team`, `devops-team`, `qa-team`, `planning-team` — each adds compliance block

**Skill-team convention text** (authoritative):

```markdown
## Visibility Convention (v5.2.0+)

Workflow skills that execute multi-phase tasks (memo writing, code
generation, test plan, etc.) MUST emit TaskUpdate at 3 levels:

1. **Phase transition** — at start and end of each major phase
   (e.g., "Phase 3.1 Thesis — starting", "Phase 3.1 — complete")

2. **Milestone** — each section / deliverable completed
   (e.g., "Executive Summary drafted", "Valuation cross-check done")

3. **Heartbeat** — no silent period > 60 seconds; emit "still working
   on {current_section} — {brief status}" if deep in extended reasoning

**Rationale**: user cannot distinguish "agent working" from "agent stuck"
without visible feedback. Silence > 60s degrades UX; silence > 2min
risks user abandoning task.

**Enforcement**: applied via agent prompt requirement. Skill authors
must include this in the prompt they build for subagent dispatch.

**Probabilistic note**: compliance depends on agent behavior; not 100%
structural guarantee. If strict guarantee needed, consider phase-split
architecture (軸 3; deferred to future release).
```

**Each workflow skill adds**:
```markdown
## Compliance: Visibility Convention (skill-team v5.2.0+)

This skill dispatches multi-phase work. When invoked, it emits
TaskUpdate at phase transitions, milestones, and heartbeat intervals
per skill-team Visibility Convention. See agent prompts for
specifics.
```

### 3.5 Commit 5 — Narration pattern (軸 1) applied to investment-memo-writer

**Files modified**:
- `investing-toolkit/skills/investment-memo-writer/SKILL.md` — add Narration Convention section

**Content**:

```markdown
## Narration Convention (v1.12.0+)

Before each Agent dispatch in this pipeline, controller narrates:
- Expected duration
- What's about to happen
- Expected TaskUpdate cadence (~60s heartbeat minimum per skill-team
  Visibility Convention)

Example before Phase 3 dispatch:
"Starting Phase 3 — dispatching research-team for deep equity memo
(expected 2-5 min). You will see TaskUpdates at phase transitions,
milestones, and heartbeats (~60s max silence). If silent > 2 min,
likely agent stuck — interrupt and I'll investigate."

This narration sets user expectation before any silent period.
Combined with skill-team Visibility Convention (TaskUpdate cadence),
provides both expectation-setting (軸 1) and real-time visibility (軸 2).
```

### 3.6 Commit 6 — Plugin-level sync

**Files modified**:
- `investing-toolkit/.claude-plugin/plugin.json` — `1.11.0` → `1.12.0`
- `investing-toolkit/README.md` — v1.12.0 Version Highlights prepended
- `investing-toolkit/ROADMAP.md` — v1.12.0 current; v1.13.0+ deferred list
- `domain-teams/.claude-plugin/plugin.json` — `5.1.0` → `5.2.0`
- `domain-teams/README.md` — v5.2.0 entry (Visibility Convention)

**Version Highlights (investing-toolkit README)**:
```markdown
### v1.12.0 (2026-04-19) — Pattern C UX improvements

Fixes 3 UX issues exposed by v1.11.0 NVDA Pattern C demo:
- investment-memo-writer Phase 5: file-write default
  `$CLAUDE_PLUGIN_DATA/memos/` + Obsidian mode auto-detect
- investment-memo-writer Phase 3: target fix (research-team, remove
  stale investing-team reference)
- Narration + TaskUpdate convention (cross-plugin with domain-teams
  v5.2.0) enforces max 60s silence via skill-team Visibility Convention

Architectural alternative (軸 3 phase-split) deferred to v1.13.0+ if
軸 1+2 insufficient in practice.
```

## 4. Data Flow

```
Commit 1 (file-write): investment-memo-writer Phase 5 → write file +
  emit chat summary

Commit 2 (Obsidian): Phase 5 detects obsidian intent → read vault
  CLAUDE.md → invoke obsidian:obsidian-markdown skill → write to
  vault research/ folder

Commit 3 (skill drift fix): Phase 3 dispatch target changes
  investing-team → research-team

Commit 4 (convention): skill-team SKILL.md adds Visibility Convention;
  7 workflow skills add compliance blocks

Commit 5 (narration): investment-memo-writer orchestration docs pre-
  dispatch narration pattern + concrete example

Commit 6 (sync): version bumps + README Version Highlights + ROADMAP
```

## 5. Testing & Verification

Per-commit verification:

| Commit | Check |
|--------|-------|
| 1 | `$CLAUDE_PLUGIN_DATA/memos/2026-04-19_NVDA_quick_memo.md` exists after quick run; chat shows exec summary + link |
| 2 | `OBSIDIAN_VAULT_PATH=...` + obsidian mode writes to `{vault}/research/`; obsidian frontmatter present |
| 3 | grep `domain-teams:investing-team` in investment-memo-writer SKILL.md returns only historical-note context (0 directives) |
| 4 | grep `Visibility Convention` in each of 7 workflow skills returns ≥1 match; skill-team SKILL.md has convention section |
| 5 | grep `Narration Convention` in investment-memo-writer SKILL.md returns ≥1 match |
| 6 | Both plugin.json versions bumped; `sync-check.sh` exit 0 in both plugins |

Global Pattern C re-run verification:
```
/invest-memo --ticker NVDA --scope quick
```
Expected:
- Pre-dispatch narration visible before Phase 3
- TaskUpdate visible at each phase / milestone
- Max observed silence < 60s
- Memo file at `$CLAUDE_PLUGIN_DATA/memos/2026-04-19_NVDA_quick_memo.md`
- Chat shows exec summary + file link, NOT full 2500-word memo

## 6. Explicit Non-goals

- **No 軸 3 phase-split** — defer to v1.13.0+ if 軸 1+2 prove insufficient
- **No memo content quality changes** — just persistence + visibility
- **No new data fetchers / analysis skills**
- **No cross-plugin delegation contract restructuring** — delegation pattern from CLAUDE.md preserved
- **No file-write extension to stock-screener / dcf-valuation / invest-portfolio** — D4 limits scope to investment-memo-writer
- **No sector ETF workflow** — v1.13.0+ candidate (per v1.11.0 discussion)
- **No new ticker type support** (ETF / TW / KR / CN stock equity data)

## 7. Branch + PR

```
Branch: feat/pattern-c-ux-v1.12.0
PR title: feat(pattern-c): v1.12.0 UX — file-write + visibility convention
Base: main
Stack: 6 commits (cross-plugin)
```

## 8. Self-Review

- **Placeholder scan**: none. Known-unknowns: Obsidian vault auto-detection paths probed at implementation; research-team internal phase granularity explored when building TaskUpdate enforcement prompts.
- **Internal consistency**: 6-commit structure follows v1.9.0 / v1.10.0 / v1.11.0 patterns. Cross-plugin precedent via v1.9.0 investing-team ISQ gate.
- **Scope check**: ~3.5 days — appropriately sized. Smaller than v1.11.0 (4 days cross-country); bigger than v1.8.1 (single skill).
- **Ambiguity check**:
  - "Visibility Convention enforcement" — acknowledged probabilistic, not structural guarantee; documented as such
  - "Obsidian vault auto-detect paths" — probe at impl; resolved via ordered fallback
  - "investment-memo-writer mode param" — implement as both explicit flag and natural-language detection

## 9. Deferred to v1.13.0+

- **軸 3 phase-split** — investment-memo-writer Phase 3 decomposed into multiple dispatches (structural guarantee for 60s max silence)
- **File-write convention extension** — apply to stock-screener / dcf-valuation / invest-portfolio
- **Sector ETF cross-plugin workflow** — needs `japan-stock-snapshot` / `korea-stock-snapshot` / `china-stock-snapshot` first
- **KR KTBi via BOK ECOS API key** (carry forward)
- **Full 5-parallel grounding re-audit** (~2026-Q3 target)
- **JGBi YTM solver** — REJECTED per v1.11.0 brainstorm (architectural consistency)
