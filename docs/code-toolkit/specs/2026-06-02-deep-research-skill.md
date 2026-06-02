# Brief: deep-research as a skill (agent-portable, key-free)

Date: 2026-06-02 · Branch: feat/dbt-wiki-nl2sql-to-sql (worktree deep-research-r2)
Supersedes the direction of: `2026-06-02-deep-research-portable-python.md`
(that brief targeted a headless Python package + own keys; this one pivots to
a skill that borrows the host agent's brain + web tools — key-free).

## Problem (Axis 1)

The CC built-in `deep-research` workflow (scope → search → dedup → fetch →
3-vote adversarial verify → synthesize) is a proven pipeline, but it ships as
a **minified binary baked into the Workflow engine** — uninspectable,
un-tunable, English-only, always-deep. The repo owner already decompiled its
content (prompts / 5 schemas / quorum rule / ranking maps — verbatim in
`docs/code-toolkit/specs/deep-research-decompiled-source.md`) and built a
Python port, but that port chose the *headless* path (own API keys), which is
not what's wanted.

JTBD: *When I want to run this adversarial-verification research pipeline
inside any coding agent I use (Claude Code today, Codex/Cursor/Gemini later),
I want it as an **inspectable, editable skill that uses the host agent's own
LLM + web tools** — so I get the pipeline with zero API-key setup, zero extra
cost beyond my existing subscription, and full freedom to read and tune every
prompt/constant.*

## Users (Axis 2)

- **Primary**: the repo owner (kouko), working in zh-TW / ja / en, inside an
  AI coding agent host that provides web search + web fetch tools (CC has
  WebSearch/WebFetch natively).
- **Job story**: *When I'm in an agent session and want a cited,
  adversarially-verified research report, I invoke the `deep-research` skill,
  so the agent runs the full pipeline using its own tools — no keys, no
  separate program, and I can edit the prompts/constants in the repo.*

## Smallest End State (Axis 3)

A **skill** (`SKILL.md` + bundled pure-logic `scripts/`) that faithfully
reproduces the built-in pipeline's *content* (byte-for-byte prompts / schemas
/ quorum / ranking from the decompiled SSOT), where:

- **The agent (skill executor) owns the I/O + reasoning** — scope / extract /
  verify / synthesize LLM steps (the agent reasons, emitting JSON conforming
  to the relevant schema), `search` (host WebSearch), `fetch` (host WebFetch),
  and orchestration (loop over angles, fan out verify voters).
- **Python owns the deterministic logic** (no network, no keys, stdlib only),
  reused from the existing port with `adapters.py` removed:
  - `rank` — stable multi-key claim sort + slice to MAX_VERIFY_CLAIMS
  - quorum survival — `valid≥2 and refuted<2` (guards the all-abstain bug)
  - `dedup` — URL-normalized novelty filter + fetch-budget accounting
  - `schemas` — the 5 JSON Schemas + constants (SSOT the agent conforms to)
  - `prompts` — the verbatim prompt templates (SSOT the agent fills)
  - report formatting / stats
- **Flexibility is delivered by the form change itself**: minified binary →
  readable SKILL.md + tested Python. Explicit tuning knobs (depth presets,
  forced language) are NOT in this first version — they're deferred (the
  point is the pipeline becomes editable, not pre-parameterized).

The pure-logic core stays provider-agnostic, so a future headless/CLI edge
(re-attaching thin API adapters) remains possible from the same core — but
that is explicitly out of scope here.

## Current State Evidence

- **Forward (what exists)**: `deep-research/` is a standalone uv Python
  package, NOT a skill — 0 SKILL.md, not registered in
  `.claude-plugin/marketplace.json` (verified: 20 plugins listed, deep-research
  absent). Modules: `src/deep_research/{core,pipeline,adapters,cli,rank,dedup,
  schemas,prompts,providers}.py`; 72 pytest pass under `--extra dev`.
- **Reverse (SSOT)**: algorithm SSOT = decompiled built-in in
  `docs/code-toolkit/specs/deep-research-decompiled-source.md` (prompts, 5
  schemas, quorum `valid>=2 && refuted<2`, ranking maps, normURL, constants
  VOTES_PER_CLAIM=3 / REFUTATIONS_REQUIRED=2 / MAX_FETCH=15 /
  MAX_VERIFY_CLAIMS=25). The built-in's orchestration shell = Workflow
  primitives (`pipeline()` / `parallel()`), per that spec's header note.
- **Boundary (what gets borrowed from host)**: LLM reasoning + WebSearch +
  WebFetch + subagent fan-out. Pre-existing in CC; mapped per-harness via
  `references/{codex,copilot}-tools.md` convention used across this repo.
- **Convention**: SKILL.md + `scripts/*.py` is established repo-wide
  (dev-workflow/skills/{distill-sessions,handoff,...}, investing-toolkit/*).
  Skill folders are flat (one-level subfolders) per CLAUDE.md; SKILL.md body
  ≤ ~6000 tokens.

## Decision

Build a `deep-research` **skill** that drives the host agent's own LLM + web
tools through the decompiled pipeline, delegating deterministic steps
(rank / quorum / dedup / format) to bundled stdlib Python scripts carried over
from the existing port with the API-adapter layer (`adapters.py`) and the
in-process LLM/search/fetch machinery (`providers.py`, `cli.py`, the
asyncio `pipeline.py`, and `core.py`'s coordinator) **removed**. The skill is
registered in `marketplace.json`. The existing Python package is restructured
into the skill's `scripts/` (pure-logic subset) — not kept as a parallel
standalone package.

We will NOT: ship API adapters, require any API key, support headless/no-agent
execution, add depth/language tuning knobs in v1, or keep a separate
standalone Python package.

## Alternatives Considered (Axis 4)

The design space here is CC-harness-internal orchestration mechanics, not a
choice among external shipped libraries — so the "research the shipped
options" mandate is satisfied by (a) the decompiled built-in itself (the
actual shipped product we are porting, SSOT already extracted) and (b) the
repo's own established skill+script convention, rather than external WebSearch
(which for "agent research-pipeline skill" returns generic, non-canonical
content).

1. **All-skill, logic rewritten in Workflow JS** — drop Python entirely; rank/
   quorum/dedup become JS inside a Workflow script. Rejected: throws away 72
   passing tests + the most bug-prone logic's unit-test seams (the all-abstain
   quorum trap); near-duplicate of the built-in; CC-only.
2. **Headless Python package + own keys** (the prior brief's path) — rejected
   by the user: requires API keys, not what's wanted; the "portability" it
   buys (cron/CI/no-agent) is explicitly not needed.
3. **Skill + pure-logic Python script** (CHOSEN) — agent does LLM+web+
   orchestration (no key), Python does deterministic logic (keeps tests).
   Maximally reuses the existing investment; delivers agent-portability +
   key-free; keeps a provider-agnostic core that could later feed a headless
   edge.

## What Becomes Obsolete (Axis 5)

Removed in the same change: `deep-research/src/deep_research/adapters.py`,
`providers.py`, `cli.py`, `pipeline.py`, `core.py` (orchestration coordinator;
its prompt-assembly/stats helpers migrate into scripts or SKILL.md),
`pyproject.toml`'s `[project.scripts]` CLI entry + `anthropic`/`search`
optional-deps, and the associated tests (`test_adapters`, `test_cli`,
`test_providers`, `test_pipeline`, `test_core*`). The
`2026-06-02-deep-research-portable-python.md` brief's direction is superseded
(file kept for history with a pointer to this brief).

## Open Questions

- **OQ1 — RESOLVED (2026-06-03)**: orchestration = **portable subagent
  fan-out**. SKILL.md describes the parallel work abstractly ("dispatch N
  subagents") per the repo's `dispatching-parallel-agents` convention, which
  maps across harnesses via `references/{codex,copilot}-tools.md`. NOT the CC
  Workflow tool (would lock to Claude Code, violating the agent-portability
  goal) and NOT inline-sequential (too slow for ~tens of verify calls). The
  orchestration logic therefore lives as prose instructions in SKILL.md, not
  as deterministic code — accepted tradeoff for portability.
- **OQ2 (skill location/name)**: top-level `deep-research/` becomes a plugin
  with `skills/deep-research/`? Or nested under an existing plugin? (lower
  stakes — resolve at plan time, follows repo convention.)

## Out of Scope

- API adapters / API keys / any paid-API path.
- Headless / cron / CI / no-agent execution.
- Depth presets, forced-language, cost-tiering, iterative deepening (v2+).
- A parallel standalone Python package (the package is consumed into the skill).
- Multi-harness verification beyond CC (the SKILL.md is written portable, but
  only CC is exercised in v1).
