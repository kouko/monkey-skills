# Changelog

All notable changes to the `collab-toolkit` plugin will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

---

## [0.2.0] - 2026-05-19 — **Migrate from agent-browser to official MCP / CLI**

`agent-browser` is **retired**. Each service is now driven by its own
official channel — official remote MCP for Asana / Slack / Notion, and
Google's official `gws` CLI for Gmail / GCal. The vendor-side gap that
justified the UI-snapshot approach in v0.1.0 has closed across all
five services.

### Per-service channels

| Service | Channel | How it's wired |
|---|---|---|
| Asana  | Official MCP V2 (`mcp.asana.com/v2/mcp`) | Auto-registered via plugin's `mcpServers` block |
| Slack  | Official MCP (GA 2026-02, `mcp.slack.com/mcp`) | Auto-registered; OAuth scopes declared inline |
| Notion | Official remote MCP (`mcp.notion.com/mcp`) | Auto-registered via plugin's `mcpServers` block |
| Gmail  | Google Workspace CLI (`gws`, brew formula `googleworkspace-cli`) | `gws auth setup` (shared OAuth w/ GCal) |
| GCal   | Google Workspace CLI (`gws`, same binary) | (same OAuth as Gmail) |

### What changed in-repo

- **MCP servers ship inside the plugin.** 3 servers (Asana / Slack /
  Notion) declared in `.claude-plugin/plugin.json` `mcpServers` block,
  HTTP+OAuth transport. **No manual `/mcp add` step needed** — Claude
  Code auto-registers when the plugin loads, and triggers OAuth on
  first tool call per server.
- 5 × `SKILL.md` rewritten to declare new tools (`mcp__asana__*` /
  `mcp__slack__*` / `mcp__notion__*` / `Bash(gws:*)`).
- 20 × `protocols/*.md` rewritten as MCP / CLI invocation recipes —
  no UI snapshots, no per-locale label tables.
- `commands/collab-setup.md` walks 4 user-side steps: `gws` install
  (brew formula `googleworkspace-cli`, npm fallback `@googleworkspace/cli`)
  + `GOOGLE_CLOUD_PROJECT` env var + `gws auth setup` + `/mcp list`
  verify.
- agent-browser fully retired: `scripts/abx`, `scripts/setup.sh`,
  `scripts/tests/` deleted.
- READMEs (en / ja / zh-TW) rewritten — drop browser framing,
  drop profile-mode table.
- Lock-step version bump 0.1.6 → 0.2.0 across `plugin.json` + 5
  SKILL.md + 3 README + 2 gmail protocols.

### Migration — user-machine cleanup

Run on each machine that previously installed v0.1.x:

```bash
rm -rf ~/.config/collab-toolkit \
       ~/.local/share/agent-browser \
       ~/.local/share/collab-toolkit/profiles \
       ~/.local/bin/abx
```

Optionally also uninstall the `agent-browser` brew / npm package — it
is no longer referenced by any skill.

### Notes

- **Read-only charter preserved** — no write operations introduced;
  v0.1.x non-goals carry forward.
- **Notion `page-backlinks` dropped** — Notion API has no native
  backlinks endpoint; the v0.1.6 UI-scraping workaround is not
  portable to the official MCP. Documented as a limitation rather
  than reinvented.
- **Cowork still N/A**, but the reason changed: it is now an MCP /
  CLI availability question, not a Chrome-for-Testing question.

Brief: `docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md`
