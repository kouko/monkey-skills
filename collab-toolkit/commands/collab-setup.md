---
description: One-time bootstrap for collab-toolkit v0.2.0 — verify the 3 auto-registered MCP servers are reachable.
---

# /collab-setup

Walks you through the one-time bootstrap for collab-toolkit v0.2.0.

## What this sets up

3 official remote MCP servers (Asana / Slack / Notion), **already auto-registered** via the plugin's `mcpServers` block. There is no install step beyond the plugin installation itself. OAuth fires the first time you invoke a tool on each server.

> Gmail + Google Calendar are **not** in collab-toolkit v0.2.0. Those services moved to [`gws-toolkit`](../gws-toolkit/) — single Google OAuth client, no binary/scope duplication. See `CHANGELOG.md` §"Late-pivot 2026-05-19".

## Step 1 — Verify MCP servers loaded

In Claude Code:

```
/mcp list
```

You should see `asana`, `slack`, `notion` listed. Status may be `disconnected` until the first tool call triggers OAuth.

> ⚠️ **`page-backlinks` is gone in v0.2.0.** The Notion API has no native backlinks endpoint; the v0.1.6 UI-scraping workaround does not port to the official MCP. See `CHANGELOG.md` §Notes.

## Step 2 — Trigger first-call OAuth (per service, one-time)

Ask Claude a simple query that hits each service:

| Service | Sample query |
|---|---|
| Asana  | "List my Asana tasks due this week" |
| Slack  | "Search Slack for messages about <topic> in #<channel>" |
| Notion | "Find Notion pages about <topic>" |

The first call per server opens a browser → OAuth consent → token cached. Subsequent calls reuse the cached token.

## Troubleshooting

| Symptom | Fix |
|---|---|
| MCP server missing from `/mcp list` | Plugin not loaded — verify `collab-toolkit` is installed via `/plugin list`; reinstall if missing. Restart Claude Code if needed. |
| MCP tool returns "auth required" | First-call OAuth not yet completed — Claude Code should auto-prompt; if not, restart Claude Code. |
| Asana OAuth fails with `redirect_uri not registered` / DCR error | Asana V2 officially does not support Dynamic Client Registration — some Claude Code builds rely on a default client that may stop working. **Escape hatch (per-user, never goes to git)**: register your own OAuth client at https://app.asana.com/0/my-apps, then add the `clientId` to your user-level `~/.claude.json` `mcpServers.asana.oauth` block — that user-level config overrides this plugin's entry. **Do NOT add `client_secret` to plugin.json** — it would be committed to git and exposed to every installer of this plugin. |
| Slack tool returns `missing_scope` | The plugin declares 17 read-only scopes; if Slack adds new APIs that need more, edit the `mcpServers.slack.oauth.scopes` line in this plugin's `plugin.json` (read-only additions only — no `chat:write`). |

## Migrating from v0.1.x?

If you previously ran v0.1.x on this machine, clean up the old user-machine state — see `CHANGELOG.md` §Migration block for the exact `rm -rf` command and the optional package-uninstall step. None of the v0.1.x dependencies are referenced by any skill in v0.2.0.

## See also

- Plugin README: `<plugin-root>/README.md`
- v0.2.0 brief: `docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md` (originally 5-service; mid-cycle pivot to 3 documented in `CHANGELOG.md`)
- Skills consuming this setup: `asana-automate`, `slack-automate`, `notion-automate`
- Gmail / Calendar successor: [`gws-toolkit`](../gws-toolkit/) (Phase 2+)
