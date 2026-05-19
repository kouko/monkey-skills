---
name: thread-read
purpose: Read an entire Slack thread (parent message + all replies).
allowed-tools: mcp__slack__read_thread
---

## Purpose

Return a Markdown rendering of a Slack thread — parent message followed by indented replies.

## Input

- `thread_url` OR (`channel` + `thread_ts`): required.
  - Parse `channel` and `thread_ts` from `https://<workspace>.slack.com/archives/<channel_id>/p<ts>?thread_ts=<thread_ts>` if URL given.
  - `thread_ts` in URL is `1234567890.123456` format (insert decimal point after 10th digit if URL uses `p1234567890123456`).
- `--json`: optional.

Mapping to MCP params:
- `channel`: required (channel ID, not name).
- `ts` or `thread_ts`: required — the parent message timestamp.

## Steps

1. Resolve `channel` and `thread_ts` from `thread_url` if given.

2. Call:
   ```
   mcp__slack__read_thread({
     "channel": "<channel_id>",
     "thread_ts": "<thread_ts>"
   })
   ```

3. Handle pagination — Slack `conversations.replies` returns up to 1000 replies per call with `has_more` / `next_cursor`. Paginate until exhausted.

4. Format Markdown:
   ```
   ## Thread in #<channel.name>

   **<user.name>** · <timestamp>  (parent)
   <text>

     **<user.name>** · <timestamp>
     <text>
   ```

   First message in array is the parent; subsequent messages are replies (indent two spaces).

## Common failure modes

- **`thread_not_found`** → URL malformed, message deleted, or no access (private channel user isn't in).
- **`channel_not_found`** → see `references/failure-modes.md` § Workspace visibility.
- **Truncated thread** → ensure pagination loop ran; if `has_more` still true after paginate budget, emit `... <N> more replies truncated.`

## Notes

- Reactions are exposed via `reactions[]` per message — omit from default Markdown unless user asks.
- Attachments / files appear in `files[]` — render as `[file: <name>]` placeholders.

## Examples

`thread_url = https://kouko.slack.com/archives/C123/p1234567890123456?thread_ts=1234567890.123456` → full thread as Markdown.
