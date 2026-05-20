# sf-query

Natural-language Salesforce SOQL / SOSL query over a connected org via the Salesforce DX MCP server. Ask a business question in prose; the skill picks the right MCP tool, composes the SOQL (or SOSL) string, echoes it for sanity-check, executes, and renders rows as a table.

Read-only. No DML, no metadata mutation — that's `sf-deploy` (Phase 2) territory.

## Prerequisites

- `/salesforce-toolkit:sf-setup` has run successfully (installs `sf` CLI + `salesforce-mcp` and completes browser OAuth).
- `salesforce-mcp` shows **connected** in `/mcp` output.

If either check fails, stop and tell the user to run `/salesforce-toolkit:sf-setup` (or pass `--force-reauth` if the OAuth token expired).

## Example prompts

The skill always echoes the composed query in a fenced block **before** executing, so the user can sanity-check. Patterns below show the expected SOQL the skill should produce.

### Example 1 — Recent records

> *"Show me the 10 most-recently-created Accounts."*

Standard SOQL on `Account`, sorted by `CreatedDate` desc, capped at 10:

```sql
SELECT Id, Name, Industry, Owner.Name, CreatedDate
FROM Account
ORDER BY CreatedDate DESC
LIMIT 10
```

### Example 2 — Filtered pipeline

> *"Open Opportunities closing in the next 30 days over $100k."*

SOQL with the `NEXT_N_DAYS:30` date literal (no quotes) and a numeric `Amount` predicate. `IsClosed = false` excludes won/lost rows so the user sees open pipe only:

```sql
SELECT Id, Name, StageName, Amount, CloseDate, Account.Name
FROM Opportunity
WHERE CloseDate = NEXT_N_DAYS:30
  AND Amount > 100000
  AND IsClosed = false
ORDER BY CloseDate ASC
LIMIT 200
```

### Example 3 — Aggregate this quarter

> *"Count Cases by Status this quarter."*

Aggregate SOQL with `GROUP BY` and the `THIS_QUARTER` date literal:

```sql
SELECT Status, COUNT(Id) cnt
FROM Case
WHERE CreatedDate = THIS_QUARTER
GROUP BY Status
ORDER BY COUNT(Id) DESC
```

The MCP server flattens aggregate results to plain JSON — render as a 2-column markdown table.

## Troubleshooting

Common errors (full table with fixes in [`SKILL.md`](SKILL.md) §"Common errors and how to handle them"):

- `INVALID_FIELD` / `INVALID_TYPE` — field or object missing, or field-level / object-level read permission denied.
- `MALFORMED_QUERY: unexpected token` — most often a quoted date literal (use `TODAY`, not `'TODAY'`) or a wrong child relationship name (use `Cases`, not `Case`).
- `INVALID_SESSION_ID` / `unauthorized` — OAuth token expired; run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/refresh-auth.sh"`.
- `QUERY_TIMEOUT` — query touched too much data; add a selective `WHERE` on an indexed field (`Id`, `Name`, `CreatedDate`, `OwnerId`) or a tighter `LIMIT`.

## References

- Full skill instructions: [`SKILL.md`](SKILL.md)
- [Salesforce SOQL & SOSL Reference](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/) — primary source
- [salesforcecli/mcp](https://github.com/salesforcecli/mcp) — upstream MCP server
