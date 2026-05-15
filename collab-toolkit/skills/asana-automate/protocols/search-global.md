---
name: search-global
purpose: Full-text search across tasks, projects, and portfolios with optional filters.
---

## Inputs

- `query`: required. Search string.
- `filter_type`: optional. One of `tasks` / `projects` / `portfolios` / `all`. Default: `all`.
- `--json`: optional.

## Output

Default Markdown groups results by type with relevance order:
```
## Search results for "OKR" (24 matches)

### Tasks (15)
- Q2 OKR planning — Project: Engineering — kouko
- ...

### Projects (3)
- OKR Tracker — Owner: alice
- ...

### Portfolios (1)
- Company OKRs Q2 2026 — Owner: ceo
```

`--json`: `{ query, total, tasks: [...], projects: [...], portfolios: [...] }`.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=asana abx open https://app.asana.com/0/inbox
ABX_SERVICE=asana abx wait --load networkidle

# Find Search button — role="button" name="Search"
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and .name=="Search") | .ref' | head -1)
[ -z "$SEARCH_REF" ] && { echo "ERR: UI changed: 'Search' button not found"; exit 1; }
ABX_SERVICE=asana abx click "$SEARCH_REF"
ABX_SERVICE=asana abx wait 500

# Type query into the active search input
ABX_SERVICE=asana abx fill --active "$QUERY"
ABX_SERVICE=asana abx press Enter
ABX_SERVICE=asana abx wait --load networkidle

# Snapshot results page
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)

# Results have role="row" within result groups
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | "- \(.name // "(untitled)")"
'
```

## Failure modes

- "Search" button not found → UI evolution
- No results → valid empty result
