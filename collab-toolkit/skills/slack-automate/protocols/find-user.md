---
name: find-user
purpose: Search Slack workspace users by display name / handle / email.
allowed-tools: mcp__slack__find_user
---

## Purpose

Return a Markdown rendering of users in the workspace matching a name / handle / email substring.

> **Tool-name verification status**: `mcp__slack__find_user` is **assumed** — see `references/failure-modes.md` § Tool name verification needed (Open Q4). If verification reveals the official Slack MCP does not expose a user-search tool, this protocol is deprecated; fall back to `users.list` + client-side filter via `execute_sql`-style raw API call only if the MCP exposes one.

## Input

- `query`: required. Substring matched against `name` / `real_name` / `display_name` / `profile.email`.
- `limit`: optional. Default 20.
- `--json`: optional.

Mapping to MCP params:
- `query` / `search`: pass through (param name depends on tool signature — verify at first call).
- `limit`: pass through.

## Steps

1. Call:
   ```
   mcp__slack__find_user({
     "query": "<query>",
     "limit": 20
   })
   ```

2. If the tool returns a full workspace user list (no server-side filter), apply client-side substring match across `real_name` / `display_name` / `profile.email` / `name`.

3. Format Markdown:
   ```
   ## Slack users matching "<query>"

   **<real_name>** · @<name> · <profile.email>
   Status: <Active | Away>
   Title: <profile.title>
   ```

   Omit `<profile.email>` if `profile.email` is absent (Slack hides email per workspace privacy settings).

## Common failure modes

- **Tool not found** → `mcp__slack__find_user` may not exist; see `references/failure-modes.md` § Tool name verification. If absent, surface `ERR: user-search tool not exposed by Slack MCP` and recommend dropping this protocol in v0.3.0.
- **Empty results** → valid.
- **Email field missing** → workspace privacy setting hides email; emit `(hidden)`.
- **Rate limit (429)** → see `references/failure-modes.md` § Rate limit. `users.list` is a Tier-2 method (~20 req/min).

## Notes

- Activity status (Active / Away) shifts in real time — snapshot only.
- Bot users include `is_bot: true` — filter out by default unless user asks.

## Examples

`query = "alice"` → Markdown list of users matching `alice` across name / handle / email.
