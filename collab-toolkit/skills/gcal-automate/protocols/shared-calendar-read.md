---
name: shared-calendar-read
purpose: Read events from a colleague's shared calendar.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown agenda for a subscribed (shared) calendar — e.g., a colleague's calendar that the current user has added to their account.

## Input

- `calendar_name`: required. Display name OR calendar id. If a display name is supplied, the protocol resolves it to a calendar id via `gws calendar list`.
- `range`: optional. `today` / `week` / `custom`. Default `today`.
- `start_date` / `end_date`: required when `range = custom`.
- `timezone`: optional.

## Steps

1. **Enumerate subscribed calendars** to resolve `calendar_name` → `calendar_id`:
   ```bash
   gws calendar list
   ```
   Returns a JSON array of `{ id, summary, accessRole, ... }`. Find the entry where `summary` (or `summaryOverride`) matches `calendar_name`. If `calendar_name` already looks like an id (contains `@`), skip resolution.

2. Compute `--time-min` / `--time-max` from `range` inputs (same logic as `agenda-view`).

3. **List events scoped to that calendar id**:
   ```bash
   gws calendar events list \
     --calendar alice@example.com \
     --time-min 2026-05-19T00:00:00+08:00 \
     --time-max 2026-05-26T00:00:00+08:00 \
     --single-events true
   ```

4. Parse the JSON array. Per event extract `start` / `end` / `summary` / `location`.

5. Group by date, sort ascending. Format Markdown:
   ```
   ## <calendar_name> (<date range>)

   ### <YYYY-MM-DD>
   - <HH:MM>–<HH:MM>: <title>  [@ <location>]
   ```

## Common failure modes

- **`calendar_name` not found in `gws calendar list`** → the user hasn't subscribed to it. Instruct: in calendar.google.com, add it via "Other calendars" → "Subscribe to calendar".
- **`accessRole: freeBusyReader`** → only busy-blocks visible; event titles return as `"Busy"` and `location` is null. Emit slots as `(busy)` with no title.
- **Empty array** → valid empty result. Emit `No events in <date range>.`
- **Auth error** → see `references/failure-modes.md` § Shared OAuth with gmail-automate.

## Notes

- The `accessRole` field on each `gws calendar list` entry indicates privacy:
  - `owner` / `writer` / `reader` — full event details visible.
  - `freeBusyReader` — only busy blocks visible.
- Calendar id is stable (typically the owner's email); cache resolved ids across invocations to skip step 1.

## Examples

`calendar_name = "Alice Chen", range = week` → Alice's events this week as grouped Markdown.
