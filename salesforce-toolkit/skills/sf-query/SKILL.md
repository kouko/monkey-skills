---
name: sf-query
description: Natural-language Salesforce SOQL query via the Salesforce DX MCP server — list objects, fetch records, filter, aggregate, traverse parent-child relationships. Read-only data toolset (single MCP tool — `run_soql_query`). Salesforce SOQL・データクエリ・自然言語。Salesforce SOQL・資料查詢・自然語言。
allowed-tools: mcp__salesforce__*
---

# sf-query

Natural-language SOQL query over a Salesforce org via the Salesforce DX MCP server (brew formula `salesforce-mcp` / npm `@salesforce/mcp`, binary `sf-mcp-server`, Apache-2.0, GA 2026). The user asks a business question in prose; this skill composes a SOQL string, calls the upstream `run_soql_query` MCP tool, and renders the JSON rows back as a table or a narrative answer.

Read-only. The `.mcp.json` ships only the `data` toolset, which exposes a single tool: `run_soql_query`. No `DML`, no `INSERT / UPDATE / DELETE`, no metadata mutation — those tools are structurally absent from the MCP surface in v0.1.0.

**SOQL only — no SOSL.** Upstream `salesforcecli/mcp` v0.30.9 `data` toolset exposes no SOSL tool. If the user asks for full-text search ("find anything about acme corp"), pick a likely target object (Account / Contact / Case) and use a SOQL `WHERE Name LIKE '%acme corp%'` (or similar) pattern; tell the user this is a SOQL approximation and SOSL is deferred to Phase 2+.

## Prerequisites

One-time setup:

1. Run `/salesforce-toolkit:sf-setup` and complete the browser OAuth flow. This installs `sf` CLI + `salesforce-mcp` via brew and authenticates the default org.
2. Verify the MCP server is alive: in Claude Code, run `/mcp` and confirm `salesforce` is listed as connected (this is the MCP server name from `.mcp.json`; the underlying binary is `sf-mcp-server`, shipped by brew formula `salesforce-mcp`). If it shows `disconnected` or `error`, run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/refresh-auth.sh"` to re-auth the OAuth token, then restart the MCP server.
3. Confirm the default org responds: `sf org display --json` should return a JSON blob with `instanceUrl` and a non-expired `accessTokenExpirationDate`.

If any of the three checks fail, stop and tell the user to run `/salesforce-toolkit:sf-setup` (or `--force-reauth` if the token expired). Do **not** try to compose queries against a dead MCP server — the error messages will be cryptic.

## Workflow

For every user question:

1. **Identify the object(s)** — `Account`, `Opportunity`, `Case`, `Contact`, custom `*__c`. If the user names no object, infer the most likely target from the prose (e.g. "deals" → `Opportunity`, "customers" → `Account`, "tickets" → `Case`) and state your inference before composing the query so the user can correct you.
2. **Compose** — write the SOQL string. Echo the string back to the user in a fenced block **before** executing, so the user can sanity-check the query.
3. **Execute** — call `mcp__salesforce__run_soql_query` with the composed SOQL string.
4. **Render** — return rows as a markdown table for ≤20 rows, or a narrative summary + truncated table for larger result sets. Always state row count and any applied `LIMIT`.

## Worked examples

### Example 1 — List custom objects on the org

> *"List all custom objects on this org."*

Custom objects in Salesforce end with `__c`. Query the `EntityDefinition` system table via SOQL and filter for `custom: true`:

```
SELECT QualifiedApiName, Label, KeyPrefix
FROM EntityDefinition
WHERE IsCustomizable = true AND QualifiedApiName LIKE '%__c'
ORDER BY QualifiedApiName
LIMIT 200
```

Echo this SOQL to the user, then call `run_soql_query` with this string. Render as a table with columns `API name | Label | Key prefix`. If `EntityDefinition` is restricted on the org (some editions hide it), tell the user — v0.1.0 has no fallback because the `metadata` toolset (which would expose dedicated list-objects / describe tools) is not enabled in this plugin's read-only build. Phase 2+ may add a safety-wrapped `metadata` toolset.

### Example 2 — 10 most-recently-created Accounts

> *"Show me the 10 most-recently-created Accounts."*

Straight SOQL on the `Account` standard object, sorted by `CreatedDate` desc, capped at 10:

```
SELECT Id, Name, Industry, Owner.Name, CreatedDate
FROM Account
ORDER BY CreatedDate DESC
LIMIT 10
```

Notes:
- `Owner.Name` traverses the `Owner` relationship (parent-to-child not needed here; this is the standard `User` lookup on the `OwnerId` field). Free of charge in SOQL.
- Render `CreatedDate` in the user's locale; the MCP server returns ISO 8601 strings.

### Example 3 — Opportunities closing in next 30 days over $100k

> *"Opportunities with CloseDate in next 30 days and Amount > 100k."*

Use SOQL date-literal `NEXT_N_DAYS:30` (no quotes, no formatting headaches across locales) and a plain numeric `Amount` predicate. Exclude closed-lost / closed-won unless the user asks for them:

```
SELECT Id, Name, StageName, Amount, CloseDate, Account.Name, Owner.Name
FROM Opportunity
WHERE CloseDate = NEXT_N_DAYS:30
  AND Amount > 100000
  AND IsClosed = false
ORDER BY CloseDate ASC
LIMIT 200
```

Why these clauses:
- `NEXT_N_DAYS:30` is a SOQL date literal — safer than computing `TODAY()` + offset on the client side.
- `IsClosed = false` filters out already-won and already-lost rows (user almost always means open pipe).
- `LIMIT 200` is a safety cap; if you hit it, tell the user and offer to widen / paginate.

Render with currency formatting on `Amount` (the org's `CurrencyIsoCode` is on each row if multi-currency is enabled — query it explicitly if you need to display per-row currency).

### Example 4 — Aggregate: count Cases by Status this quarter

> *"Count Cases by Status grouped this quarter."*

Aggregate SOQL with `GROUP BY`. The `CALENDAR_QUARTER()` function buckets by quarter, but for "this quarter" use the `THIS_QUARTER` date literal directly:

```
SELECT Status, COUNT(Id) cnt
FROM Case
WHERE CreatedDate = THIS_QUARTER
GROUP BY Status
ORDER BY COUNT(Id) DESC
```

Notes:
- `COUNT(Id) cnt` — the alias `cnt` is the column name in the result; Salesforce returns aggregate rows as `AggregateResult` objects, but the MCP server flattens them to a plain JSON list. Render as a 2-column table.
- If the user wants a multi-bucket breakdown (e.g. by `Status` × `Priority`), add both to the `GROUP BY` clause; the MCP server returns one row per combination.

### Example 5 — Cross-object: Account + total Opportunity amount + Case count

> *"Account name + total Opportunity amount + Case count."*

This is two child relationships off `Account`. Either issue one parent query with two subqueries (preferred for ≤200 parent rows), or two separate aggregate queries joined on the client. Subquery form:

```
SELECT Id, Name,
       (SELECT Id, Amount FROM Opportunities WHERE IsClosed = false),
       (SELECT Id FROM Cases WHERE IsClosed = false)
FROM Account
ORDER BY Name ASC
LIMIT 100
```

Then, in the rendering step, sum `Opportunities[].Amount` per Account and count `Cases[]` per Account. The relationship names — `Opportunities`, `Cases` — are the **child relationship names** on `Account` (plural, capital-A). If you're unsure of the child relationship name on a custom object, v0.1.0 cannot describe it directly (no `metadata` toolset enabled — see top of file); ask the user to check Setup → Object Manager → the parent object → Fields & Relationships, or wait for Phase 2+ describe support.

Alternative — two aggregate queries joined on `AccountId`:

```
SELECT AccountId, SUM(Amount) open_amount
FROM Opportunity
WHERE IsClosed = false
GROUP BY AccountId
```

```
SELECT AccountId, COUNT(Id) open_cases
FROM Case
WHERE IsClosed = false
GROUP BY AccountId
```

Prefer the subquery form when the user wants per-row detail; prefer the aggregate-pair form when result sets are large and rendering as a leaderboard.

## Common errors and how to handle them

| Symptom | Likely cause | Fix |
|---|---|---|
| `INVALID_FIELD: No such column 'XYZ__c' on entity 'Account'` | Field doesn't exist OR your user lacks field-level read permission on it. | Confirm spelling — ask the user to check Setup → Object Manager. v0.1.0 has no describe tool (metadata toolset not enabled). If the user confirms the field exists, it's a field-level security issue — they need to check the relevant profile / permission set, or you should drop the column from the query. |
| `INVALID_TYPE: sObject type 'CustomObj__c' is not supported` | Object exists but your user has no read access to the object itself. | Switch user to a profile with read, or pick a visible object. SOQL won't bypass org permissions. |
| `MALFORMED_QUERY: ... unexpected token: 'Cases'` (or similar relationship name) | Wrong child relationship name (e.g. `Case` singular vs `Cases` plural; custom relationships often end `__r` not `__c`). | Standard objects: `Account` has `Opportunities` / `Cases` / `Contacts` (plural). Custom relationships: replace the trailing `__c` of the lookup field with `__r` (e.g. `Customer__c` field → `Customer__r` relationship; the child-collection name is set on the lookup in Setup → Object Manager → Fields & Relationships). Re-issue with the correct name. |
| `MALFORMED_QUERY: line N, column M: unexpected token` (general) | SOQL syntax error — most often a `WHERE` clause comparing a string without quotes, or a date literal with quotes (`'TODAY'` instead of `TODAY`). | Re-read the echoed query carefully. String literals: `'foo'`. Date literals: `TODAY` / `THIS_QUARTER` / `NEXT_N_DAYS:30` — **no quotes**. Numeric / boolean: bare value. |
| `QUERY_TIMEOUT` or row-count over governor limits | Query touched too much data without selective filters; Salesforce throttles. | Add a more selective `WHERE` (indexed fields: `Id`, `Name`, `CreatedDate`, `LastModifiedDate`, `OwnerId`, external IDs); add `LIMIT`; or split by date range. |
| MCP tool returns `unauthorized` / `INVALID_SESSION_ID` | OAuth token expired. | Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/refresh-auth.sh"` (or `/salesforce-toolkit:sf-setup --force-reauth`). Then retry. |
| MCP tool not listed in `/mcp` output at all | `salesforce-mcp` brew formula missing (no `sf-mcp-server` binary on PATH) AND npx fallback also failed. | Run `/salesforce-toolkit:sf-setup` from scratch; if `--skip-mcp-brew` was used previously, drop it. |

## Output format

For any query result:

1. **Echo the SOQL** in a fenced code block before execution. The user sees what you're about to ask.
2. **Report row count and any `LIMIT` applied** in one line.
3. **Render rows** — markdown table for ≤20 rows; truncated table + narrative for more.
4. **Cite the org** — include `instanceUrl` from `sf org display` once per session (so the user knows which org they're looking at).

Never invent rows. If the MCP server returns an empty result set, say so explicitly — do not pad with placeholder data.

## See also

- `/salesforce-toolkit:sf-setup` — first-time install + OAuth + re-auth
- [Salesforce SOQL Reference](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/) — primary source for syntax, date literals, governor limits (covers both SOQL and SOSL, but only SOQL is reachable from this plugin in v0.1.0)
- [salesforcecli/mcp](https://github.com/salesforcecli/mcp) — upstream MCP server source + tool reference
