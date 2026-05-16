---
name: search-workspace
purpose: Full-text search across pages, databases, and content in the Notion workspace.
---

## Inputs

- `query`: required.
- `filter_type`: optional. `pages` / `databases` / `all`. Default: `all`.
- `--json`: optional.

## Output

Default Markdown:
```
## Notion search: "OKR" — 18 matches

### Pages (12)
- **Q2 OKRs** — Updated 2 days ago by alice — /OKRs/Q2-OKRs-...
- ...

### Databases (6)
- **OKR Tracker** — Owner: alice — /OKR-Tracker-...
```

`--json`: `{ query, pages: [...], databases: [...] }`.

> **Output spec note**: `path` field is extracted from the AT snapshot. This field is speculative (v0.1.0 unverified) — see `references/ui-patterns.md` AT-schema notes. Falls back to `""`.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=notion abx open https://www.notion.so
ABX_SERVICE=notion abx wait --load networkidle

# Open search — Cmd+P or top bar button
SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name=="Search" or .name=="Quick Find")) | .ref' | head -1)
[ -z "$SEARCH_REF" ] && { echo "ERR: UI changed: 'Search' / 'Quick Find' button not found"; exit 1; }
ABX_SERVICE=notion abx click "$SEARCH_REF"
ABX_SERVICE=notion abx wait 500

# Type query
ABX_SERVICE=notion abx fill --active "$QUERY"
ABX_SERVICE=notion abx wait 1000

# Snapshot results — each result is role="listitem"
# NOTE: .parent.name filter dropped (Pattern F) — agent-browser flat snapshot has no .parent.
# Accept all listitems; precision to be improved after live-snapshot verification (see ui-patterns.md).
SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="listitem")
  | "- **\(.name // "(unknown)")** — \(.path // "")"
'
```

## Failure modes

- Search button not found → UI evolution
- Empty results → valid empty (no match)
