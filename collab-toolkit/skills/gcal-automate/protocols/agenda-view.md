---
name: agenda-view
purpose: Open Google Calendar, switch to the requested view, snapshot the event grid, and extract events grouped by date.
---

## Inputs

- `range`: required. One of `today`, `week`, `YYYY-MM-DD` (single day), or `YYYY-MM-DD/YYYY-MM-DD` (custom range).
- `--json`: optional.

## Output

Default Markdown (v0.1.0 — per-date grouping not yet implemented):
```
## Calendar: 2026-05-15 (Week view)

### Friday May 15
### Saturday May 16
### Sunday May 17

- 9:00 AM, Stand-up, 30 minutes, Personal
- 11:00 AM, Design review, 1 hour, Work
- 2:00 PM, 1:1 with Alice, 30 minutes, Work
```

**v0.2.0 deferred**: per-date grouping (events listed under their date header) requires
parent-child relationship inference from the AT grid — not available in v0.1.0 flat snapshot.
v0.1.0 emits all date headers first, then a flat event list below them.

`--json`: `{ range, view, dates: [{ date, events: [{ time, title, duration_minutes }] }] }`.

> **Output spec note**: `duration_minutes` is derived by parsing the event button name string — not a direct AT field. `time` and `title` are split from the button name heuristically (format varies by locale). Both are speculative (v0.1.0 unverified) — see `references/ui-patterns.md` AT-schema notes. All use `// ""` fallbacks.

## Procedure

```bash
RANGE="${1:-today}"

ABX_SERVICE=gcal abx open https://calendar.google.com
ABX_SERVICE=gcal abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Google in Chrome (shared mode) or run /collab-setup --reauth gcal" >&2
  exit 1
fi

# Switch view based on RANGE
case "$RANGE" in
  today)
    VIEW_NAME="Day"
    ;;
  week)
    VIEW_NAME="Week"
    ;;
  *)
    # For custom date or custom range, switch to Week view and navigate date
    VIEW_NAME="Week"
    ;;
esac

# Click view switcher — role=button name=Day/Week/Month
VIEW_REF=$(echo "$SNAP" | jq -r --arg v "$VIEW_NAME" '.elements[] | select(.role=="button" and .name==$v) | .ref' | head -1)
if [ -z "$VIEW_REF" ]; then
  # Try a "More view options" or "View options" button (GCal may nest options)
  OPTIONS_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and ((.name // "") | contains("view"))) | .ref' | head -1)
  if [ -z "$OPTIONS_REF" ]; then
    echo "ERR: UI changed: view switcher button '$VIEW_NAME' not found" >&2
    exit 1
  fi
  ABX_SERVICE=gcal abx click "$OPTIONS_REF"
  ABX_SERVICE=gcal abx wait 500
  SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
  VIEW_REF=$(echo "$SNAP" | jq -r --arg v "$VIEW_NAME" '.elements[] | select(.role=="button" and .name==$v) | .ref' | head -1)
  [ -z "$VIEW_REF" ] && { echo "ERR: UI changed: view button '$VIEW_NAME' not found after options expand" >&2; exit 1; }
fi

ABX_SERVICE=gcal abx click "$VIEW_REF"
ABX_SERVICE=gcal abx wait --load networkidle

# Navigate to the target date if RANGE is a specific date
if echo "$RANGE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
  TARGET_DATE=$(echo "$RANGE" | cut -d'/' -f1)
  # GCal supports date param: ?date=YYYYMMDD
  COMPACT=$(echo "$TARGET_DATE" | tr -d '-')
  ABX_SERVICE=gcal abx open "https://calendar.google.com/calendar/r/week/$COMPACT"
  ABX_SERVICE=gcal abx wait --load networkidle
fi

# Snapshot final view
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)

# Extract date column headers — role=columnheader contains date labels
# NOTE: .name may be "(unknown)" if GCal uses aria-label with dynamic date format
DATES=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="columnheader") | .name // "(unknown)"')

# Extract event buttons — role=button, name contains time + title
# NOTE: .name format is speculative (locale-dependent). Fallback to "(unknown)" per event.
# NOTE: .parent.* filter dropped (Pattern F) — flat snapshot has no .parent.
# Accept all role=button elements whose name matches a time-like prefix.
EVENTS=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="button" and ((.name // "") | test("^[0-9]")))
  | "- \(.name // "(unknown)")"
')

if [ -z "$EVENTS" ]; then
  # Pattern H: distinguish silent empty from UI evolution
  DATE_COL_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="columnheader") | .ref' | head -1)
  if [ -z "$DATE_COL_CHECK" ]; then
    echo "ERR: UI changed: columnheader elements not found — calendar grid may have changed" >&2
    exit 1
  fi
  echo "## Calendar: $RANGE ($VIEW_NAME view)"
  echo
  echo "(no events in this view)"
else
  echo "## Calendar: $RANGE ($VIEW_NAME view)"
  echo
  echo "$DATES" | while IFS= read -r date_label; do
    echo "### $date_label"
    # Events per date: heuristic — all events listed sequentially (full per-date grouping requires
    # parent-child relationship; deferred to v0.2.0 after live-snapshot verification of grid structure)
  done
  echo
  echo "$EVENTS"
fi
```

## Failure modes

- Login wall detected → auth expiry or not logged in
- View switcher button absent → UI evolution (see `references/ui-patterns.md`)
- No columnheader elements → calendar grid restructured → UI evolution → exits 1 with `ERR: UI changed`
- No event buttons but columnheaders present → valid empty range (no events scheduled)
- Date navigation failure → GCal may not accept `?date=` param for all view types — use manual "Next" button clicks as fallback
