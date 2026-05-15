# Asana UI Patterns — Semantic Selector Reference

> **Source of truth for semantic selectors used in this skill's protocols.**
> When Asana ships a UI change that breaks a protocol, update this file first,
> then re-derive the protocol's jq filter.

## Refresh playbook

When a protocol fails with "UI changed: ...":

1. Run `ABX_SERVICE=asana abx snapshot -i --json > /tmp/asana-snap.json` against the affected page
2. Inspect `/tmp/asana-snap.json` for elements near the failing area
3. Identify the new role+name combination
4. Update the entry below
5. Update the failing protocol's jq filter

## Navigation (sidebar / top bar)

| Element | role | name | Notes |
|---|---|---|---|
| Sidebar — My Tasks link | `link` | `My tasks` | Persistent across pages |
| Sidebar — Projects link | `link` | `Projects` | Persistent across pages |
| Sidebar — Inbox link | `link` | `Inbox` | Persistent across pages |
| Top bar — Search button | `button` | `Search` | Opens search modal/input |
| Top bar — User menu | `button` | aria-label contains user name | Per-user variation |

## Task lists (grid views)

| Element | role | name | Notes |
|---|---|---|---|
| Grid container | `grid` | aria-label `Tasks` or `My tasks` | Container for all rows |
| Task row | `row` | (varies — task title via child link) | Each task is a row |
| Task title (within row) | `link` | (task title string) | First link child in row |
| Task completion checkbox | `checkbox` | `Mark complete` | Toggles completion |
| Task due date | `button` | starts with `Due date,` | aria-label includes current value |

## Task detail page

| Element | role | name | Notes |
|---|---|---|---|
| Page title | `heading` level=1 | (task title) | The H1 of the task page |
| Assignee | `button` | starts with `Assignee,` | aria-label includes current value |
| Description region | `region` | `Description` | Contains rich text |
| Subtasks list | `list` | `Subtasks` | Children are listitems |
| Activity comments | `article` | (none — has `.author` and `.text` props **— unverified, see "AT-schema notes"**) | Each comment is an article |
| Attachments list | `list` | `Attachments` | Children are listitems |

## Search results

| Element | role | name | Notes |
|---|---|---|---|
| Result row | `row` | (result title) | Within result groups |
| Result group header | `heading` level=2 | one of `Tasks` / `Projects` / `Portfolios` | Section dividers |

## AT-schema notes (v0.1.0 unverified)

Some field paths used in the protocols above are educated guesses about agent-browser's AT-snapshot output. They have NOT been verified against a live snapshot yet (v0.1.0 ships with defensive `// "(unknown)"` fallbacks for these). Validate during first dogfood run:

| Field path | Used by | Status |
|---|---|---|
| `.elements[] \| select(.role=="article") \| .author` | task-detail comments | ❓ unverified — may be nested in child element |
| `.elements[] \| select(.role=="article") \| .timestamp` | task-detail comments | ❓ unverified — may be a child `time` element |
| `.elements[] \| select(.role=="listitem") \| .checked` | task-detail subtasks | ❓ unverified — may live under `.attributes."aria-checked"` |
| `.elements[] \| select(.role=="row") \| .children[]?` | task-list tasks | ❓ assumes snapshot is nested tree; if flat list w/ ref-cross-references, fix to use `.elements[]` with parent filter |

Refresh playbook for these: run `ABX_SERVICE=asana abx snapshot -i --json > /tmp/asana-snap.json`, inspect the actual schema, update the jq filter, and remove the corresponding row from this table.
