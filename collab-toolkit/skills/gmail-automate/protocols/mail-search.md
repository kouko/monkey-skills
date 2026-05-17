---
name: mail-search
purpose: Full-text mail search with Gmail operators.
---

## Inputs
- `query`: required. May include operators.
- `--json`: optional.

## Output
```
## Gmail search: "<query>" — N results

- <YYYY-MM-DD> <from>: <subject> — <snippet>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Search input | `[combobox] "Search mail"` | `[combobox] "搜尋郵件"` | `[combobox] "メールを検索"` |
| Star/Starred button | `[button] "Star"` / `"Starred"` | `[button] "已加星號"` / `"未加星號"` | `[button] "スター付き"` / `"スター無し"` |

## Procedure

1. ```bash
   abx open https://mail.google.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find search input (locale-dependent). Gmail uses `[combobox]` (not `[textbox]`) because of suggestion dropdown.

3. Fill + submit:
   ```bash
   abx click @eN
   abx fill @eN "<query>"
   abx press Enter
   abx wait --load networkidle
   abx snapshot -i
   ```

4. **Read results**. Each row `[row]` with cells: from / subject / snippet / date.

5. Extract + format Markdown.

## Failure modes

- **Operator preservation** — `abx fill` may have autocomplete interfere with `:` / `@`. **If `from:foo@example.com` queries return wrong results, switch to** `abx type @eN "<query>"` **for character-by-character keypress simulation**.
- **No results** → valid empty.
- **Login wall** → reauth.

## Notes

- **Operators**: `from:`, `to:`, `subject:`, `has:attachment`, `before:YYYY/MM/DD`, `after:YYYY/MM/DD`, `label:`, `is:unread`, `is:starred` — all locale-stable.

## Examples

`query = "from:alice@company.com has:attachment after:2026-05-01"` → matching mail.
