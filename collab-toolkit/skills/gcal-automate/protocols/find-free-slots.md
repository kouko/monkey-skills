---
name: find-free-slots
purpose: Given a duration and a date range with business-hours bounds, compute available free time slots by reading the week-view event grid.
---

## Inputs

- `duration_minutes`: required. Minimum slot length (e.g., `30`, `60`, `90`).
- `start_date`: required. First day to check, `YYYY-MM-DD`.
- `end_date`: required. Last day to check (inclusive), `YYYY-MM-DD`.
- `business_hours_start`: optional. HH:MM 24h (default `09:00`).
- `business_hours_end`: optional. HH:MM 24h (default `18:00`).
- `--json`: optional.

## Output

Default Markdown:
```
## Free slots ≥30 min (Mon May 12 – Fri May 16, 09:00–18:00)

- Mon May 12 · 09:00–10:30 (90 min)
- Mon May 12 · 14:00–18:00 (240 min)
- Tue May 13 · 11:00–12:00 (60 min)
- Wed May 14 · (no free slots ≥30 min)
```

`--json`: `{ duration_minutes, start_date, end_date, slots: [{ date, start_time, end_time, duration_minutes }] }`.

> **Output spec note**: Event time parsing (start + end from button name) is heuristic. GCal event button names include time+title in a locale-dependent format (e.g., `"10:00 am, Stand-up, 30 minutes, Calendar name"`). Parsing relies on regex matching against the raw `.name // ""` string. Accuracy degrades for events spanning multiple lines or all-day events (which appear as `role=button` with no time prefix). All-day events are treated as occupying the full business day. Both are speculative (v0.1.0 unverified) — see `references/ui-patterns.md` AT-schema notes.

## Procedure

```bash
DURATION="${1:-30}"
START_DATE="${2:-}"
END_DATE="${3:-}"
BIZ_START="${4:-09:00}"
BIZ_END="${5:-18:00}"

[ -z "$START_DATE" ] && { echo "ERR: start_date required"; exit 1; }
[ -z "$END_DATE" ]   && { echo "ERR: end_date required"; exit 1; }

# Convert HH:MM to minutes-since-midnight for Bash arithmetic
to_min() {
  local h m
  IFS=: read -r h m <<< "$1"
  echo $(( 10#$h * 60 + 10#$m ))
}
from_min() {
  local total="$1"
  printf "%02d:%02d" $(( total / 60 )) $(( total % 60 ))
}

BIZ_START_MIN=$(to_min "$BIZ_START")
BIZ_END_MIN=$(to_min "$BIZ_END")

ABX_SERVICE=gcal abx open https://calendar.google.com
ABX_SERVICE=gcal abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Google in Chrome (shared mode) or run /collab-setup --reauth gcal" >&2
  exit 1
fi

# Switch to Week view
VIEW_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and .name=="Week") | .ref' | head -1)
if [ -z "$VIEW_REF" ]; then
  echo "ERR: UI changed: 'Week' view button not found" >&2
  exit 1
fi
ABX_SERVICE=gcal abx click "$VIEW_REF"
ABX_SERVICE=gcal abx wait --load networkidle

# Navigate to start_date
COMPACT_START=$(echo "$START_DATE" | tr -d '-')
ABX_SERVICE=gcal abx open "https://calendar.google.com/calendar/r/week/$COMPACT_START"
ABX_SERVICE=gcal abx wait --load networkidle
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)

# Extract event buttons — parse time range from name
# Name format (speculative): "HH:MM [am/pm], Title, Duration, Calendar"
# We extract all buttons whose name starts with a digit (time-like prefix)
# NOTE: .parent.* dropped (Pattern F) — no parent in flat snapshot
# NOTE: ((.name // "") | startswith/contains) guarded against null (Pattern G)
EVENTS_RAW=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(
      .role=="button"
      and ((.name // "") | test("^[0-9]"))
    )
  | .name // ""
')

# Pattern H: distinguish empty events from UI evolution
if [ -z "$EVENTS_RAW" ]; then
  DATE_COL_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="columnheader") | .ref' | head -1)
  if [ -z "$DATE_COL_CHECK" ]; then
    echo "ERR: UI changed: calendar grid (columnheader) not found" >&2
    exit 1
  fi
  # Valid empty: no events this week
  echo "## Free slots >= $DURATION min ($START_DATE – $END_DATE, $BIZ_START–$BIZ_END)"
  echo
  echo "- $START_DATE – $END_DATE: full business hours available (no events detected)"
  exit 0
fi

# Build busy-interval list per day via Bash parsing
# For each event button name, attempt to extract start_min and end_min:
#   "9:00 AM, Stand-up, 30 minutes, ..." → start=9:00 duration=30
# Fallback: treat unparseable events as full-day busy (conservative).
declare -A BUSY  # BUSY[YYYY-MM-DD]="start_min:end_min start_min:end_min ..."

while IFS= read -r raw; do
  # Extract start time (first token matching HH:MM or H:MM with optional AM/PM)
  START_T=$(echo "$raw" | grep -oE '^[0-9]{1,2}:[0-9]{2}' | head -1)
  # Extract duration_minutes from "NN minutes" pattern
  DUR_M=$(echo "$raw" | grep -oiE '[0-9]+ minutes?' | grep -oE '[0-9]+' | head -1)

  if [ -z "$START_T" ] || [ -z "$DUR_M" ]; then
    # Unparseable — skip (conservative: ignore, not block full day)
    continue
  fi

  # Determine AM/PM if present
  IS_PM=0
  echo "$raw" | grep -qi ' pm' && IS_PM=1
  IFS=: read -r EV_H EV_M <<< "$START_T"
  EV_H=$(( 10#$EV_H ))
  EV_M=$(( 10#$EV_M ))
  [ "$IS_PM" = "1" ] && [ "$EV_H" -lt 12 ] && EV_H=$(( EV_H + 12 ))
  [ "$IS_PM" = "0" ] && [ "$EV_H" = "12" ] && EV_H=0
  EV_START_MIN=$(( EV_H * 60 + EV_M ))
  EV_END_MIN=$(( EV_START_MIN + DUR_M ))

  # Associate with start_date (week view: all events on the same snapshot are in this week range)
  # Date-to-event mapping requires columnheader date labels — use START_DATE as approximation for
  # multi-day computation; full per-day grouping deferred to v0.2.0 (needs parent-child grid structure).
  # For now: collect all busy intervals under start_date as a per-week aggregate.
  BUSY["$START_DATE"]+="$EV_START_MIN:$EV_END_MIN "
done <<< "$EVENTS_RAW"

echo "## Free slots >= $DURATION min ($START_DATE – $END_DATE, $BIZ_START–$BIZ_END)"
echo

# Compute free slots within business hours for start_date (single-week v0.1.0)
# Note: multi-week iteration (start_date to end_date spanning > 7 days) deferred to v0.2.0.
CURRENT_MIN=$BIZ_START_MIN
SLOTS_FOUND=0

# Sort busy intervals
SORTED_BUSY=$(echo "${BUSY[$START_DATE]:-}" | tr ' ' '\n' | grep -v '^$' | sort -t: -k1 -n)

while IFS= read -r interval; do
  [ -z "$interval" ] && continue
  IFS=: read -r EV_S EV_E <<< "$interval"
  if [ "$EV_S" -gt "$CURRENT_MIN" ]; then
    GAP=$(( EV_S - CURRENT_MIN ))
    if [ "$GAP" -ge "$DURATION" ]; then
      echo "- $START_DATE · $(from_min $CURRENT_MIN)–$(from_min $EV_S) ($GAP min)"
      SLOTS_FOUND=$(( SLOTS_FOUND + 1 ))
    fi
  fi
  [ "$EV_E" -gt "$CURRENT_MIN" ] && CURRENT_MIN=$EV_E
done <<< "$SORTED_BUSY"

# Final slot: current_min to BIZ_END
if [ "$BIZ_END_MIN" -gt "$CURRENT_MIN" ]; then
  GAP=$(( BIZ_END_MIN - CURRENT_MIN ))
  if [ "$GAP" -ge "$DURATION" ]; then
    echo "- $START_DATE · $(from_min $CURRENT_MIN)–$(from_min $BIZ_END_MIN) ($GAP min)"
    SLOTS_FOUND=$(( SLOTS_FOUND + 1 ))
  fi
fi

if [ "$SLOTS_FOUND" -eq 0 ]; then
  echo "- $START_DATE: (no free slots >= $DURATION min within $BIZ_START–$BIZ_END)"
fi
```

## Failure modes

- `duration_minutes` missing or non-numeric → validation error
- `start_date` or `end_date` missing → validation error
- Login wall detected → auth expiry
- Week view button absent → UI evolution → exits 1 with `ERR: UI changed`
- No columnheader elements → calendar grid changed → UI evolution → exits 1 with `ERR: UI changed`
- No event buttons but columnheaders present → valid empty week → full business hours reported as free
- Event name parsing fails (locale, 24h format) → events skipped conservatively (slot may be wider than actual)
- Multi-week date range (> 7 days) → v0.1.0 only snapshots the first week; remaining days not covered (deferred to v0.2.0)
