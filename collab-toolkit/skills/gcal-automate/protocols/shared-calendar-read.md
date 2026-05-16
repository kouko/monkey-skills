---
name: shared-calendar-read
purpose: Read events from a colleague's shared calendar.
---

## Inputs
- `calendar_name`: required. Display name in "Other calendars" sidebar.
- `range`: optional. `today` / `week`.
- `--json`: optional.

## Output
```
## <calendar_name> (<date range>)

### <Date>
- <HH:MM>–<HH:MM>: <title>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Other calendars sidebar list | `[list] "Other calendars"` | `[list] "其他日曆"` | `[list] "他のカレンダー"` |
| Add-calendar button | `[button] "Add other calendars"` | `[button] "新增其他日曆"` | `[button] "他のカレンダーを追加"` |

## Procedure

1. ```bash
   abx open https://calendar.google.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find Other-calendars list in sidebar (locale-dependent). It contains `[checkbox]` items per subscribed calendar.

3. **Find target checkbox**: `[checkbox] "<calendar_name>"` (calendar display name; user-set, no translation). If unchecked, click to enable:
   ```bash
   abx click @eN
   abx wait 500
   abx snapshot -i
   ```

4. To isolate (optional): uncheck other calendars OR rely on event-color matching.

5. Run agenda-view extraction (see `protocols/agenda-view.md`) to get events.

6. Filter to target calendar (if distinguishable).

## Failure modes

- **Calendar not in Other-calendars list** → user hasn't subscribed → instruct user to add via `+` button → "Subscribe to calendar".
- **No events** → colleague has none OR calendar privacy = "Free/Busy only" (shows "Busy" blocks, no details).
- **Login wall** → reauth.

## Notes

- **Privacy levels**:
  - "See all event details" — full info visible
  - "Only free/busy" — only "Busy" blocks visible
- **Event aria-label may not include calendar source** — distinguishing via color hard. Best path: temporarily uncheck other calendars.

## Examples

`calendar_name = "Alice Chen", range = week` → Alice's events this week.
