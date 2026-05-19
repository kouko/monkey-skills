# collab-toolkit

> Read-only office-collaboration toolkit for **non-Google** services — Asana / Slack / Notion via each service's official MCP server.
> Gmail / Google Calendar moved to [`gws-toolkit`](../gws-toolkit/) (Phase 2+).

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## What it does

Connects Claude Code to the non-Google office-collaboration services you use daily — Asana, Slack, Notion — and gives you:

- **Status visibility**: company-state, work-in-flight, team activity
- **Cross-tool search**: natural-language search across your internal corporate data via Claude Code
- **Read-only by charter**: no writes, no destructive operations — v0.2.0 carries the v0.1.x non-goal forward

v0.2.0 drives each service through its own **official** MCP server — vendor-side MCP support has matured across all three, retiring the v0.1.x browser-snapshot stack.

## Quick start

```bash
# Install plugin via Claude Code marketplace
/plugin install collab-toolkit

# One-time bootstrap
/collab-setup
```

The 3 MCP servers (Asana / Slack / Notion) are **auto-registered** by the plugin's `mcpServers` block — no manual `/mcp add` step needed. OAuth fires on first tool call per server.

After that, ask Claude things like:
- "List my Asana tasks due this week"
- "Search Slack for messages about OKR in #engineering after May 1"
- "Find Notion pages about <topic>"

## Supported services

| Service | Channel | How it's wired |
|---|---|---|
| Asana  | Official MCP V2 (`mcp.asana.com/v2/mcp`)   | Auto-registered via plugin's `mcpServers` |
| Slack  | Official MCP (GA 2026-02, `mcp.slack.com/mcp`) | Auto-registered; OAuth scopes declared inline |
| Notion | Official remote MCP (`mcp.notion.com/mcp`) | Auto-registered via plugin's `mcpServers` |

> Gmail + Google Calendar were in the v0.2.0 brief (5-service plan) but mid-cycle pivoted to live under [`gws-toolkit`](../gws-toolkit/) — single Google OAuth client, no binary/scope duplication with the existing Slides/Docs/Sheets/Drive skills there. Tracking issue: see `CHANGELOG.md` §"Late-pivot 2026-05-19".

## Skills

| Skill | Hero protocols |
|---|---|
| `asana-automate`  | task-list, task-detail, project-overview, search-global |
| `slack-automate`  | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query |

> Notion `page-backlinks` was dropped in v0.2.0 — the Notion API has no native backlinks endpoint, and the v0.1.6 UI-scraping workaround does not port to the official MCP. See `CHANGELOG.md` §Notes.

## Caveats

- ⚠️ **Cowork sandbox not supported** — per-service `/mcp add` OAuth flows that the sandbox does not surface
- **Read-only charter**: no write operations are introduced; the v0.1.x non-goal carries forward

## Troubleshooting

| Symptom | Fix |
|---|---|
| MCP server missing from `/mcp list` | Plugin not loaded — verify `collab-toolkit` is installed via `/plugin list`; restart Claude Code if needed |
| MCP tool returns "auth required" | First-call OAuth not yet completed — Claude Code should auto-prompt; if not, restart Claude Code |
| Asana OAuth fails with `redirect_uri not registered` | See `commands/collab-setup.md` §Troubleshooting for the per-user `clientId` escape hatch |

## Migrating from v0.1.x?

v0.1.x relied on a browser-automation stack under `~/.local/share/` and `~/.config/collab-toolkit/`. None of that is referenced in v0.2.0. See `CHANGELOG.md` §Migration block for the exact `rm -rf` cleanup command and the optional package-uninstall step.

## Development

```bash
# Structure check (run from repo root)
python scripts/check-skill-structure.py collab-toolkit
```

## Architecture

See `docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md` for the v0.2.0 migration brief (originally scoped 5 services; mid-cycle pivot to 3 documented in `CHANGELOG.md`).
