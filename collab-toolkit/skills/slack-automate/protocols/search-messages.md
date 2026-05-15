---
name: search-messages
purpose: Full-text search across all Slack channels with optional operators (from / in / before / after / has).
---

## Inputs

- `query`: required. Search string, may include operators.
- `--json`: optional.

## Output

Default Markdown:
```
## Slack search: "OKR" (in: #engineering after: 2026-05-01) — 12 results

**#engineering** · alice · 2026-05-10 14:32
> Q2 OKRs are due next Friday. Let's align in standup.
> [Open thread →](https://kouko-workspace.slack.com/archives/...)

**#engineering** · bob · 2026-05-08 09:15
> ...
```

`--json`: `{ query, total, results: [{ channel, user, timestamp, text, url, has_thread }] }`.

> **Output spec note**: `channel`, `user`, `timestamp`, `text` fields are extracted from the snapshot accessibility tree. Fields not present in the AT snapshot will fall back to `"(unknown)"`. Validated field availability is deferred to v0.2.0 dogfood (see `references/ui-patterns.md` AT-schema notes).

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=slack abx open https://app.slack.com
ABX_SERVICE=slack abx wait --load networkidle

# Open search — role="button" name="Search"
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and .name=="Search") | .ref' | head -1)
[ -z "$SEARCH_REF" ] && { echo "ERR: UI changed: 'Search' button not found"; exit 1; }
ABX_SERVICE=slack abx click "$SEARCH_REF"
ABX_SERVICE=slack abx wait 500

# Type query
ABX_SERVICE=slack abx fill --active "$QUERY"
ABX_SERVICE=slack abx press Enter
ABX_SERVICE=slack abx wait --load networkidle

# Snapshot results — each result is role="listitem" within Search results region
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="listitem")
  | "**\(.channel // "(unknown)")** · \(.user // "(unknown)") · \(.timestamp // "")\n> \(.text // "")\n"
'
```

## Failure modes

- Search button missing → UI evolution
- 0 results for a known-good query → "Auth expiry" check (snapshot for `role=button name=Sign in`)
