# skill-log-mining v0.1 — brainstorming brief

Brainstorming brief produced 2026-05-22, consumed by `writing-plans` next session. Author: kouko + Claude session.

> **Consumes**: [`2026-05-22-skill-log-mining-research.md`](2026-05-22-skill-log-mining-research.md) (research memo, 545 lines, 4-domain landscape + Stage 1-5 v2 architecture + 6 open questions).
> **Produces**: structured brief for `code-toolkit:writing-plans` to split into atomic tasks.
> **Status**: 5-axis exploration complete; 6 open questions converged; ready for `writing-plans`.

## Locked decisions carried in from research memo

(Not re-litigated in this brief — see memo §Final convergent architecture (v2) and §`/insights` post-run verification.)

1. **`/insights` facets are Stage 1 mandatory input** (not optional sidecar) — `~/.claude/usage-data/facets/*.json` pre-classified per-session data feeds our per-skill aggregation
2. **Trigger = on-demand `Agent()` subagent fan-out** (not cron / `claude -p` headless / SessionStart hook) — within active Claude Code session, inherits auth + skill access
3. **Cross-agent = two-layer architecture** — Layer A (universal friction mining via adapters) + Layer B (Claude-only at v0.1, Codex v0.2, Gemini/Cline/Cursor v1.0)
4. **Differentiator vs 3 closest competitors**: we **iterate EXISTING SKILL.md** (claude-coach writes CLAUDE.md via real-time hooks; crune discovers NEW skills via clustering; yahav10/claude-insights generates NEW skills from `/insights` HTML)

## Problem

**JTBD (job-to-be-done)**: When I've burned through multiple PR cycles using `code-toolkit:*` and noticed the same friction patterns repeating across sessions (brainstorming-then-interrupt within 10 min; re-dispatch concentrated on code-reviewer not implementer; implementer write-before-read tool errors), I want to convert those tacit observations into structured edit proposals against the existing SKILL.md files, so I can graduate the lessons from memory-as-buffer (currently 39.9KB / over the 24.4KB MEMORY.md soft limit) into the actual skill text — without manually spelunking JSONL.

Hidden secondary job: **provide a verification layer over `/insights`**. Its session-level facets miss skill-level patterns and produced at least one documented false positive (`/ultrareview` "invented" misclassification, see research memo §`/insights` false positives).

## Users

### Primary (v0.1 dogfood target) — kouko himself

- Heavy `code-toolkit:*` iterator: 5 wiki-ingest minor versions (v3.10–v3.14) + salesforce-toolkit v0.1.0 + external-surface-grounding all in past 2 weeks (per memory)
- `/insights` warmed: 49 facets JSONs + 199 session-meta JSONs + 69KB report.html confirmed present 2026-05-22
- Single-machine `~/.claude/projects/` only at v0.1 (no multi-machine sync)
- Cron exists in his stack (per pending-repo-settings memory) but mining trigger is on-demand
- **Hard constraint**: MEMORY.md size pressure (39.9KB / 24.4KB limit) — kouko needs a graduation pipeline, not another buffer

### Secondary (v0.2–v1.0) — other monkey-skills users

- Won't have kouko's PR history / memory file context
- May or may not have `/insights` data warmed
- Need defaults that work zero-config + YAML escape hatch

### Tertiary (v1.0+) — cross-agent users

- Codex / Gemini / Cline / Cursor users
- Served by Layer A adapters
- Out of scope for v0.1

### User non-goal

This is **NOT a productivity-coach for end-users** (that's claude-coach territory). Target user is **skill maintainer**, not skill consumer.

## Smallest End State

### One-paragraph summary

User invokes `/skill-log-mining` (or `Skill(skill: "dev-workflow:skill-log-mining")`) → skill (Python script + structured subagent prompts) reads `~/.claude/projects/**/*.jsonl` + `~/.claude/usage-data/facets/*.json` → normalizes to unified Event[] schema → per-skill aggregation against `code-toolkit:*` family with friction-signal scoring → top-N high-friction skills × ≤5 trajectories each → fan-out via `code-toolkit:dispatching-parallel-agents` to subagents that produce structured Failure/Success Memory Items (Trace2Skill-style prompt) → orchestrator merges → human sees diff against SKILL.md only → approve / reject / edit → write. No silent writes. Within-run fingerprint counting for "appears in N projects" confidence tags.

### 6 open questions converged

| # | Question | v0.1 decision | Why |
|---|---|---|---|
| Q1 | Stage scope (1+2+5 / +Stage 3 / full 1-5) | **1+2+3+5** | Stage 3 IS the differentiator (turns report into proposal). Full SDD Stage 4 deferred — orchestrator merges ≤5 trajectories directly, add Stage 4 v0.2 only if merge conflicts emerge in dogfood. |
| Q2 | Skill family scope (`code-toolkit:*` only / any monkey-skills skill) | **`code-toolkit:*` default, parameterized by config glob** | 14 code-toolkit sessions in mining demo = enough proof-of-value. Engine is generic; `target_skill_pattern` glob in YAML lets users widen scope. |
| Q3 | Where lives (new plugin / `code-toolkit:mining` / `dev-workflow:*`) | **`dev-workflow:skill-log-mining`** | Slots into existing 5-strong `skill-*` family (skill-judge / skill-tuning / skill-refactor / skill-creator-advance / brief-before-asking). New plugin premature; `code-toolkit:mining` couples engine to one family. |
| Q4 | Output granularity (SKILL.md only / +references/*.md) | **SKILL.md only** | New-file proposals can't be reviewed as diff; doubles merge surface. Mark proposals needing >500 token new section as `requires_new_reference_file: true` and defer to v0.2 bucket. |
| Q5 | Friction signal threshold defaults | **baked from mining demo Pattern 1-4 + YAML override** | Defaults derived empirically (see table below); not invented. |
| Q6 | Cross-project fingerprint dedup (v0.1 / v0.2) | **count, don't persist** | Within-run fingerprint dict (≤20 LOC) gives "appears in N projects" confidence tag. Persistent ledger (SQLite or JSON) defers to v0.2. |

### Q5 default values (baked from mining demo)

Source: `/tmp/code-toolkit-mine.py` 2026-05-22 run against monkey-skills + komado-Refs + meeting-emo-transcriber (1,333 JSONL / 600MB / 14 code-toolkit sessions).

```yaml
# Default config — derived from mining demo Pattern 1-4 findings
interrupt_window_sec: 600          # Pattern 1: 4/16 interrupts within 10 min of brainstorming
needs_revision_threshold: 2        # Pattern 3: 7/10 re-dispatches were code-reviewer Round 2+
redispatch_threshold: 2            # Pattern 3 (symmetric to needs_revision)
tool_error_proximity_events: 10    # Pattern 4: write-before-read clusters within ~10 events
min_session_count: 3               # Statistical minimum for actionable signal
cross_project_count: 2             # claude-coach pattern (counted in-memory at v0.1, persisted at v0.2)
```

Single YAML config file, optional. Skill invocation reads bundled defaults if no override path passed.

## Current State Evidence

Touch points verified 2026-05-22.

| Dimension | Path / file:line | What's there |
|---|---|---|
| **Forward** (sibling skill family) | `dev-workflow/skills/{skill-judge,skill-tuning,skill-refactor,skill-creator-advance,brief-before-asking}/SKILL.md` | 5-strong `skill-*` family — naming convention + ~6k token SKILL.md budget per CLAUDE.md project rule |
| **Forward** (Stage 3 primitive) | `code-toolkit/skills/dispatching-parallel-agents/SKILL.md` | Across-domain subagent fan-out we'll invoke from Stage 3 |
| **Reverse** (raw data) | `~/.claude/projects/**/*.jsonl` | Per-project per-session JSONL transcripts (mining demo: 1,333 files / 600MB / 14 code-toolkit sessions) |
| **Reverse** (pre-classified data) | `~/.claude/usage-data/facets/*.json` (49 files, 1.0MB) | Per-session goal_categories / outcome / claude_helpfulness / friction_counts / friction_detail — pre-classified by `/insights` Haiku call |
| **Reverse** (companion data) | `~/.claude/usage-data/session-meta/*.json` (199 files) | Session-meta supplement |
| **Error** (signal anchors) | `/tmp/code-toolkit-mine.py:1-236` | Prototype that found Patterns 1-4 (interrupt-after-brainstorm 25% / brainstorm-skip 29% / code-reviewer re-dispatch concentration / write-before-read errors 86 events) |
| **Data** (graduation candidates) | `~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/MEMORY.md` (39.9KB / 24.4KB soft limit) | Feedback memos that mining should help graduate to SKILL.md text |
| **Boundary** (no name collision) | `dev-workflow/skills/skill-log-mining/` does NOT exist | Greenfield slot |
| **Boundary** (related, not touched at v0.1) | `domain-teams/skills/code-team/` exists per CLAUDE.md SSOT direction memory | Mining writes user-facing skill family `dev-workflow:*` only; does NOT touch domain-team SSOT |

**Evidence paths appendix**:

- Research memo: [`2026-05-22-skill-log-mining-research.md`](2026-05-22-skill-log-mining-research.md) (545 lines)
- Mining prototype: `/tmp/code-toolkit-mine.py` (236 LOC, retire on ship of v0.1)
- `/insights` data: `~/.claude/usage-data/{facets,session-meta,report.html}`
- Sibling skills: `dev-workflow/skills/{skill-judge,skill-tuning,skill-refactor,skill-creator-advance,brief-before-asking}/SKILL.md`
- Stage 3 primitive: `code-toolkit/skills/dispatching-parallel-agents/SKILL.md`

## Alternatives Considered

Full landscape in research memo §4-domain landscape. Three closest competitors and how we differ:

| Competitor | Stars (2026-05-22) | What they do | We differ in |
|---|---|---|---|
| [`netresearch/claude-coach-plugin`](https://github.com/netresearch/claude-coach-plugin) | 11 | Real-time hooks (UserPromptSubmit / PostToolUse:Bash / Stop) → SQLite → Haiku aggregate → CLAUDE.md | Post-hoc (no runtime intrusion); target SKILL.md not CLAUDE.md |
| [`chigichan24/crune`](https://github.com/chigichan24/crune) | 7 | Post-hoc clustering (TF-IDF + SVD + Louvain) → discovers NEW skills | Iterate EXISTING SKILL.md; no clustering |
| [`yahav10/claude-insights`](https://github.com/yahav10/claude-insights) | 4 | Parses `/insights` HTML → generates NEW SKILL.md + CLAUDE.md additions + settings hooks | Consume facets/*.json + raw JSONL (not HTML); iterate EXISTING |

Architectural template: **Trace2Skill** (arxiv 2603.25158, Mar 2026). We translate its `ThreadPoolExecutor --max-workers 128` per-trajectory parallel pattern → `Agent()` subagent fan-out via `code-toolkit:dispatching-parallel-agents` (PR #267).

No new alternatives surfaced in this brainstorming round beyond the research memo's coverage.

## What Becomes Obsolete

### Becomes obsolete (graduation candidates)

1. **`/tmp/code-toolkit-mine.py` (236 LOC throwaway prototype)** — same-PR removal on ship. Its 4 Pattern findings become **default signal definitions** (Q5 defaults) baked into the skill.

2. **Implicit "memory feedback memos as skill-iteration backlog" pattern** — currently `feedback_*.md` entries in `~/.claude/projects/.../memory/` function as a buffer where lessons accumulate before "someday" graduating to SKILL.md text. Mining skill provides the explicit graduation pipeline. **This is a process change, NOT same-PR removable.** Defer cleanup to v0.2 ledger that tracks which memos have already been promoted.

3. **Manual cross-correlation of `/insights` facets → skills** — `/insights` currently produces per-session facets that user mentally maps to skill names. Mining skill does this automatically (consumes facets/*.json as Stage 1 input). The `/insights` slash command itself is NOT obsoleted — kouko still wants the user-side report.

### Coexists with (NOT obsoleted)

- **`/insights` slash command** — provides facets/*.json that we consume. Their report is human-readable session-level; ours is machine-actionable skill-level. **Stacked, not overlapping.** Mining skill also serves as **verification layer** catching their false positives (e.g. `/ultrareview` misclassification per research memo §`/insights` post-run verification).
- **`code-toolkit:brainstorming` / `writing-plans` / SDD / TDD chain** — they're the *mechanism* through which approved proposals get implemented. Mining skill produces **input** to these pipelines, not their replacement.
- **`dev-workflow:skill-*` family** — different stages of skill lifecycle:
  - `skill-creator-advance` = create / major redesign
  - `skill-refactor` = token / structure trim with output equivalence
  - `skill-tuning` = output A/B for taste-sensitive skills
  - `skill-judge` = static quality scoring (8-dimension rubric)
  - **`skill-log-mining` (new)** = empirical evidence from real usage logs → edit proposals
- **`code-toolkit:dispatching-parallel-agents`** — Stage 3 uses it directly.

### NOT obsoleted (intentional)

The 39.9KB / 24.4KB MEMORY.md pressure is **indirectly** addressed: mining provides the mechanism to graduate feedback memos, but the act of trimming MEMORY.md is downstream of mining + manual approval. **Don't conflate** the two.

## Decision

**Build `dev-workflow:skill-log-mining` v0.1** as Stage 1+2+3+5 of the v2 architecture from research memo §Final convergent architecture (v2). Engine is generic (Layer A universal across agents per memo); `code-toolkit:*` is the v0.1 target preset. SKILL.md-only outputs at v0.1. Within-run fingerprint counting for cross-project confidence tags; persistent ledger deferred. Defaults baked from mining demo Pattern 1-4 findings; YAML override accepted. Stage 4 (full SDD spec-reviewer + code-quality-reviewer consolidation) deferred to v0.2 — orchestrator merges ≤5 trajectories per target skill directly. Cross-agent adapters (Codex / Gemini / Cline / Cursor) deferred per memo roadmap.

## Out of Scope (v0.1)

- **Stage 4 full SDD consolidation** (defer v0.2 if dogfood shows merge conflicts)
- **`references/<topic>.md` new-file creation** (mark proposals as `requires_new_reference_file: true` and bucket for v0.2)
- **Persistent cross-run fingerprint ledger** (SQLite or JSON) — v0.2
- **Codex CLI adapter** (`~/.codex/sessions/`) — v0.2
- **Gemini / Cline / Cursor adapters** — v1.0
- **AGENTS.md / GEMINI.md / .cursorrules write-back** — v0.3+
- **Auto-trigger** (cron / SessionStart hook) — memo decided: on-demand only
- **Auto-cleanup of graduated feedback memos** in MEMORY.md — process change, manual
- **Headless `claude -p` shell-out** — memo: subagent fan-out replaces this
- **Layer A standalone OSS publication** — defer to post-dogfood signal
- **Auto-merge of approved proposals to main** — human-in-loop approval gates all writes

## Open Questions (deferred to writing-plans)

These five surface only as `writing-plans` carves atomic tasks. Not blocking the brief.

1. **Implementation language**: Python (stdlib, matches monkey-skills tooling, prototype proves <5s on 600MB) vs TypeScript (crune chose TS). **Lean Python.** Defer final pick to plan-time.
2. **LLM model for Stage 3 subagents**: Haiku 4.5 for individual trajectory analysts (Trace2Skill mixed Qwen 35B + 122B) + Sonnet 4.6 for orchestrator merge. **Lean Haiku + Sonnet.** Defer.
3. **UI surface**: stdout markdown report vs file-written diff vs interactive `AskUserQuestion` per proposal. **Lean stdout markdown + diff file written to `docs/skill-mining/<date>-<target-skill>-proposals.md`** for review.
4. **Whether Layer A is later published as standalone OSS** — OTEL GenAI semantic conventions still "Development" status per memo, first-mover slot open. Out of v0.1 scope; surface as future option.
5. **JSONL retention**: `cleanupPeriodDays` default 30 means facets auto-delete after 30 days. Mining run picks up live state. **No archival policy at v0.1** — if kouko wants longer history he extends retention via Claude Code config. Surface in README, don't engineer.

## Handoff to writing-plans

Input ready for `code-toolkit:writing-plans`:

- **Brief**: this document (`docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md`)
- **Research memo**: [`2026-05-22-skill-log-mining-research.md`](2026-05-22-skill-log-mining-research.md)
- **Mining prototype reference**: `/tmp/code-toolkit-mine.py` (236 LOC, signal definitions to import)
- **Touch points verified**: dev-workflow/skills/ family layout, code-toolkit:dispatching-parallel-agents existence, `~/.claude/usage-data/` warmth

`writing-plans` should produce atomic tasks for Stage 1 (ingest + normalize), Stage 2 (per-skill aggregation + scoring + within-run fingerprint), Stage 3 (subagent fan-out + Trace2Skill prompt template), Stage 5 (human-review + diff write + SKILL.md write-back), plus skill scaffolding (SKILL.md + tests + README × tri-language per PR #150 rule).

Estimated atomic task count: 8-12 (>5 → SDD mandatory per code-toolkit router).
