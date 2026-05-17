---
name: search-messages
purpose: Full-text search across Slack channels with Slack operators.
---

## Inputs
- `query`: required. May include operators.
- `--json`: optional.

## Output
```
## Slack search: "<query>" — N results

**#<channel>** · <user> · <timestamp>
> <text>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Search button | `[button] "Search"` | `[button] "搜尋"` | `[button] "検索"` |
| Search input | `[textbox] "Search"` or `[combobox]` | `[textbox] "搜尋"` or `[combobox]` | `[textbox] "検索"` or `[combobox]` |
| Sign-in fallback button (login-detect) | `[button] "Sign in to Slack"` | `[button] "登入 Slack"` | `[button] "Slack にサインイン"` |

## Procedure

1. ```bash
   abx open https://app.slack.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find Search button (per Localized labels).

3. Click + re-snapshot:
   ```bash
   abx click @eN
   abx wait 500
   abx snapshot -i
   ```

4. **Find active search input**. Fill + submit:
   ```bash
   abx fill @eM "<query>"
   abx press Enter
   abx wait --load networkidle
   abx snapshot -i
   ```

5. **Read results**. Each result `[listitem]` (or `[article]`) with channel / user / timestamp / text. Extract + format.

## Failure modes

- **Search button missing** → top bar restructured.
- **No results for known-good query** → check for Sign-in button (any locale per table) → reauth.

## Notes

- **Slack operators** (`from:`, `in:`, `has:`, `before:`, `after:`) are locale-stable.
- Free Slack: 90-day message history.

## Examples

`query = "OKR in:#engineering after:2026-05-01"` → matching results.
