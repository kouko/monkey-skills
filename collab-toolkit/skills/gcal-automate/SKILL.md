---
name: gcal-automate
description: Google Calendar automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: agenda-view for today/week/range, event-search by title/attendee/location, find-free-slots given duration and business-hours window, shared-calendar-read for colleagues' shared calendars. Read-only v0.1.0 — search and fetch only, no writes. Google カレンダー自動化、予定読取、ヘッドレス。Google 行事曆自動化・行程讀取・無頭背景。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# gcal-automate

Read-only browser automation for Google Calendar. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed and on PATH
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- Google Calendar is verified logged-in via your daily Chrome (shared mode) or dedicated profile

If any protocol fails with "config not found": run `/collab-setup`.
If any protocol fails with "login wall detected" in title: per setup mode, either log into Google Calendar in your daily Chrome (shared mode) or run `/collab-setup --reauth gcal` (dedicated mode).

## Hero protocols

- `protocols/agenda-view.md` — open calendar.google.com, switch view (Day/Week/Custom range), snapshot event grid, extract events grouped by date
- `protocols/event-search.md` — top-bar search by title, attendee, or location; parse search results region
- `protocols/find-free-slots.md` — compute open slots given duration, date range, and business-hours window
- `protocols/shared-calendar-read.md` — enable a colleague's shared calendar from "Other calendars" sidebar, read their events

## Selector convention

See `references/ui-patterns.md`. All protocols MUST:
1. `ABX_SERVICE=gcal abx snapshot -i --json` → save to variable or /tmp
2. `jq '.elements[] | select(.role==X and .name==Y) | .ref' | head -1`
3. Empty result → exit with "UI changed: <role>+<name> not found"

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default: human-readable Markdown summary.
`--json` (passthrough to abx): structured JSON for downstream chaining.
