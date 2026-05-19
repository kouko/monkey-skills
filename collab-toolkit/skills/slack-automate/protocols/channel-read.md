---
name: channel-read
purpose: Read recent N messages in a Slack channel.
allowed-tools: mcp__slack__read_channel
---

## Purpose

Return a Markdown rendering of the last N messages in a channel, with thread-reply counts surfaced inline.

## Input

- `channel`: required. Channel name (`engineering` / `#engineering`) or channel ID (`C0123456789`).
- `limit`: optional. Number of messages. Default 20, max 200 (Slack API cap per call).
- `--json`: optional.

Mapping to MCP params:
- `channel`: pass channel ID if known; if user gave a name, the MCP server may resolve it, otherwise call `mcp__slack__find_channel` (assumed name — verify) or look up via search first.
- `limit`: pass through.
- `oldest` / `latest`: optional time bounds — omit for "most recent N".

## Steps

1. Resolve `channel` to channel ID if user supplied a name (drop leading `#`, then call channel-list / search if MCP exposes one; otherwise prompt user for ID).

2. Call:
   ```
   mcp__slack__read_channel({
     "channel": "<channel_id>",
     "limit": 20
   })
   ```

3. Handle pagination — if response includes `has_more: true` with `next_cursor`, repeat once if `limit` not yet satisfied.

4. Format Markdown:
   ```
   ## #<channel.name> (last N messages)

   **<user.name>** · <timestamp>
   <text>
   └─ <reply_count> replies
   ```

   Omit the `└─` line when `reply_count == 0`.

## Common failure modes

- **`channel_not_found`** → ID typo, or user not a member of a private channel; see `references/failure-modes.md` § Workspace visibility.
- **`not_in_channel`** → channel exists but bot/user not joined; emit `ERR: not a member of <channel>`.
- **Empty `messages: []`** → valid empty channel.
- **Rate limit (429)** → see `references/failure-modes.md` § Rate limit.

## Notes

- For thread replies on a specific message → use `protocols/thread-read.md`.
- The Slack `conversations.history` API returns messages newest-first; reverse client-side if chronological order is desired in output.

## Examples

`channel = engineering, limit = 10` → last 10 messages as Markdown.
