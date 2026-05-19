---
name: agenda-view
purpose: Fetch events for today / this week / arbitrary date range.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown agenda of calendar events for the current user across a date range (today / this week / custom).

## Input

- `range`: optional. `today` / `week` / `custom`. Default `today`.
- `start_date` / `end_date`: required when `range = custom`. ISO date (`YYYY-MM-DD`).
- `calendar_id`: optional. Defaults to primary calendar.
- `timezone`: optional. IANA tz (e.g., `Asia/Taipei`). Default: user's primary calendar timezone.

Mapping to gws params:
- `--time-min` / `--time-max`: ISO-8601 timestamps with offset (e.g., `2026-05-19T00:00:00+08:00`). Compute from `range`:
  - `today` → start = local midnight today, end = local midnight tomorrow.
  - `week` → start = local Monday 00:00, end = local Monday+7 00:00.
  - `custom` → from `start_date` / `end_date`.
- `--calendar` (optional): defaults to `primary`.
- `--single-events true` (recommended): expand recurring events into individual instances.

## Steps

1. Resolve `--time-min` / `--time-max` from `range` inputs (compute in the user's timezone).

2. Call:
   ```bash
   gws calendar events list \
     --time-min 2026-05-19T00:00:00+08:00 \
     --time-max 2026-05-26T00:00:00+08:00 \
     --single-events true
   ```

3. Parse the JSON array. Per event extract:
   - `start.dateTime` / `start.date` (all-day if `date`-only)
   - `end.dateTime` / `end.date`
   - `summary` (title)
   - `location` (optional)

4. Group events by date, sort ascending by start time. All-day events appear at the top of their date group.

5. Format Markdown:
   ```
   ## Agenda (<date range>)

   ### <YYYY-MM-DD>
   - <HH:MM>–<HH:MM>: <title>  [@ <location>]
   - (all day): <title>
   ```

## Common failure modes

- **Empty array** → valid empty result. Emit `No events in <date range>.`
- **Recurring events not expanded** → ensure `--single-events true` is passed (otherwise master events show without per-instance times).
- **Timezone mismatch** → see `references/failure-modes.md` § Timezone handling.
- **Auth error** → see `references/failure-modes.md` § Shared OAuth with gmail-automate.

## Examples

`range = week` → events for this week as grouped Markdown.
