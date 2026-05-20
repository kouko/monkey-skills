---
name: sf-query
description: Natural-language Salesforce SOQL / SOSL query via the Salesforce DX MCP server — list objects, fetch records, filter, aggregate, traverse parent-child relationships. Read-only data toolset. Salesforce SOQL・SOSL・データクエリ・自然言語。Salesforce SOQL・SOSL・資料查詢・自然語言。
allowed-tools: mcp__salesforce__*
---

# sf-query

Natural-language SOQL / SOSL query over a Salesforce org via the Salesforce DX MCP server (brew formula `salesforce-mcp` / npm `@salesforce/mcp`, binary `sf-mcp-server`, Apache-2.0, GA 2026). The user asks a business question in prose; this skill picks the right MCP tool, composes a SOQL or SOSL string, calls the tool, and renders the JSON rows back as a table or a narrative answer.

Read-only. No `DML`, no `INSERT / UPDATE / DELETE`, no metadata mutation — those are Phase 2 (`sf-deploy`) territory.

## Prerequisites

One-time setup:

1. Run `/salesforce-toolkit:sf-setup` and complete the browser OAuth flow. This installs `sf` CLI + `salesforce-mcp` via brew and authenticates the default org.
2. Verify the MCP server is alive: in Claude Code, run `/mcp` and confirm `salesforce` is listed as connected (this is the MCP server name from `.mcp.json`; the underlying binary is `sf-mcp-server`, shipped by brew formula `salesforce-mcp`). If it shows `disconnected` or `error`, run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/refresh-auth.sh"` to re-auth the OAuth token, then restart the MCP server.
3. Confirm the default org responds: `sf org display --json` should return a JSON blob with `instanceUrl` and a non-expired `accessTokenExpirationDate`.

If any of the three checks fail, stop and tell the user to run `/salesforce-toolkit:sf-setup` (or `--force-reauth` if the token expired). Do **not** try to compose queries against a dead MCP server — the error messages will be cryptic.

## When to pick SOQL vs SOSL

| You want… | Use | Why |
|---|---|---|
| Structured rows from **one** object (or a parent-child chain) with `WHERE` / `ORDER BY` / `GROUP BY` / `LIMIT`. | **SOQL** | SOQL is the relational query language; it returns typed columns. |
| Free-text search across **many** objects at once (e.g. "anything mentioning 'iChef' in Cases, Accounts, and Contacts"). | **SOSL** | SOSL hits the full-text index across multiple sObjects in one call. |
| You don't know the object yet ("find anything about acme corp") | **SOSL** | One round-trip; let the index decide. |
| You already know it's `Account` / `Opportunity` / `Case` | **SOQL** | Tighter, cheaper, easier to filter / aggregate. |

Default to SOQL. Reach for SOSL only when the user explicitly says "search" or names no object.

## Workflow

For every user question:

1. **Classify** — SOQL (structured) or SOSL (full-text). See table above.
2. **Identify the object(s)** — `Account`, `Opportunity`, `Case`, `Contact`, custom `*__c`. If unclear, call the MCP server's object-list tool first (see Example 1).
3. **Compose** — write the SOQL / SOSL string. Echo the string back to the user in a fenced block **before** executing, so the user can sanity-check the query.
4. **Execute** — call the MCP server's SOQL / SOSL tool with the composed string.
5. **Render** — return rows as a markdown table for ≤20 rows, or a narrative summary + truncated table for larger result sets. Always state row count and any applied `LIMIT`.

## Worked examples

### Example 1 — List custom objects on the org

> *"List all custom objects on this org."*

Custom objects in Salesforce end with `__c`. Use the MCP server's object-describe / object-list facility (Salesforce DX MCP exposes the metadata toolset for this).

Query the global describe and filter for `custom: true`:

```
SELECT QualifiedApiName, Label, KeyPrefix
FROM EntityDefinition
WHERE IsCustomizable = true AND QualifiedApiName LIKE '%__c'
ORDER BY QualifiedApiName
LIMIT 200
```

Echo this SOQL to the user, then call the MCP SOQL tool. Render as a table with columns `API name | Label | Key prefix`. If `EntityDefinition` is restricted on the org (some editions hide it), fall back to the MCP server's dedicated list-objects tool and pass `custom_only: true`.

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

Then, in the rendering step, sum `Opportunities[].Amount` per Account and count `Cases[]` per Account. The relationship names — `Opportunities`, `Cases` — are the **child relationship names** on `Account` (plural, capital-A). If you're unsure of the child relationship name on a custom object, call the MCP server's describe tool on the parent and look at the `childRelationships` array.

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
| `INVALID_FIELD: No such column 'XYZ__c' on entity 'Account'` | Field doesn't exist OR your user lacks field-level read permission on it. | Confirm spelling against the MCP describe tool. If the field shows in describe but not in query, it's a field-level security issue — ask user to check the relevant profile / permission set, or drop the column. |
| `INVALID_TYPE: sObject type 'CustomObj__c' is not supported` | Object exists but your user has no read access to the object itself. | Switch user to a profile with read, or pick a visible object. SOQL won't bypass org permissions. |
| `MALFORMED_QUERY: ... unexpected token: 'Cases'` (or similar relationship name) | Wrong child relationship name (e.g. `Case` singular vs `Cases` plural; custom relationships often end `__r` not `__c`). | Call the MCP describe tool on the parent object and read the `childRelationships[].relationshipName` field. Re-issue with the correct name. |
| `MALFORMED_QUERY: line N, column M: unexpected token` (general) | SOQL syntax error — most often a `WHERE` clause comparing a string without quotes, or a date literal with quotes (`'TODAY'` instead of `TODAY`). | Re-read the echoed query carefully. String literals: `'foo'`. Date literals: `TODAY` / `THIS_QUARTER` / `NEXT_N_DAYS:30` — **no quotes**. Numeric / boolean: bare value. |
| `QUERY_TIMEOUT` or row-count over governor limits | Query touched too much data without selective filters; Salesforce throttles. | Add a more selective `WHERE` (indexed fields: `Id`, `Name`, `CreatedDate`, `LastModifiedDate`, `OwnerId`, external IDs); add `LIMIT`; or split by date range. |
| MCP tool returns `unauthorized` / `INVALID_SESSION_ID` | OAuth token expired. | Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/refresh-auth.sh"` (or `/salesforce-toolkit:sf-setup --force-reauth`). Then retry. |
| MCP tool not listed in `/mcp` output at all | `salesforce-mcp` brew formula missing (no `sf-mcp-server` binary on PATH) AND npx fallback also failed. | Run `/salesforce-toolkit:sf-setup` from scratch; if `--skip-mcp-brew` was used previously, drop it. |

## Output format

For any query result:

1. **Echo the SOQL / SOSL** in a fenced code block before execution. The user sees what you're about to ask.
2. **Report row count and any `LIMIT` applied** in one line.
3. **Render rows** — markdown table for ≤20 rows; truncated table + narrative for more.
4. **Cite the org** — include `instanceUrl` from `sf org display` once per session (so the user knows which org they're looking at).

Never invent rows. If the MCP server returns an empty result set, say so explicitly — do not pad with placeholder data.

## See also

- `/salesforce-toolkit:sf-setup` — first-time install + OAuth + re-auth
- `salesforce-toolkit/skills/sf-report/SKILL.md` — Salesforce Report / Dashboard pulls (sibling skill, complementary to ad-hoc SOQL)
- [Salesforce SOQL & SOSL Reference](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/) — primary source for syntax, date literals, governor limits
- [salesforcecli/mcp](https://github.com/salesforcecli/mcp) — upstream MCP server source + tool reference
