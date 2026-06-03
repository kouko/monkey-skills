# briefing-toolkit

A daily **morning brief** across your connected tools. One read-only fan-out over the platforms you have MCP-connected, distilled into a President's-Daily-Brief-style briefing **plus** a zero-omission, link-rich action table that accumulates day-over-day for continuity.

> [`README.ja.md`](README.ja.md) ・ [`README.zh-TW.md`](README.zh-TW.md)

## What it does

`/daily-brief` fans out (in parallel, read-only) over up to **7 platforms** — Gmail / Slack / Notion / Asana / Google Drive / Google Calendar / **GitHub** — finds what's relevant to *you*, and writes two artifacts into a folder you choose:

| Artifact | Role |
|---|---|
| `<date>_晨報.md` | **Curated brief** (PDB-style): today's focus (dynamic, threshold-driven) · schedule · awaiting-your-reply · in-progress projects · upcoming N days — short, ruthless, every line clickable. |
| `<date>_完整事項.md` | **Zero-omission action table** — every item, importance-ranked, each row a deep link you can click to act on. |
| `<date>_完整事項.csv` | Machine-readable index. Its unique-id column is the **join key** for the next day's continuity diff. |

### Continuity (the headline feature)

Output files accumulate as a dated ledger. Each run reads the **most recent prior** brief's CSV and diffs against it — surfacing what's **✅ resolved**, **⏳ still waiting on you (for N days)**, and **🆕 newly surfaced**. Continuity is grounded by **re-verifying each item's ID against the live platform**, never by trusting yesterday's text (no hallucination carry-forward).

## Prerequisites

This toolkit **consumes whatever MCP servers you already have connected** and degrades gracefully — it does not register its own. Connect the services you care about via, e.g.:

- [`collab-toolkit`](../collab-toolkit/) — Slack / Asana / Notion
- [`gws-toolkit`](../gws-toolkit/) — Gmail / Google Calendar / Drive
- a GitHub MCP server (or `gh` CLI)

A platform you haven't connected simply shows up as a blind spot in the brief's coverage statement — the rest still runs.

> ⚠️ Claude Code CLI only — the underlying MCP fetches don't run in the Cowork sandbox.

## Safety

- **read-only** end to end (search / fetch / read). Nothing is modified, deleted, or sent.
- **draft-only** — writes only to your chosen local folder. **Never** writes back to Notion / Slack / Gmail / Asana or any official system; never auto-replies.

## Scheduling

The skill is on-demand. To get it **every morning**, layer a harness trigger on top — `/schedule`, system cron, or a Cowork scheduled task that invokes `/daily-brief`. Scheduling and delivery are intentionally outside the skill.

## Not this toolkit

- Performance review / self-evaluation / period retrospective → use `performance-evidence-audit` (same cross-platform mechanism, but past-facing and evidence-oriented).
- Writing back / sending / auto-acting on any platform → out of scope by design.

## Skills

| Skill | Command | Purpose |
|---|---|---|
| `daily-brief` | `/daily-brief` | Generate today's cross-tool morning brief + action table. |
