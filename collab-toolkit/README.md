# collab-toolkit

> Read-only office-collaboration toolkit — 5 skills driven by each service's official MCP server or CLI.
> Asana / Slack / Notion / Gmail / Google Calendar.

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## What it does

Connects Claude Code to the office-collaboration services you use daily — Asana, Slack, Notion, Gmail, Google Calendar — and gives you:

- **Status visibility**: company-state, work-in-flight, team activity
- **Cross-tool search**: natural-language search across your internal corporate data via Claude Code
- **Read-only by charter**: no writes, no destructive operations — v0.2.0 carries the v0.1.x non-goal forward

v0.2.0 drives each service through its own **official** channel — vendor-side MCP / CLI support has matured across all five, retiring the v0.1.x browser-snapshot stack.

## Quick start

```bash
# Install plugin via Claude Code marketplace
/plugin install collab-toolkit

# One-time bootstrap
/collab-setup
```

`/collab-setup` walks you through: installing the `gws` CLI (Homebrew preferred, npm fallback), one Google OAuth dance (covers Gmail + GCal), then `/mcp add` for Asana, Slack, Notion. 5 services, 4 OAuth dances total.

After that, ask Claude things like:
- "List my Asana tasks due this week"
- "Search Slack for messages about OKR in #engineering after May 1"
- "What's on my Google Calendar today"
- "Find free 30-minute slots between 10am-4pm next Tuesday"

## Supported services

| Service | Channel | Setup step |
|---|---|---|
| Asana  | Official MCP V2 (`mcp.asana.com/v2/mcp`)   | `/mcp add asana` — Claude Code native OAuth pre-registration |
| Slack  | Official MCP (GA 2026-02)                  | `/mcp add slack` |
| Notion | Official remote MCP (`mcp.notion.com/mcp`) | `/mcp add notion` |
| Gmail  | Google Workspace CLI (`gws`)               | `gws auth` (shared OAuth w/ GCal) |
| GCal   | Google Workspace CLI (`gws`, same binary)  | (same OAuth as Gmail) |

## Skills

| Skill | Hero protocols |
|---|---|
| `asana-automate`  | task-list, task-detail, project-overview, search-global |
| `slack-automate`  | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query |
| `gcal-automate`   | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate`  | mail-search, thread-read, inbox-summary, label-read |

> Notion `page-backlinks` was dropped in v0.2.0 — the Notion API has no native backlinks endpoint, and the v0.1.6 UI-scraping workaround does not port to the official MCP. See `CHANGELOG.md` §Notes.

## Caveats

- ⚠️ **Cowork sandbox not supported** — requires a local `gws` binary install and per-service `/mcp add` OAuth flows that the sandbox does not surface
- **Read-only charter**: no write operations are introduced; the v0.1.x non-goal carries forward
- **Personal Google accounts**: the OAuth consent screen enforces a 25-scope cap on unverified apps; trim unused APIs in the Cloud Console if you bump it

## Troubleshooting

| Symptom | Fix |
|---|---|
| `gws: command not found` | Re-run `brew install gws` (or the npm fallback); ensure your `PATH` includes the brew prefix (`brew --prefix`/bin) |
| `gws auth` → `connection refused` | Browser flow timed out — re-run `gws auth` and click through the consent screen faster (it is idempotent) |
| `OAuth scope exceeded 25` | Personal-Google-account limit on unverified apps — trim unused APIs in the Cloud Console |
| `/mcp add` fails | Update Claude Code — native OAuth pre-registration shipped late 2026; older builds lack the one-click flow |
| `GOOGLE_CLOUD_PROJECT not set` | Export the env var in your shell rc and reload — see `/collab-setup` Step 2 |

## Migrating from v0.1.x?

v0.1.x relied on a browser-automation stack under `~/.local/share/` and `~/.config/collab-toolkit/`. None of that is referenced in v0.2.0. See `CHANGELOG.md` §Migration block for the exact `rm -rf` cleanup command and the optional package-uninstall step.

## Development

```bash
# Structure check (run from repo root)
python scripts/check-skill-structure.py
```

## Architecture

See `docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md` for the v0.2.0 migration brief.
