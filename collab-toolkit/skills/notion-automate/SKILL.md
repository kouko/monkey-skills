---
name: notion-automate
description: |
  Notion automation via the official MCP server. Read-only — search-workspace / page-fetch / database-query via MCP tool calls. Locale-independent (structured JSON, no UI scraping).
allowed-tools: mcp__notion__search, mcp__notion__get_page, mcp__notion__query_database
---

# notion-automate

Read-only Notion access via the official Notion MCP server (`mcp.notion.com/mcp`, Active since 2026-03-30). Tool calls return structured JSON — no UI scraping, no locale tables, no browser daemon.

## Prerequisites

One-time setup:

1. Run `/collab-setup` and accept the notion row (records intent + verifies prerequisites).
2. Run `/mcp add notion` once — this triggers Claude Code's native OAuth pre-registration flow against `mcp.notion.com/mcp`. Token refresh is handled automatically thereafter.

If a protocol fails with an auth error, re-run `/mcp add notion` to refresh the OAuth grant.

## Hero protocols

- `protocols/search-workspace.md` — full-text search across pages and databases
- `protocols/page-fetch.md` — fetch a page's content (blocks → Markdown). Note: Notion API 2025-09-03 introduced `data_sources` as the primary abstraction over raw block lists — see protocol for the wrapper details.
- `protocols/database-query.md` — query a database with filter + sort, return matching rows

Note: `page-backlinks` is **not** offered. The Notion REST / MCP API has no native backlinks endpoint — the v0.1.6 implementation relied on UI scraping (clicking the "Show backlinks" menuitem) which does not port to API context. See `references/failure-modes.md` § "Coverage gaps from v0.1.6 → v0.2.0".

## Workflow pattern

A typical search invocation:

```
mcp__notion__search({
  "query": "OKR",
  "filter": { "value": "page", "property": "object" },
  "page_size": 20
})
```

Returns a JSON array of page / database records. Format per the protocol's `## Output` section.

## Failure modes

See `references/failure-modes.md` — OAuth scope, data-source vs page abstraction, rate limits, token refresh, tool-name verification status, page-backlinks coverage gap.
