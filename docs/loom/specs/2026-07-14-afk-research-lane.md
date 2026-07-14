# Brief: AFK research lane — parallel background research subagents for the kickoff fork harvest

Date: 2026-07-14
Origin: Pocock 檢視 roadmap 方案 B（user-approved order）; source pattern =
mattpocock/skills wayfinder-research-subagents (2026-07-13 changeset:
every research ticket fires an AFK subagent in parallel at charting time).

## Problem

When writing-plans' kickoff fork harvest finds N researchable forks, the
Axis-4-lite research runs INLINE AND SERIAL in the orchestrator — each
fork's EN+JA WebSearch round blocks the kickoff pass, so wall-clock grows
N× and the orchestrator's context absorbs every search result. The user's
goal ① (agents self-inform without human intervention) is mechanically
present but slow and context-expensive exactly when N > 1.

## Users

- Orchestrator sessions running writing-plans' kickoff briefing (firing
  point 1) and SDD's mid-implementation escalation (firing point 2,
  §f — same interface).
- Dual-host: Claude Code (async parallel Agent dispatch available) and
  Codex (subagent spawning verified live on 0.139; parallelism shape
  differs — needs a host-mapping note, not a Codex-specific redesign).

## Smallest End State

`kickoff-briefing.md` §(b) gains the parallel execution rule (~25 lines):

1. **Fan-out**: after triage marks M forks researchable, dispatch M
   research subagents in ONE fan-out step (shape: point at
   `dispatching-parallel-agents` §3 — don't duplicate), each carrying a
   compact research packet: the fork statement + the Axis-4 protocol
   pointer (EN+JA, shipped options, "My take" format) + report contract
   (approaches w/ citations + recommendation + conditional reversal,
   ≤30 lines, no file dumps).
2. **Join**: kickoff blocks until all M return (single join point — pins
   are written once, ordering stays deterministic); orchestrator distills
   each return into the existing pinned format
   `Kickoff decision: <fork> → <resolution>` + a one-line citation tail.
   Findings exceeding pin size land under `docs/loom/research/` per the
   existing convention (evidence-not-scratchpad lesson), pin points at
   the file.
3. **Pay-per-hit unchanged**: 0 researchable forks = 0 subagents.
4. **Degradation**: WebSearch-unavailable inside a worker → the worker
   reports it per the protocol's existing §If-WebSearch-unavailable
   language; that fork falls back to arm-2 (ask with vintage caveat).
   Codex host: sequential dispatch is the floor when parallel fan-out
   is unavailable — the lane's semantics (research-then-pin) hold.
5. §(f) mid-implementation firing point: single-fork case fires ONE
   background research subagent instead of inline research — same
   packet, no join complexity (pointer sentence, mechanics unchanged).

Version: loom-code 0.30.2 → 0.31.0 (new behavior, minor). Codex manifest
sync. CHANGELOG.

## Current State Evidence

- Forward: `loom-code/skills/writing-plans/references/kickoff-briefing.md:51-58`
  — "Run **Axis-4-lite** research — the batched form of brainstorming's
  Axis-4 protocol… only over forks the triage marks researchable" (no
  execution shape specified → today it defaults to inline serial);
  pin format + SDD grep key at `:60`.
- Reverse (SSOT direction): research METHOD lives in
  `loom-code/skills/brainstorming/references/axis4-research-protocol.md`
  (also cited by router rule 5); this arc adds EXECUTION shape only —
  the protocol file is not edited (no drift risk).
- Error: WebSearch-unavailable path exists at
  `axis4-research-protocol.md:55-63` — workers inherit it verbatim
  (report, never imagine).
- Data: `Kickoff decision:` pin is consumed by SDD step 1
  (`subagent-driven-development/SKILL.md:101` — rides the implementer's
  task packet); pin format unchanged, so zero downstream schema impact.
- Boundary: `kickoff-briefing.md:126-140` §(f) one-interface-two-firing-
  points contract; host tool mappings at
  `using-loom-code/references/{claude-code-tools,codex-tools}.md`;
  fan-out shape SSOT at `dispatching-parallel-agents` §3.

## Alternatives considered (researched this session, EN+JA)

1. **Pocock wayfinder-research-subagents** (source pattern) — AFK research
   tickets fired in parallel at charting time, findings on throwaway
   `research/<name>` branches (mattpocock/skills changeset 2026-07-13;
   aihero.dev/skills-wayfinder). Adopted for the fan-out timing; his
   throwaway-branch durability REJECTED — loom's plan pins + docs/loom/
   research/ are the durable carriers (evidence-dies-in-scratchpad lesson).
2. **Anthropic orchestrator-worker research** (EN, Anthropic engineering
   blog: multi-agent research system) — parallel research subagents under
   a lead agent; confirms the shape at production scale. Adopted shape;
   our workers are per-fork, narrower.
3. **Status quo** (inline serial Axis-4-lite) — rejected as the default:
   N× wall-clock + orchestrator context absorbs raw search results;
   stays as the M=1 degenerate case cost-wise... superseded by §(f)'s
   single-worker form which also moves the context cost out.
4. **Streaming pins** (write each pin as its worker returns) — rejected:
   parallel writers to one plan section reintroduce the ordering problem
   pin-transcription exists to solve; single join is strictly simpler.
   Conditional reversal: if join latency (slowest worker) measurably
   hurts, revisit streaming with a reserved-slot scheme.

JA sweep note: no JA-native coverage of Pocock's pattern exists (verified
this session); JA sources covered general Claude multi-agent usage only —
no disagreement signal.

## What Becomes Obsolete

- §(b)'s implicit inline-serial execution of Axis-4-lite — superseded in
  place by the fan-out/join rule (same file, same section; no dangling
  copy). The protocol file, pin format, triage arms, §a/§c/§d/§e are
  untouched.

## Decision

Extend kickoff-briefing.md §(b) with the fan-out/join execution rule +
worker packet contract + degradation notes, add the §(f) single-worker
pointer sentence, bump loom-code 0.31.0. Do NOT build: new agent files
(general-purpose + packet suffices per model-dispatch §4 templates), plan
schema changes (pin format untouched), Workflow-based orchestration
(kickoff is interactive-lane), ask-side changes (ask-triage/L3 shipped in
0.30.0 own the reactive lane).

## Out of Scope

- wayfinder-style persistent decision map (roadmap 方案 E — separate arc).
- Changes to axis4-research-protocol.md content (method SSOT untouched).
- SDD NEEDS_CONTEXT triage mechanics (0.30.0 territory; §f pointer only).
- Research-result caching/dedup across arcs (YAGNI until repeat-fork
  evidence exists).

## Open Questions

None blocking — worker packet wording and join bookkeeping resolve at
plan/implementation level.

## Design-side on-ramp

N/A — tooling/process increment, Axis 0 negative guard applied.
