# prompt-assembly.md — SQL Generation Prompt Assembly Spec

This file defines how `to-sql` builds the LLM prompt from the pages
retrieved in Step 1 (retrieval procedure defined in `retrieval.md`).
The prompt carries all schema context, linking rules, and the output
contract the model must satisfy. Follow this spec exactly — the prompt
shape directly determines whether the generated SQL is statically valid.

Referenced from: `SKILL.md § Step 2`

---

## 1. Schema-Linking

**Schema-linking** is the process of mapping business terms in the user's
question to the concrete entity fields and physical column names that
appear in dbt models.

### 1a. Term resolution from knowledge pages

For each business term in the question (e.g. "store", "online GMV",
"last month"):

1. Locate the matching entity or metric knowledge page under
   `.dbt-wiki/entities/` or `.dbt-wiki/metrics/`.
2. Read its `## Fields` section. Every entity knowledge page contains a
   `## Fields` table with this shape:

   | Business name | Column name | Type | Description |
   |---|---|---|---|
   | Store ID | `store_id` | varchar | Unique identifier per store |
   | ...       | ...         | ...  | ...                        |

   The **Business name** column is the schema-linking key — match against
   it case-insensitively and allow common synonyms (e.g. "shop" → "Store").
   The **Column name** column is the physical SQL identifier to use.

3. If a term matches multiple fields across multiple entities, collect all
   candidates and carry them into the join-path step (§3) to resolve which
   physical table to SELECT from.

### 1b. Evidence column grounding

After resolving via the knowledge page, confirm the column exists in the
evidence layer:

- Load the `_evidence/models/<model>.md` page listed in the entity or
  metric's `## Evidence` section.
- The evidence page's `## Columns` table carries the real column names
  extracted from `manifest.json` (and type information from `catalog.json`
  if present).
- Use the column name as it appears in the evidence page — do NOT
  synthesize or guess column names not present there.

If a business term cannot be resolved to any `## Fields` entry and does
not appear in any evidence page, stop and ask the user to clarify before
generating SQL.

---

## 2. Column-Card Use (Materialized Columns Preference)

When a metric knowledge page contains a `## Materialized Columns` section,
that section maps pre-computed business-measure variants to their physical
`model.column` location. This mapping is the product of the metric-card
work (landed in PR #364).

**Rule: prefer SELECT over synthesize.**

If the user's question can be answered by SELECTing a pre-materialized
column, do so directly — do NOT write an aggregation or GROUP BY to
re-derive a measure that is already materialized.

Example:

```
## Materialized Columns
| Business variant | Physical location         |
|---|---|
| GMV (online)     | fct_gmv_daily.gmv_online  |
| GMV (store)      | fct_gmv_daily.gmv_store   |
```

For a question asking for "online GMV", generate:

```sql
SELECT store_id, date, gmv_online
FROM fct_gmv_daily
WHERE ...
```

NOT:

```sql
SELECT store_id, date, SUM(revenue) AS gmv_online
FROM orders
WHERE channel = 'online'
GROUP BY store_id, date
```

**Fallback**: if no `## Materialized Columns` mapping exists, derive the
SQL from the metric's `## Calculation` section and the underlying evidence
model's SQL (schema-linked per §1).

---

## 3. Join-Path Assembly

Derive table joins from the knowledge pages' typed relationship edges.
Do NOT guess foreign-key names or assume join conditions not present in
the knowledge base.

### 3a. Edge sources

Knowledge pages carry a `relationships:` frontmatter block and a
`## Relationships` body section. Three edge types are relevant for
join-path derivation:

| Edge type    | Meaning for SQL generation |
|---|---|
| `measures`   | Metric is computed over an entity; the entity page names the grain table |
| `depends_on` | Metric or entity depends on a concept that defines a filter or business rule |
| `joins`      | Explicit join path between two entity pages; the edge's `note:` field describes the join key |

### 3b. Join derivation procedure

For each relationship edge relevant to the question:

1. Load the linked knowledge page.
2. Extract the join key from the edge's `note:` field. The note should
   name the column(s) used (e.g. `"JOIN on customer_id"`).
3. Confirm the join column exists in both `_evidence/` model pages
   (schema-linking via §1b).
4. Emit a JOIN clause using the confirmed physical column names.

If an edge exists but its `note:` does not specify the join key, load
the `_evidence/` pages for both sides and inspect their `## Column
Lineage Chains` or `## Columns` sections to find common key columns.
If no shared key can be confirmed from the evidence layer, include an
inline SQL comment marking the join condition as **unresolved** and
surface it in the output's validation notes.

### 3c. Join ordering

Start from the primary grain table (the model named in the `measures`
edge of the target metric), then JOIN in the dependent entity tables
in dependency order. Avoid Cartesian joins — every JOIN must have an
ON condition derived from steps above.

---

## 4. Temporal Grounding

Relative and temporal references in a business question ("上個月", "last
month", "this quarter", "YTD") must be resolved to concrete date predicates
before SQL is generated. Naively using `MAX(date_column)` as a proxy for
"the latest actual period" is **incorrect for many dbt tables**.

### 4a. Do not use MAX(date) as a proxy for "now"

Many dbt models — revenue recognition schedules, MRR amortization tables,
forecast models, calendar spines — contain **forward-dated rows** that
represent future projected periods. In those tables `MAX(report_month)` or
`MAX(date)` returns a future month, not the latest actual period. Never
emit `WHERE date_col = (SELECT MAX(date_col) FROM ...)` for a relative-time
filter without checking the date-semantics caveat first.

### 4b. Resolve relative time expressions against CURRENT_DATE

Translate natural-language temporal references to explicit date arithmetic
using `CURRENT_DATE` in the project's adapter dialect (resolved per §7
dialect rule):

| Expression (ZH / EN) | SQL (Redshift / Postgres) |
|---|---|
| 上個月 / last month | `date_trunc('month', CURRENT_DATE) - interval '1 month'` |
| 本月 / this month | `date_trunc('month', CURRENT_DATE)` |
| 今年 / this year | `date_trunc('year', CURRENT_DATE)` |
| 去年 / last year | `date_trunc('year', CURRENT_DATE) - interval '1 year'` |
| 近 N 天 / last N days | `CURRENT_DATE - interval 'N days'` |

For period-grain tables (monthly, quarterly) compare with `>=` and `<`
against the truncated boundary, not point equality, unless a single month
row is the intended grain.

### 4c. Honor date-semantics caveats from the knowledge page

Before generating a date filter, check the relevant entity or metric
knowledge page's `## Caveats` section:

- If it documents that the period column contains **forward-dated rows**
  (e.g. "report_month extends through the end of the contracted term"), use a
  `CURRENT_DATE`-anchored predicate and do NOT use `MAX(date_col)`.
- If it documents a **snapshot lag** or **reporting cutoff**, adjust the
  anchor accordingly (e.g. subtract the documented lag in days).
- If no `## Caveats` section exists but the table name or metric name
  suggests a recognition / amortization / forecast model, default to a
  `CURRENT_DATE`-anchored filter and note the assumption in the output
  (§8e Temporal assumptions).

### 4d. NULL-aware ranking and ordering

When the question asks for **top N**, **highest/lowest**, or any ranking
by a measure that can be NULL (revenue, SRR, count, etc.), the generated
SQL **must** guard NULLs explicitly. Do NOT rely on the adapter's default
NULL-ordering behavior — it varies across dialects and the default is
often the wrong choice:

| Adapter | ASC default | DESC default |
|---|---|---|
| Redshift / Postgres | NULLS LAST | **NULLS FIRST** |
| BigQuery | NULLS LAST | NULLS LAST |
| Snowflake | NULLS LAST | NULLS LAST |

**Consequence without guarding**: A `TOP N by revenue ORDER BY revenue
DESC` query in Redshift returns rows with NULL revenue ranked first —
because NULLS FIRST is the Redshift/Postgres default for DESC. "Top 3
customers by revenue" would surface 3 customers with no revenue value at
all.

**Required behavior** — apply whichever guard fits the intent:

1. **Existence-required ranking** ("top N" implies the measure must
   exist): add `WHERE <measure> IS NOT NULL` before the ORDER BY.
   This is the correct choice when a NULL measure means the row is not
   a valid candidate (e.g., a customer with no recorded revenue should
   not appear in a "top customers by revenue" list).

2. **Explicit NULL placement** (NULLs are valid rows but should sort
   last): use `ORDER BY <measure> DESC NULLS LAST` (or `ASC NULLS
   FIRST` for ascending). Use this when NULLs represent a known-missing
   value that should be retained in the result but ranked below
   non-NULL rows.

When a NULL guard is applied, note it in the output's NULL-ordering
assumptions section (§8f).

### 4e. Aggregate Semantics

When a question asks for a ratio or average measure (e.g. "average order
value", "conversion rate", "revenue per invoice"), use an **aggregate-level
formula** — `SUM(numerator) / SUM(denominator)` — not an average of
pre-computed per-row ratios (`AVG(row_level_ratio)`). The two produce
materially different results and the latter is almost always wrong for
business metrics:

- `AVG(order_value)` averages each row's value, weighting every row
  equally regardless of the invoice amount.
- `SUM(order_revenue) / SUM(invoice_count)` weights by actual volume,
  which is the business-correct definition of "average order value".

**Preferred source**: if the metric knowledge page contains a
`## Calculation` section, use the formula defined there — it is the
authoritative definition and may differ from a naive `AVG`. Only fall
back to the `SUM/SUM` form when no `## Calculation` section exists.

**Assumption surface**: whenever the aggregate-level form is used (rather
than a materialized column), state the formula as an assumption in the
output — see §8i Aggregation-form assumptions.

Example (synthetic):

```sql
-- Correct: aggregate-level average order value
SELECT
    store_id,
    SUM(order_revenue) / NULLIF(SUM(invoice_count), 0) AS avg_order_value
FROM fct_orders_daily
GROUP BY store_id

-- WRONG: row-level average (do NOT generate this form)
-- SELECT store_id, AVG(order_value) AS avg_order_value
-- FROM fct_orders_daily
-- GROUP BY store_id
```

### 4f. Join Grain / Fan-out

Every JOIN must use the **full grain key** as described in the
relationship edge's `note:` field. If the note specifies a compound key
(e.g. `"JOIN on customer_id, month"`), all columns of that key must
appear in the `ON` clause — never silently drop components of a compound
key to a single column.

When two joined tables operate at **different grains** (e.g. one row per
store-day vs. one row per store-month), a JOIN without aggregation fans
out the finer-grained table. **Never SUM over fanned-out rows** — the
result will double-count because each fine-grained row repeats the
coarser-grained measure.

The correct remediation is to aggregate the finer-grained table to the
coarser grain first (in a CTE or subquery), then JOIN.

When a grain mismatch is detected, warn in the output's validation notes
(§8c) even if the SQL is structurally valid. State the join grain key used
(and any grain-mismatch handling) as an assumption — see §8j Join-grain
assumptions.

Example (synthetic):

```sql
-- fct_orders has grain: store_id + order_date (daily)
-- dim_store_targets has grain: store_id + target_month (monthly)
-- Joining directly would fan out dim_store_targets by the number of days
-- in each month: SUM(monthly_target) would multiply the target value.

-- Correct: aggregate orders to month first, then JOIN
WITH monthly_orders AS (
    SELECT
        store_id,
        date_trunc('month', order_date) AS order_month,
        SUM(revenue)                    AS monthly_revenue
    FROM fct_orders
    GROUP BY store_id, date_trunc('month', order_date)
)
SELECT
    o.store_id,
    o.order_month,
    o.monthly_revenue,
    t.monthly_target
FROM monthly_orders AS o
JOIN dim_store_targets AS t
  ON o.store_id    = t.store_id        -- compound key: both columns required
 AND o.order_month = t.target_month
```

### 4g. Value Grounding

For a categorical equality filter (e.g. `WHERE region = ?`, `WHERE city = ?`),
check whether the relevant entity knowledge page's `## Fields` section carries
a `value_domain:` annotation for that column. A `value_domain:` annotation
lists the actual stored values and their format:

```markdown
## Fields
| Business name | Column name   | Type    | Description |
|---|---|---|---|
| Region | `region_code` | varchar | ISO market code. `value_domain: [NL, EU, APAC]` (user terms like "Northland"/"Northland" map to stored `NL`) |
```

(The `value_domain:` annotation is inline in the field's Description/Meaning
cell — a body annotation, matching `assets/SCHEMA.md` and `distill-entities.md`;
it is NOT a frontmatter key.)

**If a `value_domain:` annotation is present**: use the recorded stored value
directly in the equality filter — do NOT substitute the user's natural-language
term.

**If no `value_domain:` annotation is present**: do NOT assume the user's
natural-language term equals the stored value. Apply one of:

1. **`ILIKE` / case-folded match**: when stored format is unknown and an
   approximate match is acceptable (`WHERE region_code ILIKE 'TW%'`).
2. **Normalization note**: emit a SQL comment `-- VALUE ASSUMPTION: <user_term>
   mapped to stored value '<stored_value>' — verify against actual data` on the
   filter line, and surface the mapping in the output's value-mapping assumptions
   (§8g).

Example (synthetic):

```sql
-- User asked for "Northland" stores; knowledge page value_domain: [NL, EU, APAC]
-- Correct: use the stored code, not the natural-language term
WHERE region_code = 'NL'

-- Without value_domain: use ILIKE or emit assumption comment
-- WHERE region_code ILIKE 'TW%'
-- or: WHERE region_code = 'NL' -- VALUE ASSUMPTION: "Northland" mapped to 'NL'

-- WRONG: literal user term (not present in the column)
-- WHERE region_code = 'Northland'
```

Similarly for city fields:

```sql
-- User asked for "Eastport"; knowledge page value_domain: [Eastport City, Westport City, Northgate City]
WHERE city = 'Eastport City'   -- stored value; not 'Eastport'
```

Whenever a value mapping is applied, state it in the output's value-mapping
assumptions (§8g).

### 4h. Source Disambiguation

When **two or more candidate knowledge pages** can answer the same business
term (e.g. a metric called "revenue" exists in both an operational
`fct_orders` entity and a financial-close `fct_revenue_recognized` entity),
**do NOT silently pick one**. Surface both candidates with their basis so
the user can confirm the intended source.

**Required behavior**:

1. List each candidate source with its knowledge-page path and a brief
   description of what it measures (from the page's summary line or
   `## Definition`).
2. State the distinguishing dimension — e.g. timing basis (booking vs.
   recognition), grain (order-level vs. invoice-level), or scope
   (all channels vs. online-only).
3. Ask the user which source to use **before generating SQL**, or — if the
   question context makes the intent unambiguous — pick the best match,
   generate SQL using it, and record the choice in the output's source
   assumptions (§8h).

Example (synthetic):

```
-- User asked for "monthly revenue"
-- Two candidate sources found:

-- (A) fct_orders_daily (operational)
--     Measures: booking-time revenue; grain: store × order_date
--     Path: .dbt-wiki/entities/orders.md

-- (B) fct_revenue_recognized (financial-close)
--     Measures: recognized revenue per IFRS 15; grain: store × recognition_month
--     Path: .dbt-wiki/entities/revenue_recognized.md

-- These diverge on timing (booking date vs. recognition month).
-- Ambiguous — surface both and ask the user which basis is intended.
```

Whenever a source is chosen from multiple candidates, record it in the
output's source assumptions (§8h).

---

## 5. Few-Shot Slot

**v1 ships zero-shot. This slot is intentionally empty.**

The prompt template below contains a clearly delimited few-shot section.
In v1, no examples are inserted. The slot is preserved so the later
gold-example increment (planned in `docs/code-toolkit/specs/2026-06-02-dbt-wiki-gold-example-bank.md`)
can populate it without modifying the prompt structure.

```
<!-- FEW-SHOT EXAMPLES — populated by the gold-example increment; empty in v1 -->
<!-- EXAMPLES START -->
<!-- EXAMPLES END -->
```

When examples are added (future increment), each example must follow this
shape:

```
<!-- EXAMPLE -->
Question: <business question in plain language>
Context pages: <list of knowledge/evidence page paths used>
SQL:
```sql
<the gold SQL>
```
<!-- /EXAMPLE -->
```

**Do not insert any examples here in v1.** Do not fabricate examples.
Providing an empty slot is the correct v1 state.

---

## 6. Prompt Template

Assemble the prompt in this order. Every section marked `[REQUIRED]`
must be present; sections marked `[CONDITIONAL]` are included only when
the relevant data was retrieved.

```
You are a SQL generator for a dbt project. Generate a single, runnable
SQL query that answers the business question below. Use only the schema
context provided — do not invent table names, column names, or join keys
not listed here.

## Dialect
[REQUIRED] Generate SQL in the <ADAPTER_DIALECT> dialect.
(Derived from manifest.json `metadata.adapter_type`; see §7.)

## Business Question
[REQUIRED] <the user's verbatim question>

## Schema Context

### Entities
[REQUIRED if any entity pages were retrieved]
<For each entity knowledge page, include:
 - Entity name + summary
 - The ## Fields table (business name → column name)
 - The physical model name from ## Evidence>

### Metrics
[CONDITIONAL — include if any metric pages were retrieved]
<For each metric knowledge page, include:
 - Metric name + definition summary
 - ## Materialized Columns table (if present)
 - ## Calculation summary (if no materialized column covers the question)
 - The physical model(s) from ## Evidence>

### Relationships / Join Paths
[CONDITIONAL — include if join edges were resolved]
<For each resolved join path:
 - Left table.column = Right table.column (edge note)>

### Evidence Columns
[CONDITIONAL — include if evidence pages were loaded for column confirmation]
<For each evidence model loaded, list its column names>

## Few-Shot Examples
<!-- EXAMPLES START -->
<!-- EXAMPLES END -->

## Temporal Grounding
Apply the temporal-grounding rule (§4) for all relative/temporal references:
resolve against CURRENT_DATE, not MAX(date_column). If you must assume a
temporal anchor (e.g. no Caveats section present), emit a SQL comment
`-- TEMPORAL ASSUMPTION: <description>` on the relevant predicate line.

## NULL-aware Ordering
Apply the NULL-ordering rule (§4d) for any ranking, top-N, or highest/lowest
query. Do NOT rely on the adapter's default NULL ordering — in Redshift/Postgres,
DESC sorts NULLS FIRST by default, which will rank NULL-measure rows at the top.
Either add `WHERE <measure> IS NOT NULL` (when NULLs disqualify a row) or
append `NULLS LAST` / `NULLS FIRST` explicitly to the ORDER BY clause.
If a NULL guard was applied, emit a SQL comment
`-- NULL GUARD: <measure> IS NOT NULL — rows with no <measure> excluded`
or `-- NULL ORDER: NULLS LAST applied — dialect default overridden`
on the relevant clause.

## Semantic Guardrails
Apply all four semantic guardrails (§4e–§4h) before generating SQL:
- **Aggregate semantics (§4e)**: for ratio/average measures use
  `SUM(numerator)/SUM(denominator)`; prefer the metric's `## Calculation`
  if defined; never use `AVG(row_level_ratio)`.
- **Join grain / fan-out (§4f)**: use the full compound grain key from the
  edge `note:`; never JOIN tables at different grains without first aggregating
  the finer-grained table; never SUM over fanned-out rows.
- **Value grounding (§4g)**: for categorical equality filters use the
  `value_domain:` stored value if recorded; otherwise use `ILIKE` or emit a
  `-- VALUE ASSUMPTION:` comment; never assume user term = stored value.
- **Source disambiguation (§4h)**: when ≥2 candidate sources answer the same
  business term, surface both with their basis; do not silently pick one.
Record each guardrail that fired in the output assumptions (§8e–§8j).

## Output Requirements
- Return only a valid SQL query. No explanation, no markdown fences.
- Use table aliases where joins are present.
- Reference only the schema context above.
- If a term cannot be resolved, emit a SQL comment `-- UNRESOLVED: <term>`
  in the position where the expression would appear.
```

---

## 7. Dialect Rule

Generate SQL in the dialect of the project's dbt adapter.

**Procedure:**

1. Read `manifest.json` at `metadata.adapter_type`.
2. Pass the adapter name to sqlglot's dialect parameter. The mapping is:
   - `postgres` → `postgres`
   - `redshift` → `redshift`
   - `snowflake` → `snowflake`
   - `bigquery` → `bigquery`
   - `databricks` / `spark` → `databricks`
   - `trino` / `presto` → `trino`
   - Any other value → pass the value as-is to sqlglot; sqlglot will
     fall back to ANSI if unrecognized.
3. State the resolved dialect in the `## Dialect` prompt section (§6).
4. Do NOT assume a dialect (e.g. do not default to Postgres). If
   `metadata.adapter_type` is absent from the manifest, include a
   `## Dialect` note: "adapter unknown — generating ANSI SQL" and pass
   `dialect=None` to sqlglot for validation.

---

## 8. Output Contract

`to-sql` returns a structured result with the following fields. All
fields are required; validation and drift fields must be populated even
when they carry a passing/empty value.

### 8a. Generated SQL

```
## SQL
```sql
<the generated SQL string>
```
```

The SQL must have passed the sqlglot parse step in `assets/validate_sql.py`
before being returned. If sqlglot parse fails, return the error in the
validation section (§8c) instead of a SQL block and ask the user to clarify
the question.

### 8b. Knowledge pages cited

```
## Sources
- [<page title>](<relative path from WIKI_DIR to the .dbt-wiki/ page>)
- ...
```

List every knowledge page (entities, metrics, concepts) and every evidence
page loaded during retrieval and prompt assembly. Omit pages that were
loaded only for drift-check purposes and did not contribute schema context.

### 8c. Static validation result

```
## Validation
Status: PASS | PARTIAL | FAIL
Parse: OK | <sqlglot error message>
Missing tables: <list of table names not found in manifest, or "none">
Missing columns: <list of model.column pairs not found in manifest, or "none">
```

Run `assets/validate_sql.py` against the generated SQL and the current
`manifest.json`. Populate all four lines. A result is PASS only when
parse succeeds AND both missing-tables and missing-columns are "none".
PARTIAL means parse succeeded but one or more refs were not found in the
manifest — surface the missing refs and explain likely causes (e.g. the
model is not in the target schema, or the column is defined only in
`catalog.json` which was not present).

### 8d. Drift caveat

Include this section whenever the wiki's recorded `manifest_sha` (from
`.dbt-wiki/log.md`) differs from the sha of the current `manifest.json`:

```
## Drift Notice
The wiki was last refreshed against manifest sha <WIKI_SHA>.
The current manifest sha is <CURRENT_SHA>.
Static validation ran against the CURRENT manifest, but schema-linking
used knowledge pages that may reflect an older model structure.
Run /dbt-wiki:refresh to re-sync the knowledge base.
```

If the shas match, omit this section entirely.

### 8e. Temporal assumptions

Include this section whenever a temporal anchor was inferred rather than
read directly from a knowledge-page `## Caveats`:

```
## Temporal Assumptions
- <date_column> in <model>: resolved "上個月" to
  date_trunc('month', CURRENT_DATE) - interval '1 month'
  (knowledge page carries no Caveats; table appears to be a recognition
  schedule — MAX(date_col) not used to avoid forward-dated row risk)
```

If all temporal references were fully grounded by explicit knowledge-page
caveats, or if the question contained no relative temporal references,
omit this section.

### 8f. NULL-ordering assumptions

Include this section whenever a NULL guard was applied to a ranking or
ordering clause:

```
## NULL-Ordering Assumptions
- <measure> in <model>: WHERE <measure> IS NOT NULL applied —
  rows with no <measure> value excluded from ranking
  (Redshift DESC default is NULLS FIRST; without this filter,
  NULL-<measure> rows would rank at the top of "top N" results)
```

Or, if `NULLS LAST` was used instead of a filter:

```
## NULL-Ordering Assumptions
- <measure> in <model>: ORDER BY <measure> DESC NULLS LAST applied —
  dialect default (NULLS FIRST for Redshift DESC) overridden explicitly
```

If the query contains no ranking or ordering by a nullable measure,
omit this section.

### 8g. Value-mapping assumptions

Include this section whenever a categorical filter value was mapped from the
user's natural-language term to a stored value (either via a recorded
`value_domain:` annotation or via an `ILIKE` / assumed-value approach):

```
## Value-Mapping Assumptions
- <column> in <model>: user term "<user_term>" mapped to stored value
  '<stored_value>' (value_domain recorded in knowledge page)
```

Or, when no `value_domain:` was available:

```
## Value-Mapping Assumptions
- <column> in <model>: user term "<user_term>" — no value_domain recorded;
  used ILIKE match / assumed stored value '<stored_value>' — verify against
  actual data
```

If no categorical equality filters were applied, or all filtered columns
have unambiguous stored values matching the user's term exactly, omit
this section.

### 8h. Source-choice assumptions

Include this section whenever a specific source was chosen from two or more
candidate knowledge pages that could answer the same business term:

```
## Source Assumptions
- "<business_term>" resolved to: <page title> (<relative path>)
  Basis: <one-sentence description of what this source measures>
  Alternatives considered: <page title> (<path>) — <distinguishing dimension>
```

If the source selection was unambiguous (only one candidate matched the
business term), omit this section.

### 8i. Aggregation-form assumptions

Include this section whenever a derived ratio / average was computed and the
aggregation form was not fixed by a materialized column — i.e. the §4e
aggregate-semantics guardrail fired:

```
## Aggregation Assumptions
- "<measure>" computed as: <aggregate-level SUM(num)/SUM(denom) | metric-page formula | avg-of-row-ratios>
  Why: <e.g. "no ## Calculation defined; defaulted to aggregate-level SUM/SUM">
```

If the measure was a direct pre-materialized column (no aggregation choice),
omit this section.

### 8j. Join-grain assumptions

Include this section whenever a JOIN was emitted and the §4f grain guardrail
applied — state the grain key used and any grain-mismatch handling:

```
## Join-Grain Assumptions
- Joined <table A> ⋈ <table B> on: <full grain key, e.g. account_id + report_month>
  Source: <relationship edge note that supplied the key>
  Grain note: <e.g. "both at customer×month grain — no fan-out" | "grain mismatch: aggregated B to A's grain before join">
```

If no JOIN was emitted (single-table query), omit this section.
