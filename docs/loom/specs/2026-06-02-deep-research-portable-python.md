# Brief: Portable Python deep-research (L1 → L2 → L3)

Date: 2026-06-02 · Branch: worktree-deep-research

## Problem (Axis 1)

The Claude Code built-in `deep-research` workflow (scope → search → dedup →
fetch → 3-vote adversarial verify → synthesize) is a proven multi-agent
fact-checking pipeline, but it is **welded to the Claude Code Workflow
engine** — it only runs inside an interactive CC session, English-only,
always-deep (~97 agent calls), uninspectable (baked in a minified binary).

JTBD: *When I want to run this adversarial-verification research pipeline
outside Claude Code — from a script, a cron, CI, or any other coding agent
(Codex / Cursor / a custom orchestrator) — I want a self-contained,
provider-agnostic implementation I own, so I can call it anywhere, tune it,
and compose it into my own stack.*

## Users (Axis 2)

- **Primary**: the repo owner (kouko) — wants the pipeline callable from any
  agent runtime, not just CC. Has API keys for LLM + search providers.
- **Secondary**: any coding agent (CC / Codex / Cursor / MCP client) that
  shells out to a CLI or calls an MCP tool — does NOT need its own web
  tools, because the package carries its own provider keys.

Job story: *When I'm in agent runtime X with no native deep-research tool,
I want to invoke `deep-research "<question>"` (CLI) or a `deep_research`
MCP tool, so I get a cited, adversarially-verified report regardless of
which agent I'm in.*

## Smallest End State (Axis 3)

A self-contained Python package built in **three portability layers**, where
**L1 alone clears the "runs on any agent" bar**:

- **L1 — core**: in-process `asyncio` orchestration + injectable
  `LLMProvider` / `SearchProvider` / `FetchProvider` Protocols. Original
  prompts + 5 JSON Schemas + quorum logic ported **verbatim**. Provider-
  agnostic; unit-tested with mock adapters (no network, no keys).
- **L2 — CLI**: `deep-research "<question>" [--json|--markdown]` wrapping L1,
  wiring one concrete adapter set. The context-efficient universal interface
  (per Axis-4: CLI beats MCP on context cost for most agents).
- **L3 — MCP server**: exposes a `deep_research` tool over MCP for agents
  that want a discoverable native tool (accepts the MCP context cost).

Layers are additive and independently shippable. Feature additions
(cost-tiering, iterative deepening, etc.) are **out of scope here** —
this brief is the portability port only.

## Current State Evidence

- **Forward**: no existing `deep-research/` package — greenfield top-level
  dir. Repo is a plugin-toolkit collection; one Python precedent at
  `obsidian/pyproject.toml`. Python 3.12 + `uv` available.
- **Reverse (SSOT)**: source of truth for the algorithm is the CC binary at
  `~/.local/share/claude/versions/2.1.159` (decompiled in this session:
  prompts, 5 schemas, quorum rule `valid>=2 && refuted<2`, constants
  `VOTES_PER_CLAIM=3 / REFUTATIONS_REQUIRED=2 / MAX_FETCH=15 /
  MAX_VERIFY_CLAIMS=25`). No in-repo SSOT — we re-implement, not sync.
- **Error**: provider/network failures must degrade like the original
  (fetch fail → `claims:[] sourceQuality:unreliable`; agent null → drop;
  abstain handling in quorum).
- **Data**: claim/source/verdict shapes defined by the 5 schemas (verbatim).
- **Boundary**: `core` depends ONLY on the three Protocols — never imports a
  concrete provider. This boundary is what makes L1 the portability line.

## Decision

Build `deep-research/` as a uv-managed Python package, three layers, core
provider-agnostic. **Port the algorithm verbatim** (prompts/schemas/quorum)
to guarantee behavioral equivalence; **replace only the orchestration shell**
(CC Workflow primitives → `asyncio`). Capability self-contained: adapters
hold their own API keys so the package works on agents with no web tools.

We will NOT: add new features (cost modes, iterative deepening, calibration,
citation formatting) — those are a separate roadmap. We will NOT depend on
any Claude Code runtime API. We will NOT hard-code a provider into `core`.

## Alternatives Considered (Axis 4 — researched)

**Search backend** (EN+JA agree):
1. **Tavily** — AI-agent default, easiest onboarding, LangChain/CrewAI
   native. Con: priciest at scale ($0.008/q). (firecrawl.dev, zenn serio)
2. **Brave** — cheapest (~63% of Tavily basic / 32% advanced), highest agent
   score (14.89), lowest latency (669ms), independent 30B-page index post-
   Bing-shutdown. (webscraft, serverworks blog)
3. **Exa** — neural/semantic, best for academic discovery, top SimpleQA.
   (roundproxies, brightdata)

→ **My take**: ship `SearchProvider` Protocol + a **Brave** reference adapter
(best cost/perf for an always-deep pipeline that burns queries). Conditional
reversal: if the user's corpus is academic, prefer Exa. Tavily if onboarding
speed matters most. **Non-blocking for L1** (mock-tested).

**Cross-agent exposure** (EN finding, mild EN/JA divergence):
- MCP = universal wire format, any client calls it — but context-heavy
  (schema dump; GitHub MCP ~55k tokens). (jannikreinhard, MS Learn)
- CLI = context-efficient, "beating MCP" trend 2026; works on any
  shell-capable agent. (agensi, jannikreinhard)

→ **My take**: L2 (CLI) is the pragmatic universal interface; L3 (MCP) is
additive for agents wanting a native discoverable tool. Build both; they
share the L1 core.

**LLM provider**: ship `LLMProvider` Protocol + **Anthropic** reference
adapter (Claude ecosystem, reversible via adapter). Non-blocking for L1.

## What Becomes Obsolete (Axis 5)

Nothing in-repo (greenfield). Forward-looking: once L1 exists, any future
"deep-research as a feature" work composes on top of this package rather than
re-deriving the algorithm. The dependence on the CC built-in (for non-CC use
cases) becomes obsolete.

## Out of Scope

- Cost-tiering (quick/standard/deep modes), iterative deepening, IPCC
  confidence calibration, citation formatting, caching, provider routing —
  all deferred to a separate feature roadmap.
- Integration into `domain-teams:research-team` (separate evaluation).
- Behavioral-equivalence harness against the live CC built-in (we assert
  equivalence by verbatim prompt/schema/quorum port + unit tests on the
  pure logic; a side-by-side differential test is a future nice-to-have).

## Open Questions

- **Q1 (deferred to L2)**: confirm search backend (Brave reco) + LLM provider
  (Anthropic reco) — the user's API keys decide. Does NOT block L1.
- **Q2 — RESOLVED (2026-06-02, post whole-branch-review)**: L3 (MCP) was built
  and reviewed, then **dropped** per a deletion-first / YAGNI call — no MCP
  consumer is in sight, L2 (CLI) already clears the "runs on any agent" bar, and
  re-adding the MCP wrapper later is ~120 lines against an unchanged core (zero
  risk). Shipped surface is **two layers: L1 core + L2 CLI/adapters.** The
  removed `mcp_server.py` lives in git history (commit `00bb2ec2`) for a cheap
  revert if a real MCP-speaking, autonomous-invocation consumer appears.
