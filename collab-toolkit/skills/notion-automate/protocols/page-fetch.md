---
name: page-fetch
purpose: Fetch a Notion page's full content including embedded databases, callouts, toggles, and metadata.
---

## Inputs

- `page_url`: required. Notion page URL.
- `--json`: optional.
- `expand_toggles`: optional bool (default true).

## Output

Default Markdown: full page rendered as Markdown (headings, paragraphs, lists, callouts, embedded database row summaries).

`--json`: structured `{ title, blocks: [...] }`.

> **Output spec note**: `properties` and `embedded_dbs` fields are not reliably extractable from the AT snapshot in v0.1.0. Output is narrowed to `title` + `blocks` until live-snapshot verification confirms additional fields (v0.2.0 deferred).

## Procedure

```bash
URL="$1"
[ -z "$URL" ] && { echo "ERR: page_url required"; exit 1; }

ABX_SERVICE=notion abx open "$URL"
ABX_SERVICE=notion abx wait --load networkidle
SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)

# Page title — role="heading" level=1 within main content
TITLE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="heading" and .level==1) | .name // "(unknown)"' | head -1)
echo "# $TITLE"
echo

# Iterate blocks under main content region
# .children[]? and .text / .name on children are speculative (see ui-patterns.md AT-schema notes)
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="region" and .name=="Page content")
  | .children[]?
  | (
    if .role == "heading" then "\n## \(.name // "")"
    elif .role == "paragraph" then (.text // .name // "")
    elif .role == "listitem" then "- \(.text // .name // "")"
    elif .role == "callout" then "> 💡 \(.text // .name // "")"
    elif .role == "toggle" then "▶ \(.name // "")"
    else (.name // .text // "")
    end
  )
'
```

## Failure modes

- Page not found (404 title) → invalid URL
- Page private / no access → message about permissions
- `Page content` region absent → UI evolution (run snapshot refresh playbook in `references/ui-patterns.md`)
