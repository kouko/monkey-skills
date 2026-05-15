---
name: event-search
purpose: Search Google Calendar for events by title, attendee, or location; return matching results.
---

## Inputs

- `query`: required. Free-text search string (title, attendee name, attendee email, location).
- `--json`: optional.

## Output

Default Markdown (v0.1.0 — raw name field only):
```
## GCal search: "OKR" — 5 matches

- Q2 OKR Review, Mon May 12 2026, 10:00 AM – 11:00 AM, Conference Room A
- OKR Planning, Wed May 14 2026, 2:00 PM – 3:30 PM
- ...
```

`--json`: `{ query, events: [{ title, date, time_range, location }] }`.

> **v0.2.0 deferred**: per-field extraction (date / time_range / location) requires live AT-snapshot verification to confirm how GCal encodes these on search-result elements. v0.1.0 emits only the raw `.name` string (which typically contains title + date + time concatenated by GCal). `--json` fields other than `title` will be empty strings until v0.2.0.

> **Output spec note**: v0.1.0 outputs only the raw `.name` string from each search-result AT element. GCal typically encodes title + date + time into a single `.name` field; `.date`, `.time_range`, and `.location` do NOT exist as separate AT fields on standard article/listitem nodes. Per-field parsing is deferred to v0.2.0 after live AT-snapshot verification. See `references/ui-patterns.md` AT-schema notes.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=gcal abx open https://calendar.google.com
ABX_SERVICE=gcal abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Google in Chrome (shared mode) or run /collab-setup --reauth gcal" >&2
  exit 1
fi

# Click top-bar Search button — role=button name=Search
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and .name=="Search") | .ref' | head -1)
if [ -z "$SEARCH_REF" ]; then
  # Fallback: try combobox (GCal may expose a search combobox directly)
  SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="combobox" and ((.name // "") | contains("Search"))) | .ref' | head -1)
fi
if [ -z "$SEARCH_REF" ]; then
  echo "ERR: UI changed: 'Search' button (role=button name=Search) not found" >&2
  exit 1
fi

ABX_SERVICE=gcal abx click "$SEARCH_REF"
ABX_SERVICE=gcal abx wait 500

# Re-snapshot after click — Pattern H: verify search input opened
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)
INPUT_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="textbox" or .role=="combobox") | .ref' | head -1)
if [ -z "$INPUT_REF" ]; then
  echo "ERR: search input did not open after clicking Search button" >&2
  exit 1
fi

# Type query and submit
ABX_SERVICE=gcal abx fill --active "$QUERY"
ABX_SERVICE=gcal abx wait 300
ABX_SERVICE=gcal abx press Enter
ABX_SERVICE=gcal abx wait --load networkidle

# Snapshot search results page
SNAP=$(ABX_SERVICE=gcal abx snapshot -i --json)

# Results region — role=region name="Search results"
# Each result may be role=article or role=listitem
# NOTE: .parent.* filter dropped (Pattern F) — accept all article/listitem within snapshot.
# NOTE: name format (title + date + time) is speculative (v0.1.0 unverified).
# v0.1.0: emit only .name (raw string). .date / .time_range / .location do NOT exist on
# standard AT nodes — accessing them always yields empty strings. Per-field extraction
# deferred to v0.2.0 after live-snapshot verification.
RESULT=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="article" or .role=="listitem")
  | "- \(.name // "(unknown)")"
')

if [ -z "$RESULT" ]; then
  # Pattern H: distinguish empty results from UI evolution
  REGION_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="region" and ((.name // "") | contains("Search"))) | .ref' | head -1)
  if [ -z "$REGION_CHECK" ]; then
    echo "ERR: UI changed: 'Search results' region not found after search submission" >&2
    exit 1
  fi
  echo "## GCal search: \"$QUERY\" — 0 matches"
  echo
  echo "(no events matched)"
else
  COUNT=$(echo "$RESULT" | wc -l | tr -d ' ')
  echo "## GCal search: \"$QUERY\" — $COUNT matches"
  echo
  echo "$RESULT"
fi
```

## Failure modes

- Search button absent → UI evolution → exits 1 with `ERR: UI changed`
- Search input did not open after click → silent click failure → exits 1 with `ERR: search input did not open`
- Search results region absent after submission → UI evolution → exits 1 with `ERR: UI changed`
- Results region present but empty → valid empty → outputs `(no events matched)`
- Query matches many events → AT snapshot may be paginated; results are first visible page only (v0.1.0 limitation)
