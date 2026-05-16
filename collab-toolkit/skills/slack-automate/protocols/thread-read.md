---
name: thread-read
purpose: Read entire thread (parent + all replies).
---

## Inputs
- `thread_url`: required.
- `--json`: optional.

## Output
```
## Thread in #<channel>

**<user>** · <timestamp>  (parent)
<text>

  **<user>** · <timestamp>
  <text>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Thread complementary | `[complementary] "Thread"` | `[complementary] "討論串"` | `[complementary] "スレッド"` |
| Show-more-replies button | `[button] "Show more replies"` | `[button] "顯示更多回覆"` | `[button] "返信をさらに表示"` |

## Procedure

1. Open thread URL:
   ```bash
   abx open <thread_url>
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find Thread `[complementary]` (locale-dependent). Articles inside are parent + replies.

3. Extract each `[article]`: user, timestamp, body. Reactions are child `[button]` with emoji name. Attachments are child `[link]`.

4. Format Markdown.

## Failure modes

- **Thread `[complementary]` missing** → URL malformed / message deleted / no access.
- **Truncated replies** → click Show-more-replies button (locale-dependent) + re-snapshot.

## Examples

`thread_url = https://kouko.slack.com/archives/C123/p1234567890?thread_ts=1234.5678` → full thread.
