---
name: search-messages
purpose: Full-text search across Slack channels with Slack operators.
allowed-tools: mcp__slack__search_messages
---

## Purpose

Return a Markdown rendering of message hits for a free-text query across all channels the authenticated user can read. Slack operators (`from:`, `in:`, `has:`, `before:`, `after:`) are honored server-side.

## Input

- `query`: required. Free-text query. May include Slack operators.
- `count`: optional. Number of results to return. Default 20, max 100.
- `sort`: optional. `timestamp` (newest first) or `score` (relevance). Default `score`.
- `--json`: optional. Skip Markdown formatting, return raw API record.

Mapping to MCP params:
- `query`: pass through verbatim.
- `count`: pass through.
- `sort`: pass through (`timestamp` or `score`).

## Steps

1. Call:
   ```
   mcp__slack__search_messages({
     "query": "<query>",
     "count": 20,
     "sort": "score"
   })
   ```

2. Handle pagination — if response includes `next_cursor` / `paging.next`, repeat with that cursor until result budget exhausted.

3. Format Markdown:
   ```
   ## Slack search: "<query>" — N results

   **#<channel.name>** · <user.name> · <timestamp>
   > <text>
   ```

   Render `timestamp` as ISO date (server returns Unix epoch — convert client-side).

## Common failure modes

- **Empty array** → valid, emit `No messages matching <query>.`
- **Operator syntax rejected** → Slack search operators documented at api.slack.com/methods/search.messages; unknown operators return 400.
- **Search disabled on tier** → Free Slack tier has 90-day message history cap; older results silently missing.
- **OAuth scope insufficient** → see `references/failure-modes.md` § OAuth scope.

## Notes

- Slack search operators (`from:@alice`, `in:#engineering`, `after:2026-05-01`) are locale-stable at the API layer — pass through verbatim.
- Free Slack: 90-day message history limit applies server-side.

## Examples

`query = "OKR in:#engineering after:2026-05-01"` → matching results as Markdown.
