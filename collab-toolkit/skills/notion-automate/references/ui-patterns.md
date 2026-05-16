# Notion UI Patterns — Semantic Selector Reference

> **Source of truth for semantic selectors used in this skill's protocols.**
> When Notion ships a UI change that breaks a protocol, update this file first,
> then re-derive the protocol's jq filter.

## Refresh playbook

When a protocol fails with "UI changed: ...":

1. Run `ABX_SERVICE=notion abx snapshot -i --json > /tmp/notion-snap.json` against the affected page
2. Inspect `/tmp/notion-snap.json` for elements near the failing area
3. Identify the new role+name combination
4. Update the entry below
5. Update the failing protocol's jq filter

## Navigation

| Element | role | name | Notes |
|---|---|---|---|
| Sidebar workspace | `region` | `Sidebar` | Container |
| Sidebar page item | `treeitem` | (page name) | |
| Quick Find / Search | `button` | `Search` or `Quick Find` | Top bar; opens via Cmd+P |

## Page content

| Element | role | name | Notes |
|---|---|---|---|
| Page title | `heading` level=1 | (page title) | |
| Page content region | `region` | `Page content` | Container — used by page-fetch |
| Block: heading | `heading` (any level) | (text) | |
| Block: paragraph | `paragraph` | (text) | |
| Block: list item | `listitem` | (text) | |
| Block: callout | `callout` | (text) | |
| Block: toggle | `toggle` | (toggle title) | |

## Database / table

| Element | role | name | Notes |
|---|---|---|---|
| Grid container | `grid` | (database name) | |
| Row | `row` | (none — properties in `.cells` **— unverified, see "AT-schema notes"**) | Each row — used by database-query |
| Column header | `columnheader` | (property name) | |

## Backlinks

| Element | role | name | Notes |
|---|---|---|---|
| Backlinks region | `region` | `Backlinks` | Shown bottom of page (toggle in page settings) |
| Backlink entry | `link` | (linking page name) | `.href` = linking page URL **— unverified, see "AT-schema notes"** |
| Page menu button | `button` | `More options` or `...` | Used by page-backlinks fallback path |
| Show backlinks item | `menuitem` | `Show backlinks` | Opens backlinks panel |

## Search results

| Element | role | name | Notes |
|---|---|---|---|
| Result item | `listitem` | (page/database name) | Used by search-workspace |

## AT-schema notes (v0.1.0 unverified)

Some field paths used in the protocols above are educated guesses about agent-browser's AT-snapshot output. They have NOT been verified against a live snapshot yet (v0.1.0 ships with defensive `// ""` / `// "(unknown)"` fallbacks). Validate during first dogfood run:

| Field path | Used by | Status |
|---|---|---|
| `.elements[] \| select(.role=="listitem") \| .path` | search-workspace | ❓ unverified — page path may be nested in a child element |
| `.elements[] \| select(.role=="region" and .name=="Page content") \| .children[]?` | page-fetch | ❓ unverified — snapshot may be flat rather than nested; if flat, `.children[]?` returns nothing |
| `.elements[] \| select(.role=="paragraph") \| .text` | page-fetch | ❓ unverified — body text may be a child `textnode` or `.name` instead |
| `.elements[] \| select(.role=="callout") \| .text` | page-fetch | ❓ unverified — same concern as `.paragraph.text` |
| `.elements[] \| select(.role=="listitem") \| .text` | page-fetch (block listitem) | ❓ unverified — may be `.name` or a child element |
| `.elements[] \| select(.role=="row") \| .cells[]?` | database-query | ❓ unverified — cells array may not exist; individual properties may be child `gridcell` elements instead |
| `.elements[] \| select(.role=="row") \| .cells[]? \| .text` | database-query | ❓ unverified — cell text may be `.name` or nested |
| `.elements[] \| select(.role=="link") \| .href` | page-backlinks | ❓ unverified — href may not be a direct AT property; may require `.attributes.href` or child element |
| `.parent.name` filter (search-workspace original plan) | search-workspace | ❌ DROPPED — agent-browser flat snapshot does not expose `.parent`. Filter `select(.role=="listitem" and (.parent.name // "" \| startswith("Search results")))` replaced with permissive `select(.role=="listitem")`. Precision trade-off accepted until live-snapshot verification. |
| `.parent.role` filter (database-query original plan) | database-query | ❌ DROPPED — same reason as above. Filter `select(.role=="row" and .parent.role=="grid")` replaced with `select(.role=="row")`. Precision trade-off accepted until live-snapshot verification. |

Refresh playbook for these: run `ABX_SERVICE=notion abx snapshot -i --json > /tmp/notion-snap.json`, inspect the actual schema, update the jq filter, and remove the corresponding row from this table.
