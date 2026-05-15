---
name: page-backlinks
purpose: Find all pages that link to a target Notion page.
---

## Inputs

- `page_url`: required.
- `--json`: optional.

## Output

Default Markdown: list of linking pages with their names and URLs.

`--json`: array of `{ title, href }`.

> **Output spec note**: `path` and `last_updated` fields from the full spec are not reliably extractable from the AT snapshot in v0.1.0. Output is narrowed to `title` + `href` (from `.href // ""`). Remaining fields deferred to v0.2.0 after live-snapshot verification.

## Procedure

```bash
URL="$1"
[ -z "$URL" ] && { echo "ERR: page_url required"; exit 1; }

ABX_SERVICE=notion abx open "$URL"
ABX_SERVICE=notion abx wait --load networkidle

# Backlinks panel may be visible directly — find the Backlinks region
SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
BACKLINKS_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="region" and .name=="Backlinks") | .ref' | head -1)

if [ -z "$BACKLINKS_REF" ]; then
  # Fallback: open page menu → "Show backlinks"
  MENU_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name=="More options" or .name=="...")) | .ref' | head -1)
  [ -z "$MENU_REF" ] && { echo "ERR: page menu not found"; exit 1; }
  ABX_SERVICE=notion abx click "$MENU_REF"
  ABX_SERVICE=notion abx wait 500
  # Find "Show backlinks" menuitem
  SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
  SHOW_BL=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="menuitem" and .name=="Show backlinks") | .ref' | head -1)
  [ -z "$SHOW_BL" ] && { echo "ERR: 'Show backlinks' menu item not found"; exit 1; }
  ABX_SERVICE=notion abx click "$SHOW_BL"
  ABX_SERVICE=notion abx wait 500
  SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
fi

# Each backlink is role="link" within Backlinks region
# .children[]? and .href are speculative (see ui-patterns.md AT-schema notes)
RESULT=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="region" and .name=="Backlinks")
  | .children[]?
  | select(.role=="link")
  | "- \(.name // "(unknown)") — \(.href // "")"
')

if [ -z "$RESULT" ]; then
  echo "No pages link to this page."
else
  echo "$RESULT"
fi
```

## Failure modes

- Page has no backlinks → valid empty (outputs `No pages link to this page.`)
- Menu not found → UI evolution
- `Show backlinks` item absent → Notion version does not support backlinks via this menu path
