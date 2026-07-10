# generation-guidance.md — SQL Generation Guidance for a Warehouse-Connected Agent

This file is copied verbatim into each emitted bundle's `references/`.
It tells the consuming agent how to turn a business question into a
**correct** SQL query, grounded in the frozen knowledge under
`knowledge/`.

You are an agent that **brings your own warehouse-connect tool** (an
MCP server, a CLI, a notebook driver — whatever runs SQL against the
project's warehouse). This guidance assumes you can execute SQL and
read the rows back.

## Pre-flight checklist (scan this first)

Work the loop in §0. Scan this list per question and **drill into a
section only when the question touches it** — the sections below are
the details, not a linear read:

- [ ] Every business term schema-linked to a real column (§1 — grep
      `knowledge/_index.md` for the term to find the right pages).
- [ ] Ratios/averages use `SUM/SUM` or the metric `## Calculation`,
      never `AVG(row_level_ratio)` (§2).
- [ ] Every JOIN uses the full compound grain key; no SUM over
      fanned-out rows (§3).
- [ ] Categorical filters use the stored `value_domain` value, weighted
      by its `(via:)` confidence tier; 0-row results probed with
      `SELECT DISTINCT` (§4).
- [ ] Ambiguous sources surfaced, not silently picked (§5).
- [ ] Relative dates anchored on `CURRENT_DATE`; no `MAX(date)`-as-now
      on forward-dated tables (§6).
- [ ] **Query executed; rows inspected; numbers defensible.** ← the
      real gate (§0).

---

## 0. The loop: generate → execute → inspect → iterate

The correct workflow for answering a question is a loop, not a
one-shot emit:

1. **Ground** the question against `knowledge/` (schema-linking, §1).
2. **Generate** SQL applying the five semantic guardrails (§2–§6).
3. **Execute** the SQL via your own warehouse tool.
4. **Inspect** the returned rows: row count, value ranges, NULLs,
   obviously-wrong magnitudes (a per-store average that equals the
   grand total; a "last month" filter returning future-dated rows; a
   `region = '...'` filter returning 0 rows).
5. **Iterate**: if the result looks wrong, re-ground, fix the query,
   re-run. Repeat until the numbers are defensible.

> **Execution is the only gate — do not static-check against this
> bundle's knowledge.** `knowledge/` is a point-in-time **snapshot** of
> the project's schema; the live warehouse drifts (columns added,
> renamed, dropped) and the bundle **does not auto-update**. Validating a
> generated query against the frozen snapshot would give *false
> confidence* (a column dropped in the warehouse still "exists" in the
> snapshot) or *false errors* (a new column the snapshot never saw) — so
> there is deliberately **no static existence check** here. Only running
> the query against the live warehouse sees current truth. And the
> dangerous errors are semantically-valid wrong-number bugs anyway (a 3×
> over-count from averaging pre-aggregated rows, an 84× fan-out from a
> grain mismatch, a future date from `MAX(date)`) — **only execution +
> inspecting the rows catches those.** Use `knowledge/` to **ground**
> generation, never to **gate** it. Run the query. Look at the output.
> Iterate.

---

## 1. Schema-Linking (business term → entity field)

**Schema-linking** maps business terms in the question (e.g. "account",
"monthly revenue", "last month") to the concrete entity fields and
physical column names in the warehouse.

For each business term in the question:

1. Locate the matching entity or metric page directly under `knowledge/`
   (e.g. `knowledge/<entity>.md`, `knowledge/<metric>.md`). **Grep
   `knowledge/_index.md` for the question's business terms first**
   (`grep -i "<term>" _index.md`) — each frozen page has one line there
   (title, status, one-line summary, aliases), and the 〔aka: …〕
   aliases are designed as the grep surface — then open only the pages
   the matching lines point to. Read the whole index only when grep
   misses; never slug-guess or grep the whole folder. (If this bundle
   predates `_index.md`, fall back to matching kebab-case slugs /
   grepping.) The bundle's `knowledge/` is **flat** — pages sit as
   direct children with kebab-case slugs; a page type is prefixed into
   the filename only on a cross-type name collision (e.g.
   `knowledge/metric-<metric>.md`).
2. Read its `## Fields` table. Every entity page carries one of this
   shape:

   | Business name | Column name | Type | Description |
   |---|---|---|---|
   | Account ID | `account_id` | varchar | Unique identifier per account |
   | Report month | `report_month` | date | Month grain (first-of-month) |

   The **Business name** column is the linking key — match it
   case-insensitively and allow synonyms (e.g. "customer" → "Account").
   The **Column name** column is the physical SQL identifier to emit.

3. Confirm the column actually exists before you rely on it — via
   `knowledge/_relations.md` first. That file is the bundle's **physical
   anchor**: for every relation the knowledge pages cite, its schema +
   column list. Cross-check the column name there (and pick up the
   schema-qualified `FROM` while you're at it). **Probe the live
   warehouse** (your own tool's column listing, or a
   `SELECT ... LIMIT 0`) only when the relation is marked
   "needs introspect", the column is absent from its `_relations.md`
   entry, or execution errors suggest the snapshot has drifted.
   `_relations.md` is still a snapshot — execution remains the gate
   (§0) — but it answers the "does this column exist?" question offline
   in one read instead of one warehouse round-trip per column. Do
   **not** synthesize or guess a column that neither the knowledge page
   nor `_relations.md` names.

4. **Parallel twins may not share column names — read the per-variant
   schema map.** When a metric/entity is distilled from per-segment /
   market / brand twins, the twins can rename columns (e.g.
   `region_code` → `region`), drop columns the canonical model
   has (e.g. no `revenue__gross`), or use a narrower value
   domain (e.g. `[APAC]` vs the canonical `[NL, EU, APAC]`). A well-distilled page
   records this as a per-variant schema map (a small table in
   `## Calculation` / `## Fields`). **Read it before writing a UNION or
   cross-twin query**, and align columns explicitly per twin (alias renamed
   columns, `NULL`-fill columns a twin lacks). If the page has no such map
   but `derived_from` clearly spans twins, treat the canonical column names
   as unverified for the other twins and probe each before UNIONing — the
   names that work for the canonical model silently error on a renamed twin.

If a term resolves to multiple fields across multiple entities, carry
all candidates into source disambiguation (§5). If a term resolves to
nothing in `knowledge/`, ask the user to clarify before generating —
do not invent a column.

---

## 2. Aggregate-level guardrail (SUM/SUM, not AVG-of-ratios)

When a question asks for a **ratio or average measure** (e.g. "average
order value", "conversion rate", "revenue per invoice"), compute it at
the **aggregate level** — `SUM(numerator) / SUM(denominator)` — not as
an average of pre-computed per-row ratios (`AVG(row_level_ratio)`).
The two produce materially different numbers and the row-level average
is almost always wrong for a business metric:

- `AVG(order_value)` weights every row equally, regardless of size.
- `SUM(order_revenue) / SUM(invoice_count)` weights by actual volume —
  the business-correct definition of "average order value".

Equally: **do not average a column that is already an aggregate**. If
a column is pre-aggregated per account-month, averaging it across
months double-collapses the grain.

**Preferred source**: if the metric page has a `## Calculation`
section, use the formula defined there — it is authoritative and may
differ from a naive `SUM/SUM`. Fall back to `SUM/SUM` only when no
`## Calculation` exists.

```sql
-- Correct: aggregate-level average order value
SELECT
    account_id,
    SUM(order_revenue) / NULLIF(SUM(invoice_count), 0) AS avg_order_value
FROM fct_account_orders
GROUP BY account_id

-- WRONG (do NOT generate): row-level average over pre-aggregated rows
-- SELECT account_id, AVG(order_value) AS avg_order_value
-- FROM fct_account_orders
-- GROUP BY account_id
```

**On execution, inspect**: a per-account average that lands suspiciously
close to a row-level mean (instead of a volume-weighted figure) is the
tell that the wrong form slipped in. Re-check the formula and re-run.

---

## 3. Grain / fan-out guardrail (compound key, no multiplication)

Every JOIN must use the **full grain key** described in the
relationship edge's `note:` field. If the note specifies a compound
key (e.g. `"JOIN on account_id, report_month"`), **all** columns of
that key must appear in the `ON` clause — never silently drop a
component of a compound key to a single column.

When two joined tables sit at **different grains** (e.g. one row per
account-day vs. one row per account-month), a JOIN without aggregation
**fans out** the finer-grained side: each coarse-grained row repeats,
so `SUM(...)` over the result double-counts. **Never SUM over
fanned-out rows.**

Remediation: aggregate the finer-grained table to the coarser grain
first (in a CTE), then JOIN.

```sql
-- fct_account_orders grain: account_id + order_date  (daily)
-- dim_account_targets  grain: account_id + target_month (monthly)
-- A direct join fans out targets by the number of days in each month:
--   SUM(monthly_target) would multiply the target value ~30×.

-- Correct: roll orders up to month first, then JOIN on the compound key
WITH monthly_orders AS (
    SELECT
        account_id,
        date_trunc('month', order_date) AS report_month,
        SUM(revenue)                    AS monthly_revenue
    FROM fct_account_orders
    GROUP BY account_id, date_trunc('month', order_date)
)
SELECT
    o.account_id,
    o.report_month,
    o.monthly_revenue,
    t.monthly_target
FROM monthly_orders AS o
JOIN dim_account_targets AS t
  ON o.account_id   = t.account_id        -- compound key: BOTH columns
 AND o.report_month = t.target_month
```

**On execution, inspect**: if the joined row count is a large multiple
of either input's row count, you have a fan-out. A measure that is ~30×
or ~84× too large is the classic symptom. Re-aggregate to a common
grain and re-run.

---

## 4. Value-grounding guardrail (match the stored value domain)

For a categorical equality filter (`WHERE region_code = ?`,
`WHERE status = ?`), check whether the entity's `## Fields` row carries
a `value_domain:` annotation for that column. A `value_domain:` lists
the **actual stored values** and their format:

```markdown
## Fields
| Business name | Column name   | Type    | Description |
|---|---|---|---|
| Region | `region_code` | varchar | Market code. `value_domain: [NL, EU, APAC]` (user terms like "Asia-Pacific" map to stored `APAC`) |
```

(The `value_domain:` annotation lives inline in the Description cell —
a body annotation, not a frontmatter key.)

**Weigh the annotation by its `(via: …)` confidence tier.** A
`value_domain` may carry a provenance marker recording *how* the values
were captured — trust accordingly:

- `(via: accepted_values)` — mirrors a dbt `accepted_values` test:
  **CI-enforced contract**; filter on it directly.
- `(via: distinct)` — sampled with `SELECT DISTINCT` at distill time:
  reliable then, but **unenforced** — the domain can drift; on a 0-row
  result, re-probe before concluding "no data".
- `(via: inferred)` — the distiller's **provisional hypothesis** (from
  code/comments, not the warehouse): verify with `SELECT DISTINCT`
  before building a filter on it.
- No `(via:)` marker — treat as `inferred` (unverified).

**If `value_domain:` is present**: filter on the recorded **stored**
value — do **not** substitute the user's natural-language term.

**If `value_domain:` is absent**: do **not** assume the user's term
equals the stored value. Either use a case-folded `ILIKE` match, or
emit your best-guess value with a comment, then **verify by executing**
a quick `SELECT DISTINCT <column> ...` against the warehouse to read
the real domain before committing to the filter.

```sql
-- User asked for "Asia-Pacific"; value_domain: [NL, EU, APAC]
-- Correct: use the stored code, not the natural-language phrase
WHERE region_code = 'APAC'

-- No value_domain recorded: probe the warehouse first, or use ILIKE
-- SELECT DISTINCT region_code FROM fct_account_monthly;  -- read real domain
-- WHERE region_code ILIKE 'AP%'

-- WRONG: the literal user phrase is not a stored value → 0 rows
-- WHERE region_code = 'Asia-Pacific'
```

**On execution, inspect**: a categorical filter returning **0 rows**
is the signature of a value-domain mismatch. Before concluding "no
data", `SELECT DISTINCT` the column, find the real stored value, fix
the filter, and re-run.

---

## 5. Source-disambiguation guardrail (pick the right model)

When **two or more candidate knowledge pages** can answer the same
business term (e.g. "revenue" exists in both an operational
`fct_account_orders` and a financial-close `fct_revenue_recognized`),
**do not silently pick one**.

1. List each candidate with its `knowledge/` page path and a one-line
   description of what it measures (from the summary or `## Definition`).
2. State the distinguishing dimension — timing basis (booking vs.
   recognition), grain (order-level vs. invoice-level), or scope (all
   channels vs. one channel).
3. Ask the user which source to use **before generating SQL** — or, if
   the question context makes intent unambiguous, pick the best match,
   generate, and **record the choice** so the user can correct it.

```
-- User asked for "monthly revenue" — two candidate sources:

-- (A) fct_account_orders   (operational)
--     booking-time revenue; grain: account_id × order_date
--     Path: knowledge/account_orders.md

-- (B) fct_revenue_recognized (financial-close)
--     recognized revenue; grain: account_id × report_month
--     Path: knowledge/revenue_recognized.md

-- They diverge on timing (booking date vs. recognition month).
-- Ambiguous — surface both, ask which basis is intended.
```

**On execution, inspect**: if two plausible sources give materially
different totals, that divergence is real signal — surface it rather
than silently trusting whichever you ran first.

---

## 6. Temporal guardrail (CURRENT_DATE, never MAX(date) as "now")

Relative temporal references ("last month", "this quarter", "YTD")
must resolve to concrete date predicates anchored on `CURRENT_DATE`
in the warehouse's dialect — **not** `MAX(date_column)`.

### 6a. Do not use MAX(date) as a proxy for "now"

Many models — revenue-recognition schedules, MRR/amortization tables,
forecast models, calendar spines — contain **forward-dated rows** for
future projected periods. In those tables `MAX(report_month)` returns a
**future** month, not the latest actual period. Never write
`WHERE date_col = (SELECT MAX(date_col) FROM ...)` for a relative-time
filter without checking the date-semantics caveat first.

### 6b. Resolve relative time against CURRENT_DATE

| Expression | SQL (CURRENT_DATE-anchored) |
|---|---|
| last month | `date_trunc('month', CURRENT_DATE) - interval '1 month'` |
| this month | `date_trunc('month', CURRENT_DATE)` |
| this year | `date_trunc('year', CURRENT_DATE)` |
| last year | `date_trunc('year', CURRENT_DATE) - interval '1 year'` |
| last N days | `CURRENT_DATE - interval 'N days'` |

For period-grain tables, compare with `>=` and `<` against the
truncated boundary, not point equality.

### 6c. Honor date-semantics caveats from the knowledge page

Before emitting a date filter, read the entity/metric page's
`## Caveats` section:

- If it documents **forward-dated rows** ("report_month extends through
  the end of the contracted term"), use a `CURRENT_DATE`-anchored
  predicate; do **not** use `MAX(date_col)`.
- If it documents a **snapshot lag** / reporting cutoff, subtract the
  documented lag from the anchor.
- If no `## Caveats` exists but the model name suggests
  recognition / amortization / forecast, default to a
  `CURRENT_DATE`-anchored filter and note the assumption.

```sql
-- fct_account_monthly is an amortization schedule with forward-dated rows.
-- WRONG: MAX(report_month) forward-dates to a future month
-- WHERE report_month = (SELECT MAX(report_month) FROM fct_account_monthly)

-- Correct: anchor on CURRENT_DATE
WHERE report_month = date_trunc('month', CURRENT_DATE) - interval '1 month'
```

**On execution, inspect**: a "latest period" / "last month" query that
returns a **future** date (e.g. a month later than today) is the
forward-amortization trap. Switch to the `CURRENT_DATE` anchor and
re-run.

---

## 7. Dialect

Generate SQL in the warehouse's dialect. The bundle's `knowledge/`
records the project's adapter (e.g. `redshift`, `postgres`,
`snowflake`, `bigquery`); use its `CURRENT_DATE` / `date_trunc` /
interval syntax. When uncertain, your warehouse tool is the ground
truth — run a trivial probe (`SELECT CURRENT_DATE`) to confirm dialect
behavior before relying on it.

The summary checklist lives at the **top of this file** ("Pre-flight
checklist") — scan it per question; every box must hold before you
trust an answer.
