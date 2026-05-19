---
name: gcal-automate
description: Google Calendar read access via Google Workspace CLI (gws). Read-only v0.2.0 — agenda-view / event-search / find-free-slots / shared-calendar-read via gws calendar subcommands. Shares OAuth with gmail-automate. GCal CLI・公式 Workspace・OAuth 共有。GCal CLI・官方 Workspace・共用 OAuth。
allowed-tools: Bash(gws:*)
---

# gcal-automate

Read-only Google Calendar access via the Google Workspace CLI (`gws`). Subcommand output is structured JSON — no UI scraping, no locale tables, no browser daemon.

## Prerequisites

One-time setup:

1. Run `/collab-setup` and accept the gws row (records intent + verifies the `gws` binary is on PATH and `GOOGLE_CLOUD_PROJECT` is set).
2. Run `gws auth` once — OAuth grant covers Gmail + Calendar + Drive scopes in a single browser flow. **This same grant powers `gmail-automate`** — re-auth here re-auths there too.

If a protocol fails with an auth error, re-run `gws auth` to refresh the OAuth grant.

## Hero protocols

- `protocols/agenda-view.md` — events for today / this week / arbitrary date range
- `protocols/event-search.md` — full-text search by title / attendee / location
- `protocols/find-free-slots.md` — open time slots given duration + business-hours window (agent-side computation over `gws calendar events list` output)
- `protocols/shared-calendar-read.md` — events from a colleague's shared calendar (enumerate via `gws calendar list`, then list events scoped to that calendar id)

## Workflow pattern

A typical agenda-view invocation:

```bash
gws calendar events list \
  --time-min 2026-05-19T00:00:00+08:00 \
  --time-max 2026-05-20T00:00:00+08:00
```

Returns a JSON array of event records. Format per the protocol's `## Output` section.

## Failure modes

See `references/failure-modes.md` — shared-OAuth with gmail-automate, `GOOGLE_CLOUD_PROJECT` requirement, timezone handling, recurring-event expansion, subcommand-name verification status.
