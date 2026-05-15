# collab-toolkit

> Browser automation toolkit wrapping [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser).
> 5 read-only office-collaboration skills for personal workplace intelligence.

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## What it does

Connects to the office-collaboration services you use daily — Asana, Slack, Notion, Google Calendar, Gmail — and gives you:

- **Status visibility**: company-state, work-in-flight, team activity
- **Cross-tool search**: natural-language search across your internal corporate data via Claude Code
- **Background operation**: headless after first login, runs while you work

Built on agent-browser's semantic-first snapshot model — no fragile CSS selectors, no API tokens, just your existing Chrome login state.

## Quick start

```bash
# Install plugin via Claude Code marketplace
/plugin install collab-toolkit

# One-time bootstrap (Homebrew preferred on macOS)
/collab-setup
```

That's it. `/collab-setup` will:
1. Install `agent-browser` (brew on macOS, npm fallback)
2. Download Chrome for Testing
3. Install `~/.local/bin/abx` wrapper
4. Detect your Chrome profile, write config
5. Verify all 5 services are logged in

After that, ask Claude things like:
- "List my Asana tasks due this week"
- "Search Slack for messages about OKR in #engineering after May 1"
- "What's on my Google Calendar today"
- "Find free 30-minute slots between 10am-4pm next Tuesday"

## Profile modes

| Mode | What | When |
|---|---|---|
| **Shared** (default) | Reuses your daily Chrome's login state via `--profile <name>` | Single-user, single-machine — fastest setup |
| **Dedicated** (`--dedicated`) | 5 per-service profile dirs, manual login each | Multi-machine sync, dedicated automation environment, isolation |

Switch any time: `/collab-setup --switch-mode`.

## Skills

| Skill | Hero protocols |
|---|---|
| `asana-automate` | task-list, task-detail, project-overview, search-global |
| `slack-automate` | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query, page-backlinks |
| `gcal-automate` | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate` | mail-search, thread-read, inbox-summary, label-read |

## Caveats

- ⚠️ **Cowork sandbox not supported** — needs a local Chrome / OS access
- ⚠️ **CI / scheduled runs not supported** in v0.1.0 (shared mode is local-only; dedicated mode portability deferred to v0.2.0+)
- **Privacy scope**: in shared mode, agent-browser sees ALL your Chrome cookies, not just the 5 services. Trust comes from the local Rust binary + open source.
- **Login-state coupling**: in shared mode, if you log out of a service in your daily Chrome, automation breaks until you log back in.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ERR: config not found` | Run `/collab-setup` |
| `⚠️ ~/.local/bin not on PATH` | Add `export PATH="$HOME/.local/bin:$PATH"` to your shell rc |
| `ERR: UI changed` | Open the affected skill's `references/ui-patterns.md`, re-snapshot, update |
| `Login wall detected` | Shared: log in via Chrome. Dedicated: `/collab-setup --reauth <service>` |

## Development

```bash
# Unit tests (bats)
cd collab-toolkit && bats scripts/tests/

# Structure check (run from repo root)
python scripts/check-skill-structure.py
```

## Architecture

See `docs/superpowers/specs/2026-05-15-collab-toolkit-v0.1.0-design.md` for the full design spec.
