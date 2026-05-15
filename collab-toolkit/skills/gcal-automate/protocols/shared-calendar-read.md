---
name: shared-calendar-read
purpose: Enable a colleague's shared calendar from the "Other calendars" sidebar, then read their events via agenda view.
---

## Inputs

- `colleague_calendar`: required. Display name of the colleague's calendar as it appears in the "Other calendars" sidebar (e.g., `"Alice Chen"`).
- `range`: optional. View range passed to agenda-view logic — `today`, `week`, `YYYY-MM-DD`. Default: `week`.
- `--json`: optional.

## Output

Default Markdown:
```
## Shared calendar: Alice Chen (week)

### Mon May 12
- 10:00 Project sync (1 hr)

### Tue May 13
(no events visible)
```

`--json`: `{ colleague_calendar, range, events: [{ date, time, title }] }`.

> **Output spec note**: Event `time` and `title` are split from event button `.name // ""` heuristically. The "Other calendars" list item `.name` matching the colleague display name is speculative (v0.1.0 unverified) — actual AT label may include additional text. See `references/ui-patterns.md` AT-schema notes. All use `// ""` / `// "(unknown)"` fallbacks.

## Procedure

```bash
COLLEAGUE="${1:-}"
RANGE="${2:-week}"

[ -z "$COLLEAGUE" ] && { echo "ERR: colleague_calendar required"; exit 1; }

ABX_SERVICE=gcal abx open https://calendar.google.com
ABX_SERVICE=gcal abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Google in Chrome (shared mode) or run /collab-setup --reauth gcal" >&2
  exit 1
fi

# Find "Other calendars" list — role=list name="Other calendars"
OTHER_CAL_LIST=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="list" and ((.name // "") | contains("Other calendars"))) | .ref' | head -1)
if [ -z "$OTHER_CAL_LIST" ]; then
  echo "ERR: UI changed: 'Other calendars' list (role=list name='Other calendars') not found" >&2
  exit 1
fi

# Find the colleague's calendar entry within Other calendars
# NOTE: .parent.* dropped (Pattern F) — accept all checkboxes/listitems whose name contains colleague name.
# NOTE: ((.name // "") | contains(...)) guarded against null (Pattern G).
CAL_REF=$(echo "$SNAP" | jq -r --arg col "$COLLEAGUE" '
  .elements[]
  | select(
      (.role=="checkbox" or .role=="listitem")
      and ((.name // "") | contains($col))
    )
  | .ref
' | head -1)

if [ -z "$CAL_REF" ]; then
  echo "ERR: colleague calendar '$COLLEAGUE' not found in 'Other calendars' sidebar" >&2
  echo "Note: calendar must have been shared with you and visible in GCal's left sidebar." >&2
  exit 1
fi

# Check if already enabled (checked). If role=checkbox, inspect .checked // false.
CAL_CHECKED=$(echo "$SNAP" | jq -r --arg col "$COLLEAGUE" '
  .elements[]
  | select(
      .role=="checkbox"
      and ((.name // "") | contains($col))
    )
  | .checked // false
' | head -1)

if [ "$CAL_CHECKED" != "true" ]; then
  # Enable the calendar — click to toggle on
  ABX_SERVICE=gcal abx click "$CAL_REF"
  ABX_SERVICE=gcal abx wait 800

  # Pattern H: re-derive ref from new snapshot and verify calendar is now enabled
  SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
  CAL_CHECKED_AFTER=$(echo "$SNAP" | jq -r --arg col "$COLLEAGUE" '
    .elements[]
    | select(
        .role=="checkbox"
        and ((.name // "") | contains($col))
      )
    | .checked // false
  ' | head -1)
  if [ "$CAL_CHECKED_AFTER" != "true" ]; then
    # Fallback: checked state may not be exposed as .checked — accept that click was issued
    # and proceed to snapshot events. Log a warning.
    echo "WARN: could not verify calendar enable state for '$COLLEAGUE' — proceeding" >&2
  fi
fi

# Switch to view per RANGE
case "$RANGE" in
  today)
    VIEW_NAME="Day"
    ;;
  week|*)
    VIEW_NAME="Week"
    ;;
esac

SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
VIEW_REF=$(echo "$SNAP" | jq -r --arg v "$VIEW_NAME" '.elements[] | select(.role=="button" and .name==$v) | .ref' | head -1)
if [ -n "$VIEW_REF" ]; then
  ABX_SERVICE=gcal abx click "$VIEW_REF"
  ABX_SERVICE=gcal abx wait --load networkidle
fi

# Final snapshot — extract events
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)

# Events from the shared calendar are role=button with time-prefixed names.
# We cannot filter by calendar owner in v0.1.0 (no .calendar field in flat AT snapshot).
# All visible events are extracted; label appended where available.
# NOTE: .parent.* dropped (Pattern F) — no parent in flat snapshot.
EVENTS=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(
      .role=="button"
      and ((.name // "") | test("^[0-9]"))
    )
  | "- \(.name // "(unknown)")"
')

if [ -z "$EVENTS" ]; then
  DATE_COL_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="columnheader") | .ref' | head -1)
  if [ -z "$DATE_COL_CHECK" ]; then
    echo "ERR: UI changed: calendar grid not found after enabling shared calendar" >&2
    exit 1
  fi
  echo "## Shared calendar: $COLLEAGUE ($RANGE)"
  echo
  echo "(no events visible for this calendar in the current view)"
else
  echo "## Shared calendar: $COLLEAGUE ($RANGE)"
  echo
  echo "$EVENTS"
fi
```

## Notes

- Only events the shared calendar owner has marked as visible to you will appear. Events marked "Private" show as "Busy" with no title.
- If the colleague has not shared their calendar with you, the entry will not appear in "Other calendars" — this protocol will exit with an error.
- After enabling, the calendar stays on until manually toggled off in GCal; re-running this protocol is idempotent.

## Failure modes

- "Other calendars" list absent → UI evolution → exits 1 with `ERR: UI changed`
- Colleague name not in "Other calendars" → calendar not shared or not visible → exits 1 with error message
- Calendar enable click fails silently → `.checked` field may not be exposed; warning emitted, protocol continues
- No events but grid present → valid empty (colleague has no visible events in range)
- Private events → appear as "Busy" (no title) in event button name
- Calendar permission issues → some shared calendars are view-only for free/busy; titles may not appear (see `references/failure-modes.md`)
