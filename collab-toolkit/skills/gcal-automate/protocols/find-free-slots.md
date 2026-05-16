---
name: find-free-slots
purpose: Find open time slots given duration + business-hours window.
---

## Inputs
- `duration_minutes`: required.
- `start_date` / `end_date`: required.
- `business_hours_start` / `business_hours_end`: optional (24h format). Default 09:00 / 18:00.
- `--json`: optional.

## Output
```
## Free slots (<duration> min, business hours <start>–<end>, <date range>)

- <YYYY-MM-DD>: <HH:MM>–<HH:MM> (<duration> min)
```

## Localized labels

(Inherits from `agenda-view.md` — same view switcher / nav / time-format labels.)

| Element | en | zh-TW | ja |
|---|---|---|---|
| Week view button | `[button] "Week"` | `[button] "週"` | `[button] "週"` |
| Time AM/PM | `AM` / `PM` | `上午` / `下午` | `午前` / `午後` |
| All-day prefix | `All day, ` | `全天, ` | `終日, ` |

## Procedure

1. Open GCal Week view:
   ```bash
   abx open https://calendar.google.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. Click Week button (per labels) + re-snapshot.

3. Navigate to `start_date` if needed (prev/next-week buttons).

4. **Read week snapshot**. For each `[columnheader] "<date>"`:
   - Find all child `[button]` event entries
   - Parse start/end time from aria-label (handle locale-specific time format — AM/PM or 上午/下午 or 午前/午後, or 24h with no marker)
   - Build busy-intervals per date

5. Compute free slots = gaps between busy intervals within `business_hours_start`–`business_hours_end`, where gap ≥ `duration_minutes`.

6. Combine across all dates in range. Format Markdown.

## Failure modes

- **Time parsing fails** for non-supported locale → protocol assumes EN / zh-TW / ja. Other locales: refine logic.
- **No events** → entire business window free.
- **Login wall** → reauth.

## Notes

- **Recurring events** flattened — each instance separately.
- **All-day events** typically don't block working hours — exclude when computing busy intervals.
- **24h format** has no AM/PM marker — parse directly as 24h hour.

## Examples

`duration_minutes = 30, start_date = 2026-05-18, end_date = 2026-05-22` → free 30-min slots.
