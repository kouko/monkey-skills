---
name: inbox-summary
purpose: Summarize inbox state — unread counts + first N rows per Category tab.
---

## Inputs
- `limit_per_tab`: optional, default 5.
- `--json`: optional.

## Output
```
## Inbox Summary

### Primary (N unread)
- <from>: <subject>

### Social (N unread)
...
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Primary tab | `[tab] "Primary"` | `[tab] "主要"` | `[tab] "メイン"` |
| Social tab | `[tab] "Social"` | `[tab] "社交網路"` | `[tab] "ソーシャル"` |
| Promotions tab | `[tab] "Promotions"` | `[tab] "促銷內容"` | `[tab] "プロモーション"` |
| Updates tab | `[tab] "Updates"` | `[tab] "最新快訊"` | `[tab] "新着"` |
| Unread aria-label suffix | `, unread` | `, 未讀` | `, 未読` |

## Procedure

1. ```bash
   abx open https://mail.google.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find Category tabs (per Localized labels — try all 3 locales). If no tabs present: user has tabs disabled — single-pane mode.

3. For each tab (or single list):
   - Click tab + re-snapshot
   - Find unread count in tab aria-label (e.g., `[tab] "Primary, N unread"` / locale variant)
   - Extract first N rows (`[row]` elements). Unread rows often marked via aria-label suffix (locale-dependent).
   - Per row: from + subject

4. Format Markdown.

## Failure modes

- **No `[tab]` elements** → tabs disabled (valid). Summarize single-pane inbox.
- **Login wall** → reauth.

## Notes

- **Unread visual = bold text**. Accessibility tree may expose via aria-label suffix (locale-dependent).
- List density modes (Default / Comfortable / Compact) don't change row pattern.

## Examples

`limit_per_tab = 3` → 3 rows × 4 tabs = up to 12 summaries.
