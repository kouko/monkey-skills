# distill-metrics.md — Metric Distillation Spec (Phase B)

This file defines the procedure for Phase B metric distillation. Init
follows this procedure to produce `metrics/` knowledge pages from the
evidence layer. Do NOT invent procedure that contradicts this spec or
SCHEMA.md.

Referenced from: `SKILL.md § Phase B step 3`

---

## 1. What Is a Business Metric?

A **business metric** is a scalar or time-series business measure that
aggregates rows from one or more entities to answer a performance
question — "how much?", "how many?", "at what rate?". Metrics are
distinct from entities (which describe objects) and concepts (which
describe rules).

Signals that a column or model represents a metric rather than an
entity attribute:

- The column name contains measurement vocabulary: `revenue`, `mrr`,
  `arr`, `ltv`, `gmv`, `churn`, `rate`, `count`, `conversion`,
  `retention`, `nrr`, `acv`, `cac`, `arpu`, `margin`.
- The model is in a mart layer (`models/marts/`, `models/reporting/`,
  `models/finance/`) and its SELECT includes aggregate functions:
  `SUM(...)`, `COUNT(...)`, `AVG(...)`, `COUNT(DISTINCT ...)`.
- The model has a `GROUP BY` clause establishing a measurement grain
  (typically a time period + an entity key).
- The schema.yml description says "measures", "calculates", "tracks",
  "rate of", or "total".
- The model feeds an exposure (BI tool / dashboard) directly.

One evidence model can produce multiple metrics (e.g. `fct_mrr.sql`
computes `new_mrr`, `expansion_mrr`, `churned_mrr`, `net_mrr`). Each
distinct business measure gets its own `metrics/` page.

**Reporting-period variants are ONE metric, not many.** A mart model
often outputs a single base measure across many time windows: daily,
MTD, QTD, YTD, MoM growth, YoY growth, last-month, last-year — easily
20 columns for one measure. These are all reporting-period views of the
same underlying business measure. Produce ONE metric page and describe
the period variants inside `## Calculation`. Do NOT create 20
near-duplicate pages. Fork a new page only for a genuinely distinct
business measure (e.g. `new_mrr` vs `churned_mrr`), never for a
time-window view of the same measure.

---

## 2. MetricFlow Branch (authoritative ingest)

**Check for MetricFlow / dbt Semantic Layer definitions first** before
deriving anything from SQL.

### 2a. Detection

In `manifest.json`, check for a top-level `"semantic_models"` key —
MetricFlow (dbt Semantic Layer) always populates it. Gate on this key
alone:

```python
has_metricflow = bool(manifest.get("semantic_models"))
```

**Do NOT gate on the `"metrics"` key.** Legacy dbt (≤1.5) projects can
declare `metrics:` YAML *without* MetricFlow — those manifests carry a
non-empty `metrics` key but NO `semantic_models`. Routing them into the
ingest branch would reference an absent `semantic_models` block. A bare
`metrics` key without `semantic_models` is the legacy path and belongs
in the SQL-derivation branch. Only the co-presence of `semantic_models`
+ `metrics` indicates MetricFlow.

If `has_metricflow` is true, take the **MetricFlow ingest branch (§2b)**.
Otherwise, take the **SQL-derivation branch (§3)**.

### 2b. MetricFlow Ingest Branch

When the project defines Semantic Layer resources, **ingest them as
authoritative** — do NOT re-derive definitions from raw SQL.

For each entry in `manifest["metrics"]`:

| Manifest field | Maps to page section |
|---|---|
| `name` | kebab-case slug + `title` frontmatter |
| `description` | `## Definition` body |
| `type` (`simple` / `ratio` / `cumulative` / `derived`) | mention in `## Calculation` |
| `type_params.measure` (for simple metrics) | `## Calculation` — the aggregate expression |
| `type_params.numerator` / `denominator` (ratio) | `## Calculation` |
| `filter` | `## Caveats` — note the filter condition in plain language |
| `dimensions` (from parent semantic_model) | `## Relationships` — `measures` edge to the entity |
| `label` | use as `title` if present, else humanize `name` |

For each metric, find its parent `semantic_model` (via
`manifest["semantic_models"]` — the semantic model that contains the
`measure` this metric references). The semantic model's `node_relation`
field names the underlying dbt model. Record that model's `unique_id`
in `derived_from:`.

**Do NOT generate or author MetricFlow specs.** Only read what the
project already declared. If a metric definition is ambiguous in the
manifest, represent what is written — do not speculate about intent.

---

## 3. SQL-Derivation Branch (when MetricFlow is absent)

Use this branch when `has_metricflow` is false.

### 3a. Identify metrics from evidence

Scan `_evidence/models/` pages (built by Phase A). For each model, look
for metric signals (§1). Candidate identification heuristics in order of
confidence:

1. **Aggregate SELECT + GROUP BY** in compiled SQL — highest confidence.
   Example: `SUM(revenue) ... GROUP BY date_trunc('month', created_at), customer_id`
2. **schema.yml description** mentioning measurement vocabulary — medium
   confidence. Example: `description: "Monthly recurring revenue per customer"`.
3. **Column name pattern** matching measurement vocabulary in a mart-layer
   model — lower confidence. Confirm by checking SQL before creating a page.

For each confirmed metric candidate, determine:

- **Name**: the business name (not the SQL column name). Derive from
  schema.yml description or column name. Examples: `monthly_recurring_revenue`,
  not `mrr_usd`; `customer_churn_rate`, not `pct_churned`. The business
  name maps to the file slug by replacing underscores with hyphens per
  §8 (`monthly_recurring_revenue` → `monthly-recurring-revenue.md`).
- **Grain**: what the `GROUP BY` aggregates over — time period, entity key,
  or both. State as "one row per `<grain>`".
- **Aggregation**: `SUM`, `COUNT`, `AVG`, `COUNT DISTINCT`, ratio, etc.
- **Source model**: which evidence model computes this metric
  (`unique_id` from manifest).

### 3b. Group metrics by source model

One `fct_` or `rpt_` model often computes several related metrics. Group
them by source model to avoid redundant `derived_from` lookups. Create
one page per distinct business measure, but all pages from the same model
share the same `derived_from` entry.

**Segment-qualified parallel models = ONE metric page + a segment
concept.** When two or more structurally parallel models compute the
same business measure for different segments (e.g. `sales__total` for
total revenue vs `sales__online_channel` for a single channel's revenue),
produce ONE metric page that covers both segment variants. List both
models in `derived_from:`. Capture the segment split itself as a
`concepts/` page (e.g. `channel-segment.md`) and link it from the metric
page via a `depends_on` edge. Do NOT fork one metric page per segment —
that creates near-duplicate pages that diverge over time.

## 4. Definition Section

Write `## Definition` in plain language. Explain:

- **What the metric measures** — the business question it answers.
- **Why it matters** — why a business stakeholder cares about this number.
- **Unit** — is it a currency amount, a count, a percentage, a ratio?
- **Reporting grain** — over what time period and entity is it typically
  reported (e.g., per month per account, per week per cohort)?

Do NOT paste raw SQL. Do NOT use column names as the explanation.

Example (churn rate):

> Measures the fraction of active customers who cancelled during a period.
> A rising churn rate signals that the product is losing customers faster
> than it retains them. Reported as a percentage, typically monthly.

---

## 5. Calculation Section

### Materialization check (run before writing Calculation)

Before drafting `## Calculation`, decide whether the metric's variants
are already **pre-materialized into physical mart columns** — values
fully computed at build time; a consumer query only needs `SELECT col`,
no query-time `GROUP BY`.

**Anchor signals (check both):**

- **Signal 2 — column forest**: the model exposes five or more sibling
  columns for the same base measure, differing only by period or segment
  suffix. This is the reporting-period variant forest described in §1
  (many sibling columns for one measure — e.g. `gmv_mtd`, `gmv_ytd`,
  `gmv_mom`, `gmv_l30d`, `gmv_online`). Unlike §1's general note, five
  or more physical pre-built sibling columns is the threshold that
  confirms materialization.
- **Signal 4 — pre-aggregated grain**: the model is already at a wide,
  one-row-per-(entity/period) grain where aggregation happened at build
  time. The final SELECT has no `GROUP BY`, or its `GROUP BY` covers
  only key dimensions (e.g. `store_id, date`) — not measure sums.

Signals 1 (mart/reporting layer) and 3 (schema.yml stored-value
description) are **corroborating only** — they do NOT trigger
materialization alone.

**Deciding test:**

| Scenario | Verdict |
|---|---|
| Consumer query is `SELECT gmv_mtd FROM mart_store_metrics WHERE store_id = X AND date = Y` — no aggregation needed | **Pre-materialized** → materialization fires |
| Consumer query must `SELECT SUM(revenue) FROM fct_orders WHERE store_id = X GROUP BY date_trunc('month', order_date)` | **Still needs aggregation** → materialization does NOT fire |

**Routing:**

- **Fires** (signal 2 OR signal 4 present): write `## Calculation` as
  "value is pre-computed and stored — SELECT the mapped column from
  `## Materialized Columns`, no query-time `GROUP BY` needed"; emit the
  `## Materialized Columns` section (§5b). Do NOT author a
  numerator/denominator formula for the materialized variants.
- **Signals 1 + 3 only** (mart layer + schema.yml description, but no
  column forest and no pre-aggregated grain): materialization does NOT
  fire. Proceed with the formula path or fallback prose below.
- **Does not fire**: proceed with the formula path or fallback prose
  below. Do NOT add a `## Materialized Columns` section.

**One-page rule is unchanged.** Materialization does not fork pages —
it only changes how `## Calculation` is written and adds `## Materialized
Columns` to the same page (§1: "one metric = one page").

---

Write `## Calculation` in plain language. Cover:

1. **The formula in words** — describe the numerator and denominator (for
   rates / ratios), or the aggregation and its filter conditions (for
   sums / counts). Reference the metric `type` if MetricFlow was ingested.
2. **The measurement grain** — what one output row represents.
3. **Key edge cases or gotchas** — NULLs, division-by-zero guards,
   currency conversions, trial-period exclusions, etc. These move to
   `## Caveats` if they are data-quality issues rather than algorithmic
   choices.

Example (churn rate):

> Churn rate = (customers who cancelled in period) / (customers active at
> period start). Computed monthly: the denominator is the customer count
> on the first day of the month; the numerator counts distinct customers
> whose `cancelled_at` falls within that calendar month. Customers who
> cancelled and reactivated in the same month are excluded (see the
> "active customer" concept for the reactivation rule).

Cite the SQL model where this logic lives, but do not dump raw SQL inline.
The evidence link in `## Evidence` carries the full SQL path.

**Calculation fallback — no numerator/denominator formula.** The
numerator/denominator template fits formula metrics (e.g. churn rate =
cancelled / active). It does NOT fit measures that are a direct
sum / count / window-accumulation of an upstream base value whose
business definition lives in an upstream model outside the current
evidence slice. For such metrics, describe instead:

(a) the aggregation and grain: e.g. "sum of the daily revenue value over
the month-to-date window, one row per store per calendar day";
(b) the reporting-period variants the model exposes (daily, MTD, QTD,
YTD, MoM, YoY, etc.);
(c) a note that the underlying "what counts as X" definition lives
upstream — link it as a `depends_on` concept if a concept page exists,
or add a `## Caveats` note if the upstream model is outside the
evidence slice.

Do NOT invent a numerator/denominator that is not present in the SQL.

**Routing note — materialized vs non-materialized.** The formula
template (numerator/denominator) and the fallback prose
(aggregation + grain + period-variants) above apply ONLY to
**non-materialized metrics** — metrics where query-time aggregation is
still required. When the §5 materialization check fires, `##
Calculation` instead states that the value is pre-computed and stored
(SELECT the mapped column directly — no query-time `GROUP BY`), and
points the reader to the `## Materialized Columns` table. See §5b for
the full output spec for that section.

**Aggregation form for derived-ratio / average metrics.** When a metric
is a **derived ratio or average** — its value is computed as one
aggregate divided by another (e.g. average order value = total sales ÷
number of invoices, conversion rate = conversions ÷ sessions, churn
rate = cancellations ÷ active customers) — `## Calculation` MUST
explicitly state the **aggregation form**:

- **Aggregate-level** (correct for population ratios):
  `SUM(numerator) / SUM(denominator)` — sum the parts independently,
  then divide. This is the standard form for business KPIs like AOV,
  conversion rate, and churn rate: it weights each row by its
  contribution to the total.
- **Average of row-level ratios** (per-entity average):
  `AVG(num / denom)` — compute the ratio for each individual row
  first, then average the ratios. This gives equal weight to every
  row regardless of its contribution.

These two forms produce **materially different answers** whenever row
sizes are unequal, which is the common case.

*Synthetic divergence example — Average Order Value (AOV):*

| Order | Sales | Invoices | Row-level ratio |
|-------|-------|----------|-----------------|
| A     | 1 000 | 2        | 500             |
| B     | 100   | 10       | 10              |

- **Aggregate-level** AOV: `SUM(1000+100) / SUM(2+10)` = 1 100 / 12 ≈ **91.7**
- **Avg of row-level ratios**: `AVG(500, 10)` = **255.0**

A text-to-SQL consumer that sees only "AOV = sales / invoices" cannot
determine which form to use. **The metric page's `## Calculation`
section is the authoritative definition.** State it explicitly:
> "AOV = `SUM(order_value) / SUM(invoice_count)` — aggregate-level;
> do NOT use `AVG(order_value / invoice_count)`."

This requirement applies to non-materialized metrics only. For
materialized metrics (materialization check fired — §5b), the
aggregation form was resolved at build time; note the form in
`## Caveats` if it is non-obvious, but do NOT re-specify it as a
query-time formula.

---

## 5b. Materialized Columns Output (column cards)

**When to emit.** Add this section to the metric page only when the
§5 materialization check fired (anchor signal 2 "column forest" OR
signal 4 "pre-aggregated grain" is present — see §5 materialization
check routing block). Omit the section entirely for non-materialized
metrics. (This spec section produces the bare `## Materialized Columns`
heading in the output metric page — §10b shows a complete worked
example.)

**One-page rule is unchanged.** This section enriches the existing
single page; it does NOT create a new page type and does not fork the
metric into multiple pages. The "one metric = one page" rule from §1
still holds.

**Body-only.** This section belongs in the page body — it does NOT go
into frontmatter. No new frontmatter fields are needed or allowed.

### Table shape

The section contains a markdown table mapping each period/segment
variant to the physical column a consumer should SELECT. The table
MUST use exactly these four columns, in this order, to match SCHEMA.md:

```markdown
| Variant | Model | Column | Grain |
|---------|-------|--------|-------|
| MTD | mart_store_metrics | gmv_mtd | one row per store per calendar day |
| YTD | mart_store_metrics | gmv_ytd | one row per store per calendar day |
```

Column definitions:

| Column | Meaning |
|--------|---------|
| **Variant** | The business period or segment view the column represents — e.g. "MTD", "YTD", "online channel", "total". One row per distinct variant. |
| **Model** | The dbt model (mart) that physically holds the column. Use the model's short name (not its `unique_id`). |
| **Column** | The exact physical column name to `SELECT` from that model. |
| **Grain** | What one row of that column represents — e.g. "one row per store per calendar day". Matches the model's primary-key dimensions. |

### Forest-compression rule

When the physical columns follow a **regular naming pattern** (e.g.
`gmv_{period}_{segment}`), do NOT enumerate every combination as a
separate table row. Instead, capture the **pattern plus the enumerated
allowed dimension values** in two rows (or a short prose block above
the table):

```markdown
**Column pattern**: `gmv_{period}_{segment}` in model `mart_store_metrics`

**Dimension values**:
- `period` ∈ {daily, mtd, qtd, ytd, mom, yoy, l30d, l7d}
- `segment` ∈ {total, online, offline, b2b, b2c}

**Grain**: one row per store per calendar day.

To SELECT: `gmv_{period}_{segment}` where `{period}` and `{segment}`
are substituted from the lists above. Example: `gmv_mtd_online`.
```

Enumerate columns individually (one row per variant) ONLY when the
naming is irregular — meaning variants do not share a common template
and the allowed dimension values cannot be expressed as a compact list.

**Why the compression rule matters.** A mart model can expose 5 period
windows × 10 segment values = 50 columns for one metric. Listing all
50 rows (a) makes the page unreadably long, (b) violates §1's
"don't fork near-duplicate pages" spirit, and (c) actually hurts
text-to-SQL: a generator that sees the **pattern** `gmv_{period}_{segment}` +
the allowed dimension lists can infer any column name reliably, whereas
a 50-row table tempts it to copy a concrete example that may not match
the requested period/segment. The pattern + dimension lists is
therefore both more concise AND more generalizable.

### Calculation section consistency

When this section is present, `## Calculation` must be written as
follows for the materialized variants:

> The value is pre-computed and stored in the mart at build time.
> To retrieve it, SELECT the appropriate column from the
> `## Materialized Columns` table below — no query-time aggregation
> or `GROUP BY` is needed.

Do NOT author a numerator/denominator formula or aggregation-prose
fallback for the materialized variants. The formula templates in §5
apply only to non-materialized metrics.

---

## 6. Caveats Section

Write `## Caveats` for anything that can surprise a consumer of the metric:

- Known data-quality gaps (e.g., "trials before 2023-01 are excluded
  because the `trial_started_at` column was not backfilled").
- Test coverage from evidence: which schema.yml tests guard the
  underlying model (not_null, unique, accepted_values).
- Currency / timezone handling, if relevant.
- Lag: does this metric reflect near-real-time data or a daily snapshot?
- **Date/period-column temporal semantics** — for any date or period
  column in the metric's grain, record:
  1. **Future-extension**: does the period column extend into the
     future? Forecast models, forward revenue-recognition (e.g. SRR/MRR
     amortized over contract length), amortization schedules, and
     calendar-spine tables all produce forward-dated rows — so
     `MAX(period_col)` returns a far-future date, NOT the latest actual
     period. If this applies, note it explicitly, e.g.: *"report_month
     extends into the future because SRR is amortized forward over
     contract length; use a `CURRENT_DATE`-anchored filter for
     'current/last month', not `MAX(report_month)`."* Detect from SQL: a
     `date_spine`, `generate_series`, or forward-amortization CTE
     pattern signals future-dating; note it in schema.yml if found.
  2. **Column kind**: is it a snapshot date (the dbt run date the row
     was captured), an event date (when something happened), or a
     recognition/accrual period (the accounting period revenue is
     assigned to)? State which, because the answer changes how
     "as of last month" queries should be written.

Source caveats from evidence model pages (`columns[].tests`,
`generic_tests`, `## Description`, inline SQL comments).

---

## 7. Relationships Section (typed edges)

Write `## Relationships` in the page body and the `relationships:`
frontmatter block. The two MUST be in sync.

Two edge types for metrics:

### 7a. `measures` edge — metric → entity (the measurement grain)

Every metric measures something over an entity. The GROUP BY grain of the
aggregation determines the target entity.

- `type: measures`
- `target:` the entity page this metric aggregates over (relative path
  from the `metrics/` folder: `../entities/<entity-slug>.md`)
- `note:` the GROUP BY key(s) in plain language

Example: a monthly churn rate grouped by customer maps to a `measures`
edge targeting `../entities/customer.md`.

If the metric measures over multiple entities (e.g., revenue per customer
per product), emit one `measures` edge per entity.

**Date/time grain — no single business entity.** When the GROUP BY grain
is a date/time dimension rather than a business entity (e.g. the model
aggregates across the whole population and groups only by `date`), describe the
time grain and population in the `note` field instead:
`note: "daily grain — aggregated across the whole population"`. If a clear
business population entity exists (e.g. Store), still target it and
append the time-grain detail to `note`. If no clear entity exists,
target the most relevant entity available with the grain noted.

**Entity not yet distilled.** If the target entity page does not exist yet
(the entity is outside the current evidence slice), follow SCHEMA's
*Dangling edge targets* rule (`assets/SCHEMA.md`, Relationships spec): emit
the `measures` edge AND create a `status: seed` stub page for the target so
the markdown link resolves. Do NOT leave a broken link or drop the edge.

### 7b. `depends_on` edge — metric → concept (algorithm dependency)

When the metric's calculation depends on a cross-cutting business rule
that is also modelled as a `knowledge-concept` page, record the dependency.

- `type: depends_on`
- `target:` the concept page (`../concepts/<concept-slug>.md`)
- `note:` why the metric depends on this rule (one line)

Example: churn rate depends on the "active customer" definition because
the denominator is the active-customer count. Record this as
`depends_on → [Active Customer](../concepts/active-customer.md)`.

**Do NOT add `evidence`-type edges to `relationships:`.** Evidence links
go only in `derived_from:` frontmatter and `## Evidence` body section
(SCHEMA.md: "Do NOT double-encode evidence edges").

---

## 8. Frontmatter

All metric pages use `type: knowledge-metric`. Required fields:

```yaml
---
type: knowledge-metric
title: <Human-Readable Metric Name>
status: developing          # seed | developing | mature | archived
summary: "<≤200 chars — one-line business meaning>"
updated: <YYYY-MM-DD>
derived_from:
  - model.<project>.<evidence_model>    # unique_id of the model(s) this metric is distilled from
relationships:
  - type: measures
    target: ../entities/<entity-slug>.md
    note: "<GROUP BY grain description>"
  - type: depends_on                    # only if a concept dependency exists
    target: ../concepts/<concept-slug>.md
    note: "<why the metric depends on this concept>"
last_changed_by: "<commit SHA or PR#>"
tags: []
stale: false
stale_at: null
stale_reason: null
---
```

### Alias capture for project-language retrieval (fully automatic)

During distillation, automatically populate the `aliases:` frontmatter list
— no human step required. Collect terms you wrote into this page's body that
a query author might search for but that:

- **(a)** do NOT appear in the page's `summary`, AND
- **(b)** an LLM could NOT bridge from the summary alone.

For metrics these are typically: project-specific metric / GL codes (e.g.
`422001`), project abbreviations (e.g. `NSDD`, `FSD`), hierarchy levels
(`l3`–`l6`), and non-obvious project synonyms (e.g. `流水分潤`). EXCLUDE:
terms already in the title or summary, generic words, and anything an LLM
would naturally infer from the summary.

**When uncertain, prefer inclusion — a false-positive alias costs a prune; a
missed alias is permanent.**

Also set `title_local`: this metric's title in the project's working language.
Use the exact term as it appears in the project's schema.yml descriptions or
internal documentation — not a translation of the English title. Set to `null`
if the project is English-only.

Both fields are emitted automatically on every `init` and `refresh` run; a
human may prune `aliases` later (pruning is never required, but never add back
a term that was intentionally removed).

`derived_from` must list the `unique_id` of every evidence model that
contains the metric computation. This is the freshness anchor: refresh
flags the page stale if any listed unique_id changes.

Slug: kebab-case from the business `title`, not the SQL column name.
Examples: `monthly-recurring-revenue.md`, `customer-churn-rate.md`,
`gross-merchandise-value.md`.

---

## 9. Evidence Section

Write `## Evidence` as a bullet list of links to the `_evidence/` model
pages the metric was distilled from:

```markdown
## Evidence
- [fct_mrr](../_evidence/models/fct_mrr.md)
- [stg_subscriptions](../_evidence/models/stg_subscriptions.md)
```

Paths are relative from the `metrics/` folder. Use `../_evidence/models/`
prefix. One bullet per `derived_from` model.

---

## 10. Worked Example — Customer Churn Rate

This example shows a complete metric page distilled from synthetic
evidence (no MetricFlow — SQL-derivation branch).

**Synthetic evidence context:**
- `fct_churn_monthly.sql` computes monthly churn. Its compiled SQL
  contains `COUNT(DISTINCT customer_id)` with a `WHERE cancelled_at
  BETWEEN ...` filter and a `GROUP BY date_trunc('month', period_start)`.
- `stg_subscriptions.sql` stages raw subscription events. The schema.yml
  description on `fct_churn_monthly` says: "Monthly churn rate per
  customer cohort. Denominator is active customers at month start;
  numerator is cancellations in the month."
- Evidence `unique_ids`:
  - `model.acme.fct_churn_monthly`
  - `model.acme.stg_subscriptions`
- The concept page `active-customer.md` exists under `concepts/`
  (defines "active = had a paid subscription on the first day of the
  period").

**Output file**: `.dbt-wiki/metrics/customer-churn-rate.md`

```markdown
---
type: knowledge-metric
title: Customer Churn Rate
status: developing
summary: "Fraction of active customers who cancelled in a given month; monthly cadence, per-customer grain."
updated: 2026-06-01
derived_from:
  - model.acme.fct_churn_monthly
  - model.acme.stg_subscriptions
relationships:
  - type: measures
    target: ../entities/customer.md
    note: "GROUP BY customer_id — one rate per customer cohort per month"
  - type: depends_on
    target: ../concepts/active-customer.md
    note: "denominator uses the active-customer definition (paid sub on period start)"
last_changed_by: "PR #000"
tags: ["finance", "retention"]
stale: false
stale_at: null
stale_reason: null
aliases:
  - churn_rate         # SQL column name in fct_churn_monthly
  - pct_churned        # shorthand used in schema.yml description
title_local: null      # synthetic example — project is English-only
---

## Definition

Measures the fraction of customers who were active at the start of a
month and cancelled their subscription during that month. A rising churn
rate signals that the product is retaining customers less effectively.
Reported as a percentage on a monthly cadence.

## Calculation

Churn rate = (customers who cancelled in the month) / (customers active
at the first day of the month).

The denominator counts distinct `customer_id` values that held an active
paid subscription on the first day of the measurement month (per the
active-customer concept — see Relationships). The numerator counts
distinct `customer_id` values whose `cancelled_at` timestamp falls within
that calendar month.

Customers who cancelled and reactivated within the same calendar month
are excluded from the numerator (they do not represent net churn for the
period). The calculation is performed monthly; no intra-month cadence
is supported.

## Caveats

- Subscription records before 2022-01-01 are excluded: the
  `subscription_started_at` column was not backfilled for legacy imports.
- Trial accounts (where `plan_type = 'trial'`) are excluded from both
  numerator and denominator; only paid subscriptions are counted.
- The `stg_subscriptions` model has a `not_null` test on `customer_id`
  and a `unique` test on `subscription_id`; no known null gaps in
  production as of last schema.yml audit.
- Metric reflects a daily batch snapshot, not real-time data. Lag is
  typically one business day.

## Relationships

- measures → [Customer](../entities/customer.md) — GROUP BY customer_id grain
- depends_on → [Active Customer](../concepts/active-customer.md) — denominator definition

## Evidence

- [fct_churn_monthly](../_evidence/models/fct_churn_monthly.md)
- [stg_subscriptions](../_evidence/models/stg_subscriptions.md)
```

---

## 10b. Worked Example — Store GMV (Materialized Metric)

This example shows a complete metric page for a **pre-materialized**
metric — one where the period variants are already physical columns in
a mart model and no query-time aggregation is needed.

**Synthetic evidence context:**
- `rpt_store_gmv_daily.sql` is a wide, pre-aggregated reporting model
  in `models/reporting/`. Its compiled SQL has no top-level `GROUP BY`
  on measure columns — the aggregation was performed in an upstream CTE.
  One row per store per calendar day.
- The model exposes a **column forest**: `gmv_mtd`, `gmv_qtd`,
  `gmv_ytd`, `gmv_mom`, `gmv_yoy`, `gmv_online`, `gmv_total` (7
  sibling columns sharing the `gmv_` base measure name) — anchor
  signal 2 fires.
- The schema.yml description on `gmv_mtd` reads: "Month-to-date gross
  merchandise value as of the reporting date (pre-computed at build
  time)." This confirms a stored value (signal 3, corroborating).
- Evidence `unique_ids`:
  - `model.acme.rpt_store_gmv_daily`
- No concept dependency: GMV is defined as total order value; no
  cross-cutting concept page exists in this evidence slice.

**Materialization detection outcome:**
- Signal 2 (column forest, 7 ≥ 5 siblings) → **fires**.
- Routing: add `## Materialized Columns` section; write `## Calculation`
  as SELECT-only (no formula).

**Output file**: `.dbt-wiki/metrics/gross-merchandise-value.md`

```markdown
---
type: knowledge-metric
title: Gross Merchandise Value
status: developing
summary: "Total value of orders processed through the platform; pre-computed period variants (MTD/QTD/YTD/MoM/YoY) stored in the store GMV daily mart."
updated: 2026-06-02
derived_from:
  - model.acme.rpt_store_gmv_daily
relationships:
  - type: measures
    target: ../entities/store.md
    note: "one row per store per calendar day — store_id + date grain"
last_changed_by: "PR #000"
tags: ["finance", "gmv"]
stale: false
stale_at: null
stale_reason: null
---

## Definition

Gross Merchandise Value (GMV) is the total monetary value of all orders
placed through the platform within a reporting period, before any
deductions (returns, discounts, fees). It is the primary top-line volume
indicator for the platform. Reported per store on a daily snapshot basis,
with pre-built period-accumulation variants (MTD, QTD, YTD) and
growth-rate variants (MoM, YoY).

## Calculation

The value is pre-computed and stored in the mart at build time.
To retrieve it, SELECT the appropriate column from the
`## Materialized Columns` table below — no query-time aggregation
or `GROUP BY` is needed.

## Materialized Columns

| Variant | Model | Column | Grain |
|---------|-------|--------|-------|
| Period-to-date / growth views | rpt_store_gmv_daily | `gmv_{period}` — period ∈ {mtd, qtd, ytd, mom, yoy} | one row per store per calendar day |
| Channel segment | rpt_store_gmv_daily | `gmv_{segment}` — segment ∈ {total, online} | one row per store per calendar day |

To SELECT: substitute the appropriate value from the allowed set in the
Column cell. For example, to retrieve month-to-date GMV for store 42 on
2026-06-01: `SELECT gmv_mtd FROM rpt_store_gmv_daily WHERE store_id = 42 AND date = '2026-06-01'`.
To retrieve online-channel GMV for the same store and date:
`SELECT gmv_online FROM rpt_store_gmv_daily WHERE store_id = 42 AND date = '2026-06-01'`.

## Caveats

- GMV reflects the order-placed value; it does not net out returns or
  cancellations. See the `rpt_store_gmv_daily` model description for
  any exclusion logic applied upstream.
- `gmv_mom` and `gmv_yoy` are NULL for the first month/year of a
  store's history (no prior period to compare against).
- Model is a daily snapshot; the most recent row reflects the state as
  of the last successful dbt run (typically one business-day lag).

## Relationships

- measures → [Store](../entities/store.md) — store_id + date grain

## Evidence

- [rpt_store_gmv_daily](../_evidence/models/rpt_store_gmv_daily.md)
```

---

## 11. Summary of Decision Rules

| Situation | Action |
|---|---|
| `manifest["semantic_models"]` present (gate on this key ALONE — see §2a; a bare `metrics` key without `semantic_models` is legacy dbt ≤1.5, NOT MetricFlow) | MetricFlow ingest branch (§2b) — do not re-derive |
| No MetricFlow, mart model with `SUM`/`COUNT` + `GROUP BY` | SQL-derivation branch (§3) |
| Multiple metrics in one model | One page per distinct business measure; share `derived_from` |
| Reporting-period variants (daily/MTD/QTD/YTD/MoM/YoY) of one measure | ONE metric page; describe variants in `## Calculation` — never fork per time window (§1) |
| Parallel segment models (e.g. total vs single-channel revenue) | ONE metric page; list both models in `derived_from:`; segment split → `concepts/` page + `depends_on` edge (§3b) |
| Metric variants already materialized as pre-built mart columns (anchor signal 2 "column forest" OR signal 4 "pre-aggregated grain" fires — §5 materialization check) | Materialization branch: emit `## Materialized Columns` card (§5b); `## Calculation` = SELECT pre-built column, no formula, no query-time `GROUP BY` |
| Metric has no numerator/denominator formula (pure aggregation/window, materialization does NOT fire) | Fallback: describe aggregation + grain + period variants; note upstream definition; do NOT invent formula (§5) |
| `measures` edge — date/time grain, no clear business entity | Use `note: "daily grain — aggregated across the whole population"`; target closest entity if one exists (§7a) |
| `measures` edge — target entity not yet distilled | Emit the edge anyway AND create a `status: seed` stub for the target (SCHEMA dangling-target rule); append `"(entity not yet distilled)"` to `note` (§7a) |
| Metric depends on a concept page | Add `depends_on` edge in both frontmatter and `## Relationships` |
| Evidence link placement | `derived_from:` + `## Evidence` only — never in `relationships:` |
| Slug | kebab-case from business title, not SQL column name |
| `summary` field | ≤200 chars, one line, plain language |
