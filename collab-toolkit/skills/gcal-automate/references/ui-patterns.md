# Google Calendar UI Patterns — Semantic Selector Reference

> **Source of truth for semantic selectors used in this skill's protocols.**
> When Google Calendar ships a UI change that breaks a protocol, update this file first,
> then re-derive the protocol's jq filter.

## Refresh playbook

When a protocol fails with "UI changed: ...":

1. Run `ABX_SERVICE=gcal abx snapshot -i --json > /tmp/gcal-snap.json` against `calendar.google.com`
2. Inspect `/tmp/gcal-snap.json` for elements near the failing area
3. Identify the new role+name combination
4. Update the entry below
5. Update the failing protocol's jq filter

## Top bar

| Element | role | name | Notes |
|---|---|---|---|
| Search button | `button` | `Search` | Opens search input overlay |
| Settings/menu button | `button` | `Settings menu` | Top-right gear icon |
| Create event button | `button` | `Create` or `New event` | Top-left; write-only, not used in v0.1.0 |

## View switcher

| Element | role | name | Notes |
|---|---|---|---|
| Day view | `button` | `Day` | Switches to single-day view |
| Week view | `button` | `Week` | Switches to 7-day week view |
| Month view | `button` | `Month` | Switches to month grid |
| Year view | `button` | `Year` | Switches to year overview |
| Schedule / Agenda view | `button` | `Schedule` | Compact agenda list view |

## Event grid

| Element | role | name | Notes |
|---|---|---|---|
| Date column header | `columnheader` | `<Day> <Date>` e.g. `Mon May 12` | One per visible day — used by agenda-view |
| Event element | `button` | `<time>, <title>, <duration>` (locale-dependent format) | e.g. `"10:00 AM, Stand-up, 30 minutes, My Calendar"` **— unverified, see "AT-schema notes"** |
| All-day event | `button` | `<title>` (no time prefix) | Appears at top of column — parsed separately |
| Time column cell | `cell` or `rowheader` | `<HH:MM>` | Hour labels on left edge |

## Search overlay / results

| Element | role | name | Notes |
|---|---|---|---|
| Search input | `textbox` or `combobox` | `Search` or `(empty)` | Appears after clicking Search button |
| Search results region | `region` | `Search results` | Container after query submission **— unverified, see "AT-schema notes"** |
| Result item | `article` or `listitem` | `<title> <date> <time>` | Each matched event **— unverified, see "AT-schema notes"** |

## Sidebar

| Element | role | name | Notes |
|---|---|---|---|
| My calendars list | `list` | `My calendars` | Left sidebar section |
| Calendar entry | `checkbox` | `<calendar name>` | Toggle on/off; `.checked` = enabled state **— unverified, see "AT-schema notes"** |
| Other calendars list | `list` | `Other calendars` | Left sidebar section for shared/subscribed — used by shared-calendar-read |
| Other calendar entry | `checkbox` | `<colleague/calendar name>` | Shared calendar toggle **— unverified, see "AT-schema notes"** |
| Add other calendars button | `button` | `Add other calendars` | Opens subscription dialog |

## Mini-calendar (date picker)

| Element | role | name | Notes |
|---|---|---|---|
| Previous month | `button` | `Previous` | Navigate mini-cal backward |
| Next month | `button` | `Next` | Navigate mini-cal forward |
| Day cell | `button` | `<day number> <month>` | Click to jump to that day |

## AT-schema notes (v0.1.0 unverified)

Some field paths used in the protocols above are educated guesses about agent-browser's AT-snapshot output. They have NOT been verified against a live snapshot yet (v0.1.0 ships with defensive `// ""` / `// "(unknown)"` fallbacks). Validate during first dogfood run:

| Field path | Used by | Status |
|---|---|---|
| `.elements[] \| select(.role=="button" and ...) \| .name` (event time+title format) | agenda-view, find-free-slots, shared-calendar-read | ❓ unverified — GCal event button name format is locale-dependent; may differ by language/region |
| `.elements[] \| select(.role=="columnheader") \| .name` (date label format) | agenda-view, find-free-slots | ❓ unverified — date format may vary (`"Mon May 12"` vs `"5/12"` vs aria-label-only) |
| `.elements[] \| select(.role=="region" and .name=="Search results")` | event-search | ❓ unverified — GCal search results container may use different region name or no region wrapper |
| `.elements[] \| select(.role=="article" or .role=="listitem")` (search results) | event-search | ❓ unverified — result items may be `role="row"` or other role |
| `.elements[] \| select(.role=="list" and .name=="Other calendars")` | shared-calendar-read | ❓ unverified — sidebar list role/name may differ or may be a `navigation`/`region` |
| `.elements[] \| select(.role=="checkbox" ...) \| .checked` | shared-calendar-read | ❓ unverified — `.checked` may not be a direct AT property; may require `.attributes.aria-checked` or `.state.checked` |
| `.date` / `.time_range` / `.location` on search result elements | event-search | ❓ unverified — these are not standard AT properties; likely absent; parsed from `.name // ""` string instead |
| `.parent.name` filter (original plan, e.g. filter Other-calendar entries by parent list) | shared-calendar-read | ❌ DROPPED — agent-browser flat snapshot does not expose `.parent`. Filter uses permissive `select(.role=="checkbox" and ((.name // "") \| contains($col)))`. Precision trade-off accepted until live-snapshot verification. |
| `.parent.role` filter (event elements scoped to date column) | agenda-view, find-free-slots | ❌ DROPPED — same reason. Events extracted by time-prefix regex on `.name // ""` instead. |

Refresh playbook for these: run `ABX_SERVICE=gcal abx snapshot -i --json > /tmp/gcal-snap.json`, inspect the actual schema, update the jq filter, and remove the corresponding row from this table.
