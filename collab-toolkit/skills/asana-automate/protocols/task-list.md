---
name: task-list
purpose: List My Tasks across all projects with optional filters.
---

## Inputs
- `filter_due`: optional. `today` / `this-week` / `overdue` / `all`. Default: `all`.
- `filter_status`: optional. `incomplete` / `complete` / `all`. Default: `incomplete`.
- `filter_project`: optional. Substring match.

## Output
```
## My Tasks (N)
- [ ] <title> — Project: <project> — Due: <date>
- [x] <title> — Project: <project> — Due: <date>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Sidebar link → My Tasks | `[link] "My tasks"` | `[link] "我的任務"` | `[link] "マイタスク"` |
| Due-date button prefix | `Due date, ` | `到期日, ` | `期日, ` |
| Complete checkbox | `[checkbox] "Mark complete"` | `[checkbox] "標示為完成"` | `[checkbox] "完了としてマーク"` |
| Sort button (default) | `[button] "Recently assigned"` | `[button] "最近指派"` | `[button] "最近割り当て"` |
| Show-more pagination | `[button] "Show more"` | `[button] "顯示更多"` | `[button] "もっと表示"` |

## Procedure

1. Open inbox:
   ```bash
   abx open https://app.asana.com/0/inbox
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find My-Tasks sidebar link (label per Localized labels). Note `@eN`.

3. Click + re-snapshot:
   ```bash
   abx click @eN
   abx wait --load networkidle
   abx snapshot -i
   ```

4. **Read new snapshot**. Task rows under `[grid]` or `[list]`:
   ```
   @eX [row]
     @eX+1 [link] "<task title>"
     @eX+2 [button] "<Due-date prefix><value>"
     @eX+3 [checkbox] "<complete label>"
   ```

5. Extract per row: title (link child), due date (button name, strip locale prefix), completion (checkbox).

6. Apply filters. Format as Markdown.

## Failure modes

- **My-Tasks link not found** in any of 3 locales → sidebar restructured → re-snapshot.
- **Login wall** (title contains `Log in` / `登入` / `ログイン` / URL → `/-/login`) → `/collab-setup --reauth asana`.
- **Empty grid** → valid → `No tasks matching filter.`

## Notes (Asana quirks, locale-independent)

- **Filter dropdown uses React portal** → NOT in tree → filter post-extraction.
- **Default sort = "Recently assigned"** (or localized) — switch via Sort button if needed.
- **Lazy loading** — scroll grid + re-snapshot.

## Examples

"show my Asana tasks this week" / 「列我這週的 Asana 任務」 / 「今週のAsanaタスク」 — Markdown list.
