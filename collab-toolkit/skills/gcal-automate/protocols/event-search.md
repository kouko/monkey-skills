---
name: event-search
purpose: Search Google Calendar for events by title, attendee, or location; return matching results.
---

## Inputs

- `query`: required. Free-text search string (title, attendee name, attendee email, location).
- `--json`: optional.

## Output

Default Markdown:
```
## GCal search: "OKR" — 5 matches

- **Q2 OKR Review** — Mon May 12, 2026 · 10:00–11:00 · Conference Room A
- **OKR Planning** — Wed May 14, 2026 · 14:00–15:30
- ...
```

`--json`: `{ query, events: [{ title, date, time_range, location }] }`.

> **Output spec note**: `date`, `time_range`, `location` are extracted from the search result role+name strings. These fields are speculative (v0.1.0 unverified) — AT snapshot may expose them differently. See `references/ui-patterns.md` AT-schema notes. All use `// ""` fallbacks.

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
RESULT=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="article" or .role=="listitem")
  | "- **\(.name // "(unknown)")** — \(.date // "") \(.time_range // "") \(if (.location // "") != "" then "· \(.location // "")" else "" end)"
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
