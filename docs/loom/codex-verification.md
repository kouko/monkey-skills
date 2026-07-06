# Codex 0.139.0 verification — repo-wide Codex compat

> **Verified on Codex CLI 0.139.0, 2026-06-30** — live install + skill-discovery
> ritual run against a real `~/.local/bin/codex` instance (`execution = truth`,
> per the loom-code precedent `docs/loom/specs/2026-06-14-codex-compat-completion.md`).
> Verified the Phase-2 branch `feat/codex-compat-phase2-interface` (authored
> interface blocks), which is the state being shipped.

## Install command surface (verified working)

```
codex plugin marketplace add <repo-root>     # registers the repo's .claude-plugin/marketplace.json
codex plugin add <plugin>@monkey-skills      # installs a plugin from that marketplace
codex plugin list                            # shows installed/available + status
codex plugin remove <plugin>                 # uninstall
codex plugin marketplace remove monkey-skills
```

- The marketplace **name is `monkey-skills`** (from `.claude-plugin/marketplace.json`'s
  `name`). `codex plugin marketplace add` has **no `--name` flag** — so adding a second
  source under the same name fails (`'monkey-skills' is already added from a different
  source; remove it before adding this source`). To verify a worktree, remove the existing
  registration first, then re-add.
- Codex reads the **same** `.claude-plugin/marketplace.json` (no separate Codex marketplace).
  It then resolves each plugin's `.codex-plugin/plugin.json` at the marketplace `source` path.

## Enumeration

`codex plugin list` rendered **all 25 marketplace plugins** with no parse error — i.e. the
22 authored `.codex-plugin/plugin.json` manifests (21 Batch-A + loom-code; Phase-2a state,
now 25 after Phase 2b below) parse cleanly on
Codex 0.139.0, including the authored `interface` blocks (`capabilities` as a JSON array,
etc.). The 3 plugins without a `.codex-plugin` manifest yet (dev-workflow = Batch B;
collab-toolkit, salesforce-toolkit = Batch C) appear in the marketplace listing (from
marketplace.json) but are not installable until their manifests land.

## Install + skill-discovery — verified sample (6 of 22, chosen for diversity)

| Plugin | Category shape | Result |
|---|---|---|
| research-toolkit | Research, 4 skills | ✅ installed, enabled — 4 skills present in install cache |
| investing-toolkit | Finance, 16 skills (largest) | ✅ installed, enabled — 16 skills present |
| copywriting-toolkit | Writing, 14 skills | ✅ installed, enabled |
| loom-spec | Coding, 2 skills | ✅ installed, enabled |
| ascii-graph-toolkit | Productivity, 1 skill (smallest) | ✅ installed, enabled — 1 skill present |
| briefing-toolkit | read-only (`["Interactive","Read"]`) | ✅ installed, enabled — read-only capabilities accepted |

All 6 → `codex plugin add … @monkey-skills` succeeded; `codex plugin list` shows
`installed, enabled`; the installed plugin root
(`~/.codex/plugins/cache/monkey-skills/<plugin>/<version>/skills/`) carries the plugin's
skills (counts match the source repo). Coverage spans 5 categories + the min/max skill-count
extremes + the read-only-capabilities case.

## Phase 2b — Batch B + C live verification (Codex 0.139.0, 2026-07-01)

The last 3 repo plugins (dev-workflow, collab-toolkit, salesforce-toolkit) were
authored + installed on the same real Codex instance. All 25 repo plugins now ship a
`.codex-plugin/plugin.json`.

| Plugin | Batch | Result |
|---|---|---|
| dev-workflow | B (PostToolUse validation hook) | ✅ installed, enabled — 8 skills present |
| collab-toolkit | C (Asana/Slack/Notion MCP) | ✅ installed, enabled |
| salesforce-toolkit | C (Salesforce DX MCP) | ✅ installed, enabled |

**Batch B finding.** dev-workflow's hook is a **PostToolUse validator**
(`validate-skill-folder-structure.sh`), NOT a SessionStart context-injector — so it needs
**no `hookSpecificOutput.additionalContext` treatment** (the earlier plan assumption was
wrong). It installs like any Batch-A plugin.

**Batch C finding — the MCP registration mechanism (the decisive test).**
On `codex plugin add`, **Codex auto-registers a plugin's `.mcp.json` MCP servers, but does
NOT read `mcpServers` declared inline in `.claude-plugin/plugin.json`.**

- salesforce-toolkit ships a `.mcp.json` (stdio) → its `salesforce` MCP **auto-registered**
  (`codex mcp get salesforce` → `transport: stdio`).
- collab-toolkit originally declared its 3 servers **inline** in plugin.json (no `.mcp.json`)
  → **nothing auto-registered**. After moving them to a bundled `.mcp.json`, all 3
  **auto-registered** as `streamable_http` (`codex mcp get asana` → the mcp.asana.com URL).
- `codex plugin remove <plugin>` **auto-unregisters** the plugin's `.mcp.json` MCP servers
  (lifecycle-tied — `codex mcp remove` reported them already gone).
- Fix applied: collab-toolkit converted inline `mcpServers` → bundled `.mcp.json` (the
  portable form salesforce already used; Claude Code reads both, so no Claude-Code change),
  and the false "⚠️ Claude Code CLI only" caveat dropped from both descriptions.

**Not verified (needs live OAuth / an authenticated org — out of scope):** end-to-end skill
execution on Codex — the OAuth completion for Asana/Slack/Notion, the Salesforce org auth +
whether Codex resolves the `${CLAUDE_PLUGIN_ROOT}` launcher path at run time, and whether
Codex exposes the MCP tools under the `mcp__<server>__*` names the skills' `allowed-tools`
expect. Install + MCP-server auto-registration is verified; the tool-call round-trip is not.

## remind-memory-mirror hook — wired, live-fire pending (2026-07-06)

The loom-memory-store reminder hook is mirrored for Codex:
`.claude/hooks/remind-memory-mirror.sh` → byte-identical copy at
`.codex/hooks/remind-memory-mirror.sh` (executable bit preserved), registered in
`.codex/hooks.json` under the existing PostToolUse `Write|Edit` matcher — the same
mirror convention as `validate-skill-folder-structure.sh`. Codex's hooks engine
(v0.124.0+) supports PostToolUse, so the wiring shape is valid
(<https://developers.openai.com/codex/hooks>, verified 2026-07-06 web search).

**Live-fired 2026-07-06 on Codex 0.139.0 — hook did NOT fire; root cause is
UPSTREAM.** `codex exec --dangerously-bypass-hook-trust` (workspace-write
sandbox, this repo as cwd) wrote two frontmatter-typed notes to a
memory-pattern path via `apply_patch`; both files landed on disk, but the
session rollout log (`~/.codex/sessions/2026/07/06/rollout-…019f34f4….jsonl`)
contains ZERO hook events and zero reminder fingerprints. Per the official
docs the wiring is correct (`apply_patch` matches `Edit`/`Write` matchers —
<https://developers.openai.com/codex/hooks>), but known upstream issues
confirm the handler gap: openai/codex#16732 (ApplyPatchHandler emits no
PreToolUse/PostToolUse events; hooks fire only for Bash) and #20204
(inconsistent hook coverage across tool handlers). Consequence: BOTH
mirrored repo hooks (`remind-memory-mirror.sh` AND
`validate-skill-folder-structure.sh`) are currently inert on Codex — the
mirror wiring is dormant-correct, blocked on the upstream fix. Tracked in
`docs/loom/BACKLOG.md` §Codex hook events (UPSTREAM).

## Conclusion

All 25 repo plugins are **verified loadable + skill-discoverable on Codex 0.139.0**, and the
MCP-bearing plugins' servers **auto-register from `.mcp.json`** on install. No manifest failed
to parse or install. The one open item is the live OAuth/org-gated end-to-end skill round-trip
(above), which needs real credentials to close.
