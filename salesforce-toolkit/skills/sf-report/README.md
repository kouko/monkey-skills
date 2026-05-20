# sf-report

Read this in: **English** | 日本語 (TBD) | 繁體中文 (TBD)

Read-only access to Salesforce **Reports** and **Dashboards** via the `salesforce` MCP server shipped with this plugin (Salesforce DX MCP, `data,metadata` toolsets). The skill lists Report folders, fetches Report metadata, executes Reports, pulls row data, runs trend / aggregate / Top-N analysis, and snapshots Dashboard widgets — all returning structured JSON, no UI scraping.

## Quickstart

Pull a Salesforce Report or Dashboard widget by name, run it (optionally with ad-hoc filter overrides), and analyze the results in-conversation with the source Report ID + run timestamp cited.

## Prerequisites

- One-time: run `/salesforce-toolkit:sf-setup` and complete browser OAuth.
- Verify the `salesforce` MCP server is connected (`claude mcp list`).
- If a Report call returns `INVALID_SESSION_ID` / expired token, hand off to the user with `bash salesforce-toolkit/scripts/sf/refresh-auth.sh`.

## Example prompts

### Run a Report by name

> "Show me the 'Top 10 Won Opportunities this quarter' report."

The skill resolves the Report ID via `list-reports`, confirms the date filter via `describe-report`, runs it with `includeDetails=true`, and presents rows as a Markdown table with the Report ID + run timestamp cited.

### Dashboard widget snapshot

> "Fetch the 'Sales Pipeline Overview' dashboard's widget data."

The skill calls `list-dashboards` to resolve the Dashboard ID, `describe-dashboard` to list its widgets and their source `reportId`, then runs each widget's underlying Report. Each widget's data is cited with its title + source Report ID.

### Pipeline funnel — Lead → Qualified → Won

> "Show conversion from Lead → Qualified → Won."

The skill checks for a pre-built funnel Report first (`list-reports` substring match). If one exists, it runs with `includeDetails=false` and computes stage counts + conversion ratios (Qualified/Lead, Won/Qualified, Won/Lead) from the `factMap`. If no Report exists, the skill routes to the sibling `sf-query` skill for a direct SOQL aggregate.

## Sibling skill

- **`sf-query`** — ad-hoc SOQL / SOSL for questions that don't map to a pre-built Report, or when the 2,000-row Report API limit makes direct SOQL the cleaner answer.

## Troubleshooting

See [`SKILL.md`](SKILL.md) §Failure modes for the full table — covers Report not in any visible folder (Folder sharing model), legacy Custom Report Types raising `ReportNotSupportedException`, the 2,000-row API limit, MCP tool-name drift between releases, and mid-session auth expiry.

## References

- Full skill instructions: [`SKILL.md`](SKILL.md)
- Plugin spec: [`salesforce-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`salesforce-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
