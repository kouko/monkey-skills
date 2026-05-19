---
name: slack-automate
description: Slack automation via the official Slack MCP server. Read-only v0.2.0 — search-messages / channel-read / thread-read / find-user via MCP tool calls. Locale-independent (structured JSON, no UI scraping). Slack MCP・メッセージ読取・公式 MCP サーバ。Slack MCP・訊息讀取・官方 MCP 伺服器。
allowed-tools: mcp__slack__search_messages, mcp__slack__read_channel, mcp__slack__read_thread, mcp__slack__find_user
---

# slack-automate

Read-only Slack access via the official Slack MCP server (GA 2026-02). Tool calls return structured JSON — no UI scraping, no locale tables, no browser daemon.

## Prerequisites

One-time setup:

1. Run `/collab-setup` and accept the slack row (records intent + verifies prerequisites).
2. Run `/mcp add slack` once — this triggers Claude Code's native OAuth pre-registration flow against the Slack MCP endpoint. Token refresh is handled automatically thereafter.

If a protocol fails with an auth error, re-run `/mcp add slack` to refresh the OAuth grant.

## Hero protocols

- `protocols/search-messages.md` — full-text search with Slack operators (`from:`, `in:`, `before:`, `after:`)
- `protocols/channel-read.md` — recent N messages in a channel, with thread-reply count
- `protocols/thread-read.md` — parent + all replies for a thread
- `protocols/find-user.md` — search workspace users by name / email / handle (see § failure-modes for tool-name verification status)

## Workflow pattern

A typical search-messages invocation:

```
mcp__slack__search_messages({
  "query": "OKR in:#engineering after:2026-05-01",
  "count": 20,
  "sort": "timestamp"
})
```

Returns a JSON array of message records. Format per the protocol's `## Output` section.

## Failure modes

See `references/failure-modes.md` — OAuth scope, workspace visibility (private vs public channels), rate limits, Real-Time Search API quotas, tool-name verification status.
