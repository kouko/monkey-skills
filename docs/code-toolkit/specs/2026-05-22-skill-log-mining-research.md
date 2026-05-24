# Skill log mining — industry & architecture research

> ✏️ **2026-05-24 post-ship note** — Narrow-scope v0.1 shipped as **`dev-workflow:distill-sessions`** (PR #328) covering only "iterate existing SKILL.md from session-log evidence". The broad-scope `skill-log-mining` vision in this memo (covering existing-skill iteration + new-skill discovery + CLAUDE.md rule extraction) is queued for v1.0 re-brainstorm. Memo kept as historical research record; future v1.0 brief will re-evaluate prompt-system integration across the three surfaces.

Research memo produced 2026-05-22. **Not a brief, not a decided design** — captures the landscape so the next session doesn't re-research. Author: kouko + Claude session `be116ae7`.

> **Updated same-day 2026-05-22 (post-research convergence)** — added §`/insights` post-run verification, §Subagent vs headless `claude -p` decision, §Cross-agent compatibility layer split. Earlier sections (4-domain landscape / deep dives) unchanged; final architecture in §"Final convergent architecture (v2)" supersedes the earlier §"Convergent architecture proposal".

## Question being researched

Is there industry tooling / academic precedent for "**post-hoc mine `~/.claude/projects/*.jsonl` conversation logs → detect friction patterns → iterate existing Claude Code skills**"? If yes, can we borrow? If no, how should we build?

Triggered by ad-hoc observation that `code-toolkit` heavy use across multiple PRs (wiki-ingest v3.10–v3.14 / salesforce-toolkit v0.1.0 / external-surface-grounding) produced **repeated friction patterns** that would be worth distilling back into the skills.

## 4-domain landscape (May 2026)

### Domain 1: LLM Observability platforms

| Platform | Trace→dataset→experiment | Auto prompt suggestion |
|---|---|---|
| LangSmith | ✅ | ✅ Engine + Polly (2026) |
| Langfuse | ✅ (versioned datasets Feb 2026) | ❌ human-driven |
| Helicone | partial; experiments deprecated 2025-09 | ❌ |
| Braintrust | ✅ one-click add-trace-to-dataset | ✅ **Loop** |
| W&B Weave | ✅ | ❌ |
| Arize Phoenix | ✅ OSS | ❌ |
| PromptLayer | ✅ | ✅ AI prompt writer |

**Key caveat**: 7-of-7 platforms treat skill as `prompt template`. **None natively understand `SKILL.md + references/<topic>.md` multi-file structure**. Adopting any of them means losing skill multi-file shape unless wrapped.

### Domain 2: Academic methodology

| Paper | Year | Data needed | Match to our recipe |
|---|---|---|---|
| APE / OPRO / EvoPrompt / PromptBreeder | 2022–2023 | Labeled dev set | ❌ need labels |
| DSPy / MIPROv2 | 2023–2026 | Labels OR metric callback | ⚠ optimizer tuned for short Q&A signatures, not 1k-line SKILL.md |
| TextGrad | 2024 | Computation graph + textual feedback | ⚠ theoretical scaffolding only |
| Trace (Microsoft) | 2024 | Execution traces + rich feedback | ⚠ theoretical scaffolding |
| Logged-Bandit Prompt Opt | Apr 2025 | Logged data + reward | ⚠ need reward |
| Grounded in Reality (Alibaba) | Oct 2025 | **Free-form unlabeled prod logs** | ✅ validates "implicit preference" half |
| **Trace2Skill** | **Mar 2026** | **Execution traces** | ⭐ **closest match — see deep dive** |
| Skills-on-the-Fly / SkillTTA | May 2026 | Training trajectories | ⭐ test-time variant |

**Honest gap**: no paper combines `(free-form log)` × `(implicit friction signal, no labels)` × `(versioned persistent SKILL.md update)`. Greenfield as a triple, but each pair has precedent.

### Domain 3: Agent ecosystem (closed-loop trace→improvement)

| Vendor | Ships closed loop? |
|---|---|
| OpenAI Agent Builder + Trace Grading + **Automated Prompt Optimization** | ✅ 2025–2026 |
| AWS Bedrock AgentCore **Recommendations** | ✅ 2026 |
| LangChain LangSmith **Engine** | ✅ May 2026 |
| Vertex AI Agent Engine | ⚠ partial (Gemini-tuning preview) |
| AutoGen / Llama Stack | ❌ trace-only |
| **Anthropic Claude Code** | ❌ **zero official methodology** |

Anthropic-specific state:
- **No** official doc / CLI / product for "use JSONL logs to improve skills"
- **Open feature request**: [anthropics/claude-code#35319](https://github.com/anthropics/claude-code/issues/35319) — "0 of 183 skills had usage data" motivating ask
- Community pattern (most-cited): [Martin Alderson, "Self-improving CLAUDE.md", Feb 2026](https://martinalderson.com/posts/self-improving-claude-md-files/) + `claude-log-cli`. Grep JSONL → feed to Claude → improve CLAUDE.md. **CLAUDE.md scope, not SKILL.md scope.**
- **`/insights` slash command** (released Feb 2026 by Anthropic's Thariq Shihipar). **Interactive command, not CLI flag** — must type `/insights` in Claude Code interactive session. Analyzes last 30 days of sessions, runs Haiku-powered facet extraction → writes:
  - `~/.claude/usage-data/report.html` (auto-opens in browser) — friction points / strengths / personalized CLAUDE.md suggestions
  - `~/.claude/usage-data/facets/` — per-session `goal_categories` (10 canonical: feature / bugfix / refactor / docs / review / testing / ci / git_ops / setup / other), `outcome` (fully_achieved / mostly / partially / failed), `claude_helpfulness` (essential / very_helpful / moderately / slightly / unhelpful), friction info
  - **Nuance**: `goal_categories` counts only what USER explicitly asked — NOT Claude's autonomous exploration
  - Available in Claude Code 2.1.x; **not run on kouko's 2.1.144 yet** (verified 2026-05-22 — `~/.claude/usage-data/` doesn't exist). To enable: type `/insights` in Claude Code interactive session.
  - Downstream consumer already exists: [`yahav10/claude-insights`](https://github.com/yahav10/claude-insights) parses the HTML report to generate skills, but new-only (no existing iteration).

### Domain 4: Claude Code community competitors

| Tier | Repo | Differentiation from our idea |
|---|---|---|
| **1 — closest competitor** | [`netresearch/claude-coach-plugin`](https://github.com/netresearch/claude-coach-plugin) v2.5.0 (11⭐) | **Real-time hooks**, in-session reactive. Output = CLAUDE.md, not SKILL.md. Single-session focus. See deep dive. |
| **1 — closest competitor** | [`chigichan24/crune`](https://github.com/chigichan24/crune) (7⭐) | **Post-hoc mining**, but **discovers NEW skills via clustering**, not iterates existing. Author says outputs not production-ready. See deep dive. |
| **2** | [`hancengiz/claude-code-prompt-coach-skill`](https://github.com/hancengiz/claude-code-prompt-coach-skill) (143⭐) | Coaches USER's prompt quality, not skills |
| **2** | [`lucemia/claude-session-analyzer`](https://github.com/lucemia/claude-session-analyzer) | Measures regression; no iteration |
| **2** | [`mrothroc/claude-code-log-analyzer`](https://github.com/mrothroc/claude-code-log-analyzer) (20⭐) | Reports patterns; explicitly does not close loop |
| **1 — late find** | [`yahav10/claude-insights`](https://github.com/yahav10/claude-insights) (4⭐, Feb→May 2026) | **Consumes `/insights` HTML report** (not raw JSONL), generates NEW SKILL.md + CLAUDE.md additions + settings hooks. Author explicit: **"doesn't modify or iterate existing skills"**. TS ~500 LOC + 83 vitest. Same gap as crune (new-only) but via different input path. |
| **3 building block** | [Piebald-AI friction-analysis system prompt](https://github.com/Piebald-AI/claude-code-system-prompts/blob/main/system-prompts/system-prompt-insights-friction-analysis.md) | Building block, community-extracted, not Anthropic-official |
| **3 reader/cost** | li195111, aarora79, withLinda, daaain | Render / cost-analyze JSONL; stop short of iteration |

**Honest assessment** (updated 2026-05-22 after late find): "post-hoc cross-session mining → iterate **EXISTING** SKILL.md" is structurally unoccupied. **All 3 closest competitors (claude-coach / crune / claude-insights) generate NEW skills or write to CLAUDE.md** — none modifies existing SKILL.md content. Differentiation strengthens, not weakens.

## Deep dive: claude-coach — borrow taxonomy, skip architecture

### 4-layer pipeline

| Layer | Component | Trigger |
|---|---|---|
| 1. Hook | `UserPromptSubmit` (5s timeout async) + `PostToolUse:Bash` (5s) + `Stop` (10s) | **Every user prompt + every Bash + session end runs Python** |
| 2. Detect | `scripts/detect_signals.py` regex pattern matching | → `~/.claude-coach/events.sqlite` |
| 3. Aggregate | `scripts/aggregate.py` (Haiku LLM-assisted) | → `candidates.json` |
| 4. Apply | `/coach review` user approves → `apply.py` | → CLAUDE.md (project OR global via scope analyzer) |

### 7 signal types with priority weights

```
COMMAND_FAILURE       100  (single failure = high signal)
PROCESS_VIOLATION      90  (Claude broke its own project rule)
USER_CORRECTION        80  (need 2+ evidence)
SKILL_SUPPLEMENT       75  (user補 skill — our target pattern is similar)
VERIFICATION_QUESTION  72  (user asks "did you do X?")
VERSION_ISSUE          70
REPETITION             60  (need 3+ evidence)
TONE_ESCALATION        40  (review-only, NEVER produces rule)
```

### 5 candidate types

```
rule         "Never edit generated files"
checklist    "Run tests after code change"
snippet      "Preflight check script"
skill        "Add X guidance to Y skill"        ← closest to our intent
antipattern  "Never assume tool exists"
```

### Guardrails (directly applicable to our design)

- max 1 interrupt / 15 min
- minimum evidence ≥ 2 (hard failures excepted)
- **never produce rule from tone alone**
- rules must have explicit "when X, do Y" trigger
- auto-dedup by fingerprint before propose
- **no silent writes** — all proposals require approval

### Fingerprint pattern (cross-session dedup)

```
fingerprint = sha256(normalize(candidate_type + trigger + action))
where normalize = lowercase + strip punctuation + paths → <PATH>

ledger.sqlite: same fingerprint in 2+ repos → auto-suggest promote to global
```

### What we borrow vs reject

**Borrow** (5 things): signal taxonomy, fingerprint dedup, guardrails (6 rules), scope analyzer logic (project vs global), approval-only workflow.

**Reject** (3 things): hook-based runtime intrusion (every prompt + Bash adds latency), CLAUDE.md as sole output target (our differentiator is SKILL.md), 3-SQLite-DB architecture complexity (overkill for v0.1).

## Deep dive: Trace2Skill — our architecture template

Official code: [Qwen-Applications/Trace2Skill](https://github.com/Qwen-Applications/Trace2Skill) (Apache 2.0). Paper: [arxiv 2603.25158](https://arxiv.org/abs/2603.25158). Reproducible on SpreadsheetBench-Verified-400.

### Pipeline (4 stages)

```
Stage 1: run agent on benchmark → trajectory logs (per-task .md, SUCCEED/FAILED tag)
Stage 2: each FAILED log → 1 LLM call in parallel (ThreadPoolExecutor --max-workers 128)
         → "Failure Cause Items" + "Failure Memory Items" (max 3, generalizable)
Stage 3: each SUCCEEDED log → 1 LLM call
         → "Lean Solution Path" + "Success Memory Items" (max 3)
Stage 4: skill_evolver.run_parallel_skill_evolution
         → hierarchical merge → updated SKILL.md + references/*.md
```

### Prompt design (failure analysis) — directly translatable

Key constraints from [`error_analysis_system_llm.txt`](https://github.com/Qwen-Applications/Trace2Skill/blob/main/analysis/error_analysis_system_llm.txt):

- **Role**: failure-analysis agent
- **Input**: agent's full chat log + task description (NO ground truth — avoids hindsight bias)
- **Workflow**: 4 steps — Understand task → Identify what went wrong → Trace to behavior → Write structured report
- **Output**: strict markdown — each Item has `Title` / `Description` / `Content`
- **Hard constraint**: NEVER mention ground truth — reason from agent's PoV only
- **Cap**: max 3 Memory Items, must be generalizable (not task-specific workaround)

Success-side prompt is symmetric: Lean Solution Path strips ALL dead ends / failed attempts → keeps only winning path → ≤3 Success Memory Items.

### Output skill format

[released_skills/trace2skill-xlsx-122B-combined/](https://github.com/Qwen-Applications/Trace2Skill/tree/main/released_skills/trace2skill-xlsx-122B-combined):

- `SKILL.md` (~200-500 lines)
- `references/` × **14 topic files** (advanced-formula-patterns.md / cell-color-extraction-patterns.md / etc.)
- Helper files (`recalc.py`, `LICENSE.txt`)

**Critical: matches monkey-skills convention** (SKILL.md + flat `references/<topic>.md`, no deeper nesting).

vs baseline `xlsx-122B/SKILL.md` (paper's self-create-from-scratch comparator): same structure, ~6 references files. The Trace2Skill version is denser and more specific (14 vs 6 topics).

### Maps cleanly onto code-toolkit primitives

| Trace2Skill | code-toolkit equivalent |
|---|---|
| ThreadPoolExecutor parallel per-trajectory LLM call | `dispatching-parallel-agents` (across-domain fan-out) |
| Per-trajectory failure/success analyst | `implementer` agent with structured prompt template |
| `skill_evolver` consolidation | SDD's `spec-reviewer` + `code-quality-reviewer` + orchestrator merge |
| Strict markdown output format | code-toolkit verdict schema (PASS / NEEDS_REVISION with structured findings) |

**Implication: we don't invent architecture; we translate Trace2Skill into Claude subagent dispatches.**

### Single critical gap

Trace2Skill has **pass/fail label** from benchmark. We **don't** — real Claude Code sessions have no ground truth.

**Proxy**: friction-signal level
- High friction (interrupt + re-dispatch + NEEDS_REVISION verdict + tool errors) ≈ FAILED
- Low friction (smooth brain→plan→SDD→review→finish chain) ≈ SUCCEEDED
- Middle = drop (avoid noise)

`skill_evolver` consolidation logic is not in visible code — separate module. We must design our own merge rules (likely via SDD reviewer triad).

## Deep dive: crune — prioritization layer

Full algorithm: [`docs/skill-generation-algorithm.md`](https://github.com/chigichan24/crune/blob/main/docs/skill-generation-algorithm.md).

### Reusability scoring (the part to steal)

Without `/insights` facets (4 signals):
```
overall = 0.35*frequency + 0.25*timeCost + 0.25*crossProject + 0.15*recency
```

With facets (6 signals — add success_rate + claude_helpfulness, 0.10 each, redistribute base weights down):
```
overall = 0.30*frequency + 0.20*timeCost + 0.20*crossProject + 0.10*recency
        + 0.10*successRate + 0.10*helpfulness
```

**Directly applicable to "which skill should we iterate first?" decision.**

### 9-section LLM synthesis prompt

1. Topic Information (label / keywords / dominantRole / projects / sessionCount / duration)
2. Representative Prompts (max 3)
3. Tool Signature (Tool-IDF top tools)
4. Enriched Tool Patterns (top 5)
5. Graph Position (centrality interpretation — on-demand only)
6. Connected Topics (edge-type grouped — on-demand only)
7. Session Insights (`/insights` facets)
8. **Current Heuristic Skill** ← gives LLM a baseline anchor to refine, NOT zero-shot
9. Instructions (anthropics/skills format)

**The 8th section is the key trick** — heuristic baseline reduces LLM variance vs zero-shot.

### What we borrow vs reject

**Borrow**: reusability scoring (4-signal version), 9-section synthesis prompt template, heuristic-baseline-then-LLM-polish two-tier pattern.

**Reject**: TF-IDF + SVD + clustering (overkill — we target existing skills, not cluster discovery), Louvain/Brandes community detection (irrelevant), static web dashboard (scope creep — start with CLI/markdown reports).

## Mining demo findings (`/tmp/code-toolkit-mine.py`, 2026-05-22)

200 LOC Python stdlib, runs in <5s on 1,333 JSONL / 600MB. Scope: monkey-skills + komado-Refs + meeting-emo-transcriber. **14 sessions** with explicit `Skill(code-toolkit:*)` calls. 4 actionable patterns identified:

### Pattern 1: brainstorming followed by interrupt (25%)

16 `[Request interrupted by user]` events across 8 sessions. **4 of 16 fired within 10 min of a `brainstorming` Skill call** (Δ=-50s / -135s / -327s / -509s). Matches feedback memory `legal_toolkit_autonomous_after_design_lock.md` — brainstorming over-asks after design is locked.

### Pattern 2: brainstorm-skip 29%

4 / 14 sessions called `writing-plans` without prior `brainstorming` in session. komado-Refs has `plan → SDD → plan → SDD` loops (no brainstorm). Continuation/iteration sessions don't need brainstorm but the router rule may push for it.

### Pattern 3: re-dispatch concentrates on code-reviewer, not implementer

10 explicit `RE-DISPATCH FIX` / `Round 2+` prompts found.
- **7 of 10 are code-reviewer Round 2/3** (whole-PR review needs multiple rounds)
- 1 implementer (salesforce Part-1 T3 envelope correction)
- 1 wiki-query Task 3 implementer round 1/3
- **Implication**: whole-branch review rubric has high first-round NEEDS_REVISION rate → reviewer prompt / rubric needs tightening

### Pattern 4: implementer write-before-read violations

86 `tool_use_error` events across 12 sessions. Top patterns:
- `"File has not been read yet. Read it first before writing to it."` (repeated, especially meeting-emo-transcriber)
- "Cancelled" (user-cancelled parallel tool calls)
- "BLOCKED by dcg" (some safety guard)

→ implementer agent baseline should explicitly remind "Read before Edit/Write" (Claude Code tool discipline).

## Convergent architecture proposal (v1 — superseded by v2 below)

Composition of Trace2Skill (architecture) + crune (prioritization) + claude-coach (guardrails):

```
Stage 1: Ingest
  - Read ~/.claude/projects/**/*.jsonl  (top-level + worktree subdirs, exclude */subagents/*)
  - Optional: read ~/.claude/usage-data/facets/  (pre-classified by Anthropic /insights, if enabled)

Stage 2: Per-skill friction mining   ← differentiator
  - For each target skill (e.g. code-toolkit:* family):
    - find all invocations across all sessions
    - bucket by friction-signal level (high / mid / low) using:
        * [Request interrupted by user] within N min of skill call
        * Agent dispatch re-tries with same task ID
        * NEEDS_REVISION verdict count
        * tool_use_error count near skill calls
    - apply crune's reusability scoring to rank "which skill needs iteration most"

Stage 3: Per-trajectory analysis    ← borrow Trace2Skill prompts
  - For high-friction sessions of target skill: dispatch parallel LLM analyst
    (use code-toolkit:dispatching-parallel-agents)
  - Each analyst produces: Failure Cause Items + Failure Memory Items (max 3 generalizable)
  - For low-friction sessions: same dispatch → Lean Solution Path + Success Memory Items
  - Drop mid-friction sessions to avoid noise

Stage 4: Consolidation              ← borrow SDD pattern
  - Hierarchically merge per-trajectory outputs → unified SKILL.md patch proposal
  - Conflict resolution rules (TBD — Trace2Skill's skill_evolver is hidden in their code)
  - Dispatched as SDD: spec-reviewer + code-quality-reviewer + orchestrator merge

Stage 5: Human-in-the-loop review   ← borrow claude-coach
  - /<skill> review shows diff (proposed SKILL.md / references/*.md changes)
  - User approve / reject / edit
  - Approved → write back; no silent writes
  - Optionally fingerprint proposals for cross-session dedup
```

## `/insights` post-run verification (2026-05-22 18:00)

User ran `/insights` interactively after initial research memo. Confirmed:

### Facets data exists and is rich

- `~/.claude/usage-data/facets/` — **49 JSON files** (one per analyzed session in last 30 days, 1.0MB total)
- `~/.claude/usage-data/session-meta/` — 199 session-meta JSONs
- `~/.claude/usage-data/report.html` — 69KB browser-renderable report

### Facets schema (per session, confirmed)

```json
{
  "session_id": "...",
  "underlying_goal": "1-sentence summary",
  "goal_categories": {"research_and_documentation": 1},   // ~10 canonical
  "outcome": "fully_achieved",                            // 4 levels
  "user_satisfaction_counts": {"likely_satisfied": 1},
  "claude_helpfulness": "very_helpful",                   // 5 levels
  "session_type": "single_task",
  "friction_counts": {},                                  // key signal
  "friction_detail": "",
  "primary_success": "good_explanations",
  "brief_summary": "..."
}
```

**This is exactly what we need for Stage 1**: pre-classified per-session friction + outcome data. Big architecture simplification (described below).

### `/insights` is interactive-only; headless can't trigger it

Tested 2026-05-22:
```bash
$ claude -p "/insights"
/insights isn't available in this environment.
$ claude -p "/help"
/help isn't available in this environment.
```

From binary string inspection: `/insights` is implemented as a `local-jsx` slash command **hardcoded in the claude binary** (internal functions: `generateUsageReport`, `extractToolStats`, `detectMultiClauding`, `buildInsightsResponsePrompt`, `buildExportData`). Headless `claude -p` cannot invoke slash commands — `--disable-slash-commands` flag confirms this restriction.

**Built-in retention**: `cleanupPeriodDays` default 30 — facets `.json` and `report.html` auto-cleaned after 30 days.

### `/insights` false positives (worth catching)

`/insights` fun_ending claimed: "Claude invented a /ultrareview command that didn't exist." **This is wrong** — `/ultrareview` IS a real Claude Code subcommand (`claude ultrareview [options] [target]` runs cloud-hosted multi-agent code review, listed in `claude --help`). It's mentioned in our monkey-skills system prompt. `/insights` misclassified a system-prompt-referenced command as "invented."

→ **Our mining skill can serve as a verification layer over `/insights`** — cross-check facets findings against raw JSONL ground truth. Another differentiation point.

## Subagent vs headless `claude -p` — final architecture decision

Earlier in research I framed auto-trigger as "shell `claude -p` from cron / hook." **Wrong frame.** Within an active Claude Code session, `Agent()` subagent dispatch is the correct primitive:

| Aspect | `claude -p` headless | `Agent()` subagent |
|---|---|---|
| Trigger | shell subprocess | tool call within session |
| Authentication | re-acquire | inherits parent |
| Slash commands available | ❌ | ✅ |
| Skills available | ❌ (need `--plugin-dir` per call) | ✅ (automatic) |
| Parallelism | self-spawn | fan-out via multi-Agent message |
| Context isolation | full new | isolated + structured return |
| Integration cost | shell-out is painful | native, wrapped by `code-toolkit:dispatching-parallel-agents` |
| Cron / external trigger | ✅ | ❌ requires session |

Direct translation of Trace2Skill's `ThreadPoolExecutor --max-workers 128` parallel per-trajectory pattern: **just dispatch N `Agent()` calls in one assistant message** — already shipped via `code-toolkit:dispatching-parallel-agents` (PR #267).

**Trigger cadence rethink**: cron / scheduled auto-trigger is over-engineering for this use case. The natural cadence is **on-demand via user-typed slash command** (`/<our-skill>`) — at that moment we have an active session that can fan out subagents. No need for background scheduling.

If we ever want background scheduling, fallback options:
- SessionStart hook → echo "facets stale, type X to refresh" (semi-auto)
- Skill 內 staleness check → suggest user invocation
- Reimplement Haiku call layer ourselves (replicates `/insights` internals) — last resort, 2-3x effort

## Cross-agent compatibility — two-layer split

Verified on user's machine 2026-05-22: also installed `codex` (Codex CLI), `gemini` (Gemini CLI), `cline` (VS Code). Log layouts diverge:

| Agent | Log location | Schema |
|---|---|---|
| Claude Code | `~/.claude/projects/<cwd>/<sid>.jsonl` | `{type, message, uuid, parentUuid, sessionId, timestamp, ...}` |
| Codex CLI | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | `{timestamp, type, payload}`, types include `session_meta` / `response_item` |
| Gemini CLI | `~/.gemini/history/<sha256>/...` | hash-dir per conversation, JSON inside |
| Cline | Non-standard VS Code path — TBD | Unknown |

**All three (Claude/Codex/Gemini) use JSONL or per-event JSON, schemas differ.** Cross-agent feasible via adapter pattern.

### Two-layer architecture

```
Layer A: Cross-Agent Friction Mining (universal)
  Per-agent adapters → normalized Event schema:
    {agent, session, ts, role, text, tool_name, tool_error,
     user_interrupt, is_subagent, friction_kind, ...}
  Friction signal detection: interrupts / tool errors / repetitions
  Output: normalized FrictionReport per session

Layer B: Skill Artifact Iteration (agent-specific)
  Claude Code:  read SKILL.md + references/*.md → subagent proposes edit
  Codex CLI:    read AGENTS.md → subagent proposes edit
  Gemini CLI:   read GEMINI.md → subagent proposes edit
  Cursor:       read .cursorrules → subagent proposes edit
```

Layer A is reusable; Layer B is per-agent. OTEL GenAI semantic conventions (still "Development" as of 2026-03 per agent-ecosystem research) may converge Layer A long-term; adapter pattern is fine for now.

### Implementation rollout

| Version | Layer A | Layer B |
|---|---|---|
| **v0.1** (dogfood) | Claude Code only | SKILL.md only |
| **v0.2** | + Codex CLI adapter | unchanged |
| **v0.3** | unchanged | + AGENTS.md edit |
| **v1.0** | + Gemini, + Cline, + Cursor | + GEMINI.md, + .cursorrules etc. |

**Codex CLI is the low-cost cross-agent validation point** — similar JSONL format, 2-hour adapter. Gemini hash-dir more involved, defer.

## Final convergent architecture (v2)

Supersedes v1 above. Three architecture corrections from v1: (1) subagent fan-out, not `claude -p`. (2) Layer A vs Layer B split. (3) `/insights` facets is upstream input, not optional sidecar.

```
Stage 1: Multi-agent log ingestion
  - Adapter dispatch (Layer A):
    Claude Code: read ~/.claude/projects/**/*.jsonl + ~/.claude/usage-data/facets/*.json
    Codex CLI:   read ~/.codex/sessions/**/*.jsonl              (v0.2)
    Gemini CLI:  read ~/.gemini/history/<sha256>/...            (v1.0)
  - Normalize → unified Event[] schema
  - Friction signal extraction (universal): interrupts / tool errors /
    repetitions / re-dispatch / NEEDS_REVISION verdict

Stage 2: Per-skill aggregation + reusability scoring (Layer A)
  - For each target skill, collect all invocations + adjacent friction
  - Apply crune's 4-signal reusability score:
        overall = 0.35*freq + 0.25*timeCost + 0.25*crossProj + 0.15*recency
  - Rank skills by iteration priority

Stage 3: Per-trajectory analysis via subagent fan-out
  - For top-N skill × high-friction sessions: dispatch parallel Agent()
    (uses code-toolkit:dispatching-parallel-agents)
  - Each subagent gets Trace2Skill-style prompt:
        Input: session events + skill SKILL.md
        Output: Failure Cause Items + Failure Memory Items (max 3, generalizable)
  - Symmetric: low-friction sessions → Lean Solution Path + Success Memory Items

Stage 4: Hierarchical consolidation via SDD
  - spec-reviewer subagent: validate proposals against skill scope
  - code-quality-reviewer subagent: check actionability + non-duplication
  - Orchestrator: merge per-trajectory outputs → unified SKILL.md patch proposal
  - Conflict resolution: prefer higher-evidence, dedupe by fingerprint

Stage 5: Human review + agent-specific write (Layer B)
  - /<our-skill> review shows diff
  - claude-coach guardrails apply: max 1 interrupt/15min, evidence ≥ 2,
    rules must have triggers, no rule from tone alone
  - Approved → write back to:
        Claude Code: SKILL.md + references/*.md
        Codex CLI:   AGENTS.md                    (v0.3)
        Gemini CLI:  GEMINI.md                    (v1.0)
  - No silent writes; fingerprint for cross-session dedup
```

**Stage 1 differentiator vs claude-coach**: not regex hook in single session, but post-hoc adapter over persisted logs across all sessions and (eventually) all agents.

**Stage 3 differentiator vs `/insights`**: not pre-LLM-classified at session granularity, but per-skill granularity with skill SKILL.md content joined as analysis context. Verification layer over `/insights` findings (catches false positives like the `/ultrareview` misclassification).

**Stage 5 differentiator vs all 3 competitors**: writes to EXISTING skill artifact, not new files or CLAUDE.md.

## Open design questions (deferred to brainstorming)

**Now decided** (after post-research convergence):
- ~~`/insights` facets dependency~~ → **Stage 1 mandatory input** for Claude Code adapter (rich pre-classified data, ours is verification + per-skill aggregation layer on top)
- ~~auto-trigger mechanism~~ → **on-demand user-invoked slash command**, not cron/hook. Subagent fan-out within session, not `claude -p`.
- ~~scope cross-agent vs Claude-only~~ → **Layer A universal, Layer B Claude-only at v0.1**, Codex at v0.2-0.3

**Still open**:
- **Smallest end state for v0.1**: Stage 1+2+5 only (friction mining report → human read → manual edit) vs Stage 1+2+3+5 (add subagent analysis) vs full 1-5. Trade-off: each LLM stage adds cost but converts prose insight into actionable diff. **Lean toward**: Stage 1+2+5 only for v0.1, prove signal value before adding LLM cost.
- **Scope skill family**: code-toolkit only, or any skill in monkey-skills? code-toolkit first = tight dogfood loop (we use the skills we're iterating). **Lean toward**: code-toolkit only at v0.1.
- **Where lives**: new top-level plugin `skill-iteration-toolkit` vs `code-toolkit:mining` sub-skill vs `dev-workflow:skill-log-mining`. **Lean toward**: `code-toolkit:mining` for v0.1 (lowest scope, lives where the dogfood target is), promote to plugin if proven.
- **Output target granularity**: SKILL.md only vs SKILL.md + references/*.md. Trace2Skill does both. **Lean toward**: SKILL.md only at v0.1, references/ later.
- **Friction-signal calibration**: thresholds (interrupt Δt window / NEEDS_REVISION count / etc.) — needs empirical tuning. **Approach**: ship reasonable defaults, expose YAML config, refine in dogfood.
- **Cross-project signal pooling**: same friction pattern in 2+ projects = higher confidence (claude-coach's fingerprint pattern). **Lean toward**: adopt fingerprint dedup at v0.2 (not v0.1 — needs >1 project of data).

## What this memo deliberately doesn't decide

- Implementation language (Python vs TS — crune chose TS, Trace2Skill chose Py). Probably Python for parity with monkey-skills tooling.
- Whether to ship as skill or plugin (see "where lives" above).
- LLM model choice for analysis subagents (Haiku-fast for Stage 3 individual analysts vs Sonnet for Stage 4 consolidation — Trace2Skill used Qwen3.5-35B / 122B mixed).
- UI surface (CLI / markdown report / Obsidian integration).
- Whether to publish Layer A as standalone OSS (would be high-value contribution given OTEL GenAI is still "Development" status).

These are brainstorming-phase decisions, not research-phase.

## Sources (full list)

### Industry observability platforms
- [LangSmith Evaluation docs](https://docs.langchain.com/langsmith/evaluation)
- [Langfuse versioned datasets changelog Feb 2026](https://langfuse.com/changelog/2026-02-11-versioned-dataset-experiments)
- [Braintrust — What is Prompt Versioning](https://www.braintrust.dev/articles/what-is-prompt-versioning)
- [Arize Phoenix datasets quickstart](https://arize.com/docs/phoenix/datasets-and-experiments/quickstart-datasets)
- [PromptLayer docs](https://docs.promptlayer.com/quickstart)

### Closed-loop products
- [OpenAI Trace Grading](https://developers.openai.com/api/docs/guides/trace-grading)
- [OpenAI Agent Evals](https://developers.openai.com/api/docs/guides/agent-evals)
- [AWS Bedrock AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)

### Academic
- [APE — arxiv 2211.01910](https://arxiv.org/abs/2211.01910)
- [DSPy — arxiv 2310.03714](https://arxiv.org/abs/2310.03714) / [github](https://github.com/stanfordnlp/dspy)
- [TextGrad — arxiv 2406.07496](https://arxiv.org/abs/2406.07496)
- [Trace (MS Research) — arxiv 2406.16218](https://arxiv.org/abs/2406.16218)
- [Grounded in Reality (Alibaba) — arxiv 2510.25441](https://arxiv.org/abs/2510.25441)
- [**Trace2Skill — arxiv 2603.25158**](https://arxiv.org/abs/2603.25158) / [**official code**](https://github.com/Qwen-Applications/Trace2Skill)
- [Skills-on-the-Fly / SkillTTA — arxiv 2605.16986](https://arxiv.org/abs/2605.16986)

### Anthropic / Claude Code
- [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Issue #35319 — skill usage analytics request](https://github.com/anthropics/claude-code/issues/35319)
- [Self-improving CLAUDE.md — Martin Alderson Feb 2026](https://martinalderson.com/posts/self-improving-claude-md-files/)
- [anthropics/skills — skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [Mager.co — How to Write, Eval, and Iterate on a Skill](https://www.mager.co/blog/2026-03-08-claude-code-eval-loop/)

### Community competitors
- [netresearch/claude-coach-plugin](https://github.com/netresearch/claude-coach-plugin) v2.5.0 (deep-dived)
- [chigichan24/crune](https://github.com/chigichan24/crune) + [explainer](https://dev.to/chigichan24/mining-hidden-skills-from-claude-code-session-logs-with-semantic-knowledge-graphs-2em8) (deep-dived)
- [yahav10/claude-insights](https://github.com/yahav10/claude-insights) + [author dev.to post](https://dev.to/yahav10/i-built-a-cli-that-turns-claude-codes-insights-report-into-actionable-skills-rules-and-workflows-377)
- [hancengiz/claude-code-prompt-coach-skill](https://github.com/hancengiz/claude-code-prompt-coach-skill)
- [Piebald-AI friction-analysis system prompt](https://github.com/Piebald-AI/claude-code-system-prompts/blob/main/system-prompts/system-prompt-insights-friction-analysis.md)

### `/insights` references
- [Claude Code Changelog](https://code.claude.com/docs/en/changelog)
- [Deep Dive: How Claude Code's /insights Works (zolkos.com)](https://www.zolkos.com/2026/02/03/deep-dive-how-claude-codes-insights-command-works.html)
- [Nate Meyvis on /insights](https://www.natemeyvis.com/claude-codes-insights/)

### Local mining demo
- `/tmp/code-toolkit-mine.py` — 200 LOC stdlib Python prototype, runs 2026-05-22 against monkey-skills + komado-Refs + meeting-emo-transcriber (1,333 JSONL / 600MB / 14 code-toolkit sessions)
