# Brief — Extend Codex CLI compatibility repo-wide (all eligible plugins)

> Date: 2026-06-30 · Stage: brainstorming → writing-plans
> Branch: feat/codex-compat-all-plugins (off origin/main 99d30b05)

## Problem

(Axis 1 — JTBD) Make *"the whole monkey-skills plugin family runs on Codex CLI,
not just loom-code"* a **verified fact**. Today only `loom-code` ships a
`.codex-plugin/plugin.json` (verified on Codex 0.139.0, 2026-06-14); the other 24
plugins are Claude-only. A Codex user installing from the marketplace gets only
loom-code — not design/spec/principles/research/writing/etc. The job: **extend
the proven loom-code Codex-compat pattern repo-wide** so install-on-Codex is
parity with install-on-Claude.

## Users

(Axis 2) kouko — solo dev, macOS, **both Claude Code and Codex CLI 0.139.0
installed** (`~/.local/bin/codex`; an MCP server already configured in
`~/.codex/config.toml`). Secondary: anyone installing monkey-skills plugins from
the public marketplace who runs Codex — verified compat has external value.

## Smallest End State

(Axis 3) Each **eligible** plugin has a `.codex-plugin/plugin.json` (mirrored
shared fields + an authored `interface` block), **generated + kept in sync by ONE
shared repo-level script**, drift-guarded, and **live-verified to load + skills
discoverable on Codex 0.139.0**. Batched by eligibility:

- **Batch A — main (~22 plugins):** hookless, no MCP-server declaration, all
  skill descriptions ≤1024 (verified — repo max is 397). Straightforward.
- **Batch B — dev-workflow (1):** has hooks → needs the loom-code hook-contract
  treatment (`hookSpecificOutput.additionalContext`).
- **Batch C — collab-toolkit + salesforce-toolkit (2):** declare MCP servers
  (`mcpServers` key / `.mcp.json`) → **separable sub-task**, pending the
  plugin-MCP-auto-registration resolution (Open Q). NOT in the main batch.

YAGNI cuts (vs loom-code's full 2026-06-14 effort): **skip** per-plugin
`tests/codex-cli/` harnesses (hookless plugins have no hook-injection to test;
skill-loading = the live ritual); **skip** per-plugin `codex-tools.md` (the Codex
CLI command surface + ≤1024 constraint are SHARED facts, documented once);
**no** description trimming (all ≤1024); **no** new Codex marketplace (shared
`.claude-plugin/marketplace.json`, all plugins already registered).

## Current State Evidence

- **Forward (template):** `loom-code/.codex-plugin/plugin.json` is the proven
  template — shared fields + an `interface` block (displayName / shortDescription
  / longDescription / developerName / category / capabilities / defaultPrompt /
  websiteURL / brandColor). Verified live per
  `docs/loom/specs/2026-06-14-codex-compat-completion.md`. The other 24 plugins
  have no `.codex-plugin/`.
- **Reverse (SSOT / sync direction):** `loom-code/scripts/sync_codex_manifest.py`
  is the proven mechanism — `SHARED_FIELDS = name/version/description/author/
  homepage/repository/license/keywords` copied from `.claude-plugin/plugin.json`
  (SSOT) → `.codex-plugin/plugin.json`, preserving the Codex-only `interface`
  block. Self-locating (`ROOT = __file__.parent.parent`); must be generalized to
  a repo-level tool that iterates N plugins. (Read confirms direction: Claude
  manifest is canonical, Codex is derived.)
- **Error (the drift failure mode):** loom-code's Codex manifest DRIFTED (0.9.0
  vs 0.16.0) under manual discipline → `.claude/hooks/check-codex-manifest-drift.sh`
  + a CI gate now guard it. Without a sync tool, 24 new manifests would each be a
  fresh drift surface (8 duplicated fields × 24).
- **Data (marketplace + interface schema):** `.claude-plugin/marketplace.json` is
  the SINGLE shared marketplace — all 25 plugins already registered (guarded by
  per-plugin `test_marketplace_entry.py`); Codex reads it (no separate Codex
  marketplace). The `interface` block is the only per-plugin authored Codex
  artifact.
- **Boundary (Codex 0.139.0 facts, probed 2026-06-30):** description hard limit
  **≤1024 chars** — all 25 plugins' max skill description = 397 → **pass, zero
  trimming**. MCP support is solid: `codex mcp {list,get,add,remove,login,logout}`,
  `[mcp_servers.*]` in `~/.codex/config.toml` (or project `.codex/config.toml`),
  stdio + Streamable-HTTP/OAuth transports. **Unverified:** whether `codex plugin
  add` auto-registers a plugin's *declared* MCP servers (Batch C Open Q).

### Evidence paths appendix
- `loom-code/.codex-plugin/plugin.json`, `loom-code/.claude-plugin/plugin.json`
- `loom-code/scripts/sync_codex_manifest.py`, `loom-code/scripts/test_sync_codex_manifest.py`
- `.claude/hooks/check-codex-manifest-drift.sh`, `.claude-plugin/marketplace.json`
- `docs/loom/specs/2026-06-14-codex-compat-completion.md` (the loom-code precedent)
- `collab-toolkit/.claude-plugin/plugin.json` (mcpServers: asana/slack/notion),
  `salesforce-toolkit/.mcp.json`
- Ground truth: `codex mcp --help`, `~/.codex/config.toml` (local 0.139.0)
- Official: developers.openai.com/codex/mcp, /codex/config-reference (fetched 2026-06-30)

## Decision

Build **one shared repo-level generation+sync script** that, for each eligible
plugin, creates/syncs `.codex-plugin/plugin.json` (the 8 mechanical shared fields
+ mechanically-derivable interface fields + placeholders for the judgment ones),
**doubling as the ongoing `--check` drift gate**. Author each plugin's `interface`
block (judgment fields). Extend the drift hook + CI gate repo-wide. **Consolidate
loom-code onto the shared script** (delete its self-local copy — SSOT) — low
regression risk because the manifest OUTPUT is unchanged (verified by `--check` +
loom-code's existing tests; loom-code's live ritual need not re-run since its
manifest content does not change). Live-verify the generated manifests load on
Codex 0.139.0 in batches.

We will **NOT**: write per-plugin sync copies; build per-plugin codex-cli test
harnesses; trim any description; add a separate Codex marketplace; redesign any
skill/router; rush the MCP-declaring plugins (Batch C).

## Out of Scope

- **Batch C (collab-toolkit + salesforce-toolkit) full integration** — separable
  sub-task gated on the plugin-MCP-auto-registration Open Q; resolve via a live
  test, then mirror-the-declaration OR document a manual `codex mcp add` setup
  step.
- Cursor / web / other-host support.
- Any new Codex-only feature / AGENTS.md injection path (keep the shared hook
  mechanism for the one hooked plugin).
- Redesigning skills, routers, or descriptions (the #456 description work already
  shipped; this is purely the Codex manifest layer).

## Alternatives Considered

(Axis 4 — per the loom-code precedent: the Codex manifest mechanism is **fixed by
the official Codex contract and empirically checkable on the installed CLI** — no
competing industry approaches to research; "execution = truth" applies. The only
internal fork was the sync-script shape.)

- **Per-plugin sync copies (24 copies of the script).** Rejected: 24 drift
  surfaces of the *script logic itself*; the exact copy-drift this repo's
  `distribute.py` / `verify-drift.py` SSOT precedent exists to avoid.
- **Two patterns (loom-code self-local + a new shared one for the rest).**
  Rejected: a permanent 2-implementation inconsistency for the drift hook to
  juggle; consolidating loom-code is low-risk (output unchanged).
- **One shared repo-level generation+sync script (chosen).** Bulk scale (~22)
  makes hand-writing tedious + inconsistent; the mechanical 8 shared fields are
  perfect for a script; matches the repo's existing SSOT-tool precedent.

## What Becomes Obsolete

(Axis 5 — remove in the same change)
- The claim "monkey-skills is Claude-only except loom-code."
- `loom-code/scripts/sync_codex_manifest.py` (self-local) → migrated to the shared
  repo-level script; delete in the same change.
- The drift hook's loom-code-only scope → extended repo-wide.

## Open Questions

- **Does `codex plugin add` auto-register a plugin's *declared* MCP servers**
  (collab `mcpServers`, salesforce `.mcp.json`)? Official MCP docs describe
  user-level / manual config, not plugin-bundled auto-registration. Resolve in
  Batch C via a live test (`codex plugin add collab-toolkit@monkey-skills` →
  `codex mcp list`). If no: document a manual `codex mcp add` setup step.
- Does the local-marketplace install flow (`codex plugin marketplace add .` →
  `codex plugin add <plugin>@monkey-skills`) work for an arbitrary plugin in this
  repo layout, or need a packaged snapshot? (loom-code's open Q; resolve in the
  first Batch-A live verify.)
- The `interface` block judgment fields (category / capabilities / defaultPrompt /
  brandColor) per plugin — LLM-draft from each plugin's existing description +
  skills, human review. Is a per-plugin brandColor worth authoring, or a repo
  default? (Resolve in writing-plans / authoring.)
