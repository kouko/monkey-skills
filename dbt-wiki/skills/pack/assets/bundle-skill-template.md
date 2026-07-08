---
name: <PROJECT_SLUG>-analytics
description: >-
  Ground questions in <PROJECT_NAME>'s distilled data knowledge and
  generate correct SQL against its warehouse — <PROJECT_DESCRIPTION>.
  This skill carries the semantic knowledge + SQL-generation guidance;
  it does NOT execute SQL itself. Bring your own warehouse-connect tool
  (an MCP server or a CLI that runs SQL against the warehouse) to
  execute and inspect results. Use when asked to answer a data
  question about <PROJECT_NAME>, write a query against its tables,
  compute a metric, or explore its entities — e.g. "what was
  <PROJECT_NAME>'s revenue last month", "average order value per
  account", "how many active accounts by region". <TRIGGER_PHRASES>
# --- snapshot annotation (see references/bundle-format.md §Snapshot-annotation block) ---
source_manifest_sha: <SOURCE_MANIFEST_SHA>
build_date: <BUILD_DATE>
snapshot_note: "Snapshot — re-run dbt-wiki:pack to refresh; does not auto-update."
---

# <PROJECT_NAME> Analytics

> **What this is**: a portable, **tool-agnostic** analytics skill for
> <PROJECT_NAME>. It freezes the project's distilled semantic knowledge
> and tells you how to turn a business question into a **correct** SQL
> query. It does **not** connect to a warehouse — **you** bring the
> tool that executes SQL.
>
> **Warehouse engine**: <WAREHOUSE_DIALECT> — generate
> <WAREHOUSE_DIALECT>-dialect SQL (date functions, casts, string
> concatenation differ by engine). "Tool-agnostic" means no specific
> MCP/CLI is assumed; the dialect is still fixed.
>
> **Snapshot**: this bundle is a point-in-time snapshot
> (`build_date` above). It does not auto-update. Re-run `dbt-wiki:pack`
> against a refreshed `.dbt-wiki/` to rebuild.

## What's in this folder

All paths are **relative to this skill's directory**:

- `knowledge/` — frozen semantic knowledge, **read on demand** (it can
  be large; load only the pages relevant to the question). One file per
  business object / measure / rule: entities (with `## Fields` column
  cards + `value_domain` enums), metrics (with `## Calculation` +
  `## Materialized Columns`), concepts, syntheses (verified deep-dive
  answers, when the source wiki has them), and relationship edges (with
  the **full compound join key** in each edge `note`). Files sit
  **directly** under `knowledge/` (flat — e.g. `knowledge/account.md`,
  `knowledge/monthly-recurring-revenue.md`; a page-type prefix like
  `knowledge/metric-monthly-recurring-revenue.md` only when names
  collide).
- `knowledge/_index.md` — the **retrieval entry point**: one line per
  frozen page (title, status, one-line summary, aliases). **Grep it
  first** for the question's business terms (the 〔aka: …〕 aliases are
  the grep surface) and open only the pages the matching lines point
  to; read the whole index only when grep misses. Never guess slugs or
  grep the whole knowledge folder.
- `knowledge/_relations.md` — **physical anchor**: every relation the
  knowledge pages cite → its **schema** + column list. The knowledge pages
  name relations as `model.column` (no schema); read `_relations.md` to
  qualify a runnable `FROM <schema>.<table>`. Schemas reflect dbt
  custom-schema concatenation (e.g. marts in `<db>__marts`) — do **not**
  assume one schema for all. Relations marked "needs introspect" (or columns
  you don't see): query the live warehouse (`information_schema.columns` /
  `SELECT … LIMIT 0`). In a dev environment, swap the prod schema prefix for
  your dev schema.
- `references/generation-guidance.md` — the SQL-generation guidance
  (schema-linking + the five semantic guardrails: aggregate level,
  compound-grain joins, value-grounding, source disambiguation,
  temporal). Scan its top **Pre-flight checklist** per question; drill
  into a section only when the question touches it.
- `examples/` — gold question → correct-SQL few-shot examples. **May be
  empty** in this snapshot; read any that exist for in-domain grounding.

## How to answer a question (the loop)

This is a **generate → execute → inspect → iterate** loop, not a
one-shot emit. You supply the execution.

1. **Ground** — find the relevant pages via `knowledge/_index.md`, read
   them, and schema-link the business terms in the question to concrete
   entity fields / physical columns; resolve the **schema-qualified
   `FROM`** via `knowledge/_relations.md` (introspect the live warehouse
   for any relation it marks "needs introspect"). Follow the
   schema-linking procedure in `references/generation-guidance.md` (§1).
   If a term resolves to nothing, ask the user — do not invent a column.

2. **Generate** — write the SQL applying the semantic guardrails in
   `references/generation-guidance.md` (correct `SUM/SUM` aggregation;
   full compound join keys / no fan-out; value-grounded categorical
   filters; surfaced source ambiguity; `CURRENT_DATE`-anchored relative
   dates — never `MAX(date)` as "now"). Consult any `examples/` for
   worked patterns. Do **not** static-check the SQL against `knowledge/`
   — execution is the only gate (why: guidance §0).

3. **Execute** — run the SQL via **your own warehouse-connect tool**
   (an MCP server or a CLI that runs SQL against the warehouse). This
   bundle names no specific tool: you bring it. **If no tool in your
   environment can reach the warehouse**, do not guess at results: deliver
   the grounded SQL, tell the user you need a SQL-executing tool (MCP /
   CLI), and state the connection prerequisites — the warehouse engine
   named above, any VPN / credentials it requires, and (in a dev
   environment) the schema prefix to substitute for the one in
   `knowledge/_relations.md`. Stop at this gate rather than fabricating an
   answer; the grounded SQL is still a useful deliverable.

4. **Inspect + iterate** — read the returned rows. Check row count,
   value ranges, NULLs, and obviously-wrong magnitudes (a per-account
   average equal to the grand total; a "last month" filter returning
   future-dated rows; a categorical filter returning 0 rows). If the
   result looks wrong, re-ground, fix the query, and re-run. Repeat
   until the numbers are defensible.

> **Why execution is the only gate** — the full argument (snapshot
> drift, and why even a fresh schema check can't catch wrong-number
> bugs) lives in `references/generation-guidance.md` §0. Short version:
> run the query, look at the rows, iterate.

## Worked shape (synthetic)

A question like *"average order value per account for last month"*
against a project whose entity `account` exposes
`account_id` / `report_month` and a categorical `region_code`
(`value_domain: [NL, EU, APAC]`):

1. **Ground**: `knowledge/account.md` → `## Fields` maps "account" →
   `account_id`, "month" → `report_month`; "average order value" →
   the metric page's `## Calculation` (a `SUM/SUM` ratio, not
   `AVG(row_ratio)`).
2. **Generate**: aggregate-level `SUM(order_revenue) / NULLIF(SUM(invoice_count), 0)`;
   relative "last month" anchored on `CURRENT_DATE`, not `MAX(report_month)`;
   any join on the **full** `account_id + report_month` compound key.
3. **Execute** the query with your warehouse tool.
4. **Inspect**: confirm the per-account figure is volume-weighted (not a
   row-level mean), the month is *last* month (not a future amortization
   row), and the row count is sane. Iterate if not.

---

*Generated by `dbt-wiki:pack`. Knowledge is a snapshot — see the
`build_date` / `source_manifest_sha` in the frontmatter above (or
`PROVENANCE.md` if this bundle keeps provenance there).*
