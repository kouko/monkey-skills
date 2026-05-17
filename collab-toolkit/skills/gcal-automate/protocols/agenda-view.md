---
name: agenda-view
purpose: Fetch events for today / this week / arbitrary date range.
---

## Inputs
- `range`: optional. `today` / `week` / `custom`.
- `start_date` / `end_date`: required when `custom`.
- `--json`: optional.

## Output
```
## Agenda (<date range>)

### <Date 1>
- <HH:MM> – <HH:MM>: <title>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Day view button | `[button] "Day"` | `[button] "日"` | `[button] "日"` |
| Week view button | `[button] "Week"` | `[button] "週"` | `[button] "週"` |
| Month view button | `[button] "Month"` | `[button] "月"` | `[button] "月"` |
| Previous-week nav | `[button] "Previous week"` | `[button] "上一週"` | `[button] "前週"` |
| Next-week nav | `[button] "Next week"` | `[button] "下一週"` | `[button] "次週"` |
| Time AM/PM | `AM` / `PM` | `上午` / `下午` | `午前` / `午後` |
| All-day prefix | `All day, ` | `全天, ` | `終日, ` |

## Procedure

1. ```bash
   abx open https://calendar.google.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find view switcher (top-right toolbar). Click desired view (per Localized labels):
   ```bash
   abx click @eN
   abx wait --load networkidle
   abx snapshot -i
   ```

3. For custom range: navigate via date picker (look for `[button]` with date or use prev/next buttons).

4. **Read calendar grid snapshot**. Day columns are `[columnheader] "<date>"`. Events within columns are `[button]` with name format like `"<HH:MM AM/PM>, <title>"` or `"<HH:MM>, <title>"` (24h locale). All-day events use locale-specific All-day prefix.

5. Extract per event: time (handle locale variants), title, optional location.

6. Group by date column. Format Markdown.

## Failure modes

- **View switcher missing** → toolbar restructured.
- **No event buttons** → no events in range (valid empty).
- **Login wall** → reauth.

## Notes

- **Time format depends on locale + 12/24h preference** — protocol handles AM/PM (en) + 上午/下午 (zh-TW) + 午前/午後 (ja) + 24h (locale-independent).
- **All-day events** appear at top of day column with locale-specific All-day prefix.
- **Recurring events** show as instances per day.

## Examples

`range = week` → events for this week.
