---
name: mail-search
purpose: Open Gmail, use the top-bar search combobox with Google operators, and extract matching mail rows (from / subject / snippet / date).
---

## Inputs

- `query`: required. Search string — may include Google operators:
  - `from:sender@example.com` — filter by sender
  - `to:recipient@example.com` — filter by recipient
  - `has:attachment` — only messages with attachments
  - `before:YYYY/MM/DD` or `after:YYYY/MM/DD` — date range
  - `label:labelname` — messages with a given label
  - `in:inbox`, `in:sent`, `in:starred` — folder scoping
  - Free-text terms may be combined with operators
- `--json`: optional.

## Output

Default Markdown (v0.1.0 — raw row cell extraction):
```
## Gmail search: "from:alice has:attachment" — 3 results

- From: alice@example.com | Subject: Q2 Report | May 14, 2026 | Has attachment
- From: alice@example.com | Subject: Budget draft | May 10, 2026 | Has attachment
- From: alice@example.com | Subject: Slides | May 3, 2026 | Has attachment
```

`--json`: `{ query, results: [{ from, subject, snippet, date }] }`.

> **Output spec note**: Mail row cells (`from`, `subject`, `snippet`, `date`) are extracted from `role=row` elements in the search result grid. Cell extraction uses `.cells[] | .name // ""` — this path is speculative (v0.1.0 unverified). v0.1.0 falls back to the full `.name // "(unknown)"` of the row element if `.cells` is absent. See `references/ui-patterns.md` AT-schema notes.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=gmail abx open https://mail.google.com
ABX_SERVICE=gmail abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Gmail in Chrome (shared mode) or run /collab-setup --reauth gmail" >&2
  exit 1
fi

# Find the top-bar search combobox — role=combobox name="Search mail"
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="combobox" and ((.name // "") | contains("Search mail"))) | .ref' | head -1)
if [ -z "$SEARCH_REF" ]; then
  # Fallback: try textbox with similar name
  SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="textbox" and ((.name // "") | test("(?i)search mail"))) | .ref' | head -1)
fi
if [ -z "$SEARCH_REF" ]; then
  echo "ERR: UI changed: search combobox (role=combobox name='Search mail') not found" >&2
  exit 1
fi

ABX_SERVICE=gmail abx click "$SEARCH_REF"
ABX_SERVICE=gmail abx wait 300

# Pattern H: verify search input focused / opened
SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
FOCUSED_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="combobox" and ((.name // "") | contains("Search mail"))) | .ref' | head -1)
if [ -z "$FOCUSED_REF" ]; then
  echo "ERR: search combobox did not respond to click" >&2
  exit 1
fi

# Type query and submit
# NOTE: abx fill may not preserve Google search operators (e.g., from:, @) through Gmail's autocomplete widget
# If operators don't surface expected results, switch to abx type for character-by-character simulation
ABX_SERVICE=gmail abx fill "$FOCUSED_REF" "$QUERY"
ABX_SERVICE=gmail abx wait 300
ABX_SERVICE=gmail abx press Enter
ABX_SERVICE=gmail abx wait --load networkidle

# Snapshot results
SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)

# Extract result rows — role=row in the results grid
# Each row typically has cells: from, subject+snippet, date, attachment indicator
# NOTE: .parent.* dropped (Pattern F) — accept all role=row in snapshot
# NOTE: (.cells // []) guarded with fallback to raw .name if .cells absent
# NOTE: .name access guarded with // "" (Pattern A)
RESULT=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | if (.cells // []) | length > 0
    then
      "- From: \(.cells[0].name // "(unknown)") | Subject: \(.cells[1].name // "(unknown)") | \(.cells[2].name // "(unknown)")"
    else
      "- \(.name // "(unknown)")"
    end
')

if [ -z "$RESULT" ]; then
  # Pattern H: distinguish silent empty from UI evolution
  GRID_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="row" or .role=="rowgroup" or .role=="grid") | .ref' | head -1)
  if [ -z "$GRID_CHECK" ]; then
    echo "ERR: UI changed: mail result grid (role=row/grid) not found after search submission" >&2
    exit 1
  fi
  echo "## Gmail search: \"$QUERY\" — 0 results"
  echo
  echo "(no messages matched)"
else
  COUNT=$(echo "$RESULT" | wc -l | tr -d ' ')
  echo "## Gmail search: \"$QUERY\" — $COUNT results"
  echo
  echo "$RESULT"
fi
```

## Failure modes

- Query missing → validation error
- Login wall detected → auth expiry or session expired
- Search combobox not found → UI evolution → exits 1 with `ERR: UI changed`
- Search combobox unresponsive after click → exits 1 with `ERR: search combobox did not respond to click`
- Result grid absent after query → UI evolution → exits 1 with `ERR: UI changed`
- Grid present but empty → valid empty → outputs `(no messages matched)`
- Many results → AT snapshot covers the first visible page only (v0.1.0 limitation); pagination not implemented
- Google operators misspelled → Gmail returns no results; not distinguishable from valid empty at v0.1.0

## Notes

**Operator preservation caveat (v0.1.0)**: `abx fill` may not preserve Google search operators (`:`, `@`) through Gmail's autocomplete widget — programmatic value-setting can be intercepted and re-encoded. If `from:foo@example.com` queries don't surface expected results during first dogfood, switch this protocol to use `abx type <ref> "$QUERY"` (simulates real keypresses character-by-character) instead of `abx fill`. Document outcome in `references/ui-patterns.md` AT-schema notes.
