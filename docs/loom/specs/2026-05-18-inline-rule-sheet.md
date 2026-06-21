# Brief: Inline rule-sheet — reviewer standards-loading optimization (V1)

**Date**: 2026-05-18
**Branch**: TBD (this brief is pre-branch)
**Producer**: `code-toolkit:brainstorming` (inline session, 2026-05-18)
**Target version**: code-toolkit v0.9.0

## Problem

**Job (JTBD)**: Let the code-toolkit reviewer fire grounded flags (not gut-feel) without pre-loading 80K chars of standards on every dispatch — and keep "flag triggers can cite primary-source sections" as the toolkit's differentiator vs `obra/superpowers`.

**Klement format**:
> When (dispatching a reviewer subagent for a typical code change), I want (the reviewer to have the minimum context needed to fire grounded flags + cite primary sources), so I can (run code-toolkit's review discipline at affordable cost without compromising its differentiation).

**Symptom**: every reviewer dispatch loads ~80K chars (~20K tokens) of standards / rubrics / checklists upfront, regardless of whether the task triggers any of them. A typical 5-task SDD plan burns 250K-400K tokens in reviewer context alone — repeated for every plan.

## Users

Three readers of the inline rule-sheet:

| Reader | Already knows from training data | Needs from sheet |
|---|---|---|
| Reviewer subagent (primary) | Clean Code / SOLID / DRY / TDD / OWASP top-level concepts | code-toolkit specific thresholds (20 / 50 / 100 lines); verdict aggregation rules; 徳丸本 Ch.6 JP-encoding scope (not in training data); dimension → standard path mapping for cite-on-fire |
| Implementer subagent | same | same — implementer also benefits, as self-checking against the sheet reduces reviewer NEEDS_REVISION rate |
| Toolkit author (kouko) | full context | drift status between sheet and standards |

Usage conditions: reviewer reads the sheet **once per dispatch** at top of prompt. When firing a flag, may `Read` a full standard file for citation accuracy (subject to cite-on-fire discipline below). Sheet must be `<30s` scannable.

## Smallest End State

**Replace upfront `Read` of 7 standards** in each reviewer dispatch **with an inline `_rule-sheet.md` (~1K chars)** injected into agent prompts via the existing `_baseline.md` mechanism. The 7 standards files **stay as on-disk citation targets**, read on demand when a flag needs to cite a specific section.

**Sheet contains** (the *delta* between general LLM knowledge and code-toolkit specifics):
- code-toolkit house thresholds (20-line soft / 50-line hard / 100-line gate-warning function length; etc.)
- Verdict aggregation rules (2🟡 = NEEDS_REVISION; opaque flag = NEEDS_REVISION; etc.)
- Dimension → standard path mapping table
- Cite-on-fire discipline: which citations require `Read` (徳丸本 Ch.6 / OWASP ASVS section numbers / house thresholds) vs may cite from memory (Beck Preface / Clean Code chapters / Fowler smell names)

**Sheet does NOT contain** (general LLM knowledge — agent already has it):
- What F.I.R.S.T means
- Why DRY matters
- SOLID definitions
- Generic "long parameter lists are a smell"

**Target size**: ~800-1,200 chars / ~200-300 tokens.

## Current State Evidence

- **Forward**: 3 reviewer agents load 7 standards via `Read` at dispatch — `code-toolkit/agents/code-quality-reviewer.md:212-225`, `code-reviewer.md` (analogous section), `implementer.md` (analogous section).
- **Reverse**: standards files are consumed by 3 reviewer agents + `code-toolkit/scripts/distribute.py` (SSOT sync from `domain-teams/skills/code-team/standards/`) + `code-toolkit/scripts/verify-drift.py` (CI drift gate).
- **Error**: no error path for "couldn't load standard" — preload is silent default.
- **Data**: 7 standards total ~55K chars; +2 rubrics ~13.9K; +1 security checklist ~6.8K = ~75K chars; ~80K with frontmatter overhead. Loaded **per reviewer per task** — typical 5-task plan ≈ 700K chars.
- **Boundary**: existing injection mechanism (`scripts/_baseline.md` + `scripts/_reviewer-discipline.md` injected via BEGIN/END markers in agent files, managed by `distribute.py` lines 147-307) is the canonical pattern this brief extends.

## Decision

**Adopt Anthropic Skills 3-tier progressive disclosure model** for code-toolkit's standards layer:

- **Tier 2 (skill body, always loaded)**: rubrics (`quality-gate.md`, `arch-gate.md`) + `security-checklist.md` + inline `_rule-sheet.md` (new) + 12-rule baseline (existing) + reviewer-discipline (existing). Total ≈ 8K chars.
- **Tier 3 (referenced files, on-demand `Read`)**: 7 standards files. Read only when a flag's `source:` field cites a specific section, subject to cite-on-fire discipline.

**Inject `_rule-sheet.md` into all 4 plugin-level agents** (implementer + 3 reviewers) via the existing `_baseline.md`-style BEGIN/END marker mechanism. **Single canonical text** — implementer reads same content as reviewers; verdict aggregation rules are informational for implementer (self-check during TDD reduces NEEDS_REVISION rate).

**Cite-on-fire discipline** (binding on reviewers):

| Citation source | Must `Read` to verify before citing? |
|---|---|
| `standards/character-encoding-security.md` (徳丸本 Ch.6 sections) | ✅ MUST (section numbers not in training data; high hallucination risk) |
| `standards/app-security-standard.md` (OWASP ASVS V5 §X.Y.Z numbers) | ✅ MUST (long unfamiliar numbering structure) |
| code-toolkit house thresholds (20/50/100 line tiers; verdict aggregation rules) | ✅ MUST (specific numbers, toolkit-internal) |
| Clean Code chapter names (Ch.2 / Ch.3 / Ch.9 F.I.R.S.T) | ❌ may cite from memory |
| Fowler smell names (Duplicated Code, Long Method) | ❌ may cite from memory |
| Beck 2002 Preface rule | ❌ may cite from memory |

## Alternatives Considered (Axis 4 — research-grounded)

Researched via WebSearch (EN + JA, 2026-05-18). 4 industry approaches surveyed:

1. **Anthropic Skills 3-tier progressive disclosure** ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)) — selected. Direct quote: *"If certain contexts are mutually exclusive or rarely used together, keeping the paths separate will reduce token usage."*
2. **Greptile RAG-over-codebase** ([comparison](https://www.greptile.com/greptile-vs-coderabbit)) — not applicable; Greptile retrieves *code*, not *rules*. Rules still in system prompt.
3. **Pre-inject all PR data** ([ACM 2025](https://arxiv.org/html/2505.16339v1)) — applicable to *ephemeral per-task data*, not *stable canonical text*. PR data ≠ standards.
4. **LLMLingua-style prompt compression** ([codemajin blog](https://www.codemajin.net/llmlingua-llm-prompt-compression/)) — feasible 20× compression; kept as V2 fallback if V1 reveals cite-on-fire navigation issues.

JP industry validation ([Qiita prompt design notes](https://qiita.com/yushibats/items/ba3ecda91dfd21fd1551)): 「重要なルールは先頭に置き、トークン数を無駄なく設計」— rules first, no wasted tokens.

**Conditional reversal**: if V1 missed-flag audit reveals reviewers consistently fail cite-on-fire navigation (writing `source:` without `Read`-ing the file), fall back to alternative #4 (compression — keep inline but heavily compressed).

## What Becomes Obsolete

| Artifact | Status after V1 |
|---|---|
| Agent prompt section "Standards (load via Read)" with full preload list (e.g. `code-quality-reviewer.md:218-225`) | **Replaced** — becomes "Standards (load on cite)" pointing at cite-on-fire discipline |
| Always-load behavior at dispatch | **Removed** — inline rule-sheet replaces it |
| 7 standards files themselves | **Role shift, not deleted** — from "preload input" to "citation target". Still SSOT for canonical text. |
| `distribute.py` / `verify-drift.py` | **Extended** — add `_rule-sheet.md` to the agent-injection routing table. Existing standards routing unchanged. |

## Open Questions (resolved by user during brainstorm)

| # | Question | Resolution |
|---|---|---|
| Q1 | Sheet location: per-agent inline copies vs shared `_rule-sheet.md` injection? | Shared `_rule-sheet.md` injection (mirrors `_baseline.md`); 1 drift surface, not 4 |
| Q2 | Cite-on-fire: must Read for every citation, or memory-OK for canon? | Toolkit-specific (徳丸本 / ASVS / house thresholds) MUST Read; canonical literature (Beck/Martin/Fowler chapters) may cite from memory |
| Q3 | Sheet granularity: pure delta (~1K) vs include all-rules summary (~1.5-2K)? | Pure delta + scoring decision tree (~1K total); rely on LLM general knowledge for the rest |
| Q4 | Implementer scope: receive sheet, or reviewers only? | Implementer also receives sheet (same canonical text); self-checking reduces reviewer NEEDS_REVISION rate |
| Q5 | Sheet authoring: hand-write V1 vs auto-gen from standards? | Hand-write V1 + manual sync via `verify-drift.py` notation; defer auto-gen (would require `## quick-rules` section reformat of standards) to V2 |

## Out of Scope (deferred to V2 or different briefs)

- Adding `## quick-rules` section to each of the 7 standards files (V2 prerequisite for auto-gen)
- Auto-generating `_rule-sheet.md` from standards files (V2)
- `spec-consistency.md` inlining — different problem; spec is per-plan, standards are per-rule
- Wholesale migration of code-toolkit from plugin-agents to Anthropic Skills format
- Token measurement instrumentation (will eyeball post-V1; instrument later if needed)

## Acceptance criteria for V1 PR

- `_rule-sheet.md` exists at `code-toolkit/scripts/_rule-sheet.md` with required sections; ≤1.5K chars
- All 4 plugin-level agents (`implementer`, `spec-reviewer`, `code-quality-reviewer`, `code-reviewer`) carry BEGIN/END `rule-sheet-v1` markers with canonical text populated
- `python3 scripts/distribute.py` populates rule-sheet block correctly (idempotent)
- `python3 scripts/verify-drift.py` exits 0 after distribute
- Reviewer agent files no longer preload the 7-standards list; replaced with cite-on-fire note pointing at standards as on-demand citation targets
- Upfront load for code-quality-reviewer dispatch reduced from ~80K chars to ≤8K chars (≥90% reduction in standards portion)
- Per-reviewer total upfront token load ≤2.5K tokens (vs ~20K today)
- CHANGELOG entry documenting the change
