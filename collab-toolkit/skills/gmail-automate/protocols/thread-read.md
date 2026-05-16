---
name: thread-read
purpose: Read a single email thread — all messages, headers, attachments.
---

## Inputs
- `thread_url`: required.
- `--json`: optional.

## Output
```
# <subject>

## Message 1: <from> → <to> (<date>)
<body>

Attachments:
- <filename>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Expand-all button | `[button] "Expand all"` | `[button] "全部展開"` | `[button] "すべて展開"` |
| Show-details button | `[button] "Show details"` | `[button] "顯示詳細資料"` | `[button] "詳細を表示"` |

## Procedure

1. ```bash
   abx open <thread_url>
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**:
   - Subject: `[heading]` level=1 (locale-agnostic)
   - Each message: `[region]` or `[article]` with header + body
   - Body content: child `[region]` with body text
   - Attachments: child `[link]` with file names

3. **Expand collapsed messages** — find Expand-all button (locale-dependent) or per-message Show-details. Click + re-snapshot.

4. For each message: extract from/to from header, body via `abx get text @eN`, attachments from `[link]` children.

5. Format Markdown.

## Failure modes

- **No level=1 heading** → redirected to inbox/login. Verify URL.
- **Body in iframe** — Gmail may render HTML body in `[iframe]`. `abx get html @eN` for inspection.
- **Login wall** → reauth.

## Notes

- Per-message grouping depends on Gmail's tree structure — v0.1.6 extracts what's visible.
- `abx get text @eN` strips HTML noise.

## Examples

Input: `thread_url = ...` → full thread Markdown.
