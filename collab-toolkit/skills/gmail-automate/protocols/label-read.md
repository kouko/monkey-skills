---
name: label-read
purpose: Given a label name (including nested labels via "/" path), click the label in the Gmail sidebar and list messages with that label.
---

## Inputs

- `label_name`: required. Label display name as it appears in the Gmail sidebar. Supports nested labels with `/` separator (e.g., `Work/Projects`, `Finance/Invoices`). Case-sensitive for `contains()` matching against AT element names.
- `top_n`: optional. Max messages to return. Default: `20`.
- `--json`: optional.

**v0.1.0 nesting limit**: Only single-level nesting supported (`parent/child` like `Work/Projects`). Multi-level nesting (`parent/child/grandchild` like `Finance/Q1/Invoices`) requires iterative parent expansion — the current protocol expands only one level. For grandchild labels in v0.1.0: manually expand the parent label in your Chrome's Gmail sidebar before running the protocol, OR use the leaf label name directly without the path prefix (Gmail's sidebar shows leaf names when parent is expanded).

## Output

Default Markdown (v0.1.0 — row names as raw strings):
```
## Label: Work/Projects — 7 messages

1. alice@example.com — Project kickoff notes — May 14
2. bob@example.com — Timeline update — May 12
3. carol@example.com — Review request — May 10
...
```

`--json`: `{ label_name, messages: [{ from, subject, date }] }`.

> **Output spec note**: Label sidebar entries are `role=link` elements. For nested labels, Gmail renders the parent label as a collapsible item and child labels as nested `role=link` elements. The AT path for nested label links is speculative — v0.1.0 uses `contains($label)` against the full `.name // ""` of each link, which matches both parent and child labels if names overlap. `.cells[n].name` for message row fields are speculative; fallback to full row `.name // "(unknown)"`. See `references/ui-patterns.md` AT-schema notes.

## Procedure

```bash
LABEL="${1:-}"
TOP_N="${2:-20}"

[ -z "$LABEL" ] && { echo "ERR: label_name required"; exit 1; }

ABX_SERVICE=gmail abx open https://mail.google.com
ABX_SERVICE=gmail abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Gmail in Chrome (shared mode) or run /collab-setup --reauth gmail" >&2
  exit 1
fi

# Handle nested label: if "/" present, extract base parent and child
# Gmail sidebar shows nested labels under a collapsible parent section
# PARENT_LABEL = part before first "/" (if any)
# CHILD_LABEL  = full label name (used for final click)
PARENT_LABEL=""
if echo "$LABEL" | grep -q '/'; then
  PARENT_LABEL=$(echo "$LABEL" | cut -d'/' -f1)
fi

# If nested, expand the parent label section first
if [ -n "$PARENT_LABEL" ]; then
  PARENT_REF=$(echo "$SNAP" | jq -r --arg p "$PARENT_LABEL" '
    .elements[]
    | select(
        (.role=="link" or .role=="button" or .role=="treeitem")
        and ((.name // "") | contains($p))
      )
    | .ref
  ' | head -1)

  if [ -n "$PARENT_REF" ]; then
    ABX_SERVICE=gmail abx click "$PARENT_REF"
    ABX_SERVICE=gmail abx wait 500
    # Re-snapshot after expanding parent to get child labels
    SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
  fi
  # If parent not found, proceed to direct label search (may still find nested link)
fi

# Find the label link in the sidebar
# NOTE: .parent.* dropped (Pattern F) — flat snapshot; use contains() on full name
# NOTE: ((.name // "") | contains($label)) guarded against null (Pattern G)
LABEL_REF=$(echo "$SNAP" | jq -r --arg label "$LABEL" '
  .elements[]
  | select(
      .role=="link"
      and ((.name // "") | contains($label))
    )
  | .ref
' | head -1)

if [ -z "$LABEL_REF" ]; then
  # Fallback: try treeitem role (Gmail may use tree navigation for labels)
  LABEL_REF=$(echo "$SNAP" | jq -r --arg label "$LABEL" '
    .elements[]
    | select(
        .role=="treeitem"
        and ((.name // "") | contains($label))
      )
    | .ref
  ' | head -1)
fi

if [ -z "$LABEL_REF" ]; then
  echo "ERR: label '$LABEL' not found in Gmail sidebar" >&2
  echo "Note: label name is case-sensitive. Nested labels must include full path (e.g. 'Work/Projects')." >&2
  exit 1
fi

# Click the label
ABX_SERVICE=gmail abx click "$LABEL_REF"
ABX_SERVICE=gmail abx wait --load networkidle
SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)

# Pattern H: verify label view loaded (expect rows or a heading)
HEADING_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="heading") | .name // ""' | head -1)
ROW_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="row") | .ref' | head -1)

if [ -z "$ROW_CHECK" ] && [ -z "$HEADING_CHECK" ]; then
  # Check for any navigation/tree structure (label sidebar still present)
  TREE_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="link" or .role=="treeitem") | .ref' | head -1)
  if [ -z "$TREE_CHECK" ]; then
    echo "ERR: UI changed: Gmail label view structure not found after clicking label" >&2
    exit 1
  fi
  echo "## Label: $LABEL"
  echo "(no messages with this label, or label view did not load)"
  exit 0
fi

# Extract rows
# NOTE: (.cells // []) guarded; fallback to .name // "(unknown)" (Patterns A + G)
ROWS=$(echo "$SNAP" | jq -r --argjson n "$TOP_N" '
  [
    .elements[]
    | select(.role=="row")
  ]
  | .[0:$n]
  | to_entries[]
  | "\(.key + 1). \(
      if (.value.cells // []) | length > 0
      then "\(.value.cells[0].name // "(unknown)") — \(.value.cells[1].name // "(unknown)") — \(.value.cells[2].name // "")"
      else (.value.name // "(unknown)")
      end
    )"
')

TOTAL=$(echo "$SNAP" | jq -r '[.elements[] | select(.role=="row")] | length')

echo "## Label: $LABEL — $TOTAL messages (showing up to $TOP_N)"
echo
if [ -z "$ROWS" ]; then
  echo "(no messages with this label)"
else
  echo "$ROWS"
fi
```

## Notes

- Nested labels in Gmail are shown in the left sidebar under their parent label section. The parent section must be expanded before the child label link is visible in the AT snapshot. This protocol attempts parent expansion for nested label paths (containing `/`).
- Gmail stores labels as `LABEL_<id>` internally; display names in the sidebar are what users see and what this protocol matches against.
- Label names are case-sensitive for `contains()` matching. If the label is named `Finance` but you pass `finance`, the match will fail.
- The sidebar may scroll to show all labels only if the user has many labels. Labels below the visible fold may not appear in the AT snapshot. If a label is not found, try clicking "More labels" or "Show all labels" in the sidebar first. This is not automated in v0.1.0.
- **v0.1.0 nesting limit**: Only single-level nesting supported (`parent/child` like `Work/Projects`). Multi-level nesting (`parent/child/grandchild` like `Finance/Q1/Invoices`) requires iterative parent expansion — the current protocol expands only one level. For grandchild labels in v0.1.0: manually expand the parent label in your Chrome's Gmail sidebar before running the protocol, OR use the leaf label name directly without the path prefix (Gmail's sidebar shows leaf names when parent is expanded).

## Failure modes

- Label name missing → validation error
- Login wall detected → auth expiry
- Parent label expand click fails silently → child label may still be found if already visible
- Label not found after expand attempt → label does not exist, name mismatch, or label below visible fold → exits 1 with error
- Label click does not navigate → rare; wait + retry manually
- No rows after navigation + no heading → either valid empty label or UI changed → exits 0 with message
- "Show all labels" / "More labels" not clicked → labels below fold not accessible in v0.1.0
