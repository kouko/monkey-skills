---
name: find-free-slots
purpose: Find open time slots given duration + business-hours window. Agent-side computation over gws events list output.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown list of free time slots ≥ `duration_minutes` within a business-hours window across a date range. **Agent-side computation pattern**: `gws` returns the event list; the agent (Claude) computes the inverse to derive free intervals.

## Input

- `duration_minutes`: required. Minimum slot length.
- `start_date` / `end_date`: required. ISO date.
- `business_hours_start` / `business_hours_end`: optional 24h `HH:MM`. Default `09:00` / `18:00`.
- `timezone`: optional. IANA tz. Default user's primary calendar tz.
- `calendar_id`: optional. Defaults to primary. May accept comma-separated ids to merge busy intervals across multiple calendars.

## Computation pattern

This protocol is **CLI-fetch + agent-compute**:

1. `gws calendar events list` returns busy intervals (one event = one busy interval).
2. The agent inverts: for each date in range, compute gaps inside `[business_hours_start, business_hours_end]` between consecutive busy intervals.
3. Filter gaps where `gap_duration >= duration_minutes`.

The agent does NOT call a `freeBusy`-style endpoint here — it derives free slots from the event list. (If gws exposes a dedicated free-busy subcommand later, this protocol can be replaced with a single call.)

## Steps

1. Compute `--time-min` / `--time-max` ISO timestamps from `start_date` 00:00 → `end_date` 23:59 in the user's timezone.

2. Call:
   ```bash
   gws calendar events list \
     --time-min 2026-05-18T00:00:00+08:00 \
     --time-max 2026-05-22T23:59:59+08:00 \
     --single-events true
   ```

3. Parse the JSON array. Build per-date `busy_intervals[date] = [(start_dt, end_dt), ...]`:
   - **Skip all-day events** (they typically don't block working hours).
   - For events spanning midnight, split across dates.

4. For each date in `[start_date, end_date]`:
   - Clip busy intervals to `[business_hours_start, business_hours_end]`.
   - Sort by start time, merge overlapping intervals.
   - Compute gaps: business_hours_start → first busy start; between consecutive busys; last busy end → business_hours_end.
   - Keep gaps where `(gap_end - gap_start) >= duration_minutes`.

5. Format Markdown:
   ```
   ## Free slots (<duration> min, business hours <start>–<end>, <date range>)

   - <YYYY-MM-DD>: <HH:MM>–<HH:MM> (<duration> min)
   ```

## Common failure modes

- **No events in range** → entire business window per date is free; emit one slot per date spanning the full window.
- **Recurring events not expanded** → ensure `--single-events true` is passed.
- **Timezone confusion** → all comparisons must occur in the same tz; convert UTC `dateTime` values to the user's tz before clipping to business hours. See `references/failure-modes.md` § Timezone handling.
- **Multi-calendar busy merge** → if `calendar_id` is comma-separated, run one `gws calendar events list` per id and merge busy intervals before inversion.

## Notes

- All-day events are excluded by default (they typically don't block working hours). To treat them as busy, set an explicit override.
- The agent-side computation is intentionally simple — if gws later ships a `gws calendar freebusy` subcommand, prefer that over agent-side inversion.

## Examples

`duration_minutes = 30, start_date = 2026-05-18, end_date = 2026-05-22` → free 30-min slots within 09:00–18:00 each day.
