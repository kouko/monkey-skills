---
name: channel-read
purpose: Read recent N messages in a channel.
---

## Inputs
- `channel`: required (name or URL).
- `limit`: optional, default 20.
- `--json`: optional.

## Output
```
## #<channel> (last N messages)

**<user>** · <timestamp>
<text>
└─ <thread reply count>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Conversation region | `[region] "Conversation"` | `[region] "對話"` | `[region] "会話"` |
| Thread reply link | `[link] "<N> reply"` or `"<N> replies"` | `[link] "<N> 則回覆"` or `"<N> 個回覆"` | `[link] "<N> 件の返信"` |

## Procedure

1. If `channel` is URL: `abx open <url>`. Else: open Slack + find `[treeitem]` with channel name in sidebar (channel names are user-defined).
   ```bash
   abx open https://app.slack.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**, find channel `[treeitem]`. Click + re-snapshot:
   ```bash
   abx click @eN
   abx wait --load networkidle
   abx snapshot -i
   ```

3. **Read channel snapshot**. Messages are `[article]` within Conversation region (locale-dependent name). Per article: author, timestamp, body, optional thread-reply link.

4. Extract last N messages. Format Markdown.

## Failure modes

- **Channel `[treeitem]` not in sidebar** → user left or hidden — try direct URL `https://app.slack.com/client/<workspace>/<channel-id>`.
- **No `[article]` elements** → empty channel.

## Notes

- Scroll up + re-snapshot for older messages.
- For thread replies → use `protocols/thread-read.md`.

## Examples

`channel = engineering, limit = 10` → last 10 messages.
