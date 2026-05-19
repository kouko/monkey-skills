---
name: event-search
purpose: Search calendar events by title / attendee / location keyword.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown list of events whose title, description, location, or attendee matches a free-text query.

## Input

- `query`: required. Free-text query. Matches title / description / location / attendee per Google Calendar API `q` parameter semantics.
- `time_min` / `time_max`: optional ISO-8601 bounds. Default: now → now+90d (Calendar API ignores `q` against the entire calendar history unless bounded).
- `calendar_id`: optional. Defaults to primary.
- `--json`: optional.

Mapping to gws params:
- `--query`: pass `query` verbatim.
- `--time-min` / `--time-max` (optional): same as agenda-view.
- `--single-events true` (recommended): so recurring matches show per-instance.

## Steps

1. Call:
   ```bash
   gws calendar events search \
     --query "OKR review" \
     --time-min 2026-05-19T00:00:00+08:00 \
     --time-max 2026-08-17T00:00:00+08:00 \
     --single-events true
   ```

2. Parse the JSON array. Per event extract:
   - `start.dateTime` / `start.date`
   - `summary`
   - `location` (optional)

3. Sort ascending by start time. Format Markdown:
   ```
   ## GCal search: "<query>" — N results

   - <YYYY-MM-DD> <HH:MM>: <title>  [@ <location>]
   ```

## Common failure modes

- **Empty array** → valid empty result. Emit `No events matching "<query>".`
- **Unbounded query returns nothing** → Calendar API may default to a narrow window; explicitly pass `--time-min` / `--time-max` to widen.
- **Operator-style query (`from:`, `before:`)** → Calendar `q` does **not** support Gmail-style operators. Use `--time-min` / `--time-max` flags instead.
- **Auth error** → see `references/failure-modes.md` § Shared OAuth with gmail-automate.

## Notes

- Search covers the current account's primary + visible secondary calendars by default (subject to gws subcommand behavior; verify per `failure-modes.md` § Subcommand verification).
- For attendee-specific filtering, append the attendee email to `query` — Calendar API matches it against the attendee list field.

## Examples

`query = "OKR review"` → matching events as Markdown list.
