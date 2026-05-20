---
name: sf-report
description: Salesforce Report and Dashboard fetch + analysis via the salesforce-toolkit MCP server (data toolset). Read-only — list Report folders, fetch Report metadata, execute Reports, pull row data, do trend / aggregate / Top-N analysis, snapshot Dashboard widgets. Use when user asks for a Salesforce Report or Dashboard, KPI snapshot, pipeline funnel, or Top-N by metric. Salesforce レポート・ダッシュボード・KPI 分析。Salesforce 報表・儀表板・KPI 拉取分析。
allowed-tools: mcp__salesforce__*
---

# sf-report

Read-only access to Salesforce **Reports** and **Dashboards** via the `salesforce` MCP server shipped with this plugin (Salesforce DX MCP, `data,metadata` toolsets). Returns structured JSON — no UI scraping, no per-org URL hardcoding.

This skill teaches the agent to:
1. **List** Report folders + Reports the user has access to.
2. **Fetch** Report metadata (columns, filters, grouping, Report Type) before running it.
3. **Execute** a Report and pull row data + summary aggregates.
4. **Analyze** results — trend / aggregate / Top-N / funnel — in-conversation.
5. **Snapshot** Dashboard widgets (each widget points to a Report; fetch its data).

For ad-hoc SOQL queries that don't map to an existing Report, route to the sibling `sf-query` skill instead.

## Prerequisites

One-time setup per machine:

1. Run `/salesforce-toolkit:sf-setup` and complete the browser OAuth handoff. This installs `sf` CLI + `salesforce-mcp`, runs `sf org login web`, and registers the org alias.
2. Verify the MCP server is alive: the `salesforce` MCP server should appear in `claude mcp list` (or its IDE equivalent) with status connected.

If a Report-fetch call returns an auth error (`INVALID_SESSION_ID`, `expired access/refresh token`), the user's OAuth token has expired. Hand off to user with:

> `bash salesforce-toolkit/scripts/sf/refresh-auth.sh`

…and resume after they confirm re-auth completed.

## MCP tool surface

The `salesforce` MCP server (with `--toolsets data,metadata`) exposes Report-related tools roughly grouped as:

- `list-reports` / `find-reports` — enumerate Reports the current org alias can see, filtered by folder, name, or Report Type. Use this **first** when the user names a Report by title rather than ID.
- `describe-report` / `get-report-metadata` — fetch a Report's structure: columns, grouping levels, summary fields, filters, Report Type API name, owner. Read this **before** executing if you need to project / pivot results.
- `run-report` / `execute-report` — run the Report and return row data + factMap (aggregates per grouping). Supports `includeDetails=true` for row-level data and `reportFilters` overrides for ad-hoc date / status filters.
- `list-dashboards` / `describe-dashboard` — enumerate Dashboards and their widgets; each widget has a `reportId` pointing back to the source Report.
- `run-dashboard-widget` (or run the widget's underlying Report directly) — fetch a single Dashboard widget's data snapshot.

**Important**: the salesforce-mcp tool catalogue can shift between releases. **List the tools first** via the MCP introspection call your runtime exposes if a name above doesn't resolve. Don't assume — verify, then call.

## Workflow

1. **Resolve the Report**. If the user named it by title (e.g. *"Top 10 Won Opportunities this quarter"*), call `list-reports` with a substring match. Confirm the right Report ID with the user before running anything expensive.
2. **Describe before running** when the user wants analysis beyond what the Report's default view returns (custom grouping, additional projections, alternative date window). Cheap call; saves a wasted execute.
3. **Run the Report** with `includeDetails=true` if you need row-level data; with `includeDetails=false` if a summary aggregate is enough (cheaper, smaller payload).
4. **Apply ad-hoc filters** via `reportFilters` (date range override, status override) rather than asking the user to clone the Report in the UI.
5. **Analyze in-conversation** — summarize trend, compute Top-N, build funnel ratios. Cite Report ID + run timestamp so the user can reproduce.
6. **Cite the source**. Always include the Report's name + ID and the row count returned. If row count equals the API row limit, **say so** — results may be truncated.

## Worked examples

### Run a Report by name

User: *"Show me the 'Top 10 Won Opportunities this quarter' report."*

1. `list-reports` with `nameContains="Top 10 Won Opportunities"`. Match exactly one Report; if multiple, present the candidates and ask which.
2. `describe-report` to confirm the Report's date filter is "this quarter" (don't assume the title matches the filter).
3. `run-report` with `includeDetails=true`. Format the row payload as a Markdown table: Opportunity Name | Account | Amount | Close Date | Stage.
4. Cite: *"Report `00O...` 'Top 10 Won Opportunities this quarter', run at 2026-05-20T10:00Z, 10 rows."*

### Filter by date range

User: *"Run 'Pipeline by Stage' for Q2."*

1. `list-reports` → resolve the Report ID for "Pipeline by Stage".
2. `describe-report` → identify the date-filter column (typically `CloseDate` or `CreatedDate`) and its current bound.
3. `run-report` with `reportFilters` overriding the date column to `[2026-04-01, 2026-06-30]`. Don't ask the user to edit the Report in the UI.
4. Present aggregates by Stage (count + sum of Amount) from the Report's `factMap`. If they asked for trend, group by month and show a small inline table.

### Dashboard widget snapshot

User: *"Fetch the 'Sales Pipeline Overview' dashboard's widget data."*

1. `list-dashboards` with `nameContains="Sales Pipeline Overview"` to resolve Dashboard ID.
2. `describe-dashboard` to list its widgets — each has `title`, `componentType` (chart / metric / table), and `reportId`.
3. For each widget the user cares about (or all), run the widget's underlying Report (or `run-dashboard-widget` if your MCP build exposes it). Be explicit about which widget's data you're showing.
4. Cite the Dashboard ID + each widget's title + source Report ID. Dashboard widget data is a Report snapshot; note the run timestamp.

### Pipeline funnel — Lead → Qualified → Won conversion

User: *"Show conversion from Lead → Qualified → Won."*

1. Funnels are usually a single Report grouped by Stage with a custom date window. Try `list-reports` with `nameContains="Funnel"` or `"Conversion"` first.
2. If no pre-built Report exists, fall back to the sibling **`sf-query` skill** — a 3-stage SOQL aggregate against `Opportunity` (or `Lead` → `Opportunity` via the `ConvertedOpportunityId` linkage) is more direct than abusing a Report.
3. If a Report does exist: `run-report` with `includeDetails=false`, pull the stage-grouped counts from `factMap`, present:
   - Stage counts: Lead → Qualified → Won
   - Conversion ratios: Qualified/Lead, Won/Qualified, Won/Lead
4. Be explicit about the date window the Report uses (don't assume "this quarter" — read it from `describe-report`).

### Top-N by metric

User: *"Top 10 accounts by total opportunity value."*

1. Check for a pre-built "Top Accounts by Opportunity" Report via `list-reports`. If it exists, just run it and present.
2. If not, this is a SOQL aggregate question — route to `sf-query`:
   `SELECT Account.Name, SUM(Amount) total FROM Opportunity WHERE IsClosed=false GROUP BY Account.Name ORDER BY SUM(Amount) DESC LIMIT 10`
3. Format as a ranked table: Rank | Account | Open Pipeline | (optional: Owner).
4. Disambiguate "total opportunity value" with the user — open pipeline vs. closed-won YTD vs. all-time. Ask once, then proceed.

## Failure modes

### Report not in any visible folder

The Reports API only returns Reports the authenticated user's profile + permission sets grant access to (Report Folder sharing model). If `list-reports` returns empty for a Report the user swears exists:

- Confirm with the user which org alias is active (`sf org list --json` or check `.mcp.json` `DEFAULT_TARGET_ORG`). Wrong org → wrong Report set.
- Ask the user to confirm Report sharing in Salesforce UI (Reports → folder → share with their user / role).
- Do **not** fabricate a Report ID. Surface the gap and stop.

### Report Type limitation

`run-report` only works on Reports whose Report Type the API supports — most standard Report Types are fine, but a handful of legacy Custom Report Types (especially with cross-object joins added pre-2018) raise `ReportNotSupportedException`. If you hit this:

- Surface the error verbatim with the Report's `reportType` (from `describe-report`).
- Offer the SOQL fallback via `sf-query` — usually the user's underlying question can be answered with a direct query against the base object.

### Row limit hit

Salesforce caps Report API responses at **2,000 rows** per call (factMap aggregates are unaffected; row detail is). If `allData=false` in the response or row count equals 2000:

- Say so explicitly: *"Report returned 2000 rows (API limit hit). Results may be truncated."*
- For analysis that needs the full long tail, recommend a tighter `reportFilters` window or a direct SOQL via `sf-query` (SOQL has different limits: 50,000 rows in a single transaction).
- Don't silently assume the 2000 rows are the whole dataset.

### MCP server tool name mismatch

The salesforce-mcp tool list can shift between releases (we pin to `data,metadata` toolsets but tool names within those evolve). If a tool name above (`list-reports`, `run-report`, …) doesn't resolve:

- List available tools via your runtime's MCP introspection (e.g. `claude mcp list-tools salesforce`).
- Match by semantics (Report list / describe / run / Dashboard list / describe) and use the actual name.
- If no matching tool exists — the toolset config may have drifted. Surface the gap and ask the user to re-run `/salesforce-toolkit:sf-setup` or check `.mcp.json`.

### Auth expired mid-session

If a call returns `INVALID_SESSION_ID` or `expired access/refresh token`, hand off:

> Your Salesforce session expired. Please run `bash salesforce-toolkit/scripts/sf/refresh-auth.sh` in a terminal, complete the browser flow, and let me know when it's done.

Then resume the Report fetch.

## Sibling skill

- **`sf-query`** — ad-hoc SOQL / SOSL for questions that don't have a pre-built Report or Dashboard, or when Report row limits make direct SOQL the cleaner answer.
